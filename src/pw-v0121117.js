/* Pixel Works 0.12.11.17 – stable project ownership and legible studio controls.
 * Frontend-only; real work still happens exclusively through authenticated server routes.
 * No AI requests and no changes to existing game folders at load time. */
(() => {
  'use strict';
  const $=(q,r=document)=>r.querySelector(q);
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const validSlug=s=>/^[a-z0-9][a-z0-9-]{1,49}$/.test(s||'');
  const active=()=>window.__PIXEL_WORKS_DEMO__?.model?.activeProjectId||$('#projectSelect')?.value||null;
  const model=()=>window.__PIXEL_WORKS_DEMO__?.model;
  const nameFor=(id=active())=>model()?.projects?.find(p=>p.id===id)?.title||id||'Inget spel valt';
  // Newer browser extensions call this shared API. Protect against a dialog
  // that was opened for project A submitting a stale POST after selection B.
  // Core's own project checks remain in place on the server.
  if(typeof window.pixelWorksApi==='function'&&!window.pixelWorksApi.__pw17){
    const previousApi=window.pixelWorksApi;
    const guarded=async(path,payload)=>{
      if(payload){
        const pathProject=String(path||'').match(/^\/api\/projects\/([a-z0-9-]{2,50})\//)?.[1];
        const requested=pathProject||payload.project;
        if(requested&&validSlug(requested)&&validSlug(active())&&requested!==active())
          throw Error('Du har bytt spel. Åtgärden avbröts så att fel projekt inte ändras.');
      }
      return previousApi(path,payload);
    };
    guarded.__pw17=true;window.pixelWorksApi=guarded;
  }
  const settings={
    lead:['Arbetsledning','Här planerar Chefen nya uppdrag, fördelar arbete och följer upp beslut.'],
    code:['Programmering','Här skriver och testar programmerarna spelets kod.'],
    research:['Forskning','Här undersöker medarbetarna alternativ och tar fram underlag.'],
    qa:['Testning','Här testar medarbetarna spelet och rapporterar fel.'],
    docs:['Dokumentation','Här utvecklas Game Bible och spelets dokumentation.'],
    meeting:['Mötesrum','Här planerar och diskuterar teamet spelidéer och uppdrag.'],
    art:['Grafikstudio','Här utvecklas spelets utseende och grafik.'],
    music:['Musikstudio','Här planeras och skapas ljud och musik.'],
    voice:['Röststudio','Här utvecklas röster, dialoger och ljud.'],
    cafe:['Fikarum','Här återhämtar sig lediga medarbetare mellan uppdragen.']
  };
  const css=document.createElement('style');css.textContent=`
    #pw17-projectbar{padding:6px 9px;background:#163b4d;border:2px solid #6caba3;color:#f1e6b8;font-size:12px;line-height:1.45}
    #pw17-projectbar strong{color:white}
    #pw17-access,#pw17-decisions{margin:6px 0;background:#193748;color:#f4edcf;border:2px solid #63868d;padding:9px;font-size:12px;line-height:1.5}
    #pw17-access h3,#pw17-decisions h3{margin:0 0 5px;color:#f5d17c;font-size:13px}
    #pw17-access button,#pw17-decisions button,#pw17-welcome button,#pw17-consent button{background:#efc879;color:#273246;border:2px solid #816039;padding:7px 9px;margin:4px 5px 4px 0;cursor:pointer;font-weight:700;font:inherit}
    #pw17-access button:disabled,#pw17-decisions button:disabled{opacity:.5}
    #pw17-access [role=status],#pw17-decisions [role=status]{white-space:pre-wrap;color:#e6e2b8;font-size:11px}
    .pw17-stale-access{display:none!important}
    .pw17-context{padding:5px 9px;margin:4px 0;background:#173a4d;color:#fff3ca;border:1px solid #94bcbd;font:700 12px/1.4 system-ui,sans-serif}
    #stationLayer .station{overflow:visible!important}
    #stationLayer .station-label{font-size:10px!important;line-height:1.15!important;white-space:normal!important;max-width:122px!important;min-width:43px;overflow-wrap:normal;text-align:center}
    #stationLayer .station .pw17-tooltip{display:none;position:absolute;left:50%;bottom:105%;transform:translateX(-50%);width:204px;max-width:230px;z-index:250;box-sizing:border-box;pointer-events:none;background:#102b3c;color:#f7f0dc;border:2px solid #e8c87d;box-shadow:3px 4px #07131e;padding:8px;font:12px/1.4 system-ui,sans-serif;text-align:left;white-space:normal;overflow-wrap:break-word}
    #stationLayer .station .pw17-tooltip b{color:#ffd67b;display:block;margin-bottom:5px}
    #stationLayer .station:hover .pw17-tooltip,#stationLayer .station:focus .pw17-tooltip,#stationLayer .station:focus-within .pw17-tooltip{display:block}
    #stationLayer .station[data-id='qa'] .pw17-tooltip,#stationLayer .station[data-id='music'] .pw17-tooltip{left:auto;right:0;transform:none}
    #stationLayer .station[data-id='art'] .pw17-tooltip{left:0;transform:none}
    #pw17-consent,#pw17-welcome{width:min(610px,94vw);max-height:85vh;overflow:auto;background:#203248;color:#f7ead2;border:6px ridge #a57750;box-sizing:border-box;padding:20px;font:14px/1.5 system-ui,sans-serif}
    #pw17-consent::backdrop,#pw17-welcome::backdrop{background:#070f1cce}
    #pw17-consent h2,#pw17-welcome h2{color:#ffdb93;margin:0 0 12px}
    #pw17-consent .pw17-note{font-size:12px;color:#cbe6de}
    #pw17-welcome .pw17-choices{display:flex;gap:8px;flex-wrap:wrap;margin-top:13px}
    #pw17-welcome .pw17-choices button{min-height:41px}
    @media(max-width:620px){#stationLayer .station-label{font-size:9px!important;max-width:85px!important}#stationLayer .station .pw17-tooltip{width:175px}}
  `;document.head.append(css);

  async function api(path,payload){
    if(typeof window.pixelWorksApi==='function')return window.pixelWorksApi(path,payload);
    throw Error('Den lokala studion är ännu inte ansluten.');
  }
  function notify(message){
    const ui=window.__PIXEL_WORKS_DEMO__?.ui;
    if(typeof ui?.toast==='function')ui.toast(message);
    else console.info('[Pixel Works]',message);
  }
  // These two dialogs are explicit user actions. Creation is already confirmed
  // by the Create button and is confined to the server's verified project root.
  // No repeat native browser confirm() on each project.
  function slugify(text){return text.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,48)}
  let pendingWelcome=null;
  function hookProjectCreation(){
    const original=window.pixelWorksCreateLive;
    if(typeof original!=='function'||original.__pw17)return;
    const create=async d=>{
      const name=String(d?.name||'').trim(),idea=String(d?.description||'').trim(),slug=slugify(name);
      if(!name||slug.length<2||!idea)throw Error('Ange spelnamn och en spelidé.');
      if(idea.length>3000)throw Error('Beskrivningen får ha högst 3 000 tecken.');
      // Creation does not grant write access to the AI team. The one-time
      // studio consent below controls any subsequent autonomous file changes.
      const saved=await api('/api/projects',{slug,name,idea,genre:d.genre||'Spel',
        platform:d.platform||'Webbläsare',priority:d.priority||'Spelkänsla',
        creator:d.creator||{},weights:d.weights||{},areas:d.areas||[],approval:'CREATE_PROJECT_ON_DISK'});
      if(!saved.verified)throw Error('Det nya spelprojektet kunde inte verifieras.');
      const checked=await api('/api/projects/'+encodeURIComponent(slug));
      if(!checked.verified||checked.project?.id!==slug||checked.path!==saved.path)
        throw Error('Projektet skapades men kontrolläsningen misslyckades. Kontrollera projektlistan.');
      pendingWelcome={id:slug,name};
      return checked;
    };
    create.__pw17=true;window.pixelWorksCreateLive=create;
    const originalHire=window.pixelWorksHireLive;
    if(typeof originalHire==='function'&&!originalHire.__pw17){
      const hire=async slug=>{
        if(pendingWelcome?.id===slug){const details=pendingWelcome;pendingWelcome=null;
          setTimeout(()=>welcome(details),160);return;}
        return originalHire(slug);
      };
      hire.__pw17=true;window.pixelWorksHireLive=hire;
    }
  }
  let welcomeDialog;
  function welcome(details){
    if(!details||!validSlug(details.id))return;
    if(active()!==details.id)return; // Another project was explicitly selected.
    if(!welcomeDialog){welcomeDialog=document.createElement('dialog');welcomeDialog.id='pw17-welcome';document.body.append(welcomeDialog);}
    welcomeDialog.innerHTML=`<h2>🎉 Ditt nya spel är skapat!</h2><p><strong>${esc(details.name)}</strong> är sparat som eget projekt. Du arbetar nu i just det spelet.</p>
      <p>Du kan börja med arbetsledaren, välja personal eller gå direkt till kontoret.</p>
      <div class="pw17-choices"><button type="button" data-next="office">🏢 Gå till kontoret</button>
      <button type="button" data-next="lead">👔 Ge chefen första uppdraget</button>
      <button type="button" data-next="staff">👥 Visa personal</button></div>`;
    welcomeDialog.querySelectorAll('button').forEach(btn=>btn.onclick=()=>{
      const action=btn.dataset.next;welcomeDialog.close();
      if(active()!==details.id){notify('Byt tillbaka till '+details.name+' för att fortsätta.');return;}
      if(action==='lead')document.querySelector('#stationLayer .station[data-id="lead"]')?.click();
      if(action==='staff')window.pixelWorksHireLive?.(details.id);
    });
    if(!welcomeDialog.open)welcomeDialog.showModal();
  }
  window.addEventListener('pixelworks:project-created',event=>setTimeout(()=>welcome(event.detail),180));
  const quick=$('#pw11Quick');
  if(quick){
    const more=$('#pw11Advanced');if(more)more.textContent='🎲 Bygg med spelguiden';
    const make=$('#pw11Create');if(make)make.textContent='✍️ Skapa från min beskrivning';
  }

  // Explicit project context on ALL normal work and decision screens.
  let lastProject=active();
  const dialogIds=['localStudioDialog','dockDialog','gameDialog','pw115Review'];
  function contextForDialog(dialog){
    if(!dialog?.open||dialog.id==='pw17-welcome'||dialog.id==='pw17-consent')return;
    if(dialog.id==='gameDialog'&&dialog.classList.contains('creator-dialog'))return;
    const id=active();if(!validSlug(id))return;
    let badge=$('.pw17-context',dialog);
    if(!badge){badge=document.createElement('div');badge.className='pw17-context';
      // Outside shell body: does not break local studio's screen layout.
      if(dialog.id==='localStudioDialog'){
        const label=$('.local-shell-info',dialog);
        if(label)label.after(badge);else dialog.prepend(badge);
      }else dialog.prepend(badge);
    }
    const text='📁 AKTIVT SPEL: '+nameFor(id);
    if(badge.textContent!==text)badge.textContent=text;
    dialog.dataset.pw17Project=id;
  }
  function updateContexts(){dialogIds.forEach(id=>contextForDialog(document.getElementById(id)));normalizePlainForms();}
  // Hide technical provider labels in ordinary staffing forms. The underlying
  // adapter choice remains fully visible/editable in the employee profile.
  function normalizePlainForms(){
    const box=$('#localStudioDialog');if(!box?.open)return;
    const label=box.querySelector('label[for="hireLiveName"]');
    if(label&&label.textContent.includes('Codex'))label.textContent='Namn på ny medarbetare';
    const input=box.querySelector('#hireLiveName');
    if(input){input.placeholder='Till exempel Alex';
      if(/^Codex\s+\d+$/.test(input.value))input.value='';}
    const hire=box.querySelector('#hireLiveYes');
    if(hire&&hire.textContent.includes('Anställ agent'))hire.textContent='➕ Anställ medarbetare';
    for(const button of box.querySelectorAll('button')){
      const text=(button.textContent||'').trim();
      if(text==='Be Codex planera')button.textContent='👔 Be arbetsledaren planera';
    }
  }

  const contextObserver=new MutationObserver(()=>{
    if(contextPending)return;contextPending=true;
    queueMicrotask(()=>{contextPending=false;updateContexts();});
  });
  let contextPending=false;
  for(const id of dialogIds){const el=document.getElementById(id);if(el)
    contextObserver.observe(el,{attributes:true,attributeFilter:['open'],childList:true,subtree:false});}
  function projectChanged(){
    const id=active();if(id===lastProject)return;
    const from=lastProject;lastProject=id;
    for(const dialogId of dialogIds){const dialog=document.getElementById(dialogId);
      if(dialog?.open&&dialog.dataset.pw17Project&&dialog.dataset.pw17Project!==id&&
         !(dialog.id==='gameDialog'&&dialog.classList.contains('creator-dialog'))){
        dialog.close();notify('Du bytte spel. Det gamla projektets dialog stängdes för säkerhets skull.');
      }
    }
    if(welcomeDialog?.open)welcomeDialog.close();
    refreshProjectInfo();
    if(from&&id)console.info('[Pixel Works] Aktivt projekt:',from,'→',id);
  }
  window.addEventListener('pixelworks:project-changed',projectChanged);
  $('#projectSelect')?.addEventListener('change',()=>setTimeout(projectChanged,0));

  let stationState={};
  function stationText(station){
    const meta=settings[station.dataset.id];if(!meta)return;
    const id=station.dataset.id;
    const state=stationState[id]||{};
    const name=meta[0];
    const label=station.querySelector('.station-label');if(label&&label.textContent!==name)label.textContent=name;
    const description=meta[1];
    const people=(state.people||[]).map(p=>p.name+(p.active?' – arbetar':' – på plats')).join(', ');
    const count=state.reviews||0,waiting=state.waiting||0;
    const stat=(people?'Personal: '+people+'. ':'')+
      (count?count+' granskningsärende'+(count===1?'':'n')+'. ':'')+
      (waiting?waiting+' väntande arbetsorder. ':'');
    const hint=name+'. '+description+' '+stat+'Klicka för att öppna bordet.';
    station.setAttribute('title',hint);
    station.setAttribute('aria-label',hint);
    let tip=station.querySelector('.pw17-tooltip');
    if(!tip){tip=document.createElement('div');tip.className='pw17-tooltip';
      tip.setAttribute('aria-hidden','true');station.append(tip);}
    const contents='<b>'+esc(name)+'</b>'+esc(description)+'<br><br>'+
       esc(stat||'Inga kända ärenden vid bordet. ')+'<br><strong>Klicka för att öppna.</strong>';
    if(tip.innerHTML!==contents)tip.innerHTML=contents;
  }
  function renderStations(){document.querySelectorAll('#stationLayer .station').forEach(stationText);}
  const stationLayer=$('#stationLayer');if(stationLayer)
    new MutationObserver(renderStations).observe(stationLayer,{childList:true,subtree:false});
  renderStations();

  const rail=$('.right-rail');
  let projectbar,accessPanel,decisionPanel,access=false,accessLoaded=false,refreshBusy=false;
  function createRail(){
    if(!rail)return;
    projectbar=$('#pw17-projectbar')||document.createElement('div');
    projectbar.id='pw17-projectbar';
    accessPanel=$('#pw17-access')||document.createElement('section');
    accessPanel.id='pw17-access';
    decisionPanel=$('#pw17-decisions')||document.createElement('section');
    decisionPanel.id='pw17-decisions';
    rail.prepend(decisionPanel);rail.prepend(accessPanel);rail.prepend(projectbar);
  }
  createRail();
  function removeStaleAccess(){
    if(!rail)return;
    for(const el of rail.querySelectorAll('button,div,section,p,span')){
      if(el.closest('#pw17-access, #pw17-decisions, #pw17-projectbar'))continue;
      if(el.children.length>2)continue;
      const title=(el.textContent||'').trim();
      if(title==='Studioåtkomst behövs' || title==='🔒 Studioåtkomst behövs')
        el.classList.add('pw17-stale-access');
    }
  }
  function refreshProjectInfo(){
    if(!rail)return;
    if(!projectbar)createRail();
    const slug=active();
    projectbar.innerHTML='🎮 AKTIVT PROJEKT<br><strong>'+esc(nameFor(slug))+'</strong>';
    if(decisionPanel){decisionPanel.innerHTML='<h3>📋 Arbete och beslut</h3><p>Hämtar aktuell arbetskö…</p>';}
    stationState={};renderStations();
    accessLoaded=false;
    void refreshAll();
  }
  const consent=document.createElement('dialog');consent.id='pw17-consent';
  consent.innerHTML=`<h2>🔓 Tillåt studioarbete?</h2>
    <p>Får dina anställda använda sina anslutna arbetsverktyg och ändra filer <strong>i Pixel Works egna projektmappar</strong>?</p>
    <p>Detta är ett beslut för hela studion. Du behöver inte godkänna varje projekt igen.</p>
    <p class="pw17-note">Ingen GitHub-push, ingen extern publicering och ingen automatisk uppgradering till betalda AI-modeller. Tillståndet kan stängas av i Inställningar.</p>
    <p id="pw17-consent-error" role="alert"></p>
    <div><button type="button" id="pw17-consent-yes">✅ Ja, fråga inte igen</button>
      <button type="button" id="pw17-consent-no">Inte nu</button></div>`;
  document.body.append(consent);
  $('#pw17-consent-no').onclick=()=>consent.close();
  let consentSending=false;
  $('#pw17-consent-yes').onclick=async()=>{
    if(consentSending)return;consentSending=true;
    const yes=$('#pw17-consent-yes');yes.disabled=true;
    try{
      const response=await api('/api/pw-v01210/studio-access',{enabled:true,approval:'ALLOW_PIXELWORKS_STUDIO_WORK'});
      if(!response.enabled)throw Error('Servern bekräftade inte tillståndet.');
      access=true;accessLoaded=true;consent.close();
      window.dispatchEvent(new Event('pixelworks:studio-access-changed'));
      notify('Studioarbete aktiverat för Pixel Works projektmappar.');
      await refreshAll();
    }catch(error){$('#pw17-consent-error').textContent='⚠ '+error.message;}
    finally{yes.disabled=false;consentSending=false;}
  };
  function paintAccess(){
    if(!accessPanel)return;
    if(!accessLoaded){accessPanel.innerHTML='<h3>🔐 Studioåtkomst</h3><p>Kontrollerar inställningen…</p>';return;}
    if(access){
      accessPanel.innerHTML='<span>✅ Studioarbete tillåtet</span>';
    }else{
      accessPanel.innerHTML='<h3>🔒 Studioarbete är inte aktiverat</h3><p>Arbetsledaren kan planera, men anställda behöver ett engångstillstånd för att börja arbeta i projektmapparna.</p><button type="button" id="pw17-activate">🔓 Aktivera studioarbete</button>';
      $('#pw17-activate',accessPanel).onclick=()=>{
        const native=$('#pw11StudioConsent');
        if(native){if(!native.open)native.showModal();}
        else if(!consent.open)consent.showModal();
      };
    }
    removeStaleAccess();
  }
  const isActionable=r=>r&&!r.archived&&!r.review_decision&&!r.resolved_by&&r.state==='review';
  function paintDecisions(slug,orders,reports){
    if(!decisionPanel)return;
    const reviews=reports.filter(isActionable);
    const reviewOrderIds=new Set(reviews.map(r=>r.order_id).filter(Boolean));
    const orphaned=orders.filter(o=>o.status==='review'&&!reviewOrderIds.has(o.id));
    const waiting=orders.filter(o=>o.status==='waiting');
    decisionPanel.replaceChildren();
    const header=document.createElement('h3');header.textContent='📋 Arbete och beslut';decisionPanel.append(header);
    const text=document.createElement('div');text.textContent=reviews.length+orphaned.length+' att granska · '+waiting.length+' väntar på medarbetare';decisionPanel.append(text);
    const message=document.createElement('p');message.setAttribute('role','status');decisionPanel.append(message);
    if(!reviews.length&&!orphaned.length&&!waiting.length){message.textContent='☕ Inget behöver beslutas just nu.';return;}
    const addButton=(caption,handler)=>{const button=document.createElement('button');button.type='button';button.textContent=caption;
      button.addEventListener('click',()=>{
        if(active()!==slug){message.textContent='⚠ Du har bytt spel. Öppna ärendena i rätt projekt.';return;}
        try{handler(button,message);}catch(error){message.textContent='⚠ '+error.message;}
      });decisionPanel.append(button);return button;};
    for(const r of reviews.slice(0,3)){
      const person=r.agent_name||'Medarbetaren';
      addButton('🟡 Granska '+person+'s förslag',()=>{
        if(r.source==='gemini-api'&&window.pixelWorksGeminiReview)
          return window.pixelWorksGeminiReview(slug,r.id);
        $('#officeDesk')?.click();
      });
    }
    for(const o of orphaned.slice(0,2)){
      const where=settings[o.station]?.[0]||'arbetsbordet';
      addButton('⚠ Granska ärende vid '+where,()=>{
        const station=document.querySelector('#stationLayer .station[data-id="'+o.station+'"]');
        if(station)station.click();else $('#officeDesk')?.click();
      });
    }
    if(waiting.length){
      const o=waiting[0],where=settings[o.station]?.[0]||'arbetsbordet';
      addButton('📋 Arbetskö: '+where+' ('+waiting.length+')',()=>{
        const station=document.querySelector('#stationLayer .station[data-id="'+o.station+'"]');
        if(station)station.click();else notify('Öppna arbetskön via Uppdrag.');
      });
      // An explicit player click starts the EXISTING first waiting order at
      // this station through the protected dispatcher. No duplicate order.
      addButton('▶ Försök starta uppdrag vid '+where,async(button,status)=>{
        if(!access){status.textContent='Aktivera studioarbete ovan innan medarbetarna kan börja.';return;}
        button.disabled=true;status.textContent='Chefen kontrollerar vem som kan börja…';
        try{
          const result=await api(o.station==='lead'?'/api/pw-v0132/start-lead':'/api/pw-v0121110/dispatch',{project:slug,station:o.station,...(o.station==='lead'?{order_id:o.id}:{})});
          if(active()!==slug)return;
          status.textContent=result.message||({started:'Arbetet startade.',blocked:'Arbetet kan inte starta just nu.',
            idle:'Inga väntande jobb vid bordet.'})[result.state]||'Kontrollen är klar.';
          if(result.state==='started')setTimeout(refreshAll,400);
        }catch(error){status.textContent='⚠ Kunde inte starta: '+error.message;}
        finally{button.disabled=false;}
      });
    }
  }
  async function refreshAll(){
    if(refreshBusy||!document.body.classList.contains('live-project'))return;
    const slug=active();if(!validSlug(slug))return;
    refreshBusy=true;
    try{
      const results=await Promise.allSettled([
        api('/api/pw-v01210/studio-access'),
        api('/api/projects/'+encodeURIComponent(slug)+'/orders'),
        api('/api/projects/'+encodeURIComponent(slug)+'/reports'),
        api('/api/projects/'+encodeURIComponent(slug)+'/staff'),
        api('/api/projects/'+encodeURIComponent(slug)+'/jobs')
      ]);
      if(active()!==slug)return; // Never paint data from a previous project.
      if(results[0].status==='fulfilled'){
        access=!!results[0].value.enabled;accessLoaded=true;paintAccess();
      }else if(!accessLoaded){
        accessPanel.innerHTML='<h3>⚠ Studioåtkomst kunde inte kontrolleras</h3><p>Servern behöver svara innan ett nytt tillstånd kan ges.</p>';
      }
      if(results[1].status==='fulfilled'&&results[2].status==='fulfilled'){
        const orders=results[1].value.orders||[],reports=results[2].value.reports||[];
        paintDecisions(slug,orders,reports);
        const staff=results[3].status==='fulfilled'?results[3].value.staff||[]:[];
        const jobs=results[4].status==='fulfilled'?results[4].value.jobs||[]:[];
        stationState={};
        for(const [station] of Object.entries(settings)){
          stationState[station]={
            people:staff.filter(p=>p.station===station).map(p=>({name:p.name,
              active:jobs.some(j=>j.agent_id===p.id&&['running','queued'].includes(j.state))})),
            reviews:orders.filter(o=>o.station===station&&o.status==='review').length,
            waiting:orders.filter(o=>o.station===station&&o.status==='waiting').length};
        }
        renderStations();
      }else if(decisionPanel){decisionPanel.innerHTML='<h3>📋 Arbete och beslut</h3><p>⚠ Arbetskön kunde inte läsas. Prova igen när servern svarar.</p>';}
    }catch(error){console.warn('Projektstatus kunde inte kontrolleras:',error);}
    finally{refreshBusy=false;}
  }
  // Only refresh when the interface is already live; no external AI calls.
  hookProjectCreation();updateContexts();refreshProjectInfo();
  window.addEventListener('pixelworks:project-changed',()=>{hookProjectCreation();updateContexts();});
  window.addEventListener('pixelworks:gemini-review-changed',()=>setTimeout(refreshAll,180));
  window.addEventListener('pixelworks:studio-access-changed',()=>setTimeout(refreshAll,200));
  setInterval(()=>{projectChanged();hookProjectCreation();void refreshAll();removeStaleAccess();},8500);
  setTimeout(refreshAll,1400);
})();
