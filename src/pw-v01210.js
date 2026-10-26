/* Pixel Works v0.12.11.3 – settings home restored, Gemini test unlocked, shared provider token. */
(() => {
  'use strict';
  const $ = (q,root=document) => root.querySelector(q);
  const esc = s => String(s ?? '').replace(/[&<>"']/g, x => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]));
  let ownToken = '';
  async function api(path,payload){
    if(!ownToken){
      const bootstrap=await fetch('/api/bootstrap',{credentials:'same-origin'});
      if(!bootstrap.ok)throw Error('Pixel Works-servern är inte nåbar');
      ownToken=(await bootstrap.json()).token;
    }
    const response=await fetch(path,{method:payload?'POST':'GET',credentials:'same-origin',
      headers:{'X-Pixelworks-Token':ownToken,...(payload?{'Content-Type':'application/json'}:{})},
      ...(payload?{body:JSON.stringify(payload)}:{})});
    const data=await response.json();
    if(!response.ok)throw Error(data.error||'HTTP '+response.status);
    return data;
  }
  const slug = () => {
    const s = $('#projectSelect')?.value;
    return /^[a-z0-9][a-z0-9-]{1,49}$/.test(s || '') ? s : '';
  };
  let selectedTab = 'ai', panel, body;
  let pastedFiles = [];
  const css = document.createElement('style');
  css.textContent = `#pw12Panel{width:min(830px,95vw);max-height:90vh;overflow:auto;box-sizing:border-box;background:#202d44;color:#ffebc2;border:8px ridge #a16c45;box-shadow:12px 12px 0 #091420;padding:16px;font:14px system-ui,sans-serif;z-index:13000}#pw12Panel::backdrop{background:#071226c7;backdrop-filter:blur(2px)}#pw12Panel h2{color:#ffc96b;margin:0}#pw12Panel h3{color:#ffcf83;margin:13px 0 7px}#pw12Panel p,#pw12Panel label{line-height:1.45}#pw12Panel input,#pw12Panel textarea,#pw12Panel select{box-sizing:border-box;width:100%;padding:7px;background:#101c2e;color:white;border:2px solid #6e879c;font:inherit}#pw12Panel input[type=checkbox]{width:auto;margin-right:8px}#pw12Panel label{display:block;margin:10px 0}#pw12Panel button{background:#ecc66c;border:3px solid #8c6037;padding:7px 12px;margin:4px;cursor:pointer;font-weight:700;color:#26304a}#pw12Panel button:disabled{opacity:.45;cursor:default}#pw12Panel .pw12-tab{background:#41566f;color:white}#pw12Panel .pw12-tab.on{background:#edc66c;color:#27324a}#pw12Panel .pw12-head{display:flex;justify-content:space-between;gap:10px;align-items:center}#pw12Panel .pw12-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}#pw12Panel .pw12-card{background:#324661;border:2px solid #78929d;padding:9px}#pw12Panel .pw12-note{color:#eee0b0;font-size:12px}#pw12Panel .pw12-warn{padding:10px;background:#523747;border:1px solid #f1ab8c}#pw12Panel .pw12-status{min-height:1.5em;white-space:pre-wrap;color:#bdecc2}#pw12Panel .pw12-files{max-height:150px;overflow:auto}#pw12Panel .pw12-files label{border-bottom:1px solid #637a90}#pw12Panel .pw12-thumb{max-width:60px;max-height:40px}@media(max-width:600px){#pw12Panel .pw12-grid{grid-template-columns:1fr}}`;
  document.head.append(css);
  panel=document.createElement('dialog');panel.id='pw12Panel';panel.innerHTML='<div class="pw12-head"><h2 id="pw12Title">☕ Gemini API</h2><button type="button" id="pw12Close">✕ Stäng</button></div><div id="pw12Body"></div><div><button type="button" id="pw12Advanced" aria-expanded="false" aria-controls="pw12Nav">🧰 Avancerade verktyg ▸</button><nav id="pw12Nav" hidden><button data-pwtab="ai">Gemini API</button><button data-pwtab="workers">Codex × flera</button><button data-pwtab="materials">Arbetsbilagor</button></nav></div>';
  document.body.append(panel);body=$('#pw12Body',panel);
  $('#pw12Close',panel).onclick=()=>panel.close();
  const advanced=$('#pw12Advanced',panel), advancedNav=$('#pw12Nav',panel);
  advanced.onclick=()=>{
    advancedNav.hidden=!advancedNav.hidden;
    advanced.setAttribute('aria-expanded',String(!advancedNav.hidden));
    advanced.textContent=advancedNav.hidden?'🧰 Avancerade verktyg ▸':'🧰 Dölj avancerade verktyg ▾';
  };
  panel.querySelectorAll('[data-pwtab]').forEach(b=>b.onclick=()=>{selectedTab=b.dataset.pwtab;render()});
  function notice(s){const n=$('#pw12Notice',body);if(n)n.textContent=String(s)}
  function openPanel(tab='ai') {selectedTab=tab;advancedNav.hidden=true;advanced.setAttribute('aria-expanded','false');advanced.textContent='🧰 Avancerade verktyg ▸';if(!panel.open)panel.showModal();render()}
  window.pixelWorksAISettingsV01210 = openPanel;
  // Keep the game's original Settings overview. Gemini belongs INSIDE that menu,
  // not in place of it. The legacy dock remains the owner of the Settings button.
  // The wall prop PROJECTSTATUS was a duplicate entry to the demo task board.
  // Actual server-backed tasks remain accessible from the top Uppdrag menu.
  const obsoleteStatusBoard = document.querySelector('#officeBoard');
  if (obsoleteStatusBoard) obsoleteStatusBoard.remove();
  // Add a natural entry *inside* the existing Settings menu, rather than a new top-level tab.
  function geminiStateLabel(state){
    if(!state?.configured)return '⚪ Ingen token sparad';
    if(state.test_result==='kvotgräns nådd' || state.paused_until_day || state.paused_until_epoch)return '🟡 Kvot- eller API-paus';
    if(state.test_result==='ansluten')return '🟢 Ansluten · textsvar verifierat';
    if(state.test_result==='modellen nekas (404)' || state.test_result==='inget textsvar')return '🔴 Modelltest misslyckades';
    if(String(state.test_result||'').startsWith('anslutningsfel'))return '🔴 Anslutningsfel';
    return '🟡 Token sparad · inte verifierad';
  }
  const dock=$('#dockDialogContent');
  let statusRequest=0;
  async function updateSettingsGeminiStatus(){
    const label=$('#pw12SettingsState',dock);
    if(!label)return;
    const request=++statusRequest;
    try{
      const res=await api('/api/pw-v01210/status');
      if(request!==statusRequest || !label.isConnected)return;
      const status=res.gemini||{};
      label.textContent=geminiStateLabel(status);
    }catch(_){if(label.isConnected)label.textContent='⚪ Kan inte läsa Gemini-status';}
  }
  function injectSettings(){
    if(!dock || !dock.textContent.includes('Inställningar & diagnostik') || $('#pw12SettingsGemini',dock))return;
    const row=document.createElement('div');row.id='pw12SettingsGemini';
    row.className='dock-row';
    row.style.cssText='display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;padding:10px 4px;border-bottom:1px solid #58708b';
    const desc=document.createElement('div');
    desc.innerHTML='<strong>☕ Google Gemini</strong><br><span id="pw12SettingsState" aria-live="polite">Läser anslutning…</span>';
    const button=document.createElement('button');button.id='pw12Open';button.type='button';
    button.textContent='⚙️ API-token / Testa anslutning';
    button.addEventListener('click',()=>{const dialog=$('#dockDialog');if(dialog?.open)dialog.close();openPanel('ai')});
    row.append(desc,button);
    const localButton=$('[data-open-local]',dock);
    if(localButton)localButton.before(row);else dock.append(row);
    updateSettingsGeminiStatus();
  }
  if(dock){new MutationObserver(injectSettings).observe(dock,{childList:true,subtree:false});injectSettings()}
  window.addEventListener('pixelworks:gemini-token-changed',updateSettingsGeminiStatus);
  // Old Game Bible materials window remains exclusively for DESIGN inspiration.
  // Screenshots pasted into its former drop zone now go to a job attachment draft.
  const legacyDialog=$('#localStudioDialog');
  if(legacyDialog){
    const legacyHint=()=>{
      const zone=$('#bibleDrop',legacyDialog);
      if(!zone||$('#pw12ReferenceHelp',legacyDialog))return;
      const info=document.createElement('div');info.id='pw12ReferenceHelp';
      info.innerHTML='<p class="pw12-note">🎨 Game Bible-material är för valda utseendereferenser. Buggskärmdumpar och videofel hör hemma bland arbetsbilagor.</p>';
      const button=document.createElement('button');button.type='button';button.textContent='📎 Öppna arbetsbilagor (inte Game Bible)';
      button.onclick=()=>{legacyDialog.close();openPanel('materials')};info.append(button);zone.before(info);
    };
    new MutationObserver(legacyHint).observe(legacyDialog,{childList:true,subtree:true});legacyHint();
    // The legacy v0.12.0.9 dialog contains stale 'Gemini sjukskriven'
    // wording even after the provider has been enabled. Keep it neutral.
    const updateGeminiLabels=()=>{
      const option=legacyDialog.querySelector('#profileProvider option[value=gemini]');
      if(option && option.textContent.includes('ännu ej aktiv'))option.textContent='☕ Gemini API';
      for(const item of legacyDialog.querySelectorAll('p')){
        if(item.textContent.includes('Gemini: sjukskriven tills nyckel'))
          item.textContent='☕ Gemini-anställda arbetar automatiskt när Gemini-token finns och en lämplig order väntar.';
      }
    };
    new MutationObserver(updateGeminiLabels).observe(legacyDialog,{childList:true,subtree:true});updateGeminiLabels();
  }
  document.addEventListener('paste',e=>{
    const zone=e.target?.closest?.('#bibleDrop');
    if(!zone)return;
    const files=[...(e.clipboardData?.items||[])].filter(x=>x.kind==='file').map(x=>x.getAsFile()).filter(Boolean);
    if(!files.length)return;
    e.preventDefault();e.stopImmediatePropagation();pastedFiles.push(...files);
    if(legacyDialog?.open)legacyDialog.close();openPanel('materials');
  },true);
  document.addEventListener('drop',e=>{
    const zone=e.target?.closest?.('#stationLayer .station');
    if(!zone||!e.dataTransfer?.files?.length)return;
    e.preventDefault();e.stopImmediatePropagation();
    pastedFiles.push(...e.dataTransfer.files);
    window.pw12PreferredStation=zone.dataset.id||'code';
    if(legacyDialog?.open)legacyDialog.close();openPanel('materials');
  },true);
  async function render(){
    $('#pw12Title',panel).textContent=({ai:'☕ Gemini API',workers:'💻 Kodarbete · Avancerat',materials:'📎 Arbetsbilagor'}[selectedTab]||'☕ Gemini API');
    panel.querySelectorAll('[data-pwtab]').forEach(b=>b.classList.toggle('on',b.dataset.pwtab===selectedTab));
    body.innerHTML='<p>📡 Läser lokal och verklig status…</p>';
    try{
      if(selectedTab==='ai') await drawAI();
      else if(selectedTab==='workers') await drawWorkers();
      else await drawMaterials();
    }catch(err){body.innerHTML='<p class="pw12-warn">⚠ '+esc(err.message)+'</p><button id="pw12Retry">Försök igen</button>';$('#pw12Retry',body).onclick=render}
  }
  async function drawAI(){
    const [status,secret]=await Promise.all([
      api('/api/pw-v01210/status'),api('/api/pw-v01210/gemini/token')]);
    const s=status.gemini;let savedKey=Boolean(s.configured);
    const state=geminiStateLabel(s);
    body.innerHTML=`<section class="pw12-card" aria-label="Gemini API">
      <h3>☕ Gemini API-token</h3>
      <div style="display:flex;gap:6px;align-items:end;flex-wrap:wrap">
        <label style="flex:1;min-width:210px">Delad token för alla Gemini-anställda
          <input id="pw12Key" type="password" spellcheck="false" autocomplete="off" value="" placeholder="${s.configured?'Sparad token finns – ange bara vid byte':'Klistra in Gemini API-token'}"></label>
        <button id="pw12Eye" type="button" aria-label="Visa eller dölj API-token">👁️ Visa</button>
      </div>
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <button id="pw12KeySave" type="button">💾 Spara</button>
        <button id="pw12Test" type="button">🔎 Testa/verifiera anslutning</button>
      </div>
      <p><strong id="pw12GeminiStatus" role="status">${esc(state)}</strong></p>
      <p class="pw12-note">${s.configured?'En token är sparad säkert lokalt. Lämna fältet tomt för att behålla den.':'Ingen token sparad ännu.'}</p>
      <p class="pw12-note">Textmodell: <b>${esc(s.model)}</b>. Testknappen gör ett riktigt kort AI-anrop, som räknas mot Googles faktiska kvot. Ingen automatisk fallback till betalmodeller.</p>
      <p class="pw12-note">En Gemini-anställd använder automatiskt denna token. Arbetsledaren kan ge research-, dokumentations- och idéuppdrag. Ingen separat aktivering behövs.</p>
      <p class="pw12-note">Gratisnivå och fakturering kan inte verifieras med token. Använd ett Google-projekt utan aktiverad fakturering. Registrerade anrop i Pixel Works idag: ${s.used_today} · Ingen lokal dygnsspärr · Googles återstående kvot: okänd.</p>
      <p id="pw12Notice" class="pw12-status" role="status"></p></section>`;
    $('#pw12Eye',body).onclick=()=>{
      const field=$('#pw12Key',body);const show=field.type==='password';field.type=show?'text':'password';
      $('#pw12Eye',body).textContent=show?'🙈 Dölj':'👁️ Visa';
    };
    $('#pw12KeySave',body).onclick=async()=>{
      const b=$('#pw12KeySave',body);b.disabled=true;
      try{
        const key=$('#pw12Key',body).value.trim();if(!key)throw Error('Klistra in API-token först.');
        await api('/api/providers/gemini',{key});
        const fresh=(await api('/api/pw-v01210/status')).gemini;
        if(!fresh.configured)throw Error('Servern bekräftar inte att token sparades.');
        savedKey=true;
        $('#pw12Key',body).value=''; // Keep the saved secret out of the DOM.
        $('#pw12GeminiStatus',body).textContent='🟡 Sparad · inte verifierad';
        notice('✅ Token sparad lokalt. Klicka på Testa anslutning för verifiering hos Google.');
        window.dispatchEvent(new Event('pixelworks:gemini-token-changed'));
      }catch(err){notice('⚠ '+err.message)}finally{b.disabled=false}
    };
    $('#pw12Test',body).onclick=async()=>{
      const b=$('#pw12Test',body), save=$('#pw12KeySave',body);
      b.disabled=true;save.disabled=true;
      try{
        const key=$('#pw12Key',body).value.trim();
        if(!key&&!savedKey)throw Error('Spara en Gemini-token före anslutningstestet.');
        // Blank input means TEST the existing saved key; never require the
        // server to disclose the credential to the browser.
        if(key){
          notice('💾 Sparar token lokalt inför testet…');
          await api('/api/providers/gemini',{key});
          savedKey=true;
          $('#pw12Key',body).value='';
          window.dispatchEvent(new Event('pixelworks:gemini-token-changed'));
        }
        notice('🔎 Ber Google-modellen svara på en kort testfråga (ett riktigt API-anrop)…');
        const result=await api('/api/pw-v01210/gemini/test',{});
        $('#pw12GeminiStatus',body).textContent=result.verified?'🟢 Ansluten · textsvar verifierat':'🔴 '+result.status;
        notice(result.detail||'Googles resultat saknar förklaring.');
      }catch(err){
        $('#pw12GeminiStatus',body).textContent='🔴 Kunde inte verifiera';
        notice('⚠ '+err.message);
      }finally{b.disabled=false;save.disabled=false}
    };
  }
  async function drawWorkers(){
    const project=slug();if(!project){body.textContent='Välj ett verkligt projekt i spelmenyn först.';return}
    const [staffRes,stat,files]=await Promise.all([api('/api/projects/'+project+'/staff'),api('/api/pw-v01210/status'),api('/api/pw-v01210/materials?project='+project)]);
    const agents=staffRes.staff.filter(a=>a.provider==='codex'&&a.station!=='cafe'&&Array.isArray(a.allowed_stations)&&a.allowed_stations.includes(a.station));
    const selected=a=>agents.map(x=>`<option value="${esc(x.id)}" ${x===a?'selected':''}>${esc(x.name)} · ${esc(x.station)}</option>`).join('');
    body.innerHTML=`<h3>💻 Flera oberoende Codex-arbetare</h3><p>Det befintliga arbetsflödet i Pixel Works används: <b>en process och en Git-worktree per agent</b>. Resultat kan integreras automatiskt om de är konfliktfria. Kod går aldrig till GitHub automatiskt.</p>
      <p class="pw12-note">CLI: ${stat.codex.execution_enabled?'körbar':'inte verifierad'} · Aktiva verkliga sessioner: ${stat.active.map(x=>esc(x.agent)+' ('+x.provider+')').join(', ')||'inga'}</p>
      <label>Antal samtidiga jobb i denna omgång (2–4)<select id="pw12Count"><option>2</option><option>3</option><option>4</option></select></label>
      <div class="pw12-grid">${[1,2,3,4].map(n=>`<div class="pw12-card pw12-worker" data-workern="${n}"><h3>Arbetare ${n}</h3><label>Välj agent<select id="pw12Agent${n}">${selected(agents[n-1])}</select></label><label>Arbetsorder<textarea id="pw12Prompt${n}" maxlength="3800" rows="4" placeholder="Konkreta kodförändringar och testkrav…"></textarea></label></div>`).join('')}</div>
      <h3>Bilagor till jobben (inte Game Bible)</h3><div class="pw12-files">${files.materials.map(a=>`<label><input type="checkbox" data-pw12material="${esc(a.id)}">${esc(a.name)} · ${esc(a.station)} · ${Math.ceil(a.size/1024)} kB</label>`).join('')||'<p>Inga arbetsbilagor. Lägg till under fliken Arbetsbilagor.</p>'}</div>
      <label><input type="checkbox" id="pw12Approve">Jag godkänner att Pixel Works vid behov gör en <b>lokal Git-commit</b> för separata arbetsytor och startar flera verkliga Codex-jobb. Konfliktfria kodändringar kan integreras automatiskt.</label>
      <button id="pw12StartTwo" ${agents.length>=2&&stat.codex.execution_enabled?'':'disabled'}>▶ Starta Codex-sessioner</button><p id="pw12Notice" class="pw12-status" role="status"></p>
      ${agents.length<2?'<p class="pw12-warn">Minst två behöriga Codex-anställda måste stå vid sina tillåtna arbetsstationer (inte fikarummet). Rekrytera/placera dem via Personal.</p>':''}`;
    const updateWorkerCards=()=>{
      const count=Number($('#pw12Count',body).value);
      body.querySelectorAll('.pw12-worker').forEach(card=>card.hidden=Number(card.dataset.workern)>count);
      const b=$('#pw12StartTwo',body);b.disabled=agents.length<count||!stat.codex.execution_enabled;
    };
    $('#pw12Count',body).onchange=updateWorkerCards;updateWorkerCards();
    $('#pw12StartTwo',body).onclick=async()=>{
      const b=$('#pw12StartTwo',body), count=Number($('#pw12Count',body).value);
      if(!$('#pw12Approve',body).checked)return notice('Godkänn lokal Git-förberedelse och verkliga jobben först.');
      const numbers=Array.from({length:count},(_,i)=>i+1);
      const idsAgents=numbers.map(n=>$('#pw12Agent'+n,body).value);
      if(new Set(idsAgents).size!==count)return notice('Välj olika anställda för varje jobb.');
      const instructions=numbers.map(n=>$('#pw12Prompt'+n,body).value.trim());
      if(instructions.some(v=>v.length<10))return notice('Varje uppdrag behöver minst 10 tecken.');
      const ids=[...body.querySelectorAll('[data-pw12material]:checked')].map(x=>x.dataset.pw12material);
      if(ids.length>16)return notice('Max 16 bilagor per jobb.');
      const marker=ids.length?'\n\n[[PW12_ATTACH:'+ids.join(',')+']]':'';
      if(instructions.some(x=>x.length+marker.length>4000))return notice('För långt uppdrag inklusive bilagor.');
      b.disabled=true;
      try{
        const m=await api('/api/projects/'+project+'/mandate');
        if(!m.mandate?.enabled)await api('/api/projects/'+project+'/mandate',{enabled:true,approval:'ALLOW_CODEX_WORKSPACE_WRITE'});
        await api('/api/projects/'+project+'/dispatch/prepare',{approval:'PREPARE_PARALLEL_WORK'});
        const results=await Promise.allSettled(idsAgents.map((agent_id,i)=>api('/api/jobs',{project,agent_id,
          station:agents.find(x=>x.id===agent_id)?.station,isolated:true,approval:'STARTA_CODEX_I_WORK',instruction:instructions[i]+marker})));
        notice(results.map((r,i)=>'Arbetare '+(i+1)+': '+(r.status==='fulfilled'?'jobb '+r.value.job_id+' startat':'FEL '+r.reason.message)).join('\n'));
      }catch(e){notice('⚠ '+e.message)}finally{b.disabled=false}
    };
  }
  document.addEventListener('paste',e=>{
    if(!panel.open || selectedTab!=='materials')return;
    const files=[...(e.clipboardData?.items||[])].filter(x=>x.kind==='file').map(x=>x.getAsFile()).filter(Boolean);
    if(files.length){e.preventDefault();pastedFiles.push(...files);notice('📋 '+pastedFiles.length+' inklistrade bilagor väntar på Spara.')}
  });
  async function drawMaterials(){
    const project=slug();if(!project){body.textContent='Välj ett verkligt projekt först.';return}
    const [assets,people]=await Promise.all([api('/api/pw-v01210/materials?project='+project),api('/api/projects/'+project+'/staff')]);
    const stations=[...new Set(people.staff.flatMap(a=>a.allowed_stations||[]))].filter(Boolean).sort();
    body.innerHTML=`<h3>🖼 Arbetsbilagor – separat från Game Bible</h3><p>Buggskärmdumpar och video hamnar under projektets <code>management/task-materials/</code>. De syns inte som designreferenser i Game Bible. Bilder kopieras till respektive Codex-worktree när ett nytt jobb startar. För video används bildrutor om ffmpeg finns installerat.</p>
      <label>Arbetsstation<select id="pw12MatStation">${stations.map(x=>`<option value="${esc(x)}">${esc(x)}</option>`).join('')}</select></label>
      <label>Välj bilder, video eller dokument<input id="pw12File" type="file" multiple accept="image/*,video/mp4,video/webm,.pdf,.txt,.md"></label><p class="pw12-note">Du kan även klistra in skärmdumpar med Ctrl+V när den här dialogen är öppen.</p>
      <label>Kommentar<textarea id="pw12MatNote" rows="2" maxlength="1200"></textarea></label>
      ${pastedFiles.length?`<p class="pw12-note">📋 ${pastedFiles.length} filer inklistrade/dragna och väntar på att sparas.</p>`:''}
      <p class="pw12-note">Max 18 MB per fil. Ingen fil laddas upp till AI-leverantör vid sparning. Webbläsaren skickar endast till din lokala Pixel Works-server.</p>
      <button id="pw12Upload">📥 Spara som arbetsbilaga</button><p id="pw12Notice" class="pw12-status" role="status"></p>
      <h3>Arbetsbilagor i projektet (${assets.materials.length})</h3><div class="pw12-files">${assets.materials.map(a=>`<p>📎 ${esc(a.name)} · ${esc(a.station)} · ${Math.ceil(a.size/1024)} kB</p>`).join('')||'<p>Inga uppladdade arbetsbilagor.</p>'}</div>`;
    if(window.pw12PreferredStation&&stations.includes(window.pw12PreferredStation))$('#pw12MatStation',body).value=window.pw12PreferredStation;
    $('#pw12Upload',body).onclick=async()=>{
      const b=$('#pw12Upload',body);b.disabled=true;
      try{
        const files=[...$('#pw12File',body).files,...pastedFiles];if(!files.length)throw Error('Välj minst en fil');
        for(const file of files){
          if(file.size>18*1024*1024)throw Error(file.name+' överskrider 18 MB');
          const data=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(String(reader.result).split(',')[1]);reader.onerror=reject;reader.readAsDataURL(file)});
          await api('/api/pw-v01210/materials',{project,name:file.name,station:$('#pw12MatStation',body).value,comment:$('#pw12MatNote',body).value,data});
        }
        pastedFiles=[];notice('✅ '+files.length+' arbetsbilagor sparade.');setTimeout(()=>{if(panel.open)render()},1000);
      }catch(e){notice('⚠ '+e.message)}finally{b.disabled=false}
    };
  }
})();

