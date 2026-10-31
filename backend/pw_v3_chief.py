"""Pixel Works 3.4: Chief's deterministic, read-only assignment recommendation.

A recommendation does NOT execute AI, allocate a worker, change a project,
hire anyone, or infer model performance. v3.3's explicit start/approval is the
only way to launch an AI job. Tested scores are fictional character attributes.
"""
from __future__ import annotations
import json
from urllib.parse import urlparse
import pw_recruitment_v3 as crew
import pw_v3_jobs as jobs

CATEGORY = {
    'coding': ('Programmering', 'coding','programmer'),
    'art': ('Grafik och pixelart', 'art','artist'),
    'music': ('Musik och ljud', 'music','musician'),
    'qa': ('Test och kvalitet', 'qa','qa'),
    'writing': ('Story och dialog', 'writing','writer'),
    'research': ('Research', 'research','research'),
    'design': ('Speldesign', 'design','allround'),
    'planning': ('Planering', 'planning','lead'),
}

# Engine support refers only to ACTUAL V3.3 adapter operations, not a judgement
# of artistic quality. Neither adapter currently generates image/audio assets.
ENGINE_TYPES={'codex','gemini'}


def recommend(srv, payload):
    category=payload.get('category')
    if category not in CATEGORY:raise ValueError('Välj en arbetskategori')
    slug=srv.validate_slug(payload.get('project'))
    srv.verify_project(slug)
    instruction=payload.get('instruction')
    if not isinstance(instruction,str) or not 15<=len(instruction.strip())<=jobs.MAX_PROMPT:
        raise ValueError('Beskriv ett uppdrag med 15–3000 tecken')
    if payload.get('provider') not in ENGINE_TYPES:raise ValueError('Välj en känd AI-motor')
    provider=payload['provider']
    current=crew.read(srv)
    if not current:raise ValueError('Aktivera den nya personalstudion först')
    if not any(p.get('person_id')=='pw3-chef' and p.get('state')=='hired' for p in current['team']):
        raise ValueError('Arbetsledaren finns inte i studion')
    _,skill,role=CATEGORY[category]
    cap=jobs.provider_health(srv)[provider]
    active=[j for j in jobs.all_jobs(srv) if j.get('id') in getattr(srv,'_PW33_LIVE',{}) and j.get('state') in jobs.ACTIVE]
    with srv.LOCK:
        core=[dict(j) for j in srv.JOBS.values() if j.get('state') in jobs.ACTIVE]
    occupied={j.get('person_id') for j in active}|{j.get('agent_id') for j in core}
    project_locked=provider=='codex' and any(j.get('project')==slug for j in active+core)
    gemini_locked=provider=='gemini' and any(j.get('provider')=='gemini' for j in active+core)
    git_ok=True;git_reason=''
    if provider=='codex':
        try:git_ok,git_reason=srv.isolated_ready(slug)
        except (AttributeError,ValueError,OSError) as exc:git_ok=False;git_reason=str(exc)[:150]
    if provider=='codex':
        try:
            import pw_v01210
            access=pw_v01210.studio_access(srv).get('enabled')
        except (ImportError,AttributeError,OSError,ValueError):access=False
    else:access=True
    provider_ready=bool(cap.get('available')) and bool(git_ok) and bool(access)
    hints=[]
    if not cap.get('available'):hints.append(provider.upper()+' är inte verifierad/tillgänglig; ingen körning möjlig')
    if not access:hints.append('Studioåtkomst för skrivning saknas')
    if not git_ok:hints.append('Projektets Git-arbetsyta är inte redo: '+str(git_reason)[:150])
    if project_locked:hints.append('En annan kodkörning använder detta spel')
    if gemini_locked:hints.append('Ett Gemini-jobb pågår redan')
    # Game traits affect presentation and rank as small weights; skill and fit
    # dominate; provider has no per-character "smartness" multipliers.
    ranked=[]
    for person in current['team']:
        if person.get('state')!='hired':continue
        cid=person.get('character_id')
        character=crew.CATALOG['chef'] if cid=='chef' else crew.PEOPLE.get(cid)
        if not character:continue
        level=int(character.get('skills',{}).get(skill,0))
        traits=character.get('traits',{})
        bonus=(2 if category=='qa' and traits.get('careful',0)>=4 else 0)
        bonus+=(2 if category in ('design','art','writing') and traits.get('creative',0)>=4 else 0)
        role_match=(4 if person.get('role')==role else 0)
        # The Chief is the fallback worker for planning, not an automatic
        # competitor who monopolizes a specialized employee's role.
        if cid=='chef' and category!='planning':role_match-=8
        score=level*10+role_match+bonus
        if level>=4:fit='🌟 Bäst lämpad'
        elif level>=3:fit='👍 Kan fungera'
        else:fit='⚠️ Svag matchning'
        busy=person['person_id'] in occupied
        blocks=list(hints)
        if busy:blocks.append('Personen har ett pågående uppdrag')
        if project_locked and 'En annan kodkörning använder detta spel' not in blocks:blocks.append('Projektet är upptaget')
        if gemini_locked and 'Ett Gemini-jobb pågår redan' not in blocks:blocks.append('Gemini är upptagen')
        if category in ('art','music'):
            specialty=('bilder' if category=='art' else 'ljudfiler')
            limitation=f'Nuvarande motorer producerar inga riktiga {specialty} via v3-uppdrag; använd bara idé-/kodunderlag.'
        else:limitation=''
        reason=(f'{character["name"]}: {level}/5 i {CATEGORY[category][0].lower()} (fiktiv spelstat). '
                +('Rollen matchar uppdraget. ' if role_match>0 else 'Annan nuvarande yrkesroll. ')
                +('Föredrar noggrann kontroll. ' if bonus and category=='qa' else '')
                +('Stark kreativ ådra. ' if bonus and category in ('design','art','writing') else '')
                +('Chefen är reserv för specialistarbete. ' if cid=='chef' and category!='planning' else ''))
        ranked.append({'person_id':person['person_id'],'name':character['name'], 'character_id':cid,
             'role':person['role'],'role_name':crew.ROLES.get(person['role'],'Arbetsledare'),
             'skill':skill,'skill_name':crew.CATALOG['skills'][skill], 'level':level, 'score':score,
             'fit':fit,'reason':reason.strip(),'busy':busy,'can_start':not blocks,
             'blockers':blocks,'voice':character.get('speech_sample','')[:200], 'limitation':limitation})
    # Sort available first, then specialism – do not accidentally favor a busy
    # high-skill employee as a runnable candidate.
    ranked.sort(key=lambda p:(not p['can_start'],-p['score'],p['person_id']))
    specialists=[p for p in ranked if p['level']>=4 and p['character_id']!='chef']
    hiring=not specialists
    headline=('Vi borde rekrytera en '+CATEGORY[category][0].lower()+'-specialist.' if hiring else
              'Jag hittade '+str(len(specialists))+' specialist'+('er' if len(specialists)!=1 else '')+' i personalstyrkan.')
    available=sum(bool(p['can_start']) for p in ranked)
    return {'schema':1,'version':'3.4','project':slug,'category':category,
      'category_name':CATEGORY[category][0],'instruction':instruction.strip(),'provider':provider,
      'engine':cap,'engine_available':provider_ready,'available_people':available,
      'ranked':ranked,'chief_message':headline,
      'hiring_recommended':hiring,'hiring_role':role,
      'note':'Lokal regelbaserad rekommendation med FIKTIVA skills. Ingen AI tillfrågad och inget jobb startat.',
      'execution':'Endast spelaren kan godkänna start i v3.3:s uppdragsruta.'}


def install(srv):
    if getattr(srv,'_PW_V3_CHIEF',False):return
    srv._PW_V3_CHIEF=True
    old_post=srv.Handler.do_POST
    endpoint='/api/pw-v3/chief/recommend'
    def do_POST(self):
        if urlparse(self.path).path!=endpoint:return old_post(self)
        if not self.allowed() or not self.same_origin() or not self.auth():
            return self.reply(403,{'error':'Åtkomst nekad'})
        try:
            if self.headers.get('Content-Type','').split(';')[0].strip().lower()!='application/json':
                raise ValueError('JSON krävs')
            size=int(self.headers.get('Content-Length','0'))
            if not 2<=size<=5000:raise ValueError('Ogiltig begäran')
            data=json.loads(self.rfile.read(size))
            if not isinstance(data,dict):raise ValueError('JSON-objekt krävs')
            return self.reply(200,recommend(srv,data))
        except (ValueError,TypeError,KeyError,OSError) as exc:
            return self.reply(400,{'error':str(exc)[:260]})
    srv.Handler.do_POST=do_POST
