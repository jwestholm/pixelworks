"""Pixel Works v0.12.11.16: retry the *existing* pending order from a chief's report.

No new order, no permission bypass, no API usage until the owner clicks Retry.
The existing scheduler independently retries outstanding orders after temporary
workspace conflicts. This endpoint allows an immediate, safely checked attempt.
"""
from __future__ import annotations
import json
import re
from urllib.parse import urlparse

VERSION='0.12.11.16'
HEX12=re.compile(r'[0-9a-f]{12}\Z')
MAX_POST=2048


def report_orders(srv, slug, report_id):
    slug=srv.validate_slug(slug)
    if not isinstance(report_id,str) or not HEX12.fullmatch(report_id):
        raise ValueError('Ogiltigt rapport-ID')
    file=srv.report_path(slug,report_id)
    if not file.is_file():raise ValueError('Rapporten finns inte längre')
    report=json.loads(file.read_text(encoding='utf-8'))
    if not isinstance(report,dict) or report.get('source')!='studio-dispatch' or report.get('project')!=slug:
        raise ValueError('Omförsök gäller endast arbetsledarens egna felrapporter')
    if report.get('archived'):
        raise ValueError('Rapporten är arkiverad. Använd den aktuella arbetskön.')
    # Chief reports include the affected IDs in the persisted explanation; reject
    # unrelated orders and stale reports to avoid an accidental dispatch.
    text=str(report.get('summary') or '')
    pending=[o for o in srv.orders_read(slug)
             if o.get('status')=='waiting' and str(o.get('id') or '') in text]
    return sorted(pending,key=lambda o:(o.get('priority',2),o.get('created_at',''),o.get('id','')))


def retry(srv, data):
    import pw_v0121112 as dispatcher
    import pw_v0121111 as staffplan
    import pw_v01210 as provider
    if not isinstance(data,dict):raise ValueError('Ogiltig begäran')
    slug=srv.validate_slug(data.get('project'))
    report_id=data.get('report_id')
    choices=report_orders(srv,slug,report_id)
    if not choices:
        return {'state':'idle','message':'Ärendet är redan avslutat eller saknar väntande arbetsorder. Ingen ny order skapades.'}
    order_id=data.get('order_id')
    if order_id is not None and (not isinstance(order_id,str) or not HEX12.fullmatch(order_id)):
        raise ValueError('Ogiltigt arbetsorder-ID')
    if order_id is None:
        if len(choices)!=1:
            return {'state':'choose','message':'Välj vilken väntande arbetsorder som ska startas.',
                    'orders':[{'id':o['id'],'station':o['station']} for o in choices]}
        order=choices[0]
    else:
        order=next((o for o in choices if o['id']==order_id),None)
        if order is None:raise ValueError('Den valda arbetsordern hör inte längre till ärendet')
    roster=srv.staff_read(slug)
    person=staffplan.selection(srv,slug,order,roster)
    if not person:
        return {'order_id':order['id'],'state':'blocked','message':'Ingen behörig anställd kan ta den väntande arbetsordern.'}
    with srv.LOCK:
        active=[j for j in srv.JOBS.values() if j.get('project')==slug and j.get('state') in ('queued','running')]
    if any(j.get('agent_id')==person['id'] for j in active):
        return {'order_id':order['id'],'state':'blocked', 'agent_name':person['name'],
                'message':person['name']+' arbetar redan. Försök igen när det arbetspasset är klart.'}
    # A direct writer owns work/. Do not start, move, or disturb the worker
    # while that write is still in progress.
    if person.get('provider')=='codex' and any(j.get('provider','codex')=='codex' and
            not j.get('worktree') and not j.get('isolated') for j in active):
        return {'order_id':order['id'],'state':'blocked', 'agent_name':person['name'],
                'message':'En annan programmerare använder spelmappen. Försök igen när arbetspasset är klart.'}
    original_station=person.get('station','cafe')
    moved=False
    if person.get('provider')=='codex' and original_station!=order['station']:
        # Normal Codex dispatch requires the employee at their workstation.
        # Use the same validated move operation as the game interface.
        try:
            srv.move_staff(slug,{'agent_id':person['id'],'station':order['station']})
            moved=True
        except (ValueError,OSError) as exc:
            return {'order_id':order['id'],'state':'blocked', 'agent_name':person['name'],
                    'message':person['name']+' kunde inte gå till bordet: '+str(exc)[:170]}
    try:
        # Existing dispatcher still enforces credentials, studio consent,
        # real capacity, Git validation and atomic claim of this exact order.
        result=dispatcher.dispatch_person(srv,provider,staffplan,slug,order['station'],
                                          agent_id=person['id'],order_id=order['id'])
    finally:
        if moved:
            with srv.LOCK:
                busy=any(j.get('project')==slug and j.get('agent_id')==person['id'] and
                    j.get('state') in ('queued','running') for j in srv.JOBS.values())
            if not busy:
                try:srv.move_staff(slug,{'agent_id':person['id'],'station':original_station})
                except (ValueError,OSError):pass
    return {'order_id':order['id'],**result}


def install(srv):
    if getattr(srv,'_PW_V0121116',False):return
    srv._PW_V0121116=True
    srv.APP_VERSION=VERSION
    prev=srv.Handler.do_POST
    def do_POST(self):
        if urlparse(self.path).path!='/api/pw-v0121116/retry':return prev(self)
        if not self.allowed() or not self.same_origin() or not self.auth():
            return self.reply(403,{'error':'Otillåten begäran'})
        length=self.headers.get('Content-Length','')
        if not length.isdecimal() or not 0<int(length)<=MAX_POST:
            return self.reply(413,{'error':'Ogiltig storlek'})
        try:
            data=json.loads(self.rfile.read(int(length)))
            if not isinstance(data,dict):raise ValueError('Objekt förväntas')
            srv._PW_PORT=self.server.server_port
            return self.reply(200,retry(srv,data))
        except (ValueError,TypeError,OSError,json.JSONDecodeError) as err:
            return self.reply(400,{'error':str(err)[:300]})
    srv.Handler.do_POST=do_POST
