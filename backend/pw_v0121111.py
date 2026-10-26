"""Staff-first scheduling for Pixel Works 0.12.11.11.

Select a PERSON by aptitude before asking their tool adapter about capacity.
No external calls at import or during read-only planning.
"""
import json
from urllib.parse import urlparse

VERSION='0.12.11.13'

CREATIVE=('skapa','design','idé','berätt','sidouppdrag','karaktär','dialog','koncept','story','värld','manus')
TECH=('implement','programmer','bugg','felsök','kod','javascript','python','bygg','testa','fixa')

def _creative(order):
    instruction=str(order.get('instruction') or '').lower()
    return any(word in instruction for word in CREATIVE) and not any(word in instruction for word in TECH)

def _score(person,order,skills):
    station=order.get('station')
    role=person.get('role_type','allround')
    level=skills.get(person.get('id'),{}).get({'meeting':'meeting','docs':'documentation','research':'research','code':'coding','qa':'testing','art':'art','music':'music','voice':'voice'}.get(station,'planning'),{}).get('level',0)
    creative=_creative(order)
    # Role suitability dominates generic skills. PROVIDER IS NOT A FACTOR.
    role_match=(
       90 if station=='lead' and role=='lead' else
       60 if creative and role in ('writer','creative') else
       45 if creative and role in ('research','artist') else
       10 if creative else
       65 if station=='code' and role in ('programmer','allround') else
       60 if station=='qa' and role=='qa' else
       48 if station in ('docs','meeting') and role in ('writer','creative','research') else
       35 if station=='research' and role=='research' else
       20)
    return (role_match + int(level)*3 + (4 if person.get('home_station')==station else 0))

def _eligible(srv,slug,person,order):
    station=order.get('station')
    # The manager is a legitimate worker at the manager desk, but never a
    # generic replacement for a coder, designer or tester. The manager must
    # actually be at the desk to accept personal planning/review orders.
    if person.get('role_type')=='lead':
        return (station=='lead' and person.get('station')=='lead'
                and 'lead' in person.get('allowed_stations',[])
                and person.get('provider')=='codex'
                and srv.agent_authorized(slug,person,'lead'))
    if station not in person.get('allowed_stations',[]):return False
    if not srv.agent_authorized(slug,person,station):return False
    # A text-only adviser cannot modify code, regardless of skills.
    if station in ('code','qa') and person.get('provider')=='gemini':return False
    return True

def selection(srv,slug,order,staff=None,working=None):
    staff=staff if staff is not None else srv.staff_read(slug)
    working=working if working is not None else set()
    skill=srv.get_skill_settings(slug)
    people=[p for p in staff if _eligible(srv,slug,p,order)]
    people.sort(key=lambda p:(-_score(p,order,skill),p.get('name',''),p.get('id','')))
    # A preferred but busy specialist holds their own assignment; a second
    # provider is never silently substituted solely due to temporary load.
    return people[0] if people else None

def _capacity(srv,person):
    import pw_v01210
    if not pw_v01210.studio_access(srv).get('enabled'):
        return 'Studion är inte godkänd för arbete. Öppna Inställningar → Studioåtkomst.'
    if person.get('provider')=='gemini':
        state=pw_v01210.gemini_status(srv)
        if state.get('can_send'):return None
        if state.get('paused_until_day') or state.get('paused_until_epoch'):
            return 'Jag kan inte arbeta just nu; mina arbetsverktyg är pausade efter ett fel eller en kvotgräns.'
        return 'Jag kommer inte åt mina arbetsverktyg ännu. Kontrollera anslutningen i Inställningar.'
    if person.get('provider')=='codex':
        if not srv.status().get('execution_enabled'):
            return 'Jag kan inte starta arbetet eftersom mitt arbetsverktyg inte är tillgängligt.'
        return None
    return 'Mina arbetsverktyg kan inte starta uppdrag automatiskt ännu.'

def _chief(srv,slug,staff):
    return next((p for p in staff if p.get('role_type')=='lead' and p.get('station')=='lead' and srv.agent_authorized(slug,p,'lead')),None)

def plan_for_staff(srv,slug,old_plan):
    base=old_plan(slug)
    staff=srv.staff_read(slug)
    if not _chief(srv,slug,staff):return base
    with srv.LOCK:
        active=[j for j in srv.JOBS.values() if j.get('project')==slug and j.get('state') in ('queued','running')]
    busy={j.get('agent_id') for j in active}
    orders={o.get('id'):o for o in srv.orders_read(slug) if o.get('status')=='waiting'}
    # Leave Codex engine's safety/parallel checks intact; only veto assignments
    # whose PERSON is not the strongest available employee.
    selected=[];blocked=list(base.get('blocked',[]))
    for item in base.get('assignments',[]):
        order=orders.get(item.get('order_id'))
        if not order:continue
        preferred=selection(srv,slug,order,staff,busy)
        if preferred and preferred.get('id')!=item.get('agent_id'):
            blocked=[b for b in blocked if b.get('order_id')!=order['id']]
            reason=('Jag arbetar redan med ett uppdrag.' if preferred['id'] in busy else _capacity(srv,preferred))
            blocked.append({'order_id':order['id'],'station':order.get('station'),
              'agent_id':preferred['id'],'agent_name':preferred.get('name','Medarbetaren'),
              'reason':(preferred.get('name','Medarbetaren')+' väntar: '+reason) if reason else
                       preferred.get('name','Medarbetaren')+' är förstahandsval för uppdraget.'})
            continue
        selected.append(item)
        busy.add(item['agent_id'])
    return {**base,'assignments':selected,'next':selected[0] if selected else None,'blocked':blocked}

def candidate(srv,slug):
    import pw_v01210
    staff=srv.staff_read(slug)
    chief=_chief(srv,slug,staff)
    if not chief:return None
    with srv.LOCK:
        active=[j for j in srv.JOBS.values() if j.get('project')==slug and j.get('state') in ('queued','running')]
        all_gemini_busy=any(j.get('provider')=='gemini' and j.get('state') in ('queued','running') for j in srv.JOBS.values())
    if all_gemini_busy:return None
    busy={j.get('agent_id') for j in active}
    ordered=sorted((o for o in srv.orders_read(slug) if o.get('status')=='waiting'),key=lambda o:(o.get('priority',2),o.get('created_at',''),o.get('id','')))
    for order in ordered:
        preferred=selection(srv,slug,order,staff,busy)
        if not preferred:continue
        if preferred.get('provider')!='gemini':continue
        if preferred['id'] in busy or _capacity(srv,preferred):continue
        return order,preferred,chief
    return None

def worker_status(srv,slug):
    staff=srv.staff_read(slug)
    with srv.LOCK:
        running=[dict(j) for j in srv.JOBS.values() if j.get('project')==slug and j.get('state') in ('running','queued')]
    waiting=[o for o in srv.orders_read(slug) if o.get('status')=='waiting']
    result=[]
    for person in staff:
        if person.get('role_type')=='lead':continue
        job=next((j for j in running if j.get('agent_id')==person.get('id')),None)
        assigned=next((o for o in waiting if (selection(srv,slug,o,staff,{j.get('agent_id') for j in running}) or {}).get('id')==person.get('id')),None)
        reason=None if job else _capacity(srv,person) if assigned else None
        result.append({'id':person.get('id'),'name':person.get('name'),'role':person.get('role'),
            'state':'working' if job else 'blocked' if reason else 'waiting' if assigned else 'idle',
            'order_id':job.get('order_id') if job else assigned.get('id') if assigned else None,
            'task':(job.get('instruction') or '')[:180] if job else (assigned.get('instruction') or '')[:180] if assigned else '',
            'message':reason or (person.get('name','Medarbetaren')+' arbetar med uppdraget.' if job else
                                person.get('name','Medarbetaren')+' är redo att börja.' if assigned else
                                person.get('name','Medarbetaren')+' är ledig.')})
    return result

def install(srv):
    if getattr(srv,'_PW_V0121111',False):return
    srv._PW_V0121111=True
    srv.APP_VERSION=VERSION
    original_plan=srv.dispatch_plan
    srv.dispatch_plan=lambda slug:plan_for_staff(srv,slug,original_plan)
    import pw_v01210
    pw_v01210.auto_candidate=lambda _srv,slug:candidate(_srv,slug)
    old_health=srv.dispatch_health
    def health(slug):
        state=old_health(slug)
        workers=worker_status(srv,slug)
        pending=[w for w in workers if w['state']=='blocked' and w['order_id']]
        if pending and not state.get('active_jobs'):
            state={**state,'state':'blocked','reason':pending[0]['message']}
        elif state.get('state')=='idle' and not any(w['state']=='working' for w in workers):
            state={**state,'reason':'Inga aktiva arbetsuppgifter.'}
        return state
    srv.dispatch_health=health
    previous_post=srv.Handler.do_POST
    previous_get=srv.Handler.do_GET
    def get(self):
        route=urlparse(self.path).path
        if route.startswith('/api/projects/') and route.endswith('/staff-status'):
            if not self.allowed():return self.reply(403,{'error':'Otillåten begäran'})
            slug=route.split('/')[3]
            try:return self.reply(200,{'workers':worker_status(srv,slug)})
            except (ValueError,OSError) as exc:return self.reply(400,{'error':str(exc)[:250]})
        return previous_get(self)
    srv.Handler.do_GET=get
    def post(self):
        route=urlparse(self.path).path
        if route=='/api/pw-v0121110/dispatch':
            # The previous route dispatched only one AI provider; the personnel
            # planner now handles all station checks in one consistent place.
            if not self.allowed() or not self.same_origin() or not self.auth():return self.reply(403,{'error':'Otillåten begäran'})
            n=self.headers.get('Content-Length','')
            if not n.isdecimal() or not 0<int(n)<=2048:return self.reply(413,{'error':'Ogiltig begäran'})
            try:
                payload=json.loads(self.rfile.read(int(n)))
                slug=srv.validate_slug(payload.get('project',''))
                station=payload.get('station','')
                order=next((o for o in srv.orders_read(slug) if o.get('status')=='waiting' and o.get('station')==station),None)
                if not order:return self.reply(200,{'state':'idle','message':'Inga väntande uppdrag vid bordet.'})
                p=selection(srv,slug,order)
                if not p:return self.reply(200,{'state':'blocked','message':'Ingen behörig medarbetare för uppdraget.'})
                with srv.LOCK:
                    working=any(j.get('project')==slug and j.get('agent_id')==p['id'] and j.get('state') in ('queued','running') for j in srv.JOBS.values())
                reason='Jag arbetar redan med ett uppdrag.' if working else _capacity(srv,p)
                if reason:return self.reply(200,{'state':'blocked','agent_name':p['name'],'message':p['name']+': '+reason})
                if p.get('provider')=='gemini':
                    jid=pw_v01210.start_auto_job(srv,slug,order,p)
                    return self.reply(200,{'state':'started' if jid else 'busy','job_id':jid,'agent_name':p['name'],
                         'message':p['name']+' börjar arbeta.' if jid else p['name']+' har redan ett uppdrag.'})
                return self.reply(200,{'state':'ready','agent_name':p['name'],
                     'message':p['name']+' är vald av arbetsledaren. Uppdraget startar via arbetskön.'})
            except (ValueError,OSError,TypeError) as exc:return self.reply(400,{'error':str(exc)[:250]})
        return previous_post(self)
    srv.Handler.do_POST=post
