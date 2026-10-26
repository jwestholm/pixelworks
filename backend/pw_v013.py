"""Pixel Works 0.13: shared studio roster and safe, explicit project assignments.

The existing project workspaces, Game Bible, report files and job adapters remain
project-isolated. The studio presents all staff together; assignment moves only
the staff record (plus that person's skill overrides) after an explicit action.
No writes on GET, import or server startup. No external calls.
"""
from __future__ import annotations
import hashlib
import json
import re
import secrets
import threading
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

VERSION = '0.13.9'
GUARD = threading.RLock()
STAFF_UID = re.compile(r'^pw-[a-f0-9]{20}$')


def _id(project, worker_id):
    return 'pw-' + hashlib.sha256((project + '\0' + worker_id).encode()).hexdigest()[:20]


def _root(srv):
    folder = srv.ROOT / 'studio-v013'
    if folder.is_symlink(): raise ValueError('Osäker studiokatalog')
    return folder


def _settings(srv):
    file = _root(srv) / 'STUDIO.json'
    if file.is_symlink(): raise ValueError('Osäker studiofil')
    if not file.exists(): return {'schema':1, 'shared':False}
    data = json.loads(file.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('schema') != 1:
        raise ValueError('Ogiltig studiofil')
    return data


def _save(srv, file, value):
    if file.is_symlink(): raise ValueError('Osäker målsökväg')
    file.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if file.parent.is_symlink(): raise ValueError('Osäker katalog')
    tmp = file.with_name('.'+file.name+'.'+secrets.token_hex(6)+'.tmp')
    try:
        with tmp.open('x', encoding='utf-8') as out:
            json.dump(value, out, indent=2, ensure_ascii=False)
            out.write('\n')
        tmp.chmod(0o600)
        tmp.replace(file)
    finally:
        tmp.unlink(missing_ok=True)


def _projects(srv):
    if not srv.PROJECTS.is_dir(): return []
    result=[]
    for folder in sorted(srv.PROJECTS.iterdir()):
        if folder.is_symlink() or not folder.is_dir() or not re.fullmatch(r'[a-z0-9][a-z0-9-]{1,49}', folder.name): continue
        meta=folder/'project.json'
        if meta.is_symlink() or not meta.is_file(): continue
        try:
            item=json.loads(meta.read_text(encoding='utf-8'))
            if item.get('id') == folder.name and isinstance(item.get('name'),str):
                result.append({'id':folder.name,'name':item['name']})
        except (OSError,ValueError,TypeError,AttributeError): continue
    return result


def _has_jobs(srv, project, agent_id):
    with srv.LOCK:
        return any(j.get('project')==project and j.get('agent_id')==agent_id
                   and j.get('state') in ('queued','running') for j in srv.JOBS.values())


def inventory(srv):
    """Read-only inventory. Legacy employees are imported *virtually*."""
    with GUARD:
        projects=_projects(srv)
        people=[]
        ids=set()
        for project in projects:
            try:
                if srv.staff_file(project['id']).is_symlink():continue
                roster=srv.staff_read(project['id'])
            except (ValueError,OSError,TypeError):continue
            for p in roster:
                if not isinstance(p,dict) or not p.get('id'):continue
                uid=p.get('studio_id') or _id(project['id'],str(p['id']))
                if not STAFF_UID.fullmatch(uid):uid=_id(project['id'],str(p['id']))
                collision=uid in ids
                ids.add(uid)
                person={'studio_id':uid,'agent_id':p['id'],
                        'name':p.get('name','Medarbetare'),'role':p.get('role','Allroundare'),
                        'role_type':p.get('role_type','allround'),
                        'project_id':project['id'],'project_name':project['name'],
                        'station':p.get('station','cafe'),
                        'skills':p.get('skills') or {},
                        'busy':_has_jobs(srv,project['id'],p['id']),
                        'conflict':collision}
                people.append(person)
        settings=_settings(srv)
        return {'version':VERSION,'shared':bool(settings.get('shared')),
                'projects':projects,'staff':people,
                'staff_count':len(people),'project_count':len(projects),
                'migration': 'projektpersonal läses utan att ändras',
                'requires_attention':any(p['conflict'] for p in people),
                'pending_transfer':(_root(srv)/'TRANSFER_PENDING.json').exists()}


def activate(srv, payload):
    if payload.get('approval') != 'ENABLE_SHARED_STUDIO_V013':
        raise ValueError('Gemensam studio kräver ett aktivt användarval')
    with GUARD:
        current=_settings(srv)
        if current.get('shared'):return {'shared':True,'already_enabled':True}
        # Do not modify project staff or merge employees behind the user's back.
        data={'schema':1,'shared':True,'enabled_at':datetime.now(timezone.utc).isoformat(),
              'policy':'one-office-one-employee-one-assigned-project'}
        _save(srv,_root(srv)/'STUDIO.json',data)
        return {'shared':True,'already_enabled':False}


def _staff_file(srv,slug):
    file=srv.path_for(slug)/'management'/'STAFF.json'
    # Use the *engine-defined* path rather than assuming case/path.
    return srv.staff_file(slug)


def _skill_file(srv,slug):
    return srv.skill_settings_file(slug)


def transfer(srv,payload):
    """Move one employment to a target project, never its reports or code.

    Applies under the shared worker roster lock and stores rollback originals in
    a journal before touching either project's staff files. Any in-process error
    rolls back. A power-loss journal requires explicit recovery, never silent writes.
    """
    if payload.get('approval')!='ASSIGN_STUDIO_EMPLOYEE_V013':
        raise ValueError('Bekräfta projektbytet för den valda medarbetaren')
    uid=str(payload.get('studio_id') or '')
    if not STAFF_UID.fullmatch(uid): raise ValueError('Ogiltig personalidentitet')
    target=srv.validate_slug(str(payload.get('target_project') or ''))
    with GUARD:
        if not _settings(srv).get('shared'):raise ValueError('Aktivera gemensam studio innan du flyttar personal')
        projects={p['id'] for p in _projects(srv)}
        if target not in projects:raise ValueError('Målprojektet finns inte')
        journal=_root(srv)/'TRANSFER_PENDING.json'
        if journal.is_symlink() or journal.exists():raise ValueError('Ett tidigare personalbyte kräver kontroll innan nya byten')
        observed=[]
        for project in sorted(projects):
            if srv.staff_file(project).is_symlink():
                raise ValueError('Osäker personalfil i projekt '+project)
            for a in srv.staff_read(project):
                if not isinstance(a,dict):continue
                found=a.get('studio_id') or _id(project,str(a.get('id','')))
                if found==uid:observed.append((project,a))
        if len(observed)!=1:raise ValueError('Medarbetaren saknas eller finns i flera projekt. Ingen ändring gjord.')
        source,member=observed[0]
        if source==target:return {'moved':False,'studio_id':uid,'project_id':target,'reason':'Redan tilldelad detta projekt'}
        if _has_jobs(srv,source,member['id']):
            raise ValueError(member.get('name','Medarbetaren')+' arbetar fortfarande. Vänta på att arbetspasset avslutas.')
        for slug in (source,target):
            if srv.staff_file(slug).is_symlink(): raise ValueError('Osäker personalfil (symbolisk länk)')
        before_src=srv.staff_read(source)
        before_dst=srv.staff_read(target)
        if len(before_dst)>=24:raise ValueError('Målprojektets personalregister är fullt (24)')
        dest_ids={p['id'] for p in before_dst}
        new_id=member['id'] if member['id'] not in dest_ids else 'studio-'+secrets.token_hex(6)
        dest_member={**member,'id':new_id,'studio_id':uid,'station':'cafe'}
        new_src=[p for p in before_src if p['id'] != member['id']]
        new_dst=[*before_dst,dest_member]
        # Copy skill overrides without removing original project history.
        source_skill=_skill_file(srv,source);dest_skill=_skill_file(srv,target)
        if source_skill.is_symlink() or dest_skill.is_symlink():raise ValueError('Osäker skillfil')
        src_skills=json.loads(source_skill.read_text(encoding='utf-8')) if source_skill.exists() else {}
        dst_skills=json.loads(dest_skill.read_text(encoding='utf-8')) if dest_skill.exists() else {}
        if not isinstance(src_skills,dict) or not isinstance(dst_skills,dict):raise ValueError('Ogiltiga skills')
        new_skills={**dst_skills}
        if member['id'] in src_skills:new_skills[new_id]=src_skills[member['id']]
        backup={'source':source,'target':target,'studio_id':uid,
                'source_staff':before_src,'target_staff':before_dst,
                'target_skill':dst_skills,
                'started_at':datetime.now(timezone.utc).isoformat()}
        # Lock scheduler's worker registry throughout transfer to avoid
        # simultaneous staff reads between the two file replacements.
        with srv.LOCK:
            # Reject concurrent profile changes instead of replacing them
            # with a stale roster read earlier in this request.
            if srv.staff_read(source)!=before_src or srv.staff_read(target)!=before_dst:
                raise ValueError('Personalregistret ändrades under flytten. Försök igen.')
            if any(j.get('project')==source and j.get('agent_id')==member['id'] and j.get('state') in ('queued','running') for j in srv.JOBS.values()):
                raise ValueError('Arbetspasset startade precis. Försök senare.')
            _save(srv,journal,backup)
            try:
                # Destination first: no project is left without its worker if
                # disk writes fail. Any mid-operation error restores both.
                srv.staff_write(target,new_dst)
                srv.staff_write(source,new_src)
                if new_skills != dst_skills:_save(srv,dest_skill,new_skills)
            except Exception:
                try:
                    srv.staff_write(source,before_src)
                    srv.staff_write(target,before_dst)
                    if new_skills!=dst_skills:_save(srv,dest_skill,dst_skills)
                    journal.unlink(missing_ok=True)
                except Exception:
                    # Explicit repair required; don't pretend transaction succeeded.
                    pass
                raise
            journal.unlink()
        return {'moved':True,'studio_id':uid,'from_project':source,
                'project_id':target,'agent_id':new_id,'name':member.get('name','Medarbetare')}


def repair(srv,payload):
    """Explicit user-requested rollback of interrupted transfer."""
    if payload.get('approval')!='RESTORE_STUDIO_TRANSFER_V013':
        raise ValueError('Återställning kräver uttryckligt godkännande')
    with GUARD:
        journal=_root(srv)/'TRANSFER_PENDING.json'
        if journal.is_symlink() or not journal.is_file():raise ValueError('Ingen avbruten flytt hittades')
        b=json.loads(journal.read_text(encoding='utf-8'))
        src=srv.validate_slug(b['source']);dst=srv.validate_slug(b['target'])
        if src==dst:raise ValueError('Ogiltig journal')
        if srv.staff_file(src).is_symlink() or srv.staff_file(dst).is_symlink():
            raise ValueError('Osäker personalfil')
        if _skill_file(srv,dst).is_symlink():raise ValueError('Osäker skillfil')
        with srv.LOCK:
            if any(j.get('project') in (src,dst) and j.get('state') in ('queued','running') for j in srv.JOBS.values()):
                raise ValueError('Vänta tills aktiva arbetspass avslutats före återställning')
            # Backups only; no code, reports or Game Bible touched.
            srv.staff_write(src,b['source_staff']);srv.staff_write(dst,b['target_staff'])
            _save(srv,_skill_file(srv,dst),b['target_skill'])
            journal.unlink()
        return {'restored':True}


def install(srv):
    if getattr(srv,'_PW_V013',False):return
    srv._PW_V013=True;srv.APP_VERSION=VERSION
    # Ensure no new project quietly receives a second separate starter team
    # once the owner explicitly opted in to a single shared company.
    import pw_v01210
    original_seed=pw_v01210.seed_project_staff
    def seed(s,slug):
        if _settings(s).get('shared'):return []
        return original_seed(s,slug)
    pw_v01210.seed_project_staff=seed
    original_create=srv.create_project
    def create_project(payload):
        result=original_create(payload)
        if _settings(srv).get('shared'):
            result['starter_team_created']=False
            result['shared_studio']=True
        return result
    srv.create_project=create_project
    # Expose endpoints through existing local token/origin security, without
    # broadening the legacy static file allowlist or provider permissions.
    previous_get=srv.Handler.do_GET
    previous_post=srv.Handler.do_POST
    def do_GET(self):
        route=urlparse(self.path).path
        if route in ('/','/index.html'):
            previous_get(self)
            # HTML rewrite handled via previous response? Use explicit HTML
            # injection instead to avoid appending after already-sent bytes.
            return
        if route!='/api/pw-v013/studio':return previous_get(self)
        if not self.allowed() or not self.auth():return self.reply(403,{'error':'Ogiltig session'})
        try:return self.reply(200,inventory(srv))
        except (OSError,ValueError,TypeError) as e:return self.reply(400,{'error':str(e)[:240]})
    def do_POST(self):
        route=urlparse(self.path).path
        if route not in ('/api/pw-v013/studio/enable','/api/pw-v013/studio/transfer','/api/pw-v013/studio/repair'):
            return previous_post(self)
        if not self.allowed() or not self.auth() or not self.same_origin():
            return self.reply(403,{'error':'Otillåten begäran'})
        n=self.headers.get('Content-Length','')
        if not n.isdecimal() or not 0<int(n)<=8192:return self.reply(413,{'error':'Ogiltig begäran'})
        try:payload=json.loads(self.rfile.read(int(n)))
        except (ValueError,UnicodeError):return self.reply(400,{'error':'Ogiltig JSON'})
        if not isinstance(payload,dict):return self.reply(400,{'error':'JSON-objekt förväntas'})
        try:
            result=(activate(srv,payload) if route.endswith('/enable') else
                    transfer(srv,payload) if route.endswith('/transfer') else repair(srv,payload))
            return self.reply(200,result)
        except (ValueError,OSError,TypeError,KeyError) as e:return self.reply(400,{'error':str(e)[:300]})
    srv.Handler.do_GET=do_GET
    srv.Handler.do_POST=do_POST
    import pw_v0132
    pw_v0132.install(srv)
    import pw_v0133
    pw_v0133.install(srv)
    import pw_v0134
    pw_v0134.install(srv)
    import pw_v0135
    pw_v0135.install(srv)
    import pw_v0138
    pw_v0138.install(srv)
