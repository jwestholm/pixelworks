"""Passive, idempotent QA handoff after real, integrated studio code work.

A queued QA order is NOT evidence that tests ran or that work was verified.
Normal Pixel Works mandates and the existing dispatcher remain authoritative.
"""
from __future__ import annotations

import secrets
import threading
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

_HANDOFF_STATIONS = frozenset({'code', 'art', 'music', 'voice'})
_GUARD = threading.RLock()


def now(): return datetime.now(timezone.utc).isoformat()


def handoff(server, job):
    if (not job.get('integrated') or job.get('state') != 'done'
            or job.get('station') not in _HANDOFF_STATIONS
            or not job.get('order_id') or not job.get('id')):
        return None
    slug = server.validate_slug(job['project'])
    server.verify_project(slug)
    # Original task must still belong to this successful worker, not a newer
    # assignment, archived order, or unrelated report.
    with _GUARD, server.LOCK:
        orders = server.orders_read(slug)
        origin = next((x for x in orders if x.get('id') == job['order_id']
                       and x.get('job_id') == job['id'] and x.get('status') == 'done'), None)
        if origin is None: return None
        match = next((x for x in orders if x.get('qa_for_job') == job['id']), None)
        if match: return match
        instruction = (
            'Oberoende QA efter integrerad arbetsorder. Kontrollera det faktiska spelet i projektets '
            'arbetsyta. Reproducera centrala funktioner och testa i minst en tillgänglig webbläsare '
            'när möjligt. Dokumentera EXAKT vilka tester som faktiskt kördes, deras kommandon och '
            'resultat. Om Firefox eller manuell ljudlyssning saknas, markera uttryckligen EJ TESTAT. '
            'Skriv inte att något är verifierat utan konkreta kontroller. '
            'Originalorder: ' + str(job['order_id'])[:24] + '. '
            'Originalsession: ' + str(job['id'])[:24] + '. '
            'Mål: ' + str(origin.get('instruction') or '')[:900]
        )[:1700]
        record = {'id':secrets.token_hex(6), 'station':'qa', 'instruction':instruction,
                  'priority':2, 'attachment_ids':[], 'status':'waiting', 'created_at':now(),
                  'job_id':None, 'qa_for_job':job['id'], 'qa_for_order':origin['id'],
                  'review_required':True, 'independently_verified':False}
        orders.append(record)
        server.orders_write(slug, orders)  # passive, never starts a provider here
        return record


def status(server, slug, report_id=None):
    slug = server.validate_slug(slug)
    server.verify_project(slug)
    rows = [x for x in server.orders_read(slug) if x.get('qa_for_job')]
    if report_id:
        rows = [x for x in rows if x['qa_for_job'] == report_id]
    return {'handoffs': [{k:x.get(k) for k in ('id','qa_for_job','qa_for_order',
                       'status','job_id','independently_verified')} for x in rows],
            'warning': 'En färdig QA-order betyder inte oberoende verifierat. Granska testrapportens evidens.'}


def install(server):
    if getattr(server,'_PW_QA_HANDOFF',False): return
    server._PW_QA_HANDOFF=True
    old_finalize = server.finalize_worker_job
    def finalize(job):
        result = old_finalize(job)
        if result and isinstance(job, dict):
            try: handoff(server, job)
            except (OSError, ValueError, KeyError, TypeError) as ex:
                # Never turn a completed, integrated job into a failure because
                # optional QA queueing is unavailable. Expose the honest error.
                job['qa_handoff_error'] = str(ex)[:240]
        return result
    server.finalize_worker_job = finalize
    old_get = server.Handler.do_GET
    def do_GET(self):
        url = urlparse(self.path)
        if url.path != '/api/pw-tools/qa': return old_get(self)
        if not self.allowed() or not self.auth(): return self.reply(403, {'error':'Ogiltig session'})
        try:
            qs=parse_qs(url.query)
            return self.reply(200, status(server, qs.get('project',[''])[0],qs.get('report',[None])[0]))
        except (ValueError,OSError,TypeError) as ex:
            return self.reply(400, {'error':str(ex)[:250]})
    server.Handler.do_GET=do_GET
