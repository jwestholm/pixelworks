"""v0.12.11.12: explain local capacity and honor explicit personnel placement.

No external AI calls during installation or diagnostics.
A manually moved employee is the intended assignee, regardless of the preferred
employee in the chief's automatic ranking. Permission, capability and job guards
remain active. No automatic paid-model fallback.
"""
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

VERSION = '0.12.11.13'
def apply_limit(provider, srv, base_status):
    """Compatibility wrapper: only Google's own limit gates sending."""
    state=dict(base_status)
    state['daily_limit']=None
    state['local_limit_exhausted']=False
    state['limit_source']='Googles kvoter; inga lokala anropstak'
    state['can_send']=bool(state.get('configured') and state.get('test_is_generation')
                            and not state.get('paused_until_day')
                            and not state.get('paused_until_epoch'))
    state['execution_enabled']=state['can_send']
    return state


def explain(provider, srv, person):
    name = person.get('name') or 'Medarbetaren'
    if not provider.studio_access(srv).get('enabled'):
        return 'Studioåtkomst är avstängd. Aktivera i Inställningar.'
    if person.get('provider') == 'gemini':
        state = provider.gemini_status(srv)
        if not state.get('configured'):
            return name + ' saknar en fungerande arbetsanslutning. Öppna Inställningar.'
        if state.get('paused_until_day') or state.get('paused_until_epoch'):
            return name + ' väntar på att arbetsverktyget återhämtar sig efter ett API-fel. ' + (
                str(state.get('pause_reason') or 'Se teknisk diagnostik i Inställningar.')[:150])
        if not state.get('test_is_generation'):
            return name + ' behöver en verifierad arbetsanslutning. Kontrollera den i Inställningar.'
        return None if state.get('can_send') else name + ' kan inte starta just nu. Öppna Inställningar.'
    if person.get('provider') == 'codex':
        if not srv.status().get('execution_enabled'):
            return name + ' kan inte nå sitt kodverktyg. Kontrollera anslutningen i Inställningar.'
        return None
    return name + ' saknar en installerad arbetsmotor.'


def dispatch_person(srv, provider, staffplan, slug, station, agent_id=None, order_id=None):
    slug = srv.validate_slug(slug)
    if station not in srv.SKILL_STATIONS:
        raise ValueError('Okänd arbetsstation')
    if not provider.studio_access(srv).get('enabled'):
        return {'state':'blocked','message':'Studioåtkomst är avstängd. Öppna Inställningar.'}
    orders = sorted((o for o in srv.orders_read(slug)
                     if o.get('station') == station and o.get('status') == 'waiting'
                     and (order_id is None or o.get('id') == order_id)),
                    key=lambda o:(o.get('priority', 2), o.get('created_at',''), o.get('id','')))
    if not orders:
        return {'state':'idle','message':'Inga väntande arbetsorder vid bordet.'}
    order = orders[0]
    staff = srv.staff_read(slug)
    if agent_id:
        # A drag onto a desk is an explicit owner's selection: do not silently
        # re-select a specialist simply because they outrank this employee.
        person = next((p for p in staff if p.get('id') == agent_id), None)
        if not person or (person.get('role_type') == 'lead' and station != 'lead'):
            return {'state':'blocked','message':'Den valda personen kan inte ta den här arbetsordern.'}
        if person.get('station') != station or not staffplan._eligible(srv,slug,person,order):
            return {'state':'blocked','agent_name':person.get('name'),
                    'message':person.get('name','Medarbetaren')+' saknar behörighet till arbetsstationen.'}
    else:
        person = staffplan.selection(srv,slug,order,staff)
        if not person:
            return {'state':'blocked','message':'Ingen behörig medarbetare finns för arbetsordern.'}
    with srv.LOCK:
        busy = any(j.get('project') == slug and j.get('agent_id') == person['id']
                   and j.get('state') in ('running','queued') for j in srv.JOBS.values())
    if busy:
        return {'state':'blocked','agent_name':person.get('name'),
                'message':person.get('name','Medarbetaren')+' arbetar redan med ett annat uppdrag.'}
    reason = explain(provider,srv,person)
    if reason:
        return {'state':'blocked','agent_name':person.get('name'), 'message':reason}
    if person.get('provider') == 'gemini':
        jid = provider.start_auto_job(srv,slug,order,person)
        return {'state':'started' if jid else 'busy','job_id':jid,
                'agent_name':person['name'],
                'message':person['name']+' börjar arbeta.' if jid else person['name']+' har ett pågående uppdrag.'}
    if person.get('provider') == 'codex':
        # Use the existing authenticated localhost endpoint: it owns Git setup,
        # job reservation, the approved workspace sandbox and report creation.
        payload={'project':slug,'station':station,'agent_id':person['id'],
                 'instruction':order['instruction'],'order_id':order['id'],
                 'attachment_ids':order.get('attachment_ids',[]),
                 'isolated':True,'approval':'PROJECT_MANDATE'}
        port = getattr(srv,'_PW_PORT',8765)
        request=Request('http://127.0.0.1:'+str(port)+'/api/jobs',
            data=json.dumps(payload).encode('utf-8'),method='POST',headers={
              'Content-Type':'application/json', 'X-Pixelworks-Token':srv.TOKEN,
              'Origin':'http://127.0.0.1:'+str(port)})
        try:
            with urlopen(request,timeout=8) as response:
                data=json.loads(response.read().decode('utf-8'))
            return {'state':'started','job_id':data.get('job_id'),'agent_name':person['name'],
                    'message':person['name']+' börjar arbeta med uppdraget.'}
        except HTTPError as error:
            try: detail=json.loads(error.read().decode('utf-8')).get('error') or str(error)
            except (ValueError,UnicodeError):detail=str(error)
            return {'state':'blocked','agent_name':person['name'],
                    'message':person['name']+' kan inte starta: '+str(detail)[:220]}
        except (URLError,TimeoutError,OSError) as error:
            return {'state':'blocked','agent_name':person['name'],
                    'message':'Den lokala arbetsservern svarar inte: '+str(error)[:170]}
    return {'state':'blocked','message':person['name']+' saknar stöd för den här uppgiftstypen.'}


def install(srv):
    if getattr(srv,'_PW_V0121112',False):return
    srv._PW_V0121112=True
    srv.APP_VERSION=VERSION
    import pw_v01210 as provider
    import pw_v0121111 as staffplan
    original_status = provider.gemini_status
    provider.gemini_status = lambda _srv: apply_limit(provider,_srv,original_status(_srv))
    staffplan._capacity = lambda _srv,person: explain(provider,_srv,person)
    previous_plan = srv.dispatch_plan
    def plan(slug):
        result=previous_plan(slug)
        staff=srv.staff_read(slug)
        with srv.LOCK:
            working={j.get('agent_id') for j in srv.JOBS.values()
                if j.get('project')==slug and j.get('state') in ('queued','running')}
        all_orders=[o for o in srv.orders_read(slug) if o.get('status')=='waiting']
        assignments=result.get('assignments',[])
        assigned={a.get('order_id') for a in assignments}
        blocked=[]
        for order in all_orders:
            if order.get('id') in assigned:continue
            person=staffplan.selection(srv,slug,order,staff,working)
            if person:
                reason=(person['name']+' arbetar redan med annat uppdrag.' if person['id'] in working
                        else explain(provider,srv,person) or person['name']+' väntar på en ledig arbetsstation.')
                blocked.append({'order_id':order.get('id'),'station':order.get('station'),
                                'agent_id':person['id'],'agent_name':person.get('name'), 'reason':reason})
            else:
                blocked.append({'order_id':order.get('id'),'station':order.get('station'),
                                'reason':'Ingen behörig person för detta uppdrag.'})
        return {**result,'blocked':blocked}
    srv.dispatch_plan=plan
    previous_health=srv.dispatch_health
    def health(slug):
        result=previous_health(slug)
        plan_result=srv.dispatch_plan(slug)
        blocked=plan_result.get('blocked',[])
        if blocked and not plan_result.get('assignments') and not plan_result.get('active_jobs'):
            result=dict(result,state='person_waiting',reason=blocked[0]['reason'],blocked=blocked)
        return result
    srv.dispatch_health=health
    # Old reports in the binder remain historical. Do not create fresh
    # misleading manager reports each scheduler tick for a local capacity pause.
    original_report=srv.chief_block_report
    def report(slug,health_data):
        if health_data.get('state')=='person_waiting':return None
        return original_report(slug,health_data)
    srv.chief_block_report=report
    old_get=srv.Handler.do_GET
    old_post=srv.Handler.do_POST
    def get(self):
        if urlparse(self.path).path=='/api/pw-v0121112/capacity':
            if not self.allowed() or not self.auth():return self.reply(403,{'error':'Otillåten begäran'})
            status=provider.gemini_status(srv)
            return self.reply(200,{'used_today':status['used_today'],'local_limit':None,
              'limit_source':status['limit_source'],'can_send':status['can_send'],
              'verified':status['test_is_generation'],
              'paused':bool(status['paused_until_day'] or status.get('paused_until_epoch')),
              'pause_reason':status.get('pause_reason'),
              'paused_until_epoch':status.get('paused_until_epoch'),
              'paused_until_day':status.get('paused_until_day'),
              'google_remaining':'okänt'})
        return old_get(self)
    def post(self):
        route=urlparse(self.path).path
        if route not in ('/api/pw-v0121112/limit','/api/pw-v0121110/dispatch'):return old_post(self)
        if not self.allowed() or not self.auth() or not self.same_origin():
            return self.reply(403,{'error':'Otillåten begäran'})
        n=self.headers.get('Content-Length','')
        if not n.isdecimal() or not 0<int(n)<=2048:
            return self.reply(413,{'error':'Ogiltig begäran'})
        try:
            payload=json.loads(self.rfile.read(int(n)))
            if not isinstance(payload,dict):raise ValueError('Ogiltig begäran')
            if route.endswith('/limit'):
                return self.reply(410,{'error':'Lokal Gemini-dygnsgräns är avskaffad. Google bestämmer kvoten.'})
            slug=srv.validate_slug(payload.get('project',''))
            station=payload.get('station')
            agent_id=payload.get('agent_id')
            if agent_id is not None and (not isinstance(agent_id,str) or len(agent_id)>90):
                raise ValueError('Ogiltig anställd')
            # port is the *actual* bound server port (not a guessed default).
            srv._PW_PORT=self.server.server_port
            result=dispatch_person(srv,provider,staffplan,slug,station,agent_id)
            return self.reply(200,result)
        except (ValueError,TypeError,OSError) as exc:
            return self.reply(400,{'error':str(exc)[:320]})
    srv.Handler.do_GET=get
    srv.Handler.do_POST=post
