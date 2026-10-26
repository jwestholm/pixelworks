"""Pixel Works 0.12.11.15 – explicit creator mode and independent job planning.

The chief allocates by worker competence. Concurrent advisory sessions do not
occupy the code workspace, while Codex writers retain the engine's authenticated
Git worktree validation and conflict-aware integration.
"""
VERSION = '0.12.11.15'


def parallel_plan(srv, old, staffplan, slug):
    plan = old(slug)
    if not plan.get('leader_active'):
        return plan
    # This function only *plans*. It never makes AI calls or Git changes.
    staff = srv.staff_read(slug)
    orders = sorted((o for o in srv.orders_read(slug)
                     if o.get('status') == 'waiting'),
                    key=lambda o:(o.get('priority', 2), o.get('created_at',''), o.get('id','')))
    with srv.LOCK:
        active = [j for j in srv.JOBS.values()
                  if j.get('project') == slug and j.get('state') in ('queued','running')]
    busy = {j.get('agent_id') for j in active}
    active_codex = any(j.get('provider', 'codex') == 'codex' for j in active)
    # A second writer is only attempted when a verified local worktree is ready.
    parallel_ok = not active_codex or bool(srv.isolated_ready(slug)[0])
    skills = srv.get_skill_settings(slug)
    new_assignments = []
    blocked = []
    reserved = set(busy)
    # A manager must not start another plan while already carrying out one.
    manager_ids={p['id'] for p in staff if p.get('role_type')=='lead'}
    manager_busy=bool(manager_ids & busy)
    for order in orders:
        if manager_busy:
            blocked.append({'order_id':order['id'],'station':order.get('station'),
                            'reason':'Arbetsledaren arbetar redan med planeringen.'})
            continue
        station = order.get('station')
        suitable = [p for p in staff if staffplan._eligible(srv,slug,p,order)]
        suitable.sort(key=lambda p:(-staffplan._score(p,order,skills),
                                    p.get('name',''), p.get('id','')))
        if not suitable:
            blocked.append({'order_id':order['id'],'station':station,
                            'reason':'Ingen anställd har behörighet för uppdraget.'})
            continue
        preferred = suitable[0]
        # Never replace a creative specialist merely because their own worker
        # adapter is busy, paused or waiting. The separate adviser scheduler
        # is responsible for dispatching them.
        if preferred.get('provider') != 'codex':
            blocked.append({'order_id':order['id'],'station':station,
                            'agent_id':preferred['id'],'agent_name':preferred.get('name'),
                            'reason':preferred.get('name','Medarbetaren')+
                                     (' arbetar redan med ett annat uppdrag.' if preferred['id'] in reserved
                                      else ' väntar på sitt arbetsverktyg.')})
            continue
        # Multiple eligible coders may work in separate local Git worktrees.
        # The engine will still enforce file-safety and per-job authentication.
        coders = [p for p in suitable if p.get('provider')=='codex'
                  and p.get('id') not in reserved]
        person = coders[0] if coders else None
        if person is None or not parallel_ok or (person.get('role_type')=='lead' and reserved):
            blocked.append({'order_id':order['id'],'station':station,
                            'agent_id':preferred['id'],'agent_name':preferred.get('name'),
                            'reason':('En annan kodarbetare är aktiv och den isolerade Git-arbetsytan är inte redo.'
                                      if not parallel_ok else preferred.get('name','Medarbetaren')+' är upptagen.')})
            continue
        reserved.add(person['id'])
        new_assignments.append({'order_id':order['id'],
            'station':station,'priority':order.get('priority',2),
            'agent_id':person['id'],'agent_name':person['name'],
            'provider':person['provider'],
            'delegated_by':next((p.get('name','Arbetsledaren') for p in staff
                                 if p.get('role_type')=='lead' and p.get('station')=='lead'), 'Arbetsledaren'),
            'fallback_lead':person.get('role_type')=='lead','instruction':order['instruction'],
            'attachment_ids':order.get('attachment_ids',[])})
        if person.get('role_type')=='lead':
            manager_busy=True
    return {**plan,'assignments':new_assignments,
            'next':new_assignments[0] if new_assignments else None,
            'blocked':blocked,'waiting':len(orders)}


def install(srv):
    if getattr(srv, '_PW_V0121115', False):return
    srv._PW_V0121115=True
    srv.APP_VERSION=VERSION
    import pw_v0121111 as staffplan
    previous=srv.dispatch_plan
    srv.dispatch_plan=lambda slug:parallel_plan(srv,previous,staffplan,slug)
