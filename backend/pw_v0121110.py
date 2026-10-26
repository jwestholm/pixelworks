"""Pixel Works 0.12.11.10: explicit recheck of studio work orders after a staff move.

Only schedules pre-existing orders with verified provider access and studio consent.
"""
import json
import re
from urllib.parse import urlparse

VERSION='0.12.11.13'

def dispatch_now(srv,slug,station):
    import pw_v01210 as provider
    slug=srv.validate_slug(slug)
    if station not in provider.SAFE_GEMINI_STATIONS:
        return {'state':'not_applicable','message':'Ingen rådgivningsstation valdes.'}
    if not provider.studio_access(srv)['enabled']:
        return {'state':'blocked','message':'Studion saknar tillstånd att arbeta. Öppna Inställningar → Studioåtkomst.'}
    status=provider.gemini_status(srv)
    if not status['can_send']:
        if status.get('paused_until_day') or status.get('paused_until_epoch'):
            reason='Arbetet är pausat efter ett anslutningsfel eller en kvotgräns.'
        elif not status['configured']:
            reason='Den anställdas AI-anslutning är inte konfigurerad.'
        else:
            reason='AI-anslutningen behöver verifieras under Inställningar.'
        return {'state':'blocked','message':reason}
    orders=[o for o in srv.orders_read(slug) if o.get('status')=='waiting' and o.get('station')==station]
    if not orders:return {'state':'idle','message':'Inga väntande uppdrag vid bordet.'}
    candidate=provider.auto_candidate(srv,slug)
    if not candidate:
        return {'state':'blocked','message':'Ingen ledig och behörig medarbetare kunde tilldelas. Kontrollera chefens placering och medarbetarens stationsbehörighet.'}
    order,agent,_chief=candidate
    if order.get('station')!=station:
        return {'state':'queued_elsewhere','message':'Arbetsledaren prioriterar en annan väntande arbetsorder.'}
    jid=provider.start_auto_job(srv,slug,order,agent)
    if jid:
        return {'state':'started','job_id':jid,'agent_name':agent.get('name','Medarbetaren'),
                'message':agent.get('name','Medarbetaren')+' börjar arbeta med uppdraget.'}
    return {'state':'busy','message':'Uppdraget är redan tilldelat eller startas av arbetsledaren.'}

def install(srv):
    if getattr(srv,'_PW_V0121110',False):return
    srv._PW_V0121110=True
    srv.APP_VERSION=VERSION
    old_post=srv.Handler.do_POST
    def do_POST(self):
        if urlparse(self.path).path!='/api/pw-v0121110/dispatch':return old_post(self)
        if not self.allowed() or not self.same_origin() or not self.auth():
            return self.reply(403,{'error':'Otillåten begäran'})
        n=self.headers.get('Content-Length','')
        if not n.isdecimal() or not 0<int(n)<=2048:
            return self.reply(413,{'error':'Ogiltig begäran'})
        try:
            data=json.loads(self.rfile.read(int(n)))
            if not isinstance(data,dict):raise ValueError('Ogiltigt innehåll')
            slug=data.get('project','')
            station=data.get('station','')
            result=dispatch_now(srv,slug,station)
            return self.reply(200,result)
        except (ValueError,OSError,RuntimeError) as exc:
            return self.reply(400,{'error':str(exc)[:250]})
    srv.Handler.do_POST=do_POST
