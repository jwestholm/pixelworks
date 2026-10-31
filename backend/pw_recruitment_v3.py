"""Player-controlled, opt-in V3 recruitment. Old jobs/workers preserved, no AI calls."""
from __future__ import annotations
import copy, json, os, re, secrets, threading
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

GUARD=threading.RLock()
CATALOG=json.loads(Path(__file__).with_name('pw_v3_personas.json').read_text(encoding='utf8'))
PEOPLE={p['id']:p for p in CATALOG['candidates']}
ROLES=CATALOG['roles'];ROLE_SKILL=CATALOG['role_skill']
STYLE_AXES={'careful':'Noggrannhet','creative':'Kreativitet','social':'Social','speed':'Tempo'}
APPROVAL='START_NEW_STUDIO_CREW_V3'
DENIED=['Publicera spel','Pusha till GitHub','Använda betald AI utan spelarens tillstånd']
class Conflict(ValueError):pass

def stamp():return datetime.now(timezone.utc).isoformat()
def folder(srv):
    p=srv.ROOT/'studio-v3'
    if p.is_symlink():raise ValueError('Symbolisk länk i studiokatalogen')
    return p
def path(srv):return folder(srv)/'CREW.json'
def read(srv):
    f=path(srv)
    if f.is_symlink():raise ValueError('Symbolisk länk i personregistret')
    if not f.exists():return None
    d=json.loads(f.read_text(encoding='utf8'))
    if not isinstance(d,dict) or d.get('schema')!=1 or not isinstance(d.get('team'),list) or not isinstance(d.get('revision'),int):
        raise ValueError('Ogiltigt v3-register; nya körningar spärras')
    ids=[x.get('person_id') for x in d['team'] if isinstance(x,dict)]
    if len(ids)!=len(d['team']) or len(ids)!=len(set(ids)) or any(x.get('character_id') not in {*PEOPLE,'chef'} for x in d['team']):
        raise ValueError('Kolliderande personidentitet')
    return d

def write(srv,d):
    p=folder(srv); f=path(srv)
    if p.is_symlink() or f.is_symlink():raise ValueError('Osäker katalog')
    p.mkdir(mode=0o700,parents=True,exist_ok=True)
    raw=(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    if len(raw)>400000:raise ValueError('För stort register')
    tmp=p/('.CREW-'+secrets.token_hex(8)+'.tmp')
    try:
        fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'wb') as stream:
            stream.write(raw);stream.flush();os.fsync(stream.fileno())
        os.replace(tmp,f)
    finally:tmp.unlink(missing_ok=True)

def role_recommendations(c):
    """Game-world fit only. The ranking does not represent measured AI capability."""
    best=c.get('recommended_role')
    ordered=sorted(ROLES, key=lambda r:(0 if r==best else 1,-int(c['skills'].get(ROLE_SKILL[r],0)),list(ROLES).index(r)))
    return [{'role':r,'name':ROLES[r], 'score':int(c['skills'].get(ROLE_SKILL[r],0))} for r in ordered]

def persona_configuration(c,role='',description=''):
    """Immutable character traits -> portable, testable assistant settings. No model calls."""
    traits=copy.deepcopy(c['traits'])
    pace='Arbeta snabbt med små prototyper; märk tydligt ofärdiga delar.' if traits['speed']>=4 else ('Arbeta metodiskt och dela upp leveransen i kontrollerbara steg.' if traits['speed']<=2 else 'Håll ett jämnt tempo och avgränsa arbetet.')
    review='Be alltid om en separat kvalitetsgranskning före slutleverans.' if traits['careful']<=2 else ('Kontrollera detaljer och redovisa kontrollpunkter.' if traits['careful']>=4 else 'Utför rimlig egenkontroll och rapportera osäkerhet.')
    ideas='Föreslå gärna flera olika lösningar.' if traits['creative']>=4 else 'Håll dig främst till uppdragets givna riktning.'
    talk='Svara gärna samtalsnära och med initiativ.' if traits['social']>=4 else ('Svara hellre kort och sakligt än med småprat.' if traits['social']<=2 else 'Svara med en vänlig, tydlig ton.')
    return {'schema':1,'character_id':c['id'], 'immutable':True,'traits':traits,
      'voice':c['voice'], 'sample':c['speech_sample'],'quirk':c['quirk'],
      'work_style':[pace,review,ideas,talk],
      'role':role,'role_name':ROLES.get(role,'Arbetsledare'),
      'company_instruction':str(description or '')[:1400],
      'rules':['Följ företagets behörigheter och uppdragets krav före karaktärsstil.',
               'Gör inte medvetna fel och hitta inte på verifiering eller tester.',
               'Starta aldrig betalda verktyg, ändra GitHub eller publicera utan uttryckligt godkännande.'],
      'status':'FÖRBEREDD – v3-jobb mot en riktig AI-motor är ännu inte anslutna'}

def prompt_preview(c,role='',description=''):
    cfg=persona_configuration(c,role,description)
    return ('PERSONA (FAST): '+c['name']+'. '+cfg['voice']+' '+cfg['quirk']+' Exempel: '+cfg['sample']+'\n'
       +'SPELSTATS (ej verifierad AI-kompetens): '+', '.join(STYLE_AXES[k]+' '+str(v)+'/5' for k,v in cfg['traits'].items())+'\n'
       +'ARBETSSÄTT: '+' '.join(cfg['work_style'])+'\n'
       +'FÖRETAGETS ROLL: '+cfg['role_name']+'\n'
       +'FÖRETAGETS ARBETSBESKRIVNING: '+(cfg['company_instruction'] or 'Ej angiven')+'\n'
       +'GRÄNSER: '+' '.join(cfg['rules'])+'\n'
       +'UPPDRAG: [sätts när du tilldelar ett uppdrag – aldrig automatiskt här]')

def person_view(p):
    c=CATALOG['chef'] if p['character_id']=='chef' else PEOPLE[p['character_id']]
    config=persona_configuration(c,p['role'],p.get('work_description',''))
    return {**copy.deepcopy({k:v for k,v in p.items() if k!='engine'}),
            'name':c['name'],'role_name':ROLES.get(p['role'],'Arbetsledare'),
            'character':copy.deepcopy(c),
            'role_recommendations':role_recommendations(c),
            'persona_config':config,
            'prompt_preview':prompt_preview(c,p['role'],p.get('work_description','')),
            'engine':{'provider':None,'model':None,'verified':False,'can_execute':False,'status':'DEMO – ingen motor ansluten'},
            'persona_contract':prompt_preview(c,p['role'],p.get('work_description','')),
            # Worker interface stays stable, but V3 workers cannot execute yet.
            'worker':{'id':p['person_id'],'person_id':p['person_id'],'role':p['role'],
                      'skills':copy.deepcopy(c['skills']),'provider':None,'station':None,'status':'idle','currentTask':None,
                      'persona_config':config,'prompt_preview':prompt_preview(c,p['role'],p.get('work_description',''))}}

def state(srv):
    with GUARD:
        d=read(srv)
        return {'enabled':d is not None,'revision':d['revision'] if d else 0,
                'people':[person_view(p) for p in d['team'] if p['state']=='hired'] if d else [],
                'candidates':[{**copy.deepcopy(c),
                  'role_recommendations':role_recommendations(c),
                  'persona_config':persona_configuration(c),
                  'prompt_preview':prompt_preview(c)} for c in CATALOG['candidates']],
                'roles':ROLES,'role_skill':ROLE_SKILL,'skills':CATALOG['skills'],'interview_tasks':{k:[{'id':a,'question':b} for a,b in v] for k,v in INTERVIEW_TASKS.items()},
                'denied':DENIED,'interviews':copy.deepcopy(d.get('interviews',{})) if d else {},
                'mode':'DEMO – AI-anställningar är spelkaraktärer utan riktiga anrop',
                'projects_unchanged':True}

def revision(d,payload):
    v=payload.get('revision')
    if isinstance(v,bool) or not isinstance(v,int) or v!=d['revision']:
        raise Conflict('Personallistan ändrades på annan enhet. Uppdatera och försök igen.')

def activate(srv,p):
    if p.get('approval')!=APPROVAL:raise ValueError('Starten måste godkännas av spelaren')
    with GUARD:
        if read(srv):return state(srv)
        with srv.LOCK:
            if any(j.get('state') in ('queued','running') for j in srv.JOBS.values()):
                raise Conflict('Gamla aktiva AI-jobb måste avslutas innan nya studion kan starta')
        d={'schema':1,'revision':1,'created_at':stamp(),'mode':'demo-new-crew',
           'legacy':'Old staff and worker objects untouched; pre-v3 dispatch disabled',
           'team':[{'person_id':'pw3-chef','character_id':'chef','role':'lead','state':'hired',
                    'hired_at':stamp(),'work_description':'Planera och rekommendera rekrytering, anställ aldrig själv.'}],
           'interviews':{}}
        write(srv,d);return state(srv)

def hire(srv,p):
    if p.get('approval')!='HIRE_PERSON_V3':raise ValueError('Du måste själv godkänna anställningen')
    who=p.get('candidate_id');role=p.get('role')
    if who not in PEOPLE or role not in ROLES:raise ValueError('Fel kandidat eller arbetsroll')
    with GUARD:
        d=read(srv)
        if not d:raise ValueError('Aktivera nya studion först')
        revision(d,p)
        old=next((x for x in d['team'] if x['character_id']==who),None)
        if old and old['state']=='hired':raise Conflict('Redan anställd')
        if len([x for x in d['team'] if x['state']=='hired'])>=24:raise ValueError('Max 24 anställda')
        if old:
            old.update(role=role,state='hired',hired_at=stamp())
        else:
            d['team'].append({'person_id':'pw3-'+who,'character_id':who,'role':role,'state':'hired',
                              'hired_at':stamp(),'work_description':''})
        d['revision']+=1;write(srv,d);return state(srv)

def place(srv, payload):
    """Persist a GLOBAL employee's office position. Purely visual: never dispatch AI."""
    import math
    pid=payload.get('person_id')
    x,y=payload.get('x'),payload.get('y')
    station=payload.get('station_id')
    if (isinstance(x,bool) or isinstance(y,bool) or not isinstance(x,(int,float))
            or not isinstance(y,(int,float)) or not math.isfinite(x) or not math.isfinite(y)
            or not 5<=x<=95 or not 40<=y<=91):
        raise ValueError('Placeringen ligger utanför kontorsgolvet')
    if station is not None and station not in (
            'lead','code','art','qa','research','meeting','docs','voice','music','cafe'):
        raise ValueError('Okänd kontorsstation')
    with GUARD:
        d=read(srv)
        if not d:raise ValueError('Aktivera nya studion först')
        revision(d,payload)
        person=next((p for p in d['team'] if p['person_id']==pid and p['state']=='hired'),None)
        if not person:raise ValueError('Den anställda finns inte')
        person['office_position']={'x':round(x,1),'y':round(y,1),'station_id':station}
        d['revision']+=1
        write(srv,d)
        return state(srv)

def profile(srv,p):
    role=p.get('role');description=p.get('work_description');pid=p.get('person_id')
    if role not in ROLES and role!='lead':raise ValueError('Okänd roll')
    if not isinstance(description,str) or len(description)>1400:raise ValueError('Ogiltig arbetsbeskrivning')
    with GUARD:
        d=read(srv)
        if not d:raise ValueError('Aktivera nya studion först')
        revision(d,p)
        found=next((x for x in d['team'] if x['person_id']==pid and x['state']=='hired'),None)
        if not found:raise ValueError('Anställd saknas')
        if (pid=='pw3-chef')!=(role=='lead'):raise ValueError('Chefsrollen är förbehållen Chefen')
        found['role']=role;found['work_description']=description.strip();d['revision']+=1
        write(srv,d);return state(srv)

def dismiss(srv,p):
    if p.get('approval')!='DISMISS_PERSON_V3':raise ValueError('Bekräfta avskedning')
    with GUARD:
        d=read(srv)
        if not d:raise ValueError('Aktivera nya studion först')
        revision(d,p)
        pid=p.get('person_id')
        if pid=='pw3-chef':raise ValueError('Chefen stannar i studion')
        found=next((x for x in d['team'] if x['person_id']==pid and x['state']=='hired'),None)
        if not found:raise ValueError('Anställd saknas')
        found['state']='dismissed';found['dismissed_at']=stamp();d['revision']+=1
        write(srv,d);return state(srv)

# Finite interview catalog. Player chooses a task; answers stay explicitly fictional.
INTERVIEW_TASKS={
 'artist':[('gorilla','Rita en 32×32-gorilla med personlighet.'),('button','Skissa en tydlig pixelknapp för en spelmeny.')],
 'programmer':[('php','Hur skulle du förbättra gammal legacy-PHP?'),('bugs','Du hittar en svårreproducerad sparbugg. Var börjar du?')],
 'musician':[('menu','Skapa ett lekfullt ljud för en meny.'),('boss','Föreslå ett kort bossljud som inte tröttar ut spelaren.')],
 'qa':[('save','Testa ett spel där sparning ibland misslyckas.'),('buttons','Hur testar du en knapp som ibland klickas två gånger?')],
 'writer':[('dog','Skriv en story om en hund som blir superhjälte.'),('villain','Skapa en skurk med ett oväntat vardagsproblem.')],
 'research':[('engine','Jämför två spelmotorer för ett litet webbspel.'),('evidence','Hur kontrollerar du en tveksam uppgift?')],
 'allround':[('prototype','Planera en spelbar prototyp på en dag.'),('rescue','Två uppdrag krockar. Hur prioriterar du?')],
}
TASK_ANSWERS={
 'gorilla':'En arg men charmig 32×32-gorilla med två tydliga ögonbryn. Här visas bara en DEMO-SVG, inte en riktig AI-bild.',
 'button':'Jag föreslår en stor pixelknapp med två lägen och tydlig fokusram – bara ett fiktivt designförslag.',
 'php':'Först beteendetester för befintlig PHP-kod. Därefter små refaktoreringar med test efter varje steg – ingen riktig kod körs.',
 'bugs':'Jag loggar varje sparsteg, bygger ett minimalt reproduktionsfall och testar avbrott. Det här är en demonstrationsplan.',
 'menu':'En kort tvåtonssekvens: lätt attack och mjuk svans. Ljudet kan spelas lokalt som DEMO.',
 'boss':'Ett kort, dovt slag följt av en ljus signal – sparsamt så det inte maskerar gameplay. Bara en idé.',
 'save':'Jag testar sparning vid avbrott, fullt minne, pausmeny och dubbelklick. Varje fynd får reproduktionssteg.',
 'buttons':'Jag provar klick, dubbelklick, tangentbord, touch och snabbt byte av fokus. Inga faktiska tester har gjorts.',
 'dog':'Hunden Buster upptäcker att hans superkraft är att höra när någon behöver hjälp – även dammsugaren.',
 'villain':'Skurken vill stjäla all stadens tid. Innerst inne försöker hen bara hinna med tvätten.',
 'engine':'Jag jämför dokumentation, filstorlek, licens och testbarhet innan jag rekommenderar något. Inga externa källor har hämtats.',
 'evidence':'Jag söker primärkällan, antecknar datum, jämför två oberoende belägg och markerar osäkerheter tydligt.',
 'prototype':'Jag väljer en enda spelmekanik, en fungerande meny och ett kort speltest innan jag lägger på effekter.',
 'rescue':'Jag stoppar dubbelarbetet, visar vilka beroenden som krockar och ber dig prioritera innan jag ändrar något.',
}
PERSONA_REACTIONS={
 'joppe':'Tjaba dårå! Jag har en snabb grej: ',
 'siv':'Jag vill inleda med en kort, systematisk redogörelse. Punkt ett: ',
 'nisse':'Det ordnar sig, jag testar direkt! ',
 'mira':'Jag vill finslipa detaljerna innan vi bestämmer oss. ',
 'vera':'Hörru, lyssna på det här! ',
 'lova':'Jag ser redan början på berättelsen. ',
}
def interview(srv,p):
    who=p.get('candidate_id');role=p.get('role');test_id=p.get('test_id')
    if who not in PEOPLE or role not in ROLES:raise ValueError('Ogiltigt provjobb')
    choices=dict(INTERVIEW_TASKS[role])
    if test_id is None:test_id=next(iter(choices)) # preserve v3 requests
    if not isinstance(test_id,str) or test_id not in choices:raise ValueError('Välj ett tillgängligt intervjuprov')
    with GUARD:
        d=read(srv)
        if not d:raise ValueError('Starta nya studion först')
        revision(d,p)
        result={'candidate_id':who,'role':role,'test_id':test_id,'question':choices[test_id],
                'text':PERSONA_REACTIONS[who]+TASK_ANSWERS[test_id],
                'score':PEOPLE[who]['skills'][ROLE_SKILL[role]],'source':'DEMO',
                'note':'Förskrivet fiktivt arbetsprov. Poäng från spelvärden, inte AI-kvalitetsmätning.',
                'created_at':stamp()}
        d['interviews'][who]=result;d['revision']+=1;write(srv,d)
        return {'interview':result,'revision':d['revision']}

def enabled(srv):
    try:return read(srv) is not None
    except (ValueError,OSError):return True # corrupt state must not activate old scheduler

def install(srv):
    if getattr(srv,'_PW_RECRUITMENT_V3',False):return
    srv._PW_RECRUITMENT_V3=True
    previous_plan=srv.dispatch_plan
    def plan(slug):
        if enabled(srv):return {'project':slug,'next':None,'assignments':[],'blocked':[],
                                'waiting':0,'leader_active':False,'active_jobs':[],
                                'paused_by':'v3-personal'}
        return previous_plan(slug)
    srv.dispatch_plan=plan
    # Legacy scheduler still wakes up; prevent it from mutating order/review
    # bookkeeping in V3. Worker objects/functions remain available for NEXT.
    for name in ('reconcile_orders_from_reports','recover_completed_reviews','chief_block_report'):
        old=getattr(srv,name,None)
        if callable(old):
            def paused(*args,_old=old,**kwargs):
                if enabled(srv):return None
                return _old(*args,**kwargs)
            setattr(srv,name,paused)
    scheduler=getattr(srv,'office_scheduler',None)
    if callable(scheduler):
        def guarded_scheduler(port,stop_event):
            if enabled(srv):
                while not stop_event.wait(4):pass
                return
            return scheduler(port,stop_event)
        srv.office_scheduler=guarded_scheduler
    try:
        import pw_v01210
        old_candidate=pw_v01210.auto_candidate
        pw_v01210.auto_candidate=lambda core,slug:None if enabled(srv) else old_candidate(core,slug)
    except (ImportError,AttributeError):pass
    get=srv.Handler.do_GET;post=srv.Handler.do_POST
    prefix='/api/pw-v3/crew'
    handlers={prefix+'/activate':activate,prefix+'/hire':hire,prefix+'/profile':profile,
              prefix+'/dismiss':dismiss,prefix+'/interview':interview,prefix+'/place':place}
    def do_GET(self):
        if urlparse(self.path).path!=prefix:return get(self)
        if not self.allowed() or not self.auth():return self.reply(403,{'error':'Åtkomst nekad'})
        try:return self.reply(200,state(srv))
        except (ValueError,OSError) as e:return self.reply(409,{'error':str(e)[:260]})
    def do_POST(self):
        target=urlparse(self.path).path
        if enabled(srv) and (target in ('/api/jobs','/api/pw-v013/studio/transfer','/api/pw-v027/workforce/assign') or re.fullmatch(r'/api/projects/[a-z0-9-]+/(hire|station|staff/dismiss|assignments|skills)',target)):
            return self.reply(409,{'error':'Gamla personalmotorn är pausad i v3. Använd Rekrytering.'})
        if target not in handlers:return post(self)
        if not self.allowed() or not self.same_origin() or not self.auth():return self.reply(403,{'error':'Åtkomst nekad'})
        try:
            if self.headers.get('Content-Type','').split(';')[0].strip().lower()!='application/json':raise ValueError('JSON krävs')
            size=int(self.headers.get('Content-Length','0'))
            if size<2 or size>6000:raise ValueError('Ogiltig begäran')
            payload=json.loads(self.rfile.read(size))
            if not isinstance(payload,dict):raise ValueError('JSON-objekt krävs')
            return self.reply(200,handlers[target](srv,payload))
        except Conflict as e:return self.reply(409,{'error':str(e)[:260]})
        except (ValueError,OSError,TypeError) as e:return self.reply(400,{'error':str(e)[:260]})
    srv.Handler.do_GET=do_GET;srv.Handler.do_POST=do_POST
