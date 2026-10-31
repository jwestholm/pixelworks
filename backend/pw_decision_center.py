"""Pixel Works: one owner decision mailbox, opt-in low-risk retries, bounded Git retry.

Only existing actionable help cases are surfaced; no GET starts work.
A retry is a *normal passive work order*, never a forced git merge or AI call.
Audio/image approvals remain human-only regardless of automation settings.
"""
from __future__ import annotations

import json
import os
import secrets
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, parse_qs

_LOCK=threading.RLock()
ROOT='/api/pw-tools/decisions'
DELAY=30*60
DEFAULT={'retry_git_conflict_once':True,'auto_retry_transient_once':False}
TRANSIENT=('tillfälligt', 'temporarily unavailable', 'timed out', 'timeout', 'låst av', 'resurs tillfälligt')


def _settings_path(srv):
    folder=srv.ROOT/'secrets'
    if folder.is_symlink():raise ValueError('Osäker hemlighetskatalog')
    return folder/'decision-policy-v1.json'


def _atomic(path, data):
    if path.is_symlink() or path.parent.is_symlink():raise ValueError('Osäker inställningsfil')
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    tmp=path.parent/('.pw-decisions-'+secrets.token_hex(8))
    try:
        fd=os.open(tmp,os.O_EXCL|os.O_CREAT|os.O_WRONLY,0o600)
        with os.fdopen(fd,'w',encoding='utf-8') as out:
            json.dump(data,out,ensure_ascii=False,indent=2)
        os.replace(tmp,path)
    finally:tmp.unlink(missing_ok=True)


def settings(srv):
    path=_settings_path(srv)
    if path.is_symlink():raise ValueError('Osäker inställningsfil')
    with _LOCK:
        data=json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {}
        if not isinstance(data,dict):raise ValueError('Ogiltig beslutskonfiguration')
        return {k:data.get(k,v) is True for k,v in DEFAULT.items()}


def configure(srv,payload):
    if payload.get('approval')!='SET_OWNER_DECISION_POLICY':
        raise ValueError('Bekräfta beslutspolicyn')
    if set(payload)-{'approval'}!=set(DEFAULT):raise ValueError('Båda valen måste anges')
    if any(type(payload[k]) is not bool for k in DEFAULT):raise ValueError('Endast på/av stöds')
    with _LOCK:
        _atomic(_settings_path(srv),{k:payload[k] for k in DEFAULT})
        return settings(srv)


def _snooze_path(srv,slug):
    slug=srv.validate_slug(slug);srv.verify_project(slug)
    folder=srv.path_for(slug)/'management'
    if folder.is_symlink() or not folder.is_dir():raise ValueError('Osäker projektmapp')
    return folder/'decision-later.json'


def _snoozes(srv,slug):
    path=_snooze_path(srv,slug)
    if path.is_symlink():raise ValueError('Osäkert pausregister')
    if not path.is_file():return {}
    data=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data,dict) or len(data)>500:raise ValueError('Ogiltigt pausregister')
    return data


def cases(srv,slug):
    slug=srv.validate_slug(slug);srv.verify_project(slug)
    with _LOCK:
        pauses=_snoozes(srv,slug)
    helps=srv.list_help_cases(slug)
    now=time.time()
    return {'cases':[{'id':'help:'+str(x['id']), 'report_id':x['id'],
         'employee':x.get('agent_name'), 'title':str(x.get('agent_name') or 'Anställd')+' behöver hjälp',
         'state':x.get('state'), 'reason':x.get('friendly_reason'), 'technical_reason':x.get('reason'),
         'summary':x.get('summary'), 'instruction':x.get('instruction'),
         'station':x.get('station'), 'created_at':x.get('created_at'),
         'deferred':float(pauses.get('help:'+str(x['id']),0) or 0)>now}
         for x in helps], 'policy':settings(srv)}


def later(srv,body):
    slug=srv.validate_slug(body.get('project'));srv.verify_project(slug)
    ident=body.get('case_id')
    if not isinstance(ident,str) or not ident.startswith('help:') or len(ident)!=17:
        raise ValueError('Ogiltigt beslutsärende')
    with _LOCK:
        rows=cases(srv,slug)['cases']
        if not any(r['id']==ident for r in rows):raise ValueError('Ärendet är redan löst')
        pauses=_snoozes(srv,slug)
        pauses={k:v for k,v in pauses.items() if float(v or 0)>time.time()-86400}
        pauses[ident]=time.time()+DELAY
        _atomic(_snooze_path(srv,slug),pauses)
    return {'deferred':True,'retry_after_minutes':30}


def _mandate_ok(srv,slug):
    # No fresh cloud operations from this function, only enqueue on an existing mandate.
    if not srv.project_mandate(slug).get('enabled'):return False
    try:
        import pw_v01210
        return bool(pw_v01210.studio_access(srv).get('enabled'))
    except (ImportError, ValueError, OSError, AttributeError):return False


def retry_once(srv,job):
    """Queue exactly one followup to reapply intended change against latest work.

    Does not force merge, rewrite git history, call providers or modify worktree.
    The existing normal scheduler remains the only executor.
    """
    if not isinstance(job,dict):return None
    slug=job.get('project');jid=job.get('id');state=job.get('state')
    if not slug or not jid or state not in ('failed','review'):return None
    note=str(job.get('integration_note') or '').lower()
    error=str(job.get('error') or '').lower()
    policy=settings(srv)
    conflict=(state=='review' and 'krockar med andra ändringar' in note)
    transient=(state=='failed' and any(key in error for key in TRANSIENT))
    if not ((conflict and policy['retry_git_conflict_once']) or
            (transient and policy['auto_retry_transient_once'])):return None
    slug=srv.validate_slug(slug);srv.verify_project(slug)
    if not _mandate_ok(srv,slug):return None
    with _LOCK,srv.LOCK:
        orders=srv.orders_read(slug)
        origin=next((o for o in orders if o.get('id')==job.get('order_id') and
                     o.get('job_id')==jid and o.get('status')==state),None)
        if not origin or origin.get('auto_retry_attempt',0):return None
        if any(o.get('parent_report_id')==jid for o in orders):return None
        station=origin.get('station')
        if station not in srv.SKILL_STATIONS:return None
        brief=str(origin.get('instruction') or '').strip()
        if not brief:return None
        explanation=('Git-konflikt efter att flera arbetare ändrat spelet.' if conflict
                     else 'Tillfälligt tekniskt hinder.')
        instruction=(f'AUTOMATISKT ENGÅNGSOMFÖRSÖK: {explanation} Utgå från spelets SENASTE '
                     'version. Återskapa avsedd funktion med minsta säkra ändring. '
                     'Ingen force merge, ingen push, ingen historikomskrivning. '
                     'Kontrollera konflikter och redovisa verkliga tester. '\
                     '\nUrsprunglig arbetsorder: '+brief)[:3750]
        record={'id':secrets.token_hex(6),'station':station,'instruction':instruction,
                'priority':origin.get('priority',2),'attachment_ids':list(origin.get('attachment_ids') or []),
                'status':'waiting','created_at':datetime.now(timezone.utc).isoformat(),
                'job_id':None,'parent_report_id':jid,'auto_retry_attempt':1,
                'auto_retry_reason':'git_conflict' if conflict else 'transient_failure'}
        orders.append(record)
        srv.orders_write(slug,orders)
        return record


def install(srv):
    if getattr(srv,'_PW_DECISION_CENTER',False):return
    srv._PW_DECISION_CENTER=True
    original=srv.finalize_worker_job
    def finalize(job):
        result=original(job)
        if result and isinstance(job,dict):
            try:retry_once(srv,job)
            except (ValueError,OSError,TypeError,KeyError,RuntimeError) as ex:
                job['decision_retry_error']=str(ex)[:200]
        return result
    srv.finalize_worker_job=finalize
    prev_get=srv.Handler.do_GET;prev_post=srv.Handler.do_POST
    def do_GET(self):
        path=urlparse(self.path)
        if path.path not in (ROOT,ROOT+'/settings'):return prev_get(self)
        if not self.allowed() or not self.auth():return self.reply(403,{'error':'Ogiltig session'})
        try:
            if path.path==ROOT+'/settings':return self.reply(200,{'policy':settings(srv)})
            slug=parse_qs(path.query).get('project',[''])[0]
            return self.reply(200,cases(srv,slug))
        except (ValueError,OSError,TypeError,KeyError) as ex:return self.reply(400,{'error':str(ex)[:230]})
    def do_POST(self):
        path=urlparse(self.path).path
        if path not in (ROOT+'/settings',ROOT+'/later'):return prev_post(self)
        if not self.allowed() or not self.auth() or not self.same_origin():
            return self.reply(403,{'error':'Otillåten begäran'})
        n=self.headers.get('Content-Length','')
        if not n.isdecimal() or not 0<int(n)<=2500:return self.reply(413,{'error':'Ogiltig begäran'})
        try:
            payload=json.loads(self.rfile.read(int(n)))
            if not isinstance(payload,dict):raise ValueError('Förväntade ett JSON-objekt')
            return self.reply(200,{'policy':configure(srv,payload)} if path.endswith('/settings') else later(srv,payload))
        except (ValueError,OSError,TypeError,KeyError) as ex:return self.reply(400,{'error':str(ex)[:230]})
    srv.Handler.do_GET=do_GET;srv.Handler.do_POST=do_POST
