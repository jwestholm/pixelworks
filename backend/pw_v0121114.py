"""v0.12.11.14 – consolidate review reconciliation and trustworthy completion.

No project migration or AI calls. This is installed after the older extensions
and keeps the stable one-command launcher untouched.
"""
from __future__ import annotations

VERSION = '0.12.11.14'
DECISIONS = {'approve': 'done', 'forward': 'done',
             'revise': 'superseded', 'reject': 'archived'}
NO_CHANGE_NOTES = ('Inga nya filer att införa.', 'Resultatet finns redan i spelet.')


def normalize_reviewed_orders(srv, slug):
    """Repair a review/order pair after legacy reconciliation.

    Only touch the original linked order, never the replacement assignment.
    A human's durable decision wins over the report's older state=review.
    """
    reports = {r.get('id'): r for r in srv.list_reports(slug)
               if r.get('id') and r.get('review_decision') in DECISIONS}
    if not reports:
        return 0
    with srv.REPORT_UPDATE_LOCK:
        orders = srv.orders_read(slug)
        changed = 0
        for item in orders:
            report = reports.get(item.get('job_id'))
            if not report or report.get('order_id') != item.get('id'):
                continue
            target = DECISIONS[report['review_decision']]
            if item.get('status') in ('superseded', 'archived'):
                continue  # Never revive an owner-archived or replaced order.
            if item.get('status') not in ('running', 'claimed', 'review', 'done'):
                continue  # Another failure or action requires separate handling.
            if item.get('status') != target:
                item['status'] = target
                changed += 1
        if changed:
            srv.orders_write(slug, orders)
        return changed


def classify_codex_completion(job):
    """A zero-diff Codex run is completed, but NOT 'implemented in the game'."""
    if (job.get('provider', 'codex') != 'codex' or job.get('state') != 'done'
            or not job.get('integrated')):
        return False
    note = str(job.get('integration_note') or '').strip()
    if note not in NO_CHANGE_NOTES:
        return False
    job.update(integrated=False, changed_files_verified=False,
               completion_kind='no_code_changes',
               integration_note='Arbetspasset avslutades. Ingen ny spelkod infördes: '+note)
    return True


def install(srv):
    if getattr(srv, '_PW_V0121114', False):
        return
    srv._PW_V0121114 = True
    srv.APP_VERSION = VERSION
    old_reconcile = srv.reconcile_orders_from_reports
    def reconcile(slug):
        result = old_reconcile(slug)
        # The older reconciling code only examines report.state and can undo an
        # approved review. Do the owner-decision repair in the same cycle.
        repaired = normalize_reviewed_orders(srv, slug)
        return result + repaired if isinstance(result, int) else result
    srv.reconcile_orders_from_reports = reconcile

    old_finalize = srv.finalize_worker_job
    def finalize(job):
        classify_codex_completion(job)
        return old_finalize(job)
    srv.finalize_worker_job = finalize

    # The original runner tries optional Bible sidecar updates *before* it
    # calls finalize_worker_job. A no-change run must not publish those as
    # verified work while the integration result still says success.
    old_bible_updates = srv.apply_worker_bible_updates
    def apply_bible_updates(job):
        if str(job.get('integration_note') or '').strip() in NO_CHANGE_NOTES:
            return 0
        return old_bible_updates(job)
    srv.apply_worker_bible_updates = apply_bible_updates
