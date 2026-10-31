/* Pixel Works – one review inbox for genuine audio/image artifacts.
   The player decides YES/NO/MAYBE, with feedback routed through normal orders.
   GET/poll only reads state; preview loaded only when player presses preview.
*/
(() => {
  'use strict';
  if (window.__PW_MEDIA_REVIEW__) return;
  window.__PW_MEDIA_REVIEW__ = true;
  const API = '/api/pw-tools/review';
  const DEC = '/api/pw-tools/decisions';
  const esc = s => String(s ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const current = () => window.__PIXEL_WORKS_DEMO__?.model?.activeProjectId || document.querySelector('#projectSelect')?.value;
  const live = () => document.body.classList.contains('live-project');
  const api = (path,data) => window.pixelWorksApi(path,data);
  let latest = [], shownProject = '', busy=false, lastSig='', inFlight=false, seq=0;
  const previewUrls = new Map();
  // Preview is approved for player review only after the browser decodes it.
  // A filename, MIME header or successful download alone is not enough.
  const playable = new Set();
  const decoding = new Map();
  let policy = {retry_git_conflict_once:true,auto_retry_transient_once:false};
  // One shared dialog, regardless of which office surface opened it.
  // Context filters the same server-owned decisions; it never duplicates state.
  let category = 'all', focusEmployee = '', focusStation = '', focusLabel = '', searchText = '';
  const drafts = new Map();
  const seen = new Map();
  const css=document.createElement('style');
  css.textContent = `
   #pwReviewBell{position:fixed;z-index:77;right:20px;bottom:26px;border:3px solid #463448;background:#ffe19a;color:#242c40;padding:11px 15px;box-shadow:4px 4px 0 #182c3f;font:900 14px system-ui;cursor:pointer}
   #pwReviewBell[hidden]{display:none!important}#pwReviewBell:focus-visible{outline:3px solid #36a1bd}
   #pwReviewDlg{width:min(820px,calc(100vw - 24px));max-height:calc(100dvh - 24px);padding:0;border:6px ridge #a9754e;color:#24394a;background:#fff4dd;box-shadow:8px 8px 0 #142739;overflow:hidden}
   #pwReviewDlg::backdrop{background:#091a2cba}
   #pwReviewDlg .pwr-shell{display:flex;flex-direction:column;max-height:calc(100dvh - 38px);min-height:0}
   #pwReviewDlg .pwr-head{flex:0 0 auto;display:flex;gap:12px;align-items:start;justify-content:space-between;padding:15px 18px;background:#27445b;color:#fff5db}
   #pwReviewDlg .pwr-head h2{font-size:24px;margin:0 0 3px}#pwReviewDlg .pwr-head p{margin:0;font-size:13px;color:#d8e9ed}
   #pwReviewDlg .pwr-close{min-width:44px;min-height:44px;border:2px solid #a9b9c2;background:#e5f3fa;color:#233849;font-weight:900;cursor:pointer}
   #pwReviewDlg .pwr-body{padding:15px;overflow:auto;min-height:0;overscroll-behavior:contain}
   #pwReviewDlg .pwr-navigation{padding:10px 14px;background:#f7ebcf;border-bottom:2px solid #cfb88f;display:grid;gap:8px}
   #pwReviewDlg .pwr-tabs{display:flex;flex-wrap:wrap;gap:7px}
   #pwReviewDlg .pwr-tabs button{border:2px solid #638194;background:#fff;color:#274058;padding:8px 12px;min-height:42px;font:800 13px system-ui;border-radius:3px}
   #pwReviewDlg .pwr-tabs button[aria-pressed=true]{background:#2b5569;color:#fff;border-color:#24465a}
   #pwReviewDlg .pwr-navline{display:flex;align-items:center;gap:10px;justify-content:space-between;flex-wrap:wrap;font-size:12px;color:#3d5264}
   #pwReviewDlg .pwr-navline button{background:#fff6dd;color:#24445a;border:1px solid #b29672;padding:6px 10px;min-height:35px}
   #pwReviewDlg .pwr-search{width:100%;box-sizing:border-box;font:400 16px system-ui;border:2px solid #9daeb8;color:#17344b;background:#fff;padding:8px 10px;min-height:42px}
   #pwReviewDlg button:focus-visible{outline:3px solid #2876a7;outline-offset:2px}
   #pwReviewDlg .pwr-intro{padding:8px 12px;border-left:4px solid #4b827d;background:#e8f3e9;margin:0 0 12px;font-size:13px}
   #pwReviewDlg .pwr-offer{margin:0 0 15px;border:3px solid #ad875b;background:#fffefa;padding:13px;box-shadow:3px 3px 0 #a6a49e}
   #pwReviewDlg .pwr-top{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}
   #pwReviewDlg .pwr-offer h3{font-size:18px;margin:0 0 5px;overflow-wrap:anywhere}
   #pwReviewDlg .pwr-meta{font-size:12px;color:#496177;margin:0 0 9px}
   #pwReviewDlg .pwr-trace{font-size:12px;margin:8px 0;padding:7px;border:1px solid #b2c0c6;background:#f5f3eb}#pwReviewDlg .pwr-trace li{margin:5px 0;overflow-wrap:anywhere}
   #pwReviewDlg .pwr-desc{font-size:13px;line-height:1.55;margin:9px 0;white-space:pre-wrap}
   #pwReviewDlg .pwr-preview{margin:12px 0;border:2px dashed #8ca7ad;padding:10px;background:#ecf6f5}
   #pwReviewDlg .pwr-preview img{display:block;max-width:100%;max-height:340px;margin:auto;object-fit:contain;border:2px solid #aec4c6;background:#fff}
   #pwReviewDlg .pwr-preview audio{display:block;width:100%;min-height:44px}
   #pwReviewDlg .pwr-preview .pwr-play{display:inline-flex;align-items:center;justify-content:center;min-height:44px;border:2px solid #245360;background:#316f7c;color:#fff;font-weight:900;padding:8px 14px;margin:7px 0;cursor:pointer}
   #pwReviewDlg .pwr-preview .pwr-play:focus-visible{outline:3px solid #dc9a53}
   #pwReviewDlg button{cursor:pointer}#pwReviewDlg button:disabled{opacity:.5;cursor:not-allowed}
   #pwReviewDlg .pwr-load{min-height:42px;background:#316f7c;border:2px solid #245360;color:#fff;padding:8px 12px;font-weight:800}
   #pwReviewDlg .pwr-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
   #pwReviewDlg .pwr-actions button{border:2px solid #30465c;padding:10px 14px;min-height:44px;font:800 14px system-ui}
   #pwReviewDlg .pwr-yes{background:#92e1ae;color:#12352d}#pwReviewDlg .pwr-no{background:#f7c0ad;color:#552f2d}#pwReviewDlg .pwr-maybe{background:#ffe7a1;color:#523e1c}
   #pwReviewDlg textarea{display:block;box-sizing:border-box;width:100%;min-height:72px;max-height:180px;border:2px solid #688094;background:#fff;color:#26374a;font:400 16px/1.4 system-ui;padding:8px;resize:vertical}
   #pwReviewDlg label{display:block;font-size:13px;font-weight:750;margin:13px 0 5px}
   #pwReviewDlg .pwr-notice{color:#9a382b;font-size:13px;min-height:14px;margin:6px 0 0}
   #pwReviewDlg .pwr-badge{font-size:12px;font-weight:800;background:#dbe9f0;border:1px solid #8fb5bf;padding:3px 7px}
   #pwReviewDlg .pwr-foot{border-top:3px solid #d0af7b;flex:0 0 auto;padding:9px 15px;background:#fae9c9;display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap;font-size:12px}
   #pwReviewDlg .pwr-foot button{border:2px solid #4e5364;background:#fff6dd;color:#26394b;padding:8px 12px;font-weight:800;min-height:40px}
   #pwReviewDlg .pwr-help{border-left:7px solid #c9a45f;background:#fff7e5}
   #pwReviewDlg .pwr-help summary{cursor:pointer;font-size:13px}
   #pwReviewDlg .pwr-autofix{display:flex;align-items:flex-start;gap:9px;margin:12px 0 4px;padding:10px;border:1px solid #b3c5ab;background:#eef8ec;color:#244737;font-size:13px;line-height:1.45;cursor:pointer}
   #pwReviewDlg .pwr-autofix input{flex:0 0 21px;width:21px;height:21px;accent-color:#27856f;cursor:pointer}
   body.live-project .pw-help-indicator{display:none!important} /* Beslut visas i den gemensamma lappen, inte dubbelt över agenten */
   #pwReviewDlg .pwr-help-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
   #pwReviewDlg .pwr-help-actions button{min-height:44px;padding:10px 13px;border:2px solid #3a5261;font:800 13px system-ui;background:#eaf4f0;color:#193c42}
   #pwReviewDlg .pwr-help-actions button:last-child{background:#ffe5ad;color:#533e20}
   #pwDecisionSettings{width:min(540px,calc(100vw - 24px));max-height:90dvh;overflow:auto;border:5px ridge #ab7953;background:#fff4dc;color:#253749;padding:17px;box-shadow:5px 5px #223349}
   #pwDecisionSettings::backdrop{background:#0b192cb8}
   #pwDecisionSettings h2{font-size:22px;margin:0 0 8px}
   #pwDecisionSettings .pwd-row{display:block;padding:14px;margin:12px 0;background:#fffdf4;border:2px solid #c5a678;color:#29394b;font-size:14px;line-height:1.4}
   #pwDecisionSettings input{width:20px;height:20px;vertical-align:middle;margin-right:8px;accent-color:#247f78}
   #pwDecisionSettings small{display:block;margin-left:30px;color:#4d5f6a;line-height:1.45}
   #pwDecisionSettings button{min-height:44px;padding:9px 14px;background:#d3efdd;color:#173b36;border:2px solid #466759;font-weight:800;cursor:pointer}
   #pwDecisionSettings p{font-size:13px}
   @media(max-width:560px){#pwReviewDlg .pwr-head{padding:10px}#pwReviewDlg .pwr-head h2{font-size:18px}#pwReviewDlg .pwr-body{padding:10px}#pwReviewBell{right:10px;bottom:10px}#pwReviewDlg .pwr-actions button{flex:1 1 25%}}
  `;
  document.head.append(css);
  const bell = document.createElement('button');bell.id='pwReviewBell';bell.type='button';bell.hidden=true;bell.textContent='💌 Teamets beslut';
  document.body.append(bell);
  const dlg = document.createElement('dialog');dlg.id='pwReviewDlg';dlg.setAttribute('aria-label','Teamets beslut och granskningsärenden');
  dlg.innerHTML=`<div class="pwr-shell"><header class="pwr-head"><div><h2>💌 Teamet behöver ditt beslut</h2><p>Ljud, bilder och hjälpärenden – allt på samma lapp.</p></div><button class="pwr-close" type="button" data-pwr-close aria-label="Stäng">✕</button></header>
   <section class="pwr-navigation" aria-label="Hitta beslut">
     <div class="pwr-tabs" role="group" aria-label="Typ av beslut">
       <button type="button" data-pwr-category="all" aria-pressed="true">📬 Alla</button>
       <button type="button" data-pwr-category="audio" aria-pressed="false">🎧 Ljud</button>
       <button type="button" data-pwr-category="image" aria-pressed="false">🖼 Bilder</button>
       <button type="button" data-pwr-category="help" aria-pressed="false">🆘 Hjälp</button>
     </div><div class="pwr-navline"><span id="pwrContextLabel">Hela studion</span><button type="button" data-pwr-clear-context hidden>Visa hela studion</button></div>
     <input class="pwr-search" type="search" id="pwrSearch" aria-label="Sök bland teamets beslut" placeholder="Sök ljud, bilder, anställda eller uppdrag…" maxlength="120">
   </section>
   <div class="pwr-body"><p class="pwr-intro">🎮 Du driver studion. Lyssna och granska förslag, eller hjälp en anställd att komma vidare. Inga AI-anrop görs när lappen öppnas.</p><div class="pwr-offers"></div><p class="pwr-notice" id="pwReviewGlobal" role="status" aria-live="polite"></p></div>
   <footer class="pwr-foot"><span class="pwr-count" aria-live="polite">Läser förslag…</span><button type="button" data-pwr-settings>⚙️ Beslutsregler</button><button type="button" data-pwr-close>Till kontoret</button></footer></div>`;
  document.body.append(dlg);
  const offerHost=dlg.querySelector('.pwr-offers');
  const notice=(text)=>{dlg.querySelector('#pwReviewGlobal').textContent=text;};
  const unresolved=arr=>arr.filter(x=>x.status==='waiting'||x.status==='maybe');
  const normalized=s=>String(s||'').toLocaleLowerCase('sv-SE');
  function matches(item){
    if(category!=='all'&&item.kind!==category)return false;
    if(focusEmployee&&normalized(item.employee)!==normalized(focusEmployee))return false;
    if(focusStation&&item.station!==focusStation)return false;
    if(searchText&&!normalized([item.title,item.description,item.employee,item.reason,item.instruction,item.station].join(' ')).includes(normalized(searchText)))return false;
    return true;
  }
  function render(){
    const items=unresolved(latest).filter(matches);
    const keepText=new Map();
    offerHost.querySelectorAll('[data-pwr-id]').forEach(node=>{
      const field=node.querySelector('textarea');if(field)keepText.set(node.dataset.pwrId,field.value);
    });
    for(const [id,text] of keepText)drafts.set(id,text);
    dlg.querySelectorAll('[data-pwr-category]').forEach(btn=>{
      btn.setAttribute('aria-pressed',String(category===btn.dataset.pwrCategory));
      const n=unresolved(latest).filter(x=>btn.dataset.pwrCategory==='all'||x.kind===btn.dataset.pwrCategory).length;
      btn.title=n+' ärenden i den här kategorin';
    });
    dlg.querySelector('#pwrSearch').value=searchText;
    dlg.querySelector('#pwrContextLabel').textContent=(focusLabel||'Hela studion')+' · '+items.length+' ärenden i vyn';
    dlg.querySelector('[data-pwr-clear-context]').hidden=!focusEmployee&&!focusStation&&!focusLabel;
    const todo=latest.filter(x=>x.status==='waiting').length;
    const maybe=latest.filter(x=>x.status==='maybe').length;
    dlg.querySelector('.pwr-count').textContent=`${todo} att besluta om · ${maybe} sparade till senare`;
    bell.hidden=!live()||!items.length;
    bell.textContent=todo?`💌 ${todo} beslut väntar`:`🤔 ${maybe} till senare`;
    offerHost.innerHTML=items.length?items.map(x=>{
      if(x.kind==='help')return `<article class="pwr-offer pwr-help" data-pwr-id="${esc(x.id)}">
        <div class="pwr-top"><h3>🆘 ${esc(x.title)}</h3><span class="pwr-badge">${x.status==='maybe'?'⏳ Påminn senare':'📋 Behöver ditt svar'}</span></div>
        <p class="pwr-meta">${esc(x.employee||'Teamet')} · ${esc(x.station||'Arbetsstation')} · ${x.state==='review'?'Ändring väntar på säker integrering':'Arbetsförsök misslyckades'}</p>
        <p class="pwr-desc">${esc(x.reason||'En anställd behöver ditt besked.')}</p>
        ${x.instruction?`<details><summary>📄 Uppdraget</summary><p class="pwr-desc">${esc(x.instruction).slice(0,1800)}</p></details>`:''}
        ${x.summary?`<details><summary>👤 Vad agenten rapporterade</summary><p class="pwr-desc">${esc(x.summary).slice(0,2200)}</p></details>`:''}
        <label for="pwr-help-${esc(x.id).replace(/[^a-z0-9]/gi,'-')}">✍️ Din instruktion (om du vill ändra kurs)</label>
        <textarea id="pwr-help-${esc(x.id).replace(/[^a-z0-9]/gi,'-')}" maxlength="1800" placeholder="T.ex. Försök med den senaste koden, rör inte ljudsystemet…"></textarea>
        <label class="pwr-autofix"><input type="checkbox" data-pwr-autofix ${policy.auto_retry_transient_once?'checked':''}>
          <span>🤖 <strong>Låt Chefen försöka själv vid liknande tillfälliga teknikfel framöver</strong><br>
          <small>Högst ett extra försök per fel. Inga automatiska ljudval, bildgodkännanden eller osäkra Git-ändringar. Kan stängas av under ⚙ Beslutsregler.</small></span></label>
        <div class="pwr-help-actions"><button type="button" data-pwr-help="resolve">✅ Låt studion åtgärda</button><button type="button" data-pwr-help="instruct">✍️ Skicka min instruktion</button><button type="button" data-pwr-help="later">🤔 Kanske, senare</button></div>
        <small class="pwr-meta">Ett nytt försök använder befintlig arbetskö och mandat. Ingen manuell Git-merge eller hemlig kodändring här.</small>
        <p class="pwr-notice" role="status"></p>
      </article>`;
      const image=x.kind==='image';const path=x.source==='freesound'?'Freesound (metadata)':x.source==='agent-file'?'Agentens fil':'Saknar exporterad fil';
      const url=previewUrls.get(x.id);
      const media=url?image?`<img alt="Förhandsbild för ${esc(x.title)}" src="${esc(url)}">`:
        `<audio controls preload="metadata" src="${esc(url)}"></audio><button type="button" class="pwr-play" data-pwr-play>▶ Spela ljud</button>`:'';
      const disabled=!x.preview_available;
      return `<article class="pwr-offer" data-pwr-id="${esc(x.id)}"><div class="pwr-top"><h3>${image?'🖼️':'🎵'} ${esc(x.title)}</h3><span class="pwr-badge">${x.status==='maybe'?'🤔 Kanske':'⏳ Ditt beslut'}</span></div>
       <p class="pwr-meta">${esc(x.employee||'Teamet')} · ${esc(path)}${x.already_integrated?' · ⚠ Kod redan införd':''}${x.license?' · '+esc(x.license):''}</p>
       <p class="pwr-desc">${esc(x.description||'')}</p>
       ${Array.isArray(x.tool_events)&&x.tool_events.length?`<details class="pwr-trace"><summary>🧰 Visa verifierade verktygshändelser</summary><ul>${x.tool_events.map(t=>`<li>${esc(t.kind||'händelse')} · ${esc(t.message||'')}${t.query?' · '+esc(t.query):''}</li>`).join('')}</ul></details>`:''}
       <div class="pwr-preview" data-pwr-preview>${media||`<button class="pwr-load" data-pwr-load type="button" ${disabled?'disabled':''}>${disabled?'⚠ Förhandsfil saknas':image?'🖼️ Visa bilden':'▶ Provlyssna'}</button>`}
       ${disabled?'<p class="pwr-meta">Ingen fil finns att visa. Be agenten exportera en riktig förhandsfil.</p>':''}<p class="pwr-notice" role="status"></p></div>
       <label for="pwr-feedback-${esc(x.id).replace(/[^a-z0-9]/gi,'-')}">💬 Feedback till ${esc(x.employee||'teamet')} (frivilligt)</label>
       <textarea id="pwr-feedback-${esc(x.id).replace(/[^a-z0-9]/gi,'-')}" maxlength="700" placeholder="T.ex. Gör älgen mer cartoonig, eller hitta ett mjukare ljud…"></textarea>
       <div class="pwr-actions"><button type="button" class="pwr-yes" data-pwr-decision="yes" ${!playable.has(x.id)?'disabled title="Provlyssna eller visa först"':''}>✅ Ja, använd i spelet</button><button type="button" class="pwr-no" data-pwr-decision="no">❌ Nej${disabled?' / begär preview':''}</button><button type="button" class="pwr-maybe" data-pwr-decision="maybe">🤔 Kanske</button></div>
       ${x.already_integrated?'<small class="pwr-meta">Obs: agentens kod kan redan vara införd. Ja godkänner förslaget, men gör ingen automatisk Git-ändring.</small>':''}
       ${x.url?`<a href="${esc(x.url)}" rel="noopener noreferrer" target="_blank">Källa ↗</a>`:''}
       </article>`;
    }).join(''):(unresolved(latest).length
       ?'<p class="pwr-intro">Inget beslut matchar den här vyn. Välj en annan kategori eller <button type="button" data-pwr-show-all>visa alla beslut</button>.</p>'
       :'<p>🎉 Inga nya beslut väntar. Lappen öppnas igen när en anställd behöver hjälp eller levererar ett förslag.</p>');
    offerHost.querySelectorAll('[data-pwr-id]').forEach(node=>{
      const field=node.querySelector('textarea');if(field&&drafts.has(node.dataset.pwrId))field.value=drafts.get(node.dataset.pwrId);
    });
  }
  async function refresh(auto=false){
    if(inFlight||!live()||typeof window.pixelWorksApi!=='function'||busy)return;
    const project=current();if(!project)return;
    inFlight=true;const my=++seq;
    try{
      const [media,decision]=await Promise.all([
         api(API+'?project='+encodeURIComponent(project)),
         api(DEC+'?project='+encodeURIComponent(project))
      ]);
      if(my!==seq||project!==current())return;
      policy=decision.policy||policy;
      const incoming=[...(media.offers||[]),...(decision.cases||[]).map(x=>({
        ...x,kind:'help',source:'team-help',status:x.deferred?'maybe':'waiting',preview_available:false
      }))];
      const sig=JSON.stringify(incoming.map(x=>[x.id,x.status,x.followup_order]));
      if(project!==shownProject){shownProject=project;lastSig='';}
      latest=incoming;
      if(sig!==lastSig){
        window.dispatchEvent(new CustomEvent('pixelworks:decision-snapshot', {
          detail:{project,items:unresolved(incoming).map(x=>({id:x.id,kind:x.kind,station:x.station,employee:x.employee,status:x.status}))}
        }));
        lastSig=sig;
        // Never destroy playing <audio> nodes or lose typed feedback because a
        // different employee's status changed during the five-second poll.
        if(!dlg.open || !auto || !offerHost.querySelector('[data-pwr-id]'))render();
      }
      // A deferred case may become actionable again after its timer expires.
      // Clear the previous notification fingerprint when no pending cases remain.
      if(!latest.some(x=>x.status==='waiting'))seen.delete(project);
      const pendingIds=latest.filter(x=>x.status==='waiting').map(x=>x.id).sort().join('|');
      if(auto&&pendingIds&&seen.get(project)!==pendingIds&&!dlg.open&&!document.querySelector('dialog[open]')){
        seen.set(project,pendingIds);open();
      }
    }catch(err){if(dlg.open)notice('⚠ Kunde inte läsa förslagen: '+err.message);}
    finally{inFlight=false;}
  }
  function open(options={}){
    // Context is a view of the same decisions, not a new independent dialog.
    const allowed=new Set(['all','audio','image','help']);
    category=allowed.has(options.kind)?options.kind:'all';
    focusEmployee=String(options.employee||'').slice(0,90);
    focusStation=String(options.station||'').slice(0,35);
    focusLabel=String(options.label||'').slice(0,100);
    searchText='';
    if(dlg.open){render();return;}
    render();dlg.showModal();
  }
  function close(){dlg.close();seen.set(current(),latest.filter(x=>x.status==='waiting').map(x=>x.id).sort().join('|'));}
  dlg.addEventListener('close',()=>{for(const el of dlg.querySelectorAll('audio'))el.pause();});
  function mediaFail(card, id, message) {
    const timer=decoding.get(id);if(timer){clearTimeout(timer);decoding.delete(id);}
    playable.delete(id);
    const url=previewUrls.get(id);if(url){URL.revokeObjectURL(url);previewUrls.delete(id);}
    const host=card.querySelector('[data-pwr-preview]');if(!host)return;
    host.replaceChildren();
    const again=document.createElement('button');again.type='button';again.className='pwr-load';
    again.dataset.pwrLoad='';again.textContent='🔄 Hämta nytt förhandsprov';
    const status=document.createElement('p');status.className='pwr-notice';status.setAttribute('role','status');
    status.textContent='⚠ '+message;
    host.append(again,status);
    card.querySelector('[data-pwr-decision="yes"]')?.setAttribute('disabled','');
  }
  function mediaReady(card, id, sound) {
    const host=card.querySelector('[data-pwr-preview]');if(!host)return;
    playable.add(id);
    const yes=card.querySelector('[data-pwr-decision="yes"]');
    if(yes){yes.disabled=false;yes.removeAttribute('title');}
    const status=host.querySelector('.pwr-notice');
    if(status) status.textContent=sound?'✅ Ljudet kan spelas. Lyssna och välj Ja, Nej eller Kanske.':'✅ Bilden är klar för granskning.';
  }
  dlg.addEventListener('error', event=>{
    if(!event.target.matches?.('[data-pwr-preview] audio,[data-pwr-preview] img'))return;
    const card=event.target.closest('[data-pwr-id]');if(!card)return;
    const id=card.dataset.pwrId;
    mediaFail(card,id,'Firefox kunde inte avkoda förhandsfilen. Testa igen eller be agenten exportera en standard-WAV.');
  }, true);
  dlg.addEventListener('loadedmetadata', event=>{
    const sound=event.target;
    if(!sound.matches?.('[data-pwr-preview] audio'))return;
    const card=sound.closest('[data-pwr-id]');if(!card)return;
    const id=card.dataset.pwrId;
    if(!Number.isFinite(sound.duration) || sound.duration<=0.04){
      mediaFail(card,id,'Ljudet har ingen spelbar längd (0:00). Be om ett nytt förhandsprov.');return;
    }
    const timer=decoding.get(id);if(timer){clearTimeout(timer);decoding.delete(id);}
    mediaReady(card,id,true);
  },true);
  dlg.addEventListener('load', event=>{
    const picture=event.target;
    if(!picture.matches?.('[data-pwr-preview] img'))return;
    const card=picture.closest('[data-pwr-id]');if(card)mediaReady(card,card.dataset.pwrId,false);
  },true);
  bell.addEventListener('click',()=>open());
  dlg.querySelector('#pwrSearch').addEventListener('input',e=>{searchText=e.target.value.trim().slice(0,120);render();});
  dlg.addEventListener('input',e=>{
    if(e.target.matches?.('[data-pwr-id] textarea')){
      const card=e.target.closest('[data-pwr-id]');if(card)drafts.set(card.dataset.pwrId,e.target.value);
    }
  });
  dlg.addEventListener('click',e=>{
    const tab=e.target.closest('[data-pwr-category]');
    if(tab){category=tab.dataset.pwrCategory;render();return;}
    if(e.target.closest('[data-pwr-clear-context]')){focusEmployee='';focusStation='';focusLabel='';render();return;}
    if(e.target.closest('[data-pwr-show-all]')){focusEmployee='';focusStation='';focusLabel='';category='all';searchText='';render();}
  });
  dlg.addEventListener('change',async e=>{
    const cb=e.target.closest('[data-pwr-autofix]');
    if(!cb||busy)return;
    const desired=cb.checked;
    cb.disabled=true;
    try{
      const data=await api(DEC+'/settings',{
        approval:'SET_OWNER_DECISION_POLICY',
        retry_git_conflict_once:policy.retry_git_conflict_once,
        auto_retry_transient_once:desired
      });
      policy=data.policy;
      dlg.querySelectorAll('[data-pwr-autofix]').forEach(other=>{other.checked=!!policy.auto_retry_transient_once;});
      notice(desired?'✅ Chefen får prova igen vid liknande tillfälliga fel. Du kan ångra detta i Inställningar.':'✅ Framtida automatiska teknikförsök avstängda.');
    }catch(err){cb.checked=!!policy.auto_retry_transient_once;notice('⚠ Kunde inte spara: '+err.message);}
    finally{cb.disabled=false;}
  });
  dlg.addEventListener('click',async e=>{
    if(e.target.closest('[data-pwr-close]')){close();return;}
    if(e.target.closest('[data-pwr-settings]')){close();openSettings();return;}
    const card=e.target.closest('[data-pwr-id]');if(!card||busy)return;
    const id=card.dataset.pwrId;
    const helper=e.target.closest('[data-pwr-help]');
    if(helper){
      const action=helper.dataset.pwrHelp;
      const feedback=card.querySelector('textarea')?.value.trim()||'';
      if(action==='instruct'&&(feedback.length<5||feedback.length>1800)){
        card.querySelector('.pwr-notice').textContent='Beskriv vad du vill göra (5–1800 tecken).';return;
      }
      busy=true;card.querySelectorAll('button,textarea').forEach(el=>el.disabled=true);
      notice('Sparar ditt beslut…');
      try{
        let response;
        if(action==='later'){
          response=await api(DEC+'/later',{project:current(),case_id:id});
          notice('🤔 Ärendet ligger kvar i inkorgen. Ny påminnelse om 30 minuter.');
        }else{
          response=await api('/api/projects/'+encodeURIComponent(current())+'/help',{
            report_id:id.slice(5),action:action==='resolve'?'resolve':'instruct',
            instruction:action==='instruct'?feedback:''
          });
          notice(response?.status==='blocked'?'⚠ '+(response.reason||'Kunde inte starta ännu.'):
              '📋 Din instruktion ligger nu i den vanliga arbetskön, eller ärendet har lösts.');
        }
        lastSig='';
      }catch(err){notice('⚠ '+err.message)}
      finally{busy=false;card.querySelectorAll('button,textarea').forEach(el=>el.disabled=false);await refresh(false)}
      return;
    }
    if(e.target.closest('[data-pwr-play]')){
      const sound=card.querySelector('[data-pwr-preview] audio');
      if(!sound){card.querySelector('.pwr-notice').textContent='⚠ Ljudspelare saknas. Hämta förhandsprovet igen.';return;}
      // This play() runs DIRECTLY inside a click, not after an awaited fetch.
      // Firefox's user gesture can otherwise be lost, blocking playback.
      if(!sound.paused){sound.pause();e.target.closest('[data-pwr-play]').textContent='▶ Spela ljud';return;}
      try{
        const request=sound.play();
        if(request)request.then(()=>{
          const b=card.querySelector('[data-pwr-play]');if(b)b.textContent='⏸ Pausa';
        }).catch(err=>{
          const status=card.querySelector('[data-pwr-preview] .pwr-notice');
          if(status)status.textContent='⚠ Kunde inte starta ljud: '+(err?.name==='NotAllowedError'?'Firefox blockerade uppspelning. Klicka på ljudspelarens ▶.':err.message);
        });
      }catch(err){card.querySelector('[data-pwr-preview] .pwr-notice').textContent='⚠ '+err.message;}
      return;
    }
    if(e.target.closest('[data-pwr-load]')){
      const btn=e.target.closest('[data-pwr-load]');btn.disabled=true;btn.textContent='Hämtar och kontrollerar ljud…';
      try{
        const project=current();
        const result=await api(API+'/preview?project='+encodeURIComponent(project)+'&id='+encodeURIComponent(id));
        if(project!==current()||!card.isConnected)throw Error('Projektet har ändrats. Öppna lappen igen.');
        if(!result.base64||!/^image\/(png|jpeg|webp|gif)$|^audio\/(mpeg|wav|ogg)$/.test(result.mime))throw Error('Okänt medieformat');
        const raw=atob(result.base64);const bytes=new Uint8Array(raw.length);
        for(let i=0;i<raw.length;i++)bytes[i]=raw.charCodeAt(i);
        const old=previewUrls.get(id);if(old)URL.revokeObjectURL(old);
        const url=URL.createObjectURL(new Blob([bytes],{type:result.mime}));previewUrls.set(id,url);
        const host=card.querySelector('[data-pwr-preview]');
        host.replaceChildren();
        if(result.mime.startsWith('image/')){
          const img=document.createElement('img');img.src=url;img.alt='Förhandsbild: '+card.querySelector('h3').textContent;
          host.append(img);
        }else{
          const sound=document.createElement('audio');sound.controls=true;sound.preload='auto';sound.src=url;
          sound.setAttribute('aria-label','Förhandsljud');
          const play=document.createElement('button');play.type='button';play.className='pwr-play';play.dataset.pwrPlay='';
          play.textContent='▶ Spela ljud';
          host.append(sound,play);
          sound.addEventListener('ended',()=>{play.textContent='▶ Spela igen';});
          const timer=setTimeout(()=>{
            decoding.delete(id);
            if(!playable.has(id)&&card.isConnected)mediaFail(card,id,'Ljudfilen svarade inte i Firefox. Prova ett annat ljud eller be om en WAV-export.');
          },12000);
          decoding.set(id,timer);
          sound.load();
        }
        const status=document.createElement('p');status.className='pwr-notice';status.setAttribute('role','status');
        const sec=Number(result.seconds)||0;
        status.textContent=result.mime.startsWith('audio/')
          ? `Kontrollerar uppspelning…${sec>0?' · '+sec.toFixed(1)+' s':''}${result.excerpt?' · 20 sekunders utdrag':''}. Klicka ▶ Spela ljud när spelaren är klar.`
          : 'Läser förhandsbild…';
        host.append(status);
        // Unlike the old code, do not mark success merely because bytes arrived.
      }catch(err){
        btn.textContent='🔄 Försök igen';btn.disabled=false;
        card.querySelector('[data-pwr-preview] .pwr-notice').textContent='⚠ Kunde inte förhandsvisa: '+err.message;
      }
      return;
    }
    const action=e.target.closest('[data-pwr-decision]');if(!action)return;
    const decision=action.dataset.pwrDecision;
    const feedback=card.querySelector('textarea')?.value.trim()||'';
    if(decision==='no'&&feedback&&feedback.length<10){card.querySelector('.pwr-notice').textContent='Beskriv ändringen med minst 10 tecken, eller lämna fältet tomt för att bara avvisa.';return;}
    busy=true;card.querySelectorAll('button,textarea').forEach(el=>el.disabled=true);
    notice('Sparar ditt beslut…');
    try{
      const result=await api(API,{project:current(),offer_id:id,decision,feedback});
      notice(result.followup_order?'📋 Feedbacken ligger i den vanliga arbetskön.':'✅ Ditt val är sparat.');
      lastSig='';await refresh(false);
    }catch(err){notice('⚠ '+err.message);}
    finally{busy=false;card.querySelectorAll('button,textarea').forEach(el=>el.disabled=false);await refresh(false);}
  });

  // Shared decision policy: same Settings & diagnostics surface as Gemini.
  // Safe defaults: one passive retry on a *real Git conflict*, but NO automatic
  // yes/no on media. Transient retry requires an explicit opt-in.
  const settingDlg=document.createElement('dialog');settingDlg.id='pwDecisionSettings';
  settingDlg.setAttribute('aria-label','Regler för studions beslut');
  settingDlg.innerHTML=`<h2>💌 Teamets beslutsregler</h2>
    <p>Alla riktiga beslut samlas i beslutsbrevet. Du kan ta tillbaka automatiska behörigheter här när som helst.</p>
    <label class="pwd-row"><input type="checkbox" id="pwdRetryGit"> 🔁 Försök om en gång vid Git-konflikt
      <small>Om två agentjobb ändrar samma kod köar Chefen EN ny arbetsorder på senaste spelversionen. Ingen force merge eller extra Git-push.</small></label>
    <label class="pwd-row"><input type="checkbox" id="pwdAutoSimple"> 🤖 Låt Chefen hantera enkla tillfälliga fel själv
      <small>Frivilligt. Högst ett nytt försök vid tydliga timeout-/resursfel. Beslut om ljud, bilder, radering, publicering och betalningar kräver alltid ditt svar.</small></label>
    <p id="pwdStatus" role="status" aria-live="polite"></p>
    <div style="display:flex;gap:10px;flex-wrap:wrap"><button id="pwdSave" type="button">💾 Spara beslutspolicy</button><button id="pwdClose" type="button">Stäng</button></div>`;
  document.body.append(settingDlg);
  settingDlg.querySelector('#pwdClose').onclick=()=>settingDlg.close();
  async function openSettings(){
    if(dlg.open)close();
    try{const data=await api(DEC+'/settings');policy=data.policy||policy;
      settingDlg.querySelector('#pwdRetryGit').checked=!!policy.retry_git_conflict_once;
      settingDlg.querySelector('#pwdAutoSimple').checked=!!policy.auto_retry_transient_once;
      settingDlg.querySelector('#pwdStatus').textContent='Gäller alla projekt i denna Pixel Works-installation.';
    }catch(err){settingDlg.querySelector('#pwdStatus').textContent='⚠ '+err.message;}
    if(!settingDlg.open)settingDlg.showModal();
  }
  settingDlg.querySelector('#pwdSave').onclick=async()=>{
    const button=settingDlg.querySelector('#pwdSave');button.disabled=true;
    try{
      const data=await api(DEC+'/settings',{
        approval:'SET_OWNER_DECISION_POLICY',
        retry_git_conflict_once:settingDlg.querySelector('#pwdRetryGit').checked,
        auto_retry_transient_once:settingDlg.querySelector('#pwdAutoSimple').checked
      });
      policy=data.policy;
      settingDlg.querySelector('#pwdStatus').textContent='✅ Sparat. Du kan ändra eller stänga av båda valen här när som helst.';
    }catch(err){settingDlg.querySelector('#pwdStatus').textContent='⚠ '+err.message}
    finally{button.disabled=false}
  };
  const dock=document.querySelector('#dockDialogContent');
  function injectSettings(){
    if(!dock||!dock.textContent.includes('Inställningar & diagnostik')||dock.querySelector('#pwDecisionSettingsRow'))return;
    const row=document.createElement('div');row.id='pwDecisionSettingsRow';row.className='dock-row';
    row.style.cssText='display:flex;align-items:center;justify-content:space-between;gap:9px;flex-wrap:wrap;padding:10px 4px;border-bottom:1px solid #58708b;color:#203e55';
    const title=document.createElement('div');title.innerHTML='<strong>💌 Teamets beslut</strong><br><small>Beslutsbrev · Git-omförsök · egna beslut</small>';
    const button=document.createElement('button');button.type='button';button.textContent='⚙️ Hantera beslut';
    button.addEventListener('click',()=>{document.querySelector('#dockDialog')?.close();openSettings();});
    row.append(title,button);
    const loc=dock.querySelector('#pwToolsFreesound')||dock.querySelector('[data-open-local]');
    if(loc)loc.before(row);else dock.append(row);
  }
  if(dock){new MutationObserver(injectSettings).observe(dock,{childList:true,subtree:false});injectSettings();}

  window.addEventListener('pixelworks:project-changed',()=>{seq++;lastSig='';shownProject='';for(const url of previewUrls.values())URL.revokeObjectURL(url);previewUrls.clear();playable.clear();drafts.clear();for(const t of decoding.values())clearTimeout(t);decoding.clear();latest=[];if(dlg.open)dlg.close();render();refresh(false)});
  window.pixelWorksOpenDecisionContext=(options={})=>{
    if(!live()||typeof window.pixelWorksApi!=='function')return false;
    open(options);
    // Show the current snapshot immediately. Fresh data comes asynchronously;
    // if another dialog is open behind this one, preserve its unsent draft.
    refresh(false);
    return true;
  };
  window.pixelWorksOpenMediaReview=()=>window.pixelWorksOpenDecisionContext();
  setInterval(()=>refresh(true),5000);
  setTimeout(()=>refresh(true),1800);
})();
