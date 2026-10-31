"""Pixel Works v2.5: opt-in stable studio identities and lossless migration snapshot.

This is a transitional registry, NOT a replacement for the existing project
execution adapters yet. GET/startup never writes. The browser must explicitly
approve creation. Reports and project STAFF.json remain untouched.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import threading
from datetime import datetime, timezone
from urllib.parse import urlparse

LOCK = threading.RLock()
UID = re.compile(r'^pw-[a-f0-9]{20}$')
SLUG = re.compile(r'^[a-z0-9][a-z0-9-]{1,49}$')
APPROVAL = 'CREATE_GLOBAL_STAFF_V25'


def studio_folder(srv):
    root = srv.ROOT / 'studio-v013'
    if root.is_symlink(): raise ValueError('Osäker studiokatalog')
    return root


def registry_file(srv):
    return studio_folder(srv) / 'PEOPLE_V25.json'


def read_registry(srv):
    f = registry_file(srv)
    if f.is_symlink(): raise ValueError('Osäker personregisterfil')
    if not f.exists(): return None
    data = json.loads(f.read_text(encoding='utf-8'))
    if not isinstance(data,dict) or data.get('schema') != 1 or not isinstance(data.get('people'),list):
        raise ValueError('Felaktigt globalt personregister')
    ids = [p.get('studio_id') for p in data['people'] if isinstance(p,dict)]
    if len(ids) != len(data['people']) or len(set(ids)) != len(ids) or not all(isinstance(x,str) and UID.fullmatch(x) for x in ids):
        raise ValueError('Dubbletter eller ogiltig identitet i personregistret')
    return data


def source_roster(srv):
    """Observe existing verified staff/UIDs, never guess identity from names."""
    import pw_v013
    info = pw_v013.inventory(srv)
    if not isinstance(info,dict) or not isinstance(info.get('staff'),list) or not isinstance(info.get('projects'),list):
        raise ValueError('Det äldre personalregistret kunde inte läsas')
    staff = info['staff']
    ids = [p.get('studio_id') for p in staff]
    if any(not isinstance(i,str) or not UID.fullmatch(i) for i in ids) or len(set(ids)) != len(ids):
        raise ValueError('Personal-ID kolliderar. Migreringen stoppas för manuell kontroll.')
    return info


def _alias(p):
    return {'project_id':str(p['project_id']),'agent_id':str(p['agent_id'])}


def _record(p,when):
    return {'studio_id':p['studio_id'], 'name':str(p.get('name') or 'Medarbetare'),
            'role':str(p.get('role') or ''), 'role_type':str(p.get('role_type') or ''),
            'origin':_alias(p), 'aliases':[_alias(p)], 'registered_at':when}


def preview(srv):
    with LOCK:
        info = source_roster(srv)
        data = read_registry(srv)
        found = {p['studio_id']:p for p in info['staff']}
        saved = {p['studio_id']:p for p in data['people']} if data else {}
        extra = [p for k,p in found.items() if k not in saved]
        absent = [p for k,p in saved.items() if k not in found]
        moved = []
        if data:
            for k,p in found.items():
                if k in saved and _alias(p) not in saved[k].get('aliases',[]):
                    moved.append({'studio_id':k,'name':p['name'],'project_id':p['project_id']})
        return {'registered':data is not None,'people_count':len(data['people']) if data else 0,
                'current_count':len(info['staff']),'projects':info['projects'],
                'staff':[{k:p.get(k) for k in ('studio_id','agent_id','name','role','role_type','project_id','project_name','busy')}
                         for p in info['staff']],
                'new_count':len(extra), 'missing_count':len(absent),'changed_assignments':moved,
                'needs_reconciliation':bool(extra or absent or moved),
                'registry_created_at':data.get('created_at') if data else None,
                'backup_ref':data.get('backup_ref') if data else None,
                'mode':'global-identities / project-execution-compatibility',
                'notice':'Ett personregister för hela Pixel Works. Projektens arbetsmotor och rapporter använder ännu gamla projektalias.'}


def _safe_copy_sources(srv,folder,projects):
    """Backup bytes exactly, never follow a symlink; reject missing source STAFF."""
    manifest=[]
    for p in projects:
        slug = p.get('id')
        if not isinstance(slug,str) or not SLUG.fullmatch(slug):raise ValueError('Ogiltigt projekt i säkerhetskopian')
        base = srv.PROJECTS / slug / 'management'
        if base.is_symlink() or not base.is_dir():raise ValueError('Saknar säker projektmapp '+slug)
        backup = folder / slug
        backup.mkdir(mode=0o700)
        for name in ('STAFF.json','SKILL_SETTINGS.json','STATION_ASSIGNMENTS.json'):
            original = base / name
            if original.is_symlink():raise ValueError('Symbolisk länk i projektdata '+slug+'/'+name)
            if not original.exists():
                # Fresh shared-studio projects can legitimately have no staff
                # file until someone is assigned. Empty means nothing to back up.
                if name=='STAFF.json' and srv.staff_read(slug):
                    raise ValueError('Saknar personalfil för befintlig personal: '+slug)
                continue
            if not original.is_file():raise ValueError('Ogiltig projektfil: '+slug+'/'+name)
            raw = original.read_bytes()
            # Avoid accidentally copying an unexpected massive file into the registry.
            if len(raw)>4_000_000:raise ValueError('Personalfil för stor för säkerhetskopia: '+slug+'/'+name)
            target=backup/name
            with target.open('xb') as out:out.write(raw)
            target.chmod(0o600)
            manifest.append({'project_id':slug,'file':name,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
    return manifest


def _atomic_new(path,value):
    """Create exactly once; fail closed on concurrent writers."""
    if path.exists() or path.is_symlink():raise ValueError('Personregistret finns redan; inga filer har ersatts.')
    raw=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as out:out.write(raw);out.flush();os.fsync(out.fileno())


def activate(srv,payload):
    if not isinstance(payload,dict) or payload.get('approval')!=APPROVAL:
        raise ValueError('Välj uttryckligen Konvertera personalen i Min studio')
    with LOCK:
        if read_registry(srv) is not None:
            return {'created':False,'already_registered':True,**preview(srv)}
        info=source_roster(srv)
        expected=payload.get('expected_ids')
        ids=sorted(p['studio_id'] for p in info['staff'])
        if not isinstance(expected,list) or expected!=ids:
            raise ValueError('Personallistan har ändrats sedan du granskade den. Öppna konverteringen igen.')
        if not ids:raise ValueError('Ingen personal att registrera. Inga filer skapade.')
        base=studio_folder(srv)
        base.mkdir(mode=0o700,parents=True,exist_ok=True)
        if base.is_symlink():raise ValueError('Osäker studiokatalog')
        backup_parent=base/'staff-backups-v25'
        if backup_parent.is_symlink():raise ValueError('Osäker backupkatalog')
        backup_parent.mkdir(mode=0o700,exist_ok=True)
        stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        tag=stamp+'-'+secrets.token_hex(4)
        backup=backup_parent/tag
        backup.mkdir(mode=0o700)
        try:
            files=_safe_copy_sources(srv,backup,info['projects'])
            now=datetime.now(timezone.utc).isoformat()
            data={'schema':1,'created_at':now,'identity_policy':'one-studio-person-per-studio_id; names are not identities',
                  'compatibility':'project STAFF.json remains execution adapter',
                  'backup_ref':str(backup.relative_to(srv.ROOT)),
                  'people':[_record(p,now) for p in info['staff']]}
            _atomic_new(backup/'MANIFEST.json',{'schema':1,'created_at':now,'source_files':files,'ids':ids})
            _atomic_new(registry_file(srv),data)
        except BaseException:
            # Partial backup is kept for forensic recovery, but no project data changed.
            raise
        return {'created':True,**preview(srv)}


def install(srv):
    if getattr(srv,'_PW_GLOBAL_STAFF_V25',False):return
    srv._PW_GLOBAL_STAFF_V25=True
    handler=srv.Handler
    prior_get=handler.do_GET
    prior_post=handler.do_POST
    path='/api/pw-v025/global-staff'

    def do_GET(self):
        if urlparse(self.path).path!=path:return prior_get(self)
        if not self.allowed() or not self.auth():return self.reply(403,{'error':'Åtkomst nekad'})
        try:return self.reply(200,preview(srv))
        except (ValueError,OSError,TypeError) as exc:return self.reply(400,{'error':str(exc)[:300]})

    def do_POST(self):
        if urlparse(self.path).path!=path+'/activate':return prior_post(self)
        if not self.allowed() or not self.same_origin() or not self.auth():return self.reply(403,{'error':'Åtkomst nekad'})
        try:
            if self.headers.get('Content-Type','').split(';')[0].strip().lower()!='application/json':
                raise ValueError('Endast JSON tillåtet')
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=20000:raise ValueError('Ogiltig storlek på begäran')
            data=json.loads(self.rfile.read(size))
            result=activate(srv,data)
            return self.reply(200,result)
        except (ValueError,OSError,TypeError,json.JSONDecodeError) as exc:return self.reply(400,{'error':str(exc)[:300]})
    handler.do_GET=do_GET
    handler.do_POST=do_POST
