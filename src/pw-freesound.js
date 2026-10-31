/* Pixel Works – server-owned tools + QA handoff UX (dev fb70d1c).
 * No separate sound-job modal. Normal workstation -> order -> dispatcher.
 * Credential controls live INSIDE the existing Settings & diagnostics dialog.
 * No API/AI work on page load or while creating a waiting order.
 */
(() => {
  'use strict';
  if (window.__PW_FREESOUND__) return;
  window.__PW_FREESOUND__ = true;
  const API = '/api/pw-tools/audio';
  const esc = s => String(s ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const project = () => window.__PIXEL_WORKS_DEMO__?.model?.activeProjectId || document.querySelector('#projectSelect')?.value;
  const api = (url, body) => {
    if (typeof window.pixelWorksApi !== 'function') throw Error('Lokal studio saknar anslutning');
    return window.pixelWorksApi(url, body);
  };
  // The office drawer has a dark-text-on-cream task card inside a dark panel.
  // Earlier inherited white text made the real job description unreadable.
  const contrastFix = document.createElement('style');
  contrastFix.id = 'pwToolContrastFix';
  contrastFix.textContent = `
    #agentDrawer .agent-detail .task-card{color:#213447;background:#fff6d8}
    #agentDrawer .agent-detail .task-card .task-title{color:#213447;overflow-wrap:anywhere;white-space:normal;line-height:1.45;padding-right:0}
    #agentDrawer .agent-detail .task-card .task-meta{color:#475766}
    #agentDrawer .agent-detail .task-card .task-details{color:#59483c}
  `;
  document.head.append(contrastFix);
  const style = document.createElement('style');
  style.textContent = `
    #pwToolsFreesound{display:block;border-bottom:1px solid #58708b;padding:10px 4px;color:inherit}
    #pwToolsFreesound .pwt-summary{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}
    #pwToolsFreesound p{margin:5px 0;font-size:12px}
    #pwToolsFreesound button{cursor:pointer;min-height:34px;padding:6px 10px}
    #pwToolsFreesound .pwt-config{background:#172b3c18;border:1px solid #78909b;padding:10px;margin-top:8px;display:grid;gap:8px}
    #pwToolsFreesound input{box-sizing:border-box;display:block;width:100%;padding:8px;background:#fff;color:#24394b;border:1px solid #91a7af}
    #pwToolsFreesound .pwt-controls{display:flex;flex-wrap:wrap;gap:8px}
    #pwToolsFreesound .pwt-note{font-size:11px;line-height:1.5}
    #pw18Desk .pwt-station{background:#fffef3d9;border:2px solid #a1bdac;border-radius:5px;padding:11px;margin:10px 0}
    #pw18Desk .pwt-station h3{margin:0 0 5px;font-size:15px;color:#30485b}
    #pw18Desk .pwt-caption{font-size:12px;color:#496370;margin:5px 0}
    #pw18Desk .pwt-result{margin:9px 0;padding:9px;background:white;border:1px solid #a3b8aa;border-radius:4px;overflow-wrap:anywhere}
    #pw18Desk .pwt-result p{font-size:12px;margin:5px 0}
    #pw18Desk .pwt-result audio{display:block;max-width:100%;width:100%;margin:8px 0}
    #pw18Desk .pwt-result button{min-height:35px}
    #pw18Desk .pwt-inline-btn{background:#216f80!important;color:#fff!important}
    #pw18Desk .pwt-error{color:#9b3e38;font-weight:700;white-space:pre-wrap}
    #dockDialog{max-height:88dvh;overflow-y:auto;overscroll-behavior:contain}
    #pwToolsFreesound .pwt-summary{padding:5px 1px}
    #pwToolsFreesound .pwt-summary button{white-space:nowrap}
    #pwtManage{box-sizing:border-box;width:min(650px,calc(100vw - 22px));max-height:85dvh;overflow:auto;
      border:7px ridge #b78d67;outline:3px solid #173b54;border-radius:4px;background:#f7f1e6;color:#234254;
      box-shadow:8px 10px 0 #102c3f;padding:17px;font:14px/1.45 system-ui,sans-serif}
    #pwtManage::backdrop{background:#09192bc4}
    #pwtManage .pwt-head{display:flex;align-items:start;justify-content:space-between;gap:12px;border-bottom:3px solid #c5a27c;padding-bottom:11px}
    #pwtManage h2{margin:0 0 4px;font-size:24px;color:#2a5064}
    #pwtManage .pwt-config{display:grid;gap:12px;margin-top:14px}
    #pwtManage .pwt-config label{display:block;font-weight:700}
    #pwtManage input{box-sizing:border-box;width:100%;padding:12px;border:2px solid #a4b5b3;background:white;color:#132f42;font:inherit}
    #pwtManage button{padding:9px 11px;background:#207b9c;color:#fff;border:2px solid #22536b;border-radius:3px;font-weight:700;cursor:pointer}
    #pwtManage button:disabled{opacity:.5}
    #pwtManage .pwt-controls{display:flex;gap:8px;flex-wrap:wrap}
    #pwtManage .pwt-note{font-size:12px;color:#37536a}
    #pwtManage .pwt-state{padding:10px;background:#e5f0e9;border:1px solid #95acaa}
    #pw18Desk .pwt-tool-trace{margin:8px 0;font-size:12px;color:#375669}
    #pw18Desk .pwt-tool-trace li{margin:4px 0}
    #localStudioDialog .pwt-qa{border:2px solid #b79866;background:#e5f1e9;color:#234756;padding:10px 12px;margin:8px 0;font-size:13px}
    #localStudioDialog .pwt-qa strong{display:block;margin-bottom:4px}
    .pwt-heading{margin:8px 0;font-weight:900;font-size:12px;letter-spacing:.08em;color:#a8cfe5}
    @media(max-width:620px){#pwToolsFreesound .pwt-summary{align-items:start}#pw18Desk .pwt-station{padding:7px}#pwtManage{padding:12px}}
  `;
  document.head.append(style);

  const dock = document.querySelector('#dockDialogContent');
  let cfg = null, busy = false;
  const stateLabel = s => !s?.connected ? '⚪ Inte ansluten' : s.verified ? '🟢 Ansluten · Freesound-sökning testad' : '🟡 Nyckel sparad · ej testad';
  const manage = document.createElement('dialog');
  manage.id = 'pwtManage';
  manage.setAttribute('aria-label', 'Freesound – verktygsinställningar');
  manage.innerHTML = `<div class="pwt-head"><div><h2>🧰 Freesound</h2><small>Verktyg · tillgängligt för Musikstudion och Röststudion</small></div><button type="button" id="pwtClose">✕ Stäng</button></div>
    <div class="pwt-config">
      <div class="pwt-state" role="status" id="pwtModalState">Läser anslutning…</div>
      <label>Freesound API-nyckel <input type="password" id="pwtKey" spellcheck="false" autocomplete="off" placeholder="Ange endast vid första anslutning eller byte"></label>
      <div class="pwt-controls"><button type="button" id="pwtSave">💾 Spara nyckel</button><button type="button" id="pwtTest">🧪 Testa anslutning</button><button type="button" id="pwtDisconnect">Koppla från</button></div>
      <p id="pwtFeedback" role="status" aria-live="polite"></p>
      <p class="pwt-note">Anslutningstestet kontrollerar API-åtkomst, inte att varje ljudsökning ger träffar. Sökningar med noll träffar prövas försiktigt med bredare sökord.</p>
      <p class="pwt-note"><strong>Vad används verktyget till?</strong> En godkänd ljudagent kan söka och föreslå högst tre Freesound-ljud inom sin vanliga arbetsorder. Ljudval görs utifrån metadata, inte automatiserad lyssning. Du godkänner alltid import.</p>
      <p class="pwt-note">Privat testläge: ljudförslag filtreras inte efter licens. Källa, upphovsperson och licens sparas för eventuell framtida publicering. Kommersiell API-användning kräver separat Freesound-avtal. Freesounds återstående kvot: <strong>okänd</strong>.</p>
      <p class="pwt-note">ElevenLabs och Suno: inte installerade. Nya verktyg läggs till via serverns verktygsregister – inte som nya anställda.</p>
    </div>`;
  document.body.append(manage);
  manage.querySelector('#pwtClose').onclick = () => manage.close();
  function setFeedback(message, error = false) {
    const label = manage.querySelector('#pwtFeedback');
    if (label) { label.textContent = message; label.style.color = error ? '#ad3636' : '#286549'; }
  }
  function paintStatus() {
    const label = dock?.querySelector('#pwtState');
    if (label) label.textContent = stateLabel(cfg);
    manage.querySelector('#pwtModalState').textContent = stateLabel(cfg) + ' · API-kvot: okänd';
    manage.querySelector('#pwtDisconnect').disabled = !cfg?.connected;
  }
  async function refreshConfig() {
    try { cfg = await api(API + '/status'); paintStatus(); }
    catch (error) { setFeedback('Freesound-servern svarar inte: ' + error.message, true); }
  }
  function injectSettings() {
    if (!dock || !dock.textContent.includes('Inställningar & diagnostik')) return;
    const gemini = dock.querySelector('#pw12SettingsGemini');
    if (gemini && !dock.querySelector('#pwtAiHeading')) {
      const head = document.createElement('div');head.id='pwtAiHeading';head.className='pwt-heading';
      head.textContent='🤖 AI-MOTORER & TOKENS';gemini.before(head);
    }
    const existing = dock.querySelector('#pwToolsFreesound');
    if (existing) {
      const heading = dock.querySelector('#pwtToolHeading');
      if (gemini && heading && heading.previousElementSibling !== gemini) gemini.after(heading, existing);
      return;
    }
    const row = document.createElement('section');
    row.id = 'pwToolsFreesound'; row.className = 'dock-row';
    row.innerHTML = `<div class="pwt-summary"><div><strong>🎧 Freesound · Verktyg</strong><br><span id="pwtState" aria-live="polite">Läser status…</span></div><button type="button" id="pwtExpand">⚙️ Hantera / Testa</button></div>`;
    const heading=document.createElement('div');heading.id='pwtToolHeading';heading.className='pwt-heading';
    heading.textContent='🧰 VERKTYG & API-NYCKLAR';
    const after = gemini || dock.querySelector('#pwtAiHeading');
    if (after) after.after(heading, row);
    else { const local = dock.querySelector('[data-open-local]'); if(local) local.before(heading,row);else dock.append(heading,row); }
    row.querySelector('#pwtExpand').onclick = () => { if (!manage.open) manage.showModal(); refreshConfig(); };
    refreshConfig();
  }
  manage.querySelector('#pwtSave').addEventListener('click', () => changeConfig('connect'));
  manage.querySelector('#pwtTest').addEventListener('click', () => changeConfig('test'));
  manage.querySelector('#pwtDisconnect').addEventListener('click', () => changeConfig('disconnect'));
  async function changeConfig(action) {
    if (busy) return;
    if (action === 'disconnect' && !confirm('Koppla från Freesound? Sparade ljud och tidigare förslag behålls.')) return;
    const field = manage.querySelector('#pwtKey');
    if (action === 'connect' && !field.value.trim()) { setFeedback('Klistra in API-nyckeln först.',true); return; }
    busy = true;
    const buttons = [...manage.querySelectorAll('.pwt-controls button')];
    buttons.forEach(b => b.disabled = true);
    setFeedback(action === 'test' ? 'Kontrollerar med ett riktigt Freesound-anrop…' : 'Sparar…');
    try {
      cfg = await api(API + '/config', action === 'connect' ? {action,api_key:field.value.trim()} : {action});
      field.value = '';
      paintStatus();
      setFeedback(action === 'test' ? '✅ Freesound-sökning verifierad.' : action === 'disconnect' ? 'Freesound frånkopplat.' : '✅ Nyckel sparad. Testa anslutningen innan en agent använder verktyget.');
    } catch (error) { setFeedback('⚠ ' + error.message,true); }
    finally { busy = false; buttons.forEach(b => b.disabled = false); paintStatus(); }
  }
  if (dock) {
    new MutationObserver(injectSettings).observe(dock, {childList:true,subtree:false});
    injectSettings();
  }

  // Result navigation is now shared by music, voice, art, cafe, QA and reports.
  // The global dialog hub owns the SINGLE entry point in each context.
  // Link reports to passive QA handoffs. A completed QA report still requires
  // separate evidence review; never change the core verified flag.
  let reportLookup = 0;
  async function paintQA() {
    const page = document.querySelector('#localStudioDialog[open] .pw-report-detail');
    if (!page || page.querySelector('.pwt-qa')) return;
    const technical = page.querySelector('.pw-report-tech p')?.textContent || '';
    const match = technical.match(/Session:\s*([a-f0-9]{12})/);
    if (!match) return;
    const current = project(), rid = match[1], seq = ++reportLookup;
    const hint = document.createElement('div');hint.className='pwt-qa';
    hint.textContent='🧪 Läser QA-uppföljning…';
    page.querySelector('.pw-detail-badges')?.after(hint);
    try {
      const response = await api('/api/pw-tools/qa?project=' + encodeURIComponent(current) + '&report=' + rid);
      if (seq !== reportLookup || !hint.isConnected || project() !== current) return;
      const qa = response.handoffs?.[0];
      if (!qa) { hint.remove(); return; }
      const label = {waiting:'📋 QA väntar i arbetskön',running:'🧪 QA arbetar',review:'🔎 QA-rapport för granskning',done:'📄 QA avslutad – läs testrapporten',failed:'⚠️ QA misslyckades'};
      hint.innerHTML='<strong>'+esc(label[qa.status] || '🧪 QA-status: '+qa.status)+'</strong><small>Detta är en separat testorder. Kod införd betyder inte verifierad. QA-rapporten måste innehålla verklig test-evidens.</small>';
    } catch (error) { if(hint.isConnected) hint.textContent='QA-status ej tillgänglig: '+error.message; }
  }
  new MutationObserver(paintQA).observe(document.body,{subtree:true,childList:true});
  paintQA();
})();
