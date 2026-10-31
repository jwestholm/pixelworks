/* Pixel Works · provider presence v1.9
   A real Gemini API pause is an agent availability state, not a game task.
   Uses only the existing server-backed /api/providers endpoint; no AI requests.
   Temporary network/API failures differ from quota stops. No invented reset.
*/
(() => {
  'use strict';
  if (window.__PW_PROVIDER_PRESENCE__) return;
  window.__PW_PROVIDER_PRESENCE__ = true;

  const POLL_MS = 12000;
  let latest = null, lastSignature = '', busy = false, timer = null;
  let lastProject = '', appliedState = '';
  const assignedBlocks = new Set();
  const host = document.querySelector('.right-rail .event-panel') || document.querySelector('.right-rail');
  const panel = document.createElement('section');
  panel.id = 'pwProviderPresence';
  panel.hidden = true;
  panel.setAttribute('aria-label', 'AI-personalens tillgänglighet');
  panel.innerHTML = '<div class="pwpp-heading">👥 Personalläge <span class="pwpp-tag">VERIFIERAD API-STATUS</span></div><p class="pwpp-message"></p><div class="pwpp-actions"><button type="button" id="pwppGeminiSettings">⚙ Gemini-inställningar</button></div>';
  if (host) host.insertBefore(panel, host.querySelector('#eventFeed') || null);

  const css = document.createElement('style');
  css.textContent = `
    #pwProviderPresence[hidden]{display:none!important}
    #pwProviderPresence{flex:0 0 auto;border:2px solid #97764d;background:#fff0c7;color:#23354a;padding:10px 12px;font:600 12px/1.45 system-ui,sans-serif;box-sizing:border-box}
    #pwProviderPresence.pwpp-api{background:#fff2d7;border-color:#9e7945}
    #pwProviderPresence.pwpp-quota{background:#f8e0b2;border-color:#a96735}
    #pwProviderPresence .pwpp-heading{font-weight:900;font-size:13px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
    #pwProviderPresence .pwpp-tag{font:700 9px system-ui,sans-serif;letter-spacing:.03em;color:#29485b;background:#e5f0ee;border:1px solid #91a9a6;padding:2px 4px}
    #pwProviderPresence .pwpp-message{margin:7px 0;color:#243a4e;overflow-wrap:anywhere}
    #pwProviderPresence .pwpp-actions{display:flex;gap:6px;flex-wrap:wrap}
    #pwProviderPresence button{background:#2c5872;border:2px solid #1a3a54;color:#fff;min-height:35px;padding:5px 10px;font:700 11px system-ui,sans-serif;cursor:pointer}
    #pwProviderPresence button:focus-visible{outline:3px solid #cc7629;outline-offset:2px}
    #agentLayer .agent.pwpp-home{opacity:0!important;visibility:hidden!important;pointer-events:none!important;transition:opacity .35s ease, visibility .35s}
    #agentLayer .agent.pwpp-cafe{filter:grayscale(.32);transition:left .65s ease,top .65s ease}
    #agentLayer .agent .pwpp-bubble{position:absolute;z-index:80;left:50%;top:-52px;transform:translateX(-50%);min-width:110px;max-width:175px;border:2px solid #765c3b;background:#fff1c5;color:#24374a;padding:4px 6px;box-shadow:2px 2px 0 #3c3344;font:900 10px/1.3 system-ui,sans-serif;text-align:center;pointer-events:none;white-space:normal}
    #agentDrawerContent .pwpp-drawer-note{border:2px solid #8e764e;background:#fff0ce;color:#25384a;font:700 12px/1.4 system-ui,sans-serif;padding:9px;margin:8px 0;overflow-wrap:anywhere}
    @media(max-width:700px){#pwProviderPresence{padding:8px;font-size:11px}}
    @media(prefers-reduced-motion:reduce){#agentLayer .agent.pwpp-home,#agentLayer .agent.pwpp-cafe{transition:none}}
  `;
  document.head.append(css);

  function mode(status) {
    if (!status || typeof status !== 'object') return null;
    if (status.can_send === true && status.execution_enabled === true) return 'ready';
    const quotaPattern = /\b429\b|kvot|quota|rate.limit|per.day|rpd\b|tpm\b|rpm\b/i;
    const apiPattern = /\b50[0-4]\b|anslutningsfel|timeout|nätverk|network|unavailable|overload|tillfäll/i;
    // The newest pause reason takes precedence over an older connection test.
    const pause = String(status.pause_reason || '');
    if (pause && apiPattern.test(pause)) return 'api';
    if (pause && quotaPattern.test(pause)) return 'quota';
    const test = String(status.test_result || '');
    if (quotaPattern.test(test)) return 'quota';
    if (apiPattern.test(test)) return 'api';
    return status.configured ? 'unavailable' : 'missing';
  }
  const titleFor = (state) => ({
    quota:'🏠 Gick hem – Gemini-kvot/API-gräns',
    api:'☕ Paus i fikarummet – Gemini svarar inte',
    unavailable:'⏸ Kan inte arbeta – Gemini ej verifierad',
    missing:'⏸ Kan inte arbeta – Gemini-nyckel saknas'
  })[state] || '';
  const reasonFor = (state, data, names) => {
    const who = names.join(', ');
    if (state === 'quota') return `${who} tar inga nya uppdrag. Google har rapporterat en kvot-/hastighetsgräns. Vi vet inte när kvoten återställs; inga påhittade tokenvärden visas.`;
    if (state === 'api') return `${who} kan inte arbeta just nu eftersom Gemini har ett API-/anslutningsfel. Tillfällig paus – inte bevis för att kvoten är slut. Kontrollera anslutningen senare.`;
    if (state === 'missing') return `${who} kan inte ta uppdrag eftersom Gemini saknar en sparad nyckel.`;
    return `${who} kan inte ta uppdrag förrän Gemini åter är verifierad och tillgänglig.`;
  };
  const runtime = () => window.__PIXEL_WORKS_DEMO__ || null;
  const current = () => runtime()?.model?.project || null;
  const activeSlug = () => runtime()?.model?.activeProjectId || '';
  const geminiStaff = project => (project?.agents || []).filter(a => a.provider === 'gemini');
  const identifier = (slug, id) => `${slug}:${id}`;

  function reconcileModel(state, data) {
    const r = runtime(), project = current();
    if (!r || !project?.live) return;
    for (const p of r.model.projects || []) {
      if (!p.live) continue;
      const provider = p.providers?.gemini;
      if (provider) {
        provider.engineState = state === 'ready' ? 'TEXTSVAR TESTAT' :
          state === 'quota' ? 'KVOT-/API-GRÄNS · PAUS' :
          state === 'api' ? 'API-FEL · KAN INTE ARBETA' : 'KAN INTE ARBETA';
        provider.quota = 'okänt';
      }
      for (const agent of geminiStaff(p)) {
        agent.engineAvailable = state === 'ready';
        const key = identifier(p.id, agent.id);
        if (state !== 'ready' && agent.status !== 'working') {
          // Only UI availability. Never change server staff files or active work.
          agent.status = 'blocked';
          assignedBlocks.add(key);
        } else if (state === 'ready' && assignedBlocks.has(key)) {
          if (agent.status === 'blocked') agent.status = 'idle';
          assignedBlocks.delete(key);
        }
      }
    }
  }

  function decorate() {
    const r = runtime(), project = current();
    if (!r || !project?.live) { panel.hidden = true; return; }
    const staff = geminiStaff(project);
    if (!staff.length) { panel.hidden = true; return; }
    const state = mode(latest);
    if (!state) { panel.hidden = true; return; }
    const disabled = state !== 'ready';
    panel.hidden = !disabled;
    if (disabled) {
      panel.classList.toggle('pwpp-quota', state === 'quota');
      panel.classList.toggle('pwpp-api', state === 'api');
      panel.querySelector('.pwpp-heading').firstChild.textContent = titleFor(state) + ' ';
      panel.querySelector('.pwpp-message').textContent = reasonFor(state, latest, staff.map(a => a.name));
    }
    for (const agent of staff) {
      const node = [...document.querySelectorAll('#agentLayer .agent')].find(n => n.dataset.id === String(agent.id));
      if (!node) continue;
      const activelyWorking = agent.status === 'working';
      const home = state === 'quota' && !activelyWorking;
      const cafe = state === 'api' && !activelyWorking;
      node.classList.toggle('pwpp-home', home);
      node.classList.toggle('pwpp-cafe', cafe);
      if (disabled && !activelyWorking) {
        node.classList.remove('idle','working'); node.classList.add('blocked');
        const label = state === 'quota' ? '🏠 Gick hem · kvot' : state === 'api' ? '☕ API-paus' : '⏸ Kan inte arbeta';
        node.setAttribute('aria-label', `${agent.name}, ${label}`);
        node.title = `${agent.name}: ${label}. Detta är verklig leverantörsstatus, inte en AI-replik.`;
        if (cafe) {
          const table = r.model.getStation?.('cafe');
          if (table && !r.ui.walks?.has(agent.id)) {
            node.style.left = `${table.x}%`;
            node.style.top = `${table.y + 8}%`;
          }
        }
        let note = node.querySelector('.pwpp-bubble');
        if (!home) {
          if (!note) { note = document.createElement('span'); note.className = 'pwpp-bubble'; node.append(note); }
          note.textContent = state === 'api' ? '☕ Kan inte arbeta · API-paus' : '⏸ Kan inte arbeta';
        } else if (note) note.remove();
      } else {
        node.querySelector('.pwpp-bubble')?.remove();
        node.classList.remove('pwpp-home','pwpp-cafe');
        node.title = agent.role || '';
      }
    }
    const drawer = document.querySelector('#agentDrawerContent');
    drawer?.querySelector('.pwpp-drawer-note')?.remove();
    if (disabled && drawer && r.ui.selectedAgentId && staff.some(a => a.id === r.ui.selectedAgentId)) {
      const note = document.createElement('div');
      note.className = 'pwpp-drawer-note'; note.setAttribute('role','status');
      note.textContent = reasonFor(state, latest, staff.filter(a => a.id === r.ui.selectedAgentId).map(a => a.name));
      drawer.querySelector('.agent-detail-head')?.after(note);
    }
  }

  function patchUI() {
    const r = runtime();
    if (!r?.ui || r.ui.__PW_PROVIDER_PRESENCE__) return;
    const ui = r.ui;
    ui.__PW_PROVIDER_PRESENCE__ = true;
    const render = ui.renderAgents.bind(ui);
    ui.renderAgents = function(...args) {
      const state = mode(latest);
      if (state) reconcileModel(state, latest);
      const result = render(...args);
      decorate();
      return result;
    };
    const renderDrawer = ui.renderDrawer.bind(ui);
    ui.renderDrawer = function(...args) {
      const result = renderDrawer(...args);
      decorate();
      return result;
    };
  }

  function apply(data) {
    latest = data;
    patchUI();
    const r = runtime(), project = current();
    if (!r || !project?.live) return;
    const state = mode(data);
    if (!state) return;
    reconcileModel(state, data);
    r.ui.renderAgents();
    if (r.ui.selectedAgentId && geminiStaff(project).some(a => a.id === r.ui.selectedAgentId)) r.ui.renderDrawer(r.model.getAgent(r.ui.selectedAgentId));
    const slug = activeSlug();
    const signature = slug + ':' + state;
    if (signature !== lastSignature) {
      // One actionable notification per real status transition; never a fabricated AI message.
      if (lastSignature && slug === lastProject) {
        const names = geminiStaff(project).map(a => a.name).join(', ');
        r.ui.toast?.(state === 'ready' ? `${names} kan ta uppdrag igen · Gemini verifierad` :
          state === 'quota' ? `${names} gick hem · Gemini-kvot/API-gräns` :
          `${names} kan inte arbeta just nu · Gemini-status: ${state === 'api' ? 'API-fel' : 'ej verifierad'}`);
      }
      lastSignature = signature;
    }
    lastProject = slug;
  }

  async function poll() {
    if (busy || document.hidden) return;
    busy = true;
    try {
      const response = await fetch('/api/providers', {credentials:'same-origin', cache:'no-store'});
      if (!response.ok) throw Error('API-status kan inte läsas');
      const data = await response.json();
      const status = data?.providers?.gemini;
      if (status && typeof status.can_send === 'boolean') apply(status);
    } catch (_error) {
      // Never infer provider availability from a failed local status request.
      if (!latest && panel) panel.hidden = true;
    } finally { busy = false; }
  }

  panel.querySelector('#pwppGeminiSettings').addEventListener('click', () => {
    const open = window.pixelWorksAISettingsV01210;
    if (typeof open === 'function') open('ai');
    else document.querySelector('#settingsBtn')?.click();
  });
  window.addEventListener('pixelworks:project-changed', () => {
    lastProject = activeSlug();
    patchUI(); decorate(); poll();
  });
  window.addEventListener('pixelworks:gemini-token-changed', poll);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) poll(); });
  const start = setInterval(() => {
    if (!runtime()) return;
    patchUI(); clearInterval(start);
    poll();
    timer = setInterval(poll, POLL_MS);
  }, 250);
  // Exposed for local regression tests and settings refresh, not AI execution.
  window.pixelWorksRefreshProviderPresence = poll;
})();
