"""Pixel Works v2.7: opt-in authoritative global workforce, legacy execution bridge.

No migration on GET/import/startup. No project STAFF.json writes after activation;
source STAFF.json files remain intact as archival recovery inputs. Old project job
IDs remain aliases of the same stable studio person. No external AI calls.
"""
from __future__ import annotations
import copy
import hashlib
import json
import os
import re
import secrets
import threading
from datetime import datetime, timezone
from urllib.parse import urlparse

LOCK=threading.RLock()
UID=re.compile(r'^pw-[a-f0-9]{20}$')
SLUG=re.compile(r'^[a-z0-9][a-z0-9-]{1,49}$')
APPROVAL='ACTIVATE_GLOBAL_WORKFORCE_V27'
ACTIVE_STATES={'queued','running','claimed','in_progress'}
ALLOWED={'lead','code','research','qa','cafe','meeting','docs','music','voice','art'}


def workforce_file(srv):
    folder=srv.ROOT/'studio-v013'
    if folder.is_symlink():raise ValueError('Osäker studiokatalog')
    f=folder/'WORKFORCE_V27.json'
    if f.is_symlink():raise ValueError('Osäker arbetsstyrkefil')
    return f


def _read(srv):
    f=workforce_file(srv)
    if not f.exists():return None
    data=json.loads(f.read_text(encoding='utf-8'))
    if not isinstance(data,dict) or data.get('schema')!=1 or not isinstance(data.get('people'),list):
        raise ValueError('Felaktigt globalt arbetsregister; arbetsmotorn stoppas')
    members=data['people'];ids=[x.get('studio_id') for x in members if isinstance(x,dict)]
    if len(ids)!=len(members) or len(ids)!=len(set(ids)) or any(not isinstance(x,str) or not UID.fullmatch(x) for x in ids):
        raise ValueError('Kolliderande global personalidentitet')
    for p in members:
        if not isinstance(p.get('profile'),dict) or not isinstance(p.get('aliases'),dict):
            raise ValueError('Ogiltig global personalpost')
        project=p.get('project_id')
        if project is not None and (not isinstance(project,str) or not SLUG.fullmatch(project)):
            raise ValueError('Ogiltig projekttilldelning')
    return data


def _write(srv,data):
    file=workforce_file(srv)
    if not file.parent.is_dir() or file.parent.is_symlink():raise ValueError('Studiofilens katalog saknas')
    raw=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    if len(raw)>8_000_000:raise ValueError('Personregistret är för stort')
    tmp=file.with_name('.'+file.name+'.'+secrets.token_hex(7)+'.tmp')
    fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(fd,'wb') as out:
            out.write(raw);out.flush();os.fsync(out.fileno())
        os.replace(tmp,file)
    finally:tmp.unlink(missing_ok=True)


def _alias(uid,slug,known=None):
    if known:return known
    return 'studio-'+hashlib.sha256((uid+'\0'+slug).encode()).hexdigest()[:12]


def _active(srv,project,agent_id):
    with srv.LOCK:
        jobs=list(srv.JOBS.values())
    if any(j.get('project')==project and j.get('agent_id')==agent_id
           and j.get('state') in ACTIVE_STATES for j in jobs):return True
    try:
        orders=srv.orders_read(project)
        if any(o.get('status') in ACTIVE_STATES and o.get('agent_id') in (None,'',agent_id) for o in orders):
            return True
    except (OSError,ValueError,AttributeError):
        # Don't silently bypass corrupt order files while moving a person.
        raise ValueError('Arbetsorder kunde inte kontrolleras för '+project)
    return False


def _project_list(srv):
    import pw_v013
    return pw_v013._projects(srv)


def preview(srv):
    import pw_global_staff_v25 as v25
    with LOCK:
        snapshot=v25.read_registry(srv)
        data=_read(srv)
        if data:
            people=[{'studio_id':p['studio_id'],'name':p['profile'].get('name','Medarbetare'),
                     'role':p['profile'].get('role',''),'provider':p['profile'].get('provider',''),
                     'project_id':p.get('project_id'),'station':p['profile'].get('station','cafe'),
                     'agent_id':p['aliases'].get(p['project_id']) if p.get('project_id') else None,
                     'dismissed':bool(p.get('dismissed'))} for p in data['people']]
        else:
            observed=v25.source_roster(srv)
            people=[{'studio_id':p['studio_id'],'name':p['name'],'role':p['role'],
                     'project_id':p['project_id'],'agent_id':p['agent_id'],'dismissed':False}
                    for p in observed['staff']]
        return {'active':data is not None,'registered':bool(snapshot),
                'revision':data.get('revision') if data else None,
                'people':people,'count':sum(not x['dismissed'] for x in people),
                'projects':_project_list(srv),
                'notice':('Global personal är primär källa för uppdragsmotorn. '
                          'Äldre personalfiler sparas som orörda historiska kopior.' if data else
                          'Det globala arbetsregistret är ännu inte aktiverat. Ingen ändring sker förrän du godkänner.')}


def activate(srv,payload,old_read,old_skills=None):
    import pw_global_staff_v25 as v25
    if not isinstance(payload,dict) or payload.get('approval')!=APPROVAL:
        raise ValueError('Aktivering kräver ditt uttryckliga godkännande i Min studio')
    with LOCK:
        if _read(srv):return {'created':False,**preview(srv)}
        registered=v25.read_registry(srv)
        if not registered:raise ValueError('Skapa globalt personregister v2.5 först')
        info=v25.source_roster(srv)
        ids=sorted(p['studio_id'] for p in info['staff'])
        if payload.get('expected_ids')!=ids:
            raise ValueError('Personallistan ändrades sedan du granskade den. Öppna rutan igen.')
        recorded=sorted(p['studio_id'] for p in registered['people'])
        if ids!=recorded:raise ValueError('Personregistret skiljer sig från aktuell personal; ingen aktivering')
        # No cutover while a job is live, even if the browser itself is closed.
        with srv.LOCK:
            if any(j.get('state') in ACTIVE_STATES for j in srv.JOBS.values()):
                raise ValueError('Vänta tills pågående AI-arbetspass är färdiga före bytet')
        for project in _project_list(srv):
            try:
                if any(o.get('status') in ('running','claimed','in_progress') for o in srv.orders_read(project['id'])):
                    raise ValueError('Pågående arbetsorder i '+project['name']+' – avsluta den först')
            except (ValueError,OSError):raise
        now=datetime.now(timezone.utc).isoformat()
        people=[]
        for p in info['staff']:
            slug=p['project_id'];member=next((x for x in old_read(slug) if x.get('id')==p['agent_id']),None)
            if not member:raise ValueError('En personalpost försvann under aktiveringen')
            if member.get('studio_id') and member['studio_id']!=p['studio_id']:
                raise ValueError('Globalt ID skiljer sig från personalfilen')
            initial_skills=(old_skills(slug).get(p['agent_id'],{}) if callable(old_skills) else {})
            people.append({'studio_id':p['studio_id'],'project_id':slug,
                           'aliases':{slug:p['agent_id']},'profile':{**copy.deepcopy(member),'studio_id':p['studio_id']},
                           'registered_at':now,'dismissed':False,
                           'skill_overrides':copy.deepcopy(initial_skills)})
        data={'schema':1,'revision':1,'activated_at':now,
              'source_backup_ref':registered.get('backup_ref'),
              'storage_policy':'global-authoritative; legacy STAFF.json read-only recovery',
              'people':people}
        if workforce_file(srv).parent.is_symlink():raise ValueError('Osäker studiokatalog')
        _write(srv,data)
        return {'created':True,**preview(srv)}


def _project_roster(srv,slug,old_read):
    # Always check slug/project structure as the original engine would.
    original=old_read(slug)
    data=_read(srv)
    if data is None:return original
    roster=[];identities=set()
    for person in data['people']:
        if person.get('dismissed') or person.get('project_id')!=slug:continue
        profile=copy.deepcopy(person['profile'])
        agent_id=_alias(person['studio_id'],slug,person['aliases'].get(slug))
        if agent_id in identities:raise ValueError('Projektpersonal har kolliderande ID')
        identities.add(agent_id)
        profile.update(id=agent_id,studio_id=person['studio_id'])
        roster.append(profile)
    return roster


def _project_write(srv,slug,agents,old_read,old_write):
    with LOCK:
        data=_read(srv)
        if data is None:return old_write(slug,agents)
        if not isinstance(agents,list) or len(agents)>24:raise ValueError('Felaktig personalstyrka')
        existing=_project_roster(srv,slug,old_read)
        old={p['id']:p for p in existing}
        new_ids=set();matched=set();updates=[]
        for agent in agents:
            if not isinstance(agent,dict) or not isinstance(agent.get('id'),str):raise ValueError('Ogiltig anställd')
            ident=agent['id']
            if ident in new_ids:raise ValueError('Dubbel personalpost')
            new_ids.add(ident)
            if ident in old:
                before=old[ident]
                if agent.get('studio_id',before['studio_id'])!=before['studio_id']:
                    raise ValueError('Personalens globala ID får inte ändras')
                updates.append((before['studio_id'],dict(agent)))
                matched.add(before['studio_id'])
            else:
                if agent.get('studio_id'):
                    raise ValueError('En person från annat projekt måste tilldelas via Min studio')
                if not agent.get('name') or not agent.get('provider'):
                    raise ValueError('Ny personalpost måste ha namn och AI-motor')
                updates.append((None,dict(agent)))
        # Hiring may add, but ordinary staff_write must not silently fire anybody.
        if set(old)-new_ids:
            raise ValueError('Avskedning måste gå via den bekräftade avskedningsfunktionen')
        for uid,profile in updates:
            if uid:
                person=next(x for x in data['people'] if x['studio_id']==uid)
                person['profile']={**profile,'studio_id':uid}
            else:
                uid='pw-'+hashlib.sha256((slug+'\0'+profile['id']).encode()).hexdigest()[:20]
                if any(x['studio_id']==uid for x in data['people']):
                    raise ValueError('En tidigare personidentitet har samma projekt-ID')
                data['people'].append({'studio_id':uid,'project_id':slug,
                     'aliases':{slug:profile['id']},'profile':{**profile,'studio_id':uid},
                     'registered_at':datetime.now(timezone.utc).isoformat(),'dismissed':False,
                     'skill_overrides':{}})
        data['revision']+=1
        _write(srv,data)
        # Nothing is written to legacy STAFF.json; only global source changes.


def global_skills(srv,slug,original_get):
    with LOCK:
        default=original_get(slug)
        data=_read(srv)
        if data is None:return default
        result={}
        for person in data['people']:
            if person.get('dismissed') or person.get('project_id')!=slug:continue
            ident=_alias(person['studio_id'],slug,person['aliases'].get(slug))
            # Existing project defaults remain available, but changes to skills
            # live on the person and move with them between projects.
            combined=copy.deepcopy(default.get(ident,{}))
            combined.update(copy.deepcopy(person.get('skill_overrides') or {}))
            result[ident]=combined
        return result


def global_save_skill(srv,slug,payload,original_get,original_save):
    with LOCK:
        data=_read(srv)
        if data is None:return original_save(slug,payload)
        ident=str(payload.get('agent_id') or '')
        key=str(payload.get('skill') or '')
        defaults=getattr(srv,'SKILL_DEFAULTS',{})
        if key not in defaults and not re.fullmatch(r'custom-[a-z0-9-]{1,45}',key):
            raise ValueError('Okänd skill')
        level=payload.get('level')
        if isinstance(level,bool) or not isinstance(level,int) or not 0<=level<=5:
            raise ValueError('Skillnivån måste vara 0–5')
        instructions=payload.get('instruction')
        if not isinstance(instructions,str) or not 5<=len(instructions.strip())<=3000:
            raise ValueError('Instruktionen måste vara 5–3000 tecken')
        name=payload.get('name')
        if key.startswith('custom-') and (not isinstance(name,str) or not 2<=len(name.strip())<=60):
            raise ValueError('Egen skill behöver ett namn')
        owner=next((p for p in data['people'] if not p.get('dismissed') and p.get('project_id')==slug
                    and _alias(p['studio_id'],slug,p['aliases'].get(slug))==ident),None)
        if owner is None:raise ValueError('Den anställde är inte tilldelad spelet')
        old=global_skills(srv,slug,original_get).get(ident,{}).get(key,{})
        default_name=(defaults.get(key) or ('Egen skill',''))[0]
        record={'name':name.strip() if key.startswith('custom-') else old.get('name',default_name),
                'level':level,'instruction':instructions.strip()}
        owner.setdefault('skill_overrides',{})[key]=record
        data['revision']+=1
        _write(srv,data)
        return record


def assign(srv,payload,old_read):
    if not isinstance(payload,dict) or payload.get('approval')!='ASSIGN_GLOBAL_EMPLOYEE_V27':
        raise ValueError('Bekräfta personalens projektval')
    uid=str(payload.get('studio_id') or '')
    slug=str(payload.get('target_project') or '')
    if not UID.fullmatch(uid) or not SLUG.fullmatch(slug):raise ValueError('Ogiltig personal eller projekt')
    with LOCK:
        data=_read(srv)
        if data is None:raise ValueError('Aktivera global arbetsstyrka först')
        projects={p['id'] for p in _project_list(srv)}
        if slug not in projects:raise ValueError('Projektet finns inte')
        person=next((p for p in data['people'] if p['studio_id']==uid and not p.get('dismissed')),None)
        if person is None:raise ValueError('Personen saknas eller är avskedad')
        current=person.get('project_id')
        if current==slug:return {'moved':False,'studio_id':uid,'project_id':slug,'reason':'Redan tilldelad spelet'}
        if current:
            agent_id=_alias(uid,current,person['aliases'].get(current))
            if _active(srv,current,agent_id):raise ValueError('Medarbetaren har ett pågående arbetspass eller en aktiv order')
        old_read(slug) # Verify project exists and is safe before any mutation.
        agent_id=_alias(uid,slug,person['aliases'].get(slug))
        # Refuse collisions, not another employee's identity takeover.
        if any(x['studio_id']!=uid and not x.get('dismissed') and x.get('project_id')==slug
               and _alias(x['studio_id'],slug,x['aliases'].get(slug))==agent_id for x in data['people']):
            raise ValueError('Målprojektet har redan agent-ID:t')
        count=sum(not x.get('dismissed') and x.get('project_id')==slug for x in data['people'])
        if count>=24:raise ValueError('Projektet har redan 24 tilldelade personer')
        person['aliases'][slug]=agent_id
        person['project_id']=slug
        person['profile']['station']='cafe'
        data['revision']+=1
        _write(srv,data)
        return {'moved':True,'studio_id':uid,'from_project':current,'project_id':slug,
                'agent_id':agent_id,'name':person['profile'].get('name','Medarbetare')}


def dismiss(srv,slug,payload,old_read):
    if not isinstance(payload,dict) or payload.get('approval')!='DISMISS_STAFF':
        raise ValueError('Avskedningen kräver bekräftelse')
    ident=str(payload.get('agent_id') or '')
    with LOCK:
        data=_read(srv)
        if data is None:raise ValueError('Global personal är inte aktiverad')
        person=next((p for p in data['people'] if not p.get('dismissed') and p.get('project_id')==slug
            and _alias(p['studio_id'],slug,p['aliases'].get(slug))==ident),None)
        if person is None:raise ValueError('Anställd saknas')
        if _active(srv,slug,ident):raise ValueError('Medarbetaren arbetar fortfarande')
        person['dismissed']=True
        person['dismissed_at']=datetime.now(timezone.utc).isoformat()
        data['revision']+=1
        _write(srv,data)
        return {'dismissed':ident,'studio_id':person['studio_id'],
                'name':person['profile'].get('name'),'history_preserved':True}


def install(srv):
    if getattr(srv,'_PW_GLOBAL_WORKFORCE_V27',False):return
    srv._PW_GLOBAL_WORKFORCE_V27=True
    original_read=srv.staff_read
    original_write=srv.staff_write
    original_dismiss=srv.dismiss_staff
    original_get_skills=getattr(srv,'get_skill_settings',None)
    original_save_skill=getattr(srv,'save_skill_setting',None)
    # The engine and its installed adapters resolve these on the core module.
    srv.staff_read=lambda slug:_project_roster(srv,slug,original_read)
    srv.staff_write=lambda slug,people:_project_write(srv,slug,people,original_read,original_write)
    def dismiss_bridge(slug,payload):
        return dismiss(srv,slug,payload,original_read) if _read(srv) is not None else original_dismiss(slug,payload)
    srv.dismiss_staff=dismiss_bridge
    if callable(original_get_skills):
        srv.get_skill_settings=lambda slug:global_skills(srv,slug,original_get_skills)
    if callable(original_get_skills) and callable(original_save_skill):
        srv.save_skill_setting=lambda slug,payload:global_save_skill(srv,slug,payload,original_get_skills,original_save_skill)
    try:
        import pw_v013
        older=pw_v013.transfer
        def transfer_bridge(s,payload):
            if _read(s) is None:return older(s,payload)
            if payload.get('approval')!='ASSIGN_STUDIO_EMPLOYEE_V013':
                raise ValueError('Bekräfta projekttilldelningen')
            return assign(s,{**payload,'approval':'ASSIGN_GLOBAL_EMPLOYEE_V27'},original_read)
        pw_v013.transfer=transfer_bridge
    except ImportError:
        pass
    Handler=srv.Handler;prior_get=Handler.do_GET;prior_post=Handler.do_POST
    base='/api/pw-v027/workforce'
    def do_GET(self):
        if urlparse(self.path).path!=base:return prior_get(self)
        if not self.allowed() or not self.auth():return self.reply(403,{'error':'Åtkomst nekad'})
        try:return self.reply(200,preview(srv))
        except (ValueError,OSError,TypeError) as e:return self.reply(400,{'error':str(e)[:280]})
    def do_POST(self):
        route=urlparse(self.path).path
        if route not in (base+'/activate',base+'/assign'):return prior_post(self)
        if not self.allowed() or not self.same_origin() or not self.auth():
            return self.reply(403,{'error':'Åtkomst nekad'})
        try:
            if self.headers.get('Content-Type','').split(';')[0].strip().lower()!='application/json':
                raise ValueError('JSON krävs')
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=16000:raise ValueError('Ogiltig begäran')
            payload=json.loads(self.rfile.read(size))
            result=(activate(srv,payload,original_read,original_get_skills) if route.endswith('activate')
                    else assign(srv,payload,original_read))
            return self.reply(200,result)
        except (ValueError,OSError,TypeError) as e:return self.reply(400,{'error':str(e)[:280]})
    Handler.do_GET=do_GET;Handler.do_POST=do_POST
