/* Pixel Works v0.12.11.15 – creator-mode choice and resilient project selection. */
(() => {
  'use strict';
  const $ = selector => document.querySelector(selector);
  const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const SAVED_PROJECT='pixelworks.last-project.v01211';
  const fallbackStorage=new Map();
  function savedGet(key){try{return localStorage.getItem(key)||fallbackStorage.get(key)||null}catch(_){return fallbackStorage.get(key)||null}}
  function savedSet(key,value){fallbackStorage.set(key,value);try{localStorage.setItem(key,value)}catch(_){/* Spelbyte fungerar under sessionen även utan lagring. */}}
  const slugify = x => x.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,48);
  let token='', advancedPassthrough=false, busy=false;
  let firstProjectRestored=false;
  const style=document.createElement('style');style.textContent=`
    #pw11Quick{width:min(540px,95vw);background:#26334b;color:#ffe8bc;border:7px ridge #a3744e;box-sizing:border-box;padding:18px;box-shadow:8px 9px 0 #0a1520}
    #pw11Quick::backdrop{background:#071122b9}
    #pw11Quick h2{color:#ffd587;font-size:21px;margin:0 0 8px}
    #pw11Quick .pw11mode{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:16px 0}
    #pw11Quick .pw11mode button{margin:0;min-height:98px;text-align:left;font-size:15px}
    #pw11Quick .pw11mode button small{display:block;font-size:12px;line-height:1.5;font-weight:400;margin-top:8px}
    #pw11Quick .pw11idea[hidden],#pw11Quick .pw11mode[hidden]{display:none!important}
    @media(max-width:480px){#pw11Quick .pw11mode{grid-template-columns:1fr}}
    #pw11Quick p{font-size:13px;line-height:1.55}
    #pw11Quick label{display:block;font-size:13px;margin:13px 0 5px}
    #pw11Quick input,#pw11Quick textarea{width:100%;box-sizing:border-box;background:#111d2c;color:white;border:2px solid #7188a0;padding:10px;font:inherit}
    #pw11Quick button,.pw11Action{background:#efc76f;color:#252c3c;font-weight:700;border:3px solid #845b33;padding:9px 11px;cursor:pointer;margin:5px 5px 5px 0}
    #pw11Quick .pw11alt{background:#6c819b;color:white}
    #pw11Quick .pw11error{color:#ffb5ad;min-height:16px}
    #pw11ChiefAuth{position:relative;display:block;width:100%;font:inherit;text-align:left;white-space:normal;margin:8px 0 6px}
    #pw11SavedIndicator{font-size:12px;padding:5px 8px;max-width:360px}
  `;document.head.append(style);
  const d=document.createElement('dialog');d.id='pw11Quick';d.innerHTML=`
    <h2>🎮 Skapa ett nytt spel</h2>
    <p>Hur vill du börja? Du väljer själv spelidé, eller bygger den steg för steg med våra gamla spelval.</p>
    <div class="pw11mode" id="pw11Mode">
      <button id="pw11Wizard" type="button">🎲 Bygg med spelguiden<small>Välj genre, värld, karaktärer, spelmekanik, grafik och fler kategorier med knappar.</small></button>
      <button id="pw11Manual" type="button">✍️ Skriv min egen spelidé<small>Skriv spelnamn och beskrivning direkt, utan att gå igenom alla steg.</small></button>
    </div>
    <section class="pw11idea" id="pw11ManualFields" hidden>
      <p><button id="pw11Back" class="pw11alt" type="button">◀ Byt sätt att skapa spel</button></p>
      <label for="pw11GameTitle">Vad ska spelet heta?</label>
      <input id="pw11GameTitle" maxlength="90" placeholder="Vårt nya äventyr">
      <label for="pw11GameIdea">Vad handlar spelet om?</label>
      <textarea id="pw11GameIdea" rows="4" maxlength="3000" placeholder="Beskriv spelidén med några meningar…"></textarea>
      <p>Skapar ett eget spelprojekt och startar inget AI-arbete automatiskt. Studioarbete godkänns en gång för dina projektmappar.</p>
      <button id="pw11Create" type="button">🚀 Skapa spel och starta studion</button>
    </section>
    <div><button id="pw11Cancel" class="pw11alt" type="button">Avbryt</button></div>
    <p id="pw11Error" class="pw11error" role="alert"></p>`;
  document.body.append(d);
  $('#pw11Cancel').onclick=()=>d.close();
  function chooseMode(mode){
    $('#pw11Error').textContent='';
    if(mode==='wizard'){
      d.close();advancedPassthrough=true;
      try{$('#newProjectBtn')?.click()}finally{advancedPassthrough=false}
      return;
    }
    $('#pw11Mode').hidden=mode==='manual';
    $('#pw11ManualFields').hidden=mode!=='manual';
    if(mode==='manual')$('#pw11GameTitle').focus();
    else $('#pw11Wizard').focus();
  }
  $('#pw11Wizard').onclick=()=>chooseMode('wizard');
  $('#pw11Manual').onclick=()=>chooseMode('manual');
  $('#pw11Back').onclick=()=>chooseMode('choice');
  function openQuick(){
    chooseMode('choice');
    if(!d.open)d.showModal();
    $('#pw11Wizard').focus();
  }
  document.addEventListener('click',event=>{
    if(advancedPassthrough)return;
    const b=event.target.closest?.('#newProjectBtn');
    if(!b)return;
    event.preventDefault();event.stopImmediatePropagation();openQuick();
  },true);
  async function api(url,data){
    if(!token){const response=await fetch('/api/bootstrap');if(!response.ok)throw Error('Den lokala servern svarar inte.');token=(await response.json()).token;}
    const response=await fetch(url,{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-Pixelworks-Token':token},body:JSON.stringify(data)});
    const result=await response.json();if(!response.ok)throw Error(result.error||'HTTP '+response.status);return result;
  }
  $('#pw11Create').onclick=async()=>{
    if(busy)return;
    const name=$('#pw11GameTitle').value.trim(),idea=$('#pw11GameIdea').value.trim(),slug=slugify(name);
    if(name.length<2||slug.length<2||idea.length<10){$('#pw11Error').textContent='Ange ett spelnamn och en spelidé på minst 10 tecken.';return}
    busy=true;$('#pw11Create').disabled=true;$('#pw11Error').textContent='Skapar studion…';
    try{
      const r=await api('/api/projects',{slug,name,idea,genre:'Spel',platform:'Webbläsare',priority:'Spelkänsla',
        creator:{},weights:{},areas:[],approval:'CREATE_PROJECT_ON_DISK'});
      if(!r.verified)throw Error('Projektet sparades inte och kunde inte verifieras.');
      // Read-after-write: never celebrate a game that did not persist to disk.
      const response=await fetch('/api/projects/'+encodeURIComponent(slug));
      const checked=await response.json();
      if(!response.ok||!checked.verified||checked.project?.id!==slug)throw Error('Projektet hittas inte vid kontrolläsning.');
      if(r.team_warning)throw Error('Projekt sparat men teamet behöver ses över: '+r.team_warning);
      savedSet(SAVED_PROJECT,slug);
      await window.pixelWorksRefreshLive?.();
      const model=window.__PIXEL_WORKS_DEMO__?.model,ui=window.__PIXEL_WORKS_DEMO__?.ui;
      if(model?.projects.some(p=>p.id===slug)){model.switchProject(slug);ui?.renderAll();}
      window.dispatchEvent(new CustomEvent('pixelworks:project-created',{detail:{id:slug,name}}));
      d.close();$('#pw11GameTitle').value='';$('#pw11GameIdea').value='';$('#pw11Error').textContent='';
      const status=$('#pw11SavedIndicator');if(status){status.textContent='💾 '+name+' sparat – studio redo';}
    }catch(e){$('#pw11Error').textContent='⚠ '+e.message;}
    finally{busy=false;$('#pw11Create').disabled=false}
  };
  function persistSelection(){const slug=$('#projectSelect')?.value;if(slug)savedSet(SAVED_PROJECT,slug);}
  $('#projectSelect')?.addEventListener('change',persistSelection);
  const select=$('#projectSelect');
  if(select){const note=document.createElement('div');note.id='pw11SavedIndicator';note.textContent='💾 Projekt laddas från disk';select.after(note)}
  // Startup restore runs once. A staff refresh must NEVER switch away from
  // the project the player explicitly chose or just created.
  function restoreSelection(){
    const model=window.__PIXEL_WORKS_DEMO__?.model,ui=window.__PIXEL_WORKS_DEMO__?.ui;
    if(!model||!model.projects?.some(p=>p.live))return;
    const saved=savedGet(SAVED_PROJECT);
    if(!firstProjectRestored){
      firstProjectRestored=true;
      if(saved&&model.projects.some(p=>p.id===saved)&&model.activeProjectId!==saved){
        model.switchProject(saved);ui?.renderAll();
      }
    }
    const active=model.projects.find(p=>p.id===model.activeProjectId);
    if(active?.live)savedSet(SAVED_PROJECT,active.id);
    const label=$('#pw11SavedIndicator');
    if(label)label.textContent=active?.live?'💾 '+active.title+' · aktivt projekt':'⚠ Inget verkligt projekt valt';
  }
  // Project menu stays a game menu but gains quick return and storage warnings.
  const menuContent=$('#dockDialogContent');
  if(menuContent){
    const updateProjectsMenu=()=>{
      if(!menuContent.textContent.includes('Välj spelprojekt')||menuContent.querySelector('#pw11Recent'))return;
      const saved=savedGet(SAVED_PROJECT);
      const available=[...($('#projectSelect')?.options||[])].some(x=>x.value===saved);
      const row=document.createElement('div');row.id='pw11Recent';
      if(saved&&available){
        const b=document.createElement('button');b.className='pw11Action';b.textContent='🕘 Fortsätt senaste spelet';
        b.onclick=()=>{const input=$('#projectSelect');input.value=saved;input.dispatchEvent(new Event('change',{bubbles:true}));$('#dockDialog')?.close();};
        row.append(b);
      }else if(saved&&!available){
        row.textContent='⚠ Senast spelade projekt ('+saved+') syns inte i serverns lista. Inga filer har raderats av projektbytet.';
      }
      menuContent.append(row);
      fetch('/api/projects').then(r=>r.json()).then(data=>{
        if(!row.isConnected)return;
        if(data.needs_attention?.length){
          const note=document.createElement('p');note.textContent='⚠ '+data.needs_attention.length+' projektmapp(ar) behöver granskas i '+(data.root||'arbetsroten')+'.';
          row.append(note);
        }
      }).catch(()=>{});
    };
    new MutationObserver(updateProjectsMenu).observe(menuContent,{childList:true,subtree:false});
  }
  let attempts=0;const init=setInterval(()=>{
    if(window.pixelWorksApplyLive && window.__PIXEL_WORKS_DEMO__){
      clearInterval(init);
      const original=window.pixelWorksApplyLive;
      window.pixelWorksApplyLive=function(...args){original(...args);restoreSelection();refreshGeminiStatus();};
      const model=window.__PIXEL_WORKS_DEMO__.model;
      const priorSwitch=model.switchProject.bind(model);
      model.switchProject=function(id){
        if(!model.projects.some(p=>p.id===id))return;
        const previous=model.activeProjectId;
        const result=priorSwitch(id);
        savedSet(SAVED_PROJECT,id);
        if(previous!==id)window.dispatchEvent(new CustomEvent('pixelworks:project-changed',
          {detail:{from:previous,to:id}}));
        return result;
      };
      const originalStaff=model.setLiveStaff.bind(model);
      model.setLiveStaff=function(id,staff,available){
        originalStaff(id,staff,available);
        const project=model.projects.find(p=>p.id===id);if(!project)return;
        const geminiConfigured=window.__PW11_GEMINI_CONFIGURED__;
        const geminiVerified=window.__PW11_GEMINI_VERIFIED__;
        project.providers.gemini={label:'Gemini API',engineState:geminiVerified?'TEXTSVAR TESTAT':geminiConfigured?'TESTA ANSLUTNING':'TOKEN SAKNAS',quota:'okänt'};
        for(const agent of project.agents){
          if(agent.provider==='gemini'){
            agent.engineAvailable=!!geminiVerified;
            agent.status=geminiConfigured?'idle':'blocked';
          }
        }
      };
      restoreSelection();refreshGeminiStatus();
    }else if(++attempts>30)clearInterval(init);
  },300);
  window.addEventListener('pixelworks:gemini-token-changed',()=>{refreshGeminiStatus()});
  async function refreshGeminiStatus(){
    try{const response=await fetch('/api/providers');if(!response.ok)return;
      const p=(await response.json()).providers;
      window.__PW11_GEMINI_CONFIGURED__=!!p?.gemini?.configured;
      window.__PW11_GEMINI_VERIFIED__=!!p?.gemini?.execution_enabled;
      const model=window.__PIXEL_WORKS_DEMO__?.model,ui=window.__PIXEL_WORKS_DEMO__?.ui;
      if(!model)return;
      for(const project of model.projects){
        project.providers.gemini={label:'Gemini API',engineState:p.gemini?.execution_enabled?'TEXTSVAR TESTAT':p.gemini?.configured?'TESTA ANSLUTNING':'TOKEN SAKNAS',quota:'okänt'};
        for(const agent of project.agents.filter(x=>x.provider==='gemini')){
          agent.engineAvailable=!!p.gemini?.execution_enabled;
          if(agent.status==='blocked'&&p.gemini?.configured)agent.status='idle';
        }
      }
      ui?.renderAgents();
    }catch(_){/* Anslutningsfel: visa senast hämtade status. */}
  }
  // Single studio-wide opt-in, stored on the local server rather than in a
  // browser cookie. 'Inte nu' is also remembered; no repetitive modal loop.
  const consent=document.createElement('dialog');consent.id='pw11StudioConsent';
  consent.setAttribute('aria-labelledby','pw11ConsentTitle');
  consent.innerHTML=`<h2 id="pw11ConsentTitle">🎮 Välkommen till Pixel Works</h2>
    <p>Vill du låta din AI-studio arbeta automatiskt i <strong>Pixel Works egna spelprojektmappar</strong> och använda dina redan konfigurerade AI-anslutningar?</p>
    <p>Arbetarna får skapa och ändra filer i studions projekt. De får <strong>inte</strong> publicera på GitHub, ändra andra mappar eller aktivera betalmodeller. AI-modellernas kvoter och tester gäller fortfarande.</p>
    <p><strong>Du kan ändra detta senare under Inställningar.</strong> Inget API-anrop startas av att du godkänner.</p>
    <p id="pw11ConsentError" class="pw11error" role="alert"></p>
    <button id="pw11ConsentAllow" type="button">✅ Ja, fråga mig inte igen</button>
    <button id="pw11ConsentDecline" type="button" class="pw11alt">Inte nu – bara titta</button>`;
  document.body.append(consent);
  // Same in-game style as the project wizard.
  const dialogStyle=document.createElement('style');dialogStyle.textContent=`
    #pw11StudioConsent{width:min(540px,94vw);background:#26334b;color:#ffe8bc;border:7px ridge #a3744e;padding:18px;box-sizing:border-box;box-shadow:8px 9px 0 #0a1520;font:14px system-ui,sans-serif}
    #pw11StudioConsent::backdrop{background:#071122be}
    #pw11StudioConsent h2{color:#ffd587;font-size:21px}
    #pw11StudioConsent p{line-height:1.55}
    #pw11StudioConsent button{background:#efc76f;color:#252c3c;font-weight:700;border:3px solid #845b33;padding:9px;cursor:pointer;margin:4px}
    #pw11StudioConsent button.pw11alt{background:#71849c;color:white}
    #pw11StudioAccessRow{font-size:13px;padding:9px 4px}
  `;document.head.append(dialogStyle);
  let access={decided:false,enabled:false};let consentPending=false;
  async function accessRequest(payload){
    if(!token){const bootstrap=await fetch('/api/bootstrap');if(!bootstrap.ok)throw Error('Servern svarar inte');token=(await bootstrap.json()).token;}
    const options={credentials:'same-origin',headers:{'X-Pixelworks-Token':token}};
    if(payload){options.method='POST';options.headers['Content-Type']='application/json';options.body=JSON.stringify(payload)}
    const response=await fetch('/api/pw-v01210/studio-access',options);
    const data=await response.json();if(!response.ok)throw Error(data.error||'HTTP '+response.status);
    return data;
  }
  function openConsent(){if(!consent.open)consent.showModal();$('#pw11ConsentError').textContent=''}
  async function saveConsent(enabled){
    if(consentPending)return;consentPending=true;
    $('#pw11ConsentAllow').disabled=true;$('#pw11ConsentDecline').disabled=true;
    try{
      access=await accessRequest({enabled,approval:enabled?'ALLOW_PIXELWORKS_STUDIO_WORK':'DISABLE_PIXELWORKS_STUDIO_WORK'});
      consent.close();updateAccessRow();window.dispatchEvent(new Event('pixelworks:studio-access-changed'));
    }catch(e){$('#pw11ConsentError').textContent='Kunde inte spara: '+e.message;}
    finally{consentPending=false;$('#pw11ConsentAllow').disabled=false;$('#pw11ConsentDecline').disabled=false;}
  }
  $('#pw11ConsentAllow').onclick=()=>saveConsent(true);
  $('#pw11ConsentDecline').onclick=()=>saveConsent(false);
  // The developer diagnostics panel stays intact. Add a single concise toggle.
  function updateAccessRow(){
    const state=$('#pw11StudioAccessState');if(state)state.textContent=access.enabled?'🟢 Tillåtet för studions projekt':'⚪ Avstängt';
    const b=$('#pw11AccessToggle');if(b)b.textContent=access.enabled?'Stäng av studioarbete':'Ändra åtkomst';
  }
  function injectAccessRow(){
    if(!menuContent||!menuContent.textContent.includes('Inställningar & diagnostik')||$('#pw11StudioAccessRow'))return;
    const row=document.createElement('div');row.id='pw11StudioAccessRow';row.className='dock-row';
    const label=document.createElement('span');label.id='pw11StudioAccessState';
    const button=document.createElement('button');button.id='pw11AccessToggle';button.type='button';
    button.onclick=async()=>{
      if(access.enabled){
        try{access=await accessRequest({enabled:false,approval:'DISABLE_PIXELWORKS_STUDIO_WORK'});updateAccessRow()}
        catch(e){alert('Kunde inte stänga av: '+e.message)}
      }else{const d=$('#dockDialog');if(d?.open)d.close();openConsent()}
    };
    row.append('🏢 Studioåtkomst: ',label,' ',button);menuContent.append(row);updateAccessRow();
  }
  if(menuContent)new MutationObserver(injectAccessRow).observe(menuContent,{childList:true,subtree:false});
  function setupConsent(){
    accessRequest().then(result=>{
      access=result;updateAccessRow();
      if(!access.decided)openConsent();
    }).catch(e=>console.warn('Studioåtkomst kunde inte läsas: '+e.message));
  }
  setupConsent();
  // Advanced creator in the older local.js still contains a browser confirm().
  // Once studio access is granted, the same server-side create validation is
  // used directly. This avoids a second permissions popup after the first yes.
  let createHookAttempts=0;
  function bindAdvancedCreator(){
    const old=window.pixelWorksCreateLive;
    if(typeof old!=='function'){
      if(++createHookAttempts<28)setTimeout(bindAdvancedCreator,250);
      return;
    }
    if(old.__pw14StudioWrapped)return;
    const withoutRepeatedConfirmation=async function(d){
      if(!access.enabled)return old(d);
      const name=String(d.name||'').trim(),slug=slugify(name);
      if(name.length<2||slug.length<2)throw Error('Ange ett projektnamn på minst två tecken.');
      const created=await api('/api/projects',{
        slug,name,idea:d.description,genre:d.genre,platform:d.platform,
        priority:d.priority,creator:d.creator||{},weights:d.weights||{},
        areas:d.areas||[],approval:'CREATE_PROJECT_ON_DISK'});
      if(!created.verified)throw Error('Projektets lagring kunde inte verifieras.');
      const response=await fetch('/api/projects/'+encodeURIComponent(slug));
      const checked=await response.json();
      if(!response.ok||!checked.verified||checked.project?.id!==slug)
        throw Error('Projektet kunde inte läsas tillbaka från disk.');
      return checked;
    };
    withoutRepeatedConfirmation.__pw14StudioWrapped=true;
    window.pixelWorksCreateLive=withoutRepeatedConfirmation;
  }
  bindAdvancedCreator();
  // Legacy chief buttons must not turn one-time permission into a second per-
  // project confirmation. Open the studio dialog only if the user explicitly
  // requests access; otherwise guide them to Settings.
  document.addEventListener('click',e=>{
    const button=e.target.closest?.('.chief-mandate-button,#pw11ChiefAuth');
    if(!button)return;
    e.preventDefault();e.stopImmediatePropagation();
    if(access.enabled)return;
    if(access.decided){alert('Studioarbete är avstängt. Aktivera det via Inställningar → Studioåtkomst.');return}
    openConsent();
  },true);
  const chiefButton=document.createElement('button');chiefButton.id='pw11ChiefAuth';chiefButton.type='button';chiefButton.className='pw11Action';chiefButton.hidden=true;
  chiefButton.textContent='🔓 Studioåtkomst behövs';
  ($('#realJobProject')?.parentElement||document.querySelector('.right-rail')||document.body).append(chiefButton);
  async function pollMandate(){
    try{
      const id=$('#projectSelect')?.value;
      if(!id||!document.body.classList.contains('live-project')){chiefButton.hidden=true;return;}
      // Re-read actual studio consent: another tab or a restart may have changed it.
      access=await accessRequest();updateAccessRow();
      if(access.enabled){chiefButton.hidden=true;return;}
      const response=await fetch('/api/projects/'+id+'/dispatch/health');if(!response.ok)return;
      const status=await response.json();chiefButton.hidden=status.state!=='mandate_required';
    }catch(_){chiefButton.hidden=true}
  }
  setInterval(pollMandate,4000);setTimeout(pollMandate,1000);
})();
