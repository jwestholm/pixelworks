/* Pixel Works v0.12.11.5 – Gemini in the office activity rail + proposal decisions. */
(() => {
  'use strict';
  const $=(q,root=document)=>root.querySelector(q);
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const validSlug=s=>/^[a-z0-9][a-z0-9-]{1,49}$/.test(s||'');
  const validId=s=>/^[0-9a-f]{12}$/.test(s||'');
  const currentProject=()=>$('#projectSelect')?.value||'';
  let token='',pending=false,lastProject='',jobsCache=[],reportsCache=[];
  const reviewModal=document.createElement('dialog');reviewModal.id='pw115Review';
  reviewModal.setAttribute('aria-label','Granska förslag');
  reviewModal.innerHTML='<h2>📋 Granska medarbetarens förslag</h2><div id="pw115ReviewContent"></div><div class="pw115-actions"><button id="pw115Close" type="button">✕ Stäng</button></div>';
  document.body.append(reviewModal);
  $('#pw115Close').onclick=()=>reviewModal.close();
  const style=document.createElement('style');style.textContent=`
    #pw115Review{width:min(710px,94vw);max-height:85vh;overflow:auto;color:#ffebc2;background:#223149;border:7px ridge #aa7951;padding:18px;box-sizing:border-box;box-shadow:8px 9px 0 #0b1622;font:14px system-ui,sans-serif;z-index:16000}
    #pw115Review::backdrop{background:#07101dd0}
    #pw115Review h2{color:#ffd58b;margin:0 0 12px}
    #pw115Review .pw115-proposal{background:#ffefbf;color:#3d3029;padding:12px;white-space:pre-wrap;overflow-wrap:anywhere;max-height:37vh;overflow:auto;line-height:1.55}
    #pw115Review .pw115-caption{font-size:12px;line-height:1.5;color:#f5e4bd;margin:9px 0}
    #pw115Review textarea{box-sizing:border-box;width:100%;min-height:85px;background:#111e31;color:#fff;border:2px solid #8294aa;padding:8px;font:inherit}
    #pw115Review button,.pw115-rail button,.pw115-inbinder{cursor:pointer;padding:6px 10px;background:#f0c76d;border:2px solid #785336;color:#212d45;font-weight:700}
    #pw115Review button:disabled{opacity:.5;cursor:default}
    #pw115Review .pw115-actions{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
    #pw115Review #pw115Close{background:#768ba7;color:white}
    #pw115Review .pw115-note{font-size:12px;color:#d8ebc0;min-height:1.5em;white-space:pre-wrap}
    .pw115-rail{margin:8px 1px;padding:9px;background:#183650;border:1px solid #5e8e94;font-size:12px;line-height:1.4;color:#f3e6c8}
    .pw115-rail h4{color:#bceee0;margin:0 0 6px;font-size:12px}
    .pw115-event{padding:5px 0;border-top:1px solid #426277}
    .pw115-event strong{display:block;color:#fff}
    .pw115-event small{display:block;color:#c5d7df;margin:4px 0}
    .pw115-rail button{margin-top:5px;font-size:12px}
    .pw115-inbinder{display:inline-block;margin:8px 0}
  `;document.head.append(style);
  async function api(path,payload){
    if(!token){const b=await fetch('/api/bootstrap',{credentials:'same-origin'});if(!b.ok)throw Error('Servern svarar inte');token=(await b.json()).token}
    const o={credentials:'same-origin',headers:{'X-Pixelworks-Token':token}};
    if(payload){o.method='POST';o.headers['Content-Type']='application/json';o.body=JSON.stringify(payload)}
    const res=await fetch(path,o),value=await res.json();
    if(!res.ok)throw Error(value.error||'HTTP '+res.status);return value;
  }
  function decisionLabel(r){const value=r.review_decision;
    return {approve:'✅ Godkänt som idé',forward:'🛠️ Skickat till programmeraren',
      revise:'💬 Förbättring beställd',reject:'🗑️ Avvisat'}[value]||'🟡 Väntar på granskning';
  }
  function errorOutput(where,message){const e=$(where,reviewModal);if(e)e.textContent=message}
  async function openReview(project,id){
    if(!validSlug(project)||!validId(id))return;
    reviewModal.dataset.reportId=id;
    if(!reviewModal.open)reviewModal.showModal();
    const box=$('#pw115ReviewContent');box.textContent='Läser rapporten…';
    try{
      const response=await api('/api/projects/'+project+'/reports');
      const r=(response.reports||[]).find(x=>x.id===id&&x.source==='gemini-api');
      if(!r)throw Error('Förslaget finns inte i projektet');
      api('/api/projects/'+project+'/reports/'+id,{action:'read'}).catch(()=>{});
      const processed=Boolean(r.review_decision);
      box.innerHTML=`<h3>${esc(r.agent_name||'Gemini')} · ${esc(r.station||'Dokumentation')}</h3>
        <p class="pw115-caption">${esc(decisionLabel(r))} · ${esc(r.created_at||'')} · Ej oberoende speltestat</p>
        <div class="pw115-proposal">${esc(r.summary||'Inget förslag sparat.')}</div>
        <p class="pw115-caption"><strong>Godkännande sparar beslutad design i Game Bible, inte kod.</strong> Välj ”Skicka till programmeraren” för att låta en behörig programmerare implementera idén.</p>
        ${processed?`<p>✅ Beslutet är redan sparat: ${esc(decisionLabel(r))}</p>`:
          `<label for="pw115Feedback">Din feedback (används när du ber medarbetaren förbättra)<br>
             <textarea id="pw115Feedback" maxlength="1400" placeholder="Exempel: Gör instruktionerna kortare och lägg dem bredvid spelplanen."></textarea></label>
           <div class="pw115-actions">
             <button data-pw115-action="approve" type="button">✅ Godkänn förslaget</button>
             <button data-pw115-action="forward" type="button">🛠️ Skicka till programmeraren</button>
             <button data-pw115-action="revise" type="button">💬 Be ${esc(r.agent_name||"medarbetaren")} förbättra</button>
             <button data-pw115-action="reject" type="button">Avvisa</button>
           </div>`}<p class="pw115-note" id="pw115Message" role="status"></p>`;
      box.querySelectorAll('[data-pw115-action]').forEach(button=>button.onclick=async()=>{
        const action=button.dataset.pw115Action,feedback=$('#pw115Feedback',box)?.value||'';
        if(action==='revise'&&feedback.trim().length<5){errorOutput('#pw115Message','Beskriv vad som ska förbättras.');return}
        box.querySelectorAll('[data-pw115-action]').forEach(b=>b.disabled=true);
        errorOutput('#pw115Message','Sparar beslutet…');
        try{
          const result=await api('/api/pw-v012115/review',{project,report_id:id,action,feedback});
          errorOutput('#pw115Message',result.message||'Beslutet sparat');
          // Don't display a second set of clickable buttons: decisions are final.
          box.querySelectorAll('[data-pw115-action]').forEach(b=>b.remove());
          const input=$('#pw115Feedback',box);if(input)input.disabled=true;
          await update();
          window.dispatchEvent(new Event('pixelworks:gemini-review-changed'));
        }catch(e){errorOutput('#pw115Message','⚠ '+e.message);
          box.querySelectorAll('[data-pw115-action]').forEach(b=>b.disabled=false);}
      });
    }catch(e){box.textContent='⚠ '+e.message}
  }
  window.pixelWorksGeminiReview=openReview;
  function ensureFeed(){
    const panel=$('#realSessionPanel');if(!panel)return null;
    let feed=$('#pw115GeminiRail');
    if(!feed){feed=document.createElement('div');feed.id='pw115GeminiRail';feed.className='pw115-rail';
      const events=$('#realJobEvents',panel);if(events)events.before(feed);else panel.append(feed);
      feed.addEventListener('click',e=>{
        const b=e.target.closest('[data-pw115-review]');if(b)openReview(currentProject(),b.dataset.pw115Review);
      });}
    return feed;
  }
  const stateLabels={queued:'⏳ Köad',running:'🔵 Arbetar',review:'📄 Klar – granska förslag',failed:'🔴 Kunde inte slutföra',done:'✅ Klar'};
  function logGemini(){
    const feed=ensureFeed();if(!feed)return;
    const geminiJobs=jobsCache.filter(j=>j.provider==='gemini');
    const reports=reportsCache.filter(r=>r.source==='gemini-api');
    const active=geminiJobs.filter(j=>['queued','running'].includes(j.state));
    // Work the real project queue, not any fictitious demo events.
    const reportIds=new Set(reports.map(x=>x.id));
    const recent=[...active.map(j=>({id:j.id,agent_name:j.agent_name,state:j.state,
      detail: (j.state==='queued'?'I kö: ':'Arbetar med: ')+(String(j.instruction||'Läs-/analysuppdrag')).slice(0,140)})),
      ...reports.slice(0,5).filter(r=>!r.archived).map(r=>({id:r.id,agent_name:r.agent_name,
        state:r.state,detail:(r.work_request?'Uppdrag: '+r.work_request.slice(0,110)+' · ':'')+(r.review_decision?decisionLabel(r):r.state==='review'?'Förslaget är klart och väntar på ditt beslut.':String(r.error||r.summary||'').slice(0,140)),report:r}))]
      .filter((item,index,array)=>array.findIndex(x=>x.id===item.id)===index).slice(0,4);
    if(!recent.length){feed.hidden=true;return}feed.hidden=false;
    const rows=recent.map(j=>`<div class="pw115-event"><strong>☕ ${esc(j.agent_name||'Gemini')} · ${esc(stateLabels[j.state]||j.state)}</strong>
      <small>${esc(j.detail)}</small>${j.report?.state==='review'&&!j.report.review_decision?
      `<button type="button" data-pw115-review="${esc(j.id)}">📝 Granska / godkänn</button>`:''}</div>`).join('');
    feed.innerHTML='<h4>☕ GEMINI · VERKLIGA ARBETEN</h4>'+rows;
    // Correct the legacy Codex-only renderer for Gemini sessions, while keeping
    // Codex event history untouched for real Codex jobs.
    correctLegacyProvider();
  }
  function correctLegacyProvider(){
    const line=$('#realJobProject'),root=$('#realJobEvents');if(!line)return;
    const match=line.textContent.match(/Session ([a-f0-9]{12})/);
    const job=match?jobsCache.find(x=>x.id===match[1]):null;
    if(!job||job.provider!=='gemini')return;
    const corrected=line.textContent.replace(' · Codex CLI · ',' · Gemini API · ');
    if(corrected!==line.textContent)line.textContent=corrected;
    const report=reportsCache.find(r=>r.id===job.id&&r.source==='gemini-api');
    const label=report?.review_decision?decisionLabel(report):(stateLabels[job.state]||job.state);
    const state=$('#realJobState');if(state&&state.textContent!==label)state.textContent=label;
    const badge=$('#agentModeBadge');if(badge&&badge.textContent.includes('CODEX'))badge.textContent='☕ SKARPT · GEMINI '+(job.state||'').toUpperCase();
    if(root&&!root.querySelector('.pw115-gemini-session')){
      const hasGemini=Array.from(root.children).some(x=>x.classList.contains('pw115-gemini-session'));
      if(!hasGemini){root.replaceChildren();const line=document.createElement('div');line.className='real-event info pw115-gemini-session';
        line.textContent=job.state==='running'?'Gemini arbetar med en riktig läs-/analysuppgift.':job.state==='review'?'Gemini har lämnat ett förslag för granskning.':job.state==='failed'?'Gemini kunde inte slutföra uppdraget. Se rapportpärmen.':'Gemini väntar på sitt API-anrop.';root.append(line);}
    }
  }
  // App's report drawer is kept unchanged. Add a visible review button inside
  // existing Gemini report pages so player doesn't need to navigate elsewhere.
  const oldDialog=$('#localStudioDialog');
  let injectedBusy=false;
  function enhanceBinderList(){
    if(!oldDialog?.open)return;
    for(const r of reportsCache.filter(x=>x.source==='gemini-api'&&x.review_decision)){
      const button=oldDialog.querySelector('button[data-report="'+r.id+'"]');
      if(!button)continue;
      const card=button.closest('.pw-report-letter'),badges=card?.querySelector('.pw-report-badges');
      const status=badges?.querySelector('[class*="pw-status-"]');
      if(status)status.textContent=decisionLabel(r);
    }
  }
  async function enhanceOldReport(){
    if(injectedBusy||!oldDialog?.open)return;
    const section=$('.pw-report-detail',oldDialog);
    if(!section||$('#pw115BinderAction',section))return;
    const ident=section.textContent.match(/Session:\s*([a-f0-9]{12})/);
    const project=currentProject();if(!ident||!validSlug(project))return;
    const r=reportsCache.find(x=>x.id===ident[1]&&x.source==='gemini-api');
    if(!r)return;
    injectedBusy=true;
    try{
      const button=document.createElement('button');button.id='pw115BinderAction';button.type='button';button.className='pw115-inbinder';
      button.textContent=r.review_decision?decisionLabel(r):'📝 Granska / godkänn förslag';
      button.onclick=()=>openReview(project,r.id);
      const footer=$('.local-actions',section);if(footer)footer.before(button);else section.append(button);
    }finally{injectedBusy=false}
  }
  if(oldDialog)new MutationObserver(()=>{void enhanceOldReport()}).observe(oldDialog,{subtree:true,childList:true});
  let watching=false;
  async function update(){
    if(watching)return;const project=currentProject();
    if(!validSlug(project)||!document.body.classList.contains('live-project'))return;
    watching=true;
    try{
      if(project!==lastProject){jobsCache=[];reportsCache=[];lastProject=project}
      const [jobs,reports]=await Promise.allSettled([
        api('/api/projects/'+project+'/jobs'),api('/api/projects/'+project+'/reports')]);
      if(project!==currentProject())return;
      if(jobs.status==='fulfilled')jobsCache=jobs.value.jobs||[];
      if(reports.status==='fulfilled')reportsCache=reports.value.reports||[];
      if(jobs.status==='fulfilled'||reports.status==='fulfilled'){
        logGemini();void enhanceOldReport();enhanceBinderList();
      }
    }catch(_){/* Behåll senaste verifierade status. */}
    finally{watching=false}
  }
  // The Codex viewer updates every three seconds. This lightweight observer
  // fixes only mislabeled Gemini sessions, without touching Codex history.
  const rail=$('.right-rail');
  if(rail)new MutationObserver(()=>correctLegacyProvider()).observe(rail,{subtree:true,childList:true});
  $('#projectSelect')?.addEventListener('change',()=>{jobsCache=[];reportsCache=[];lastProject='';update()});
  setTimeout(update,1100);setInterval(update,3200);
})();
