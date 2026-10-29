/* Pixel Works cafe UI delta for dev 02de042e: image attachments and explicit start.
   Existing authenticated API handles storage and real conversation execution. */
(() => {
  'use strict';
  if (window.__PW_CAFE_IMAGES__) return;
  window.__PW_CAFE_IMAGES__ = true;

  let box = null, selectedTopic = null, queued = [], forwarding = false;
  let lastMode = '', busy = false, apiWrapped = false, lastSession = null;
  const uploadCache = new WeakMap();
  const MAX_FILES = 2, MAX_BYTES = 3 * 1024 * 1024;
  const types = new Set(['image/png', 'image/jpeg', 'image/webp', 'image/gif']);
  const currentProject = () => window.__PIXEL_WORKS_DEMO__?.model?.activeProjectId || document.querySelector('#projectSelect')?.value;

  function notice(text) {
    const el = box?.querySelector('#pwCafeImageStatus');
    if (el) { el.textContent = text; el.setAttribute('role', 'status'); }
  }
  function cleanFile(file) {
    if (!types.has(file.type)) throw Error('Välj PNG, JPEG, WebP eller GIF.');
    if (file.size < 1 || file.size > MAX_BYTES) throw Error('Bilder får vara högst 3 MB styck.');
    if (queued.length >= MAX_FILES) throw Error('Högst två bilder per inlägg.');
    queued.push(file);
  }
  function addFiles(files) {
    if (busy) return;
    for (const file of [...files]) {
      try { cleanFile(file); } catch (error) { notice(error.message); break; }
    }
    renderFiles();
  }
  function renderFiles() {
    if (!box) return;
    const gallery = box.querySelector('#pwCafeImagePreview');
    if (!gallery) return;
    gallery.replaceChildren();
    queued.forEach((file, index) => {
      const tile = document.createElement('div');
      tile.className = 'pwc-img-tile';
      const img = document.createElement('img');
      const url = URL.createObjectURL(file);
      img.src = url; img.alt = `Förhandsvisning av ${file.name}`;
      img.addEventListener('load', () => URL.revokeObjectURL(url), {once: true});
      img.addEventListener('error', () => URL.revokeObjectURL(url), {once: true});
      const label = document.createElement('span'); label.textContent = file.name;
      const remove = document.createElement('button');
      remove.type = 'button'; remove.textContent = '×'; remove.title = `Ta bort ${file.name}`;
      remove.setAttribute('aria-label', `Ta bort ${file.name}`);
      remove.addEventListener('click', () => { if (!busy) { queued.splice(index, 1); renderFiles(); } });
      tile.append(img, label, remove); gallery.append(tile);
    });
  }
  function imagePicker() {
    const panel = document.createElement('div');
    panel.className = 'pwc-image-panel';
    panel.innerHTML = '<div class="pwc-image-controls"><label class="pwc-file-label">🖼️ Bifoga bild <input type="file" class="pwc-image-input" accept="image/png,image/jpeg,image/webp,image/gif" multiple></label><small>PNG, JPEG, WebP eller GIF · max 2 bilder à 3 MB · klistra även in med Ctrl+V</small></div><div id="pwCafeImagePreview" class="pwc-image-previews" aria-live="polite"></div><p id="pwCafeImageStatus" class="pwc-image-status" aria-live="polite"></p>';
    const picker = panel.querySelector('input');
    picker.addEventListener('change', () => { addFiles(picker.files); picker.value = ''; });
    panel.addEventListener('dragover', event => { event.preventDefault(); panel.classList.add('pwc-drag'); });
    panel.addEventListener('dragleave', () => panel.classList.remove('pwc-drag'));
    panel.addEventListener('drop', event => { event.preventDefault(); panel.classList.remove('pwc-drag'); addFiles(event.dataTransfer?.files || []); });
    return panel;
  }
  const styles = document.createElement('style');
  styles.textContent = `
    #pw138Cafe .pwc-image-panel{border:2px dashed #a1b7a9;background:#f7faf4de;border-radius:5px;padding:9px;margin:10px 0}
    #pw138Cafe .pwc-image-controls{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
    #pw138Cafe .pwc-file-label{display:inline-flex;position:relative;align-items:center;gap:8px;padding:9px 12px;border:2px solid #759c8c;border-radius:4px;background:#fff;color:#205362;font-weight:700;cursor:pointer}
    #pw138Cafe .pwc-file-label:focus-within{outline:3px solid #147cad;outline-offset:2px}
    #pw138Cafe .pwc-image-input{position:absolute;inset:0;width:100%;opacity:0;cursor:pointer}
    #pw138Cafe .pwc-image-controls small{color:#486472;flex:1}
    #pw138Cafe .pwc-image-previews{display:flex;gap:8px;flex-wrap:wrap}
    #pw138Cafe .pwc-img-tile{display:flex;align-items:center;gap:7px;max-width:100%;border:1px solid #aabeb4;background:white;padding:4px;border-radius:5px}
    #pw138Cafe .pwc-img-tile img{height:52px;width:67px;object-fit:contain;background:#e9efef}
    #pw138Cafe .pwc-img-tile span{font-size:11px;max-width:115px;overflow-wrap:anywhere}
    #pw138Cafe .pwc-img-tile button{min-height:30px;padding:3px 8px;color:#943e35}
    #pw138Cafe .pwc-image-status{color:#9a4336;margin:5px 0 0;font-size:12px}
    #pw138Cafe .pwc-topic-picked{background:#d5f0e6;border-color:#2b816a;outline:2px solid #2b816a}
    #pw138Cafe #pwcStartConversation{background:#236d81;color:white;border-color:#184c5c;margin-top:5px}
    #pw138Cafe #pwcStartConversation:disabled{opacity:.55}
  `;
  document.head.append(styles);

  function showSentImages() {
    if (!box?.open || !lastSession || lastSession.project !== currentProject()) return;
    const turns = lastSession.turns || [];
    const bubbles = [...box.querySelectorAll('.pw138-speech')];
    if (!bubbles.length || bubbles.length !== turns.length) return;
    turns.forEach((turn, index) => {
      const ids = turn.image_ids || [];
      const bubble = bubbles[index];
      if (ids.length && !bubble.querySelector('.pwc-sent-images')) {
        const label = document.createElement('small');
        label.className = 'pwc-sent-images';
        label.textContent = '🖼️ ' + ids.length + ' bifogad' + (ids.length === 1 ? ' bild' : 'e bilder') + ' · sparade i spelets bildarkiv';
        bubble.append(label);
      }
    });
  }
  function enhance() {
    box = document.querySelector('#pw138Cafe');
    if (!box || !box.open) return;
    const menuField = box.querySelector('#pw138Note');
    const messageField = box.querySelector('#pw139Owner');
    const mode = menuField ? 'menu' : messageField ? 'message' : 'other';
    if (mode !== lastMode) { lastMode = mode; selectedTopic = null; queued = []; }
    if (mode === 'menu' && !box.querySelector('#pwcStartConversation')) {
      const panel = imagePicker();
      menuField.insertAdjacentElement('afterend', panel);
      const button = document.createElement('button');
      button.type = 'button'; button.id = 'pwcStartConversation';
      button.textContent = '💬 Starta konversation'; button.disabled = true;
      const status = document.createElement('span'); status.className = 'pw138-muted'; status.id = 'pwcSelectedTopic';
      box.querySelector('.pw138-grid')?.insertAdjacentElement('afterend', button);
      button.insertAdjacentElement('afterend', status);
      renderFiles();
    }
    if (mode === 'message' && !box.querySelector('#pwCafeImagePreview')) {
      messageField.insertAdjacentElement('afterend', imagePicker());
      renderFiles();
      const send = box.querySelector('button[data-cafe="speak"]');
      if (send) send.textContent = '💬 Skicka inlägg';
    }
    showSentImages();
  }
  function selectTopic(btn) {
    selectedTopic = btn.dataset.topic;
    box.querySelectorAll('button[data-topic]').forEach(b => {
      b.classList.toggle('pwc-topic-picked', b === btn);
      b.setAttribute('aria-pressed', String(b === btn));
    });
    const start = box.querySelector('#pwcStartConversation');
    if (start) start.disabled = false;
    const label = box.querySelector('#pwcSelectedTopic');
    if (label) label.textContent = ' Vald: ' + btn.querySelector('strong')?.textContent;
    notice('');
  }
  function loadScriptUI() {
    box = document.querySelector('#pw138Cafe');
    if (!box || box.dataset.pwcReady) return;
    box.dataset.pwcReady = '1';
    box.addEventListener('paste', event => {
      if (!box.open) return;
      const files = [...(event.clipboardData?.files || [])].filter(f => types.has(f.type));
      if (files.length) { event.preventDefault(); addFiles(files); }
    });
    box.addEventListener('click', event => {
      const btn = event.target.closest?.('button');
      if (!btn || busy) return;
      if (btn.dataset.topic && !forwarding) {
        event.preventDefault(); event.stopImmediatePropagation(); selectTopic(btn); return;
      }
      if (btn.id === 'pwcStartConversation') {
        event.preventDefault(); event.stopImmediatePropagation();
        const chosen = box.querySelector(`button[data-topic="${selectedTopic || ''}"]`);
        if (!chosen) return;
        forwarding = true;
        try { chosen.click(); } finally { forwarding = false; }
        return;
      }
      if (btn.dataset.cafe === 'speak' && queued.length) {
        const field = box.querySelector('#pw139Owner');
        if (field && field.value.trim().length < 2) {
          field.value = 'Titta på de bifogade bilderna och kommentera dem.';
          field.dispatchEvent(new Event('input', {bubbles: true}));
        }
      }
    }, true);
  }
  const encode = file => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).split(',')[1]);
    reader.onerror = () => reject(Error('Kunde inte läsa ' + file.name));
    reader.readAsDataURL(file);
  });
  async function upload(native, slug, files) {
    const ids = [];
    for (const file of files) {
      if (slug !== currentProject()) throw Error('Projektet ändrades. Bildbilagorna skickades inte.');
      const cached = uploadCache.get(file);
      if (cached?.project === slug) { ids.push(cached.id); continue; }
      const data = await encode(file);
      const saved = await native('/api/projects/' + encodeURIComponent(slug) + '/assets', {
        kind: 'file', name: file.name, station: 'meeting',
        comment: 'Bild bifogad i Fikarummet av spelägaren.', data
      });
      if (!saved?.asset?.id) throw Error('Servern sparade inte bilden.');
      uploadCache.set(file, {project: slug, id: saved.asset.id});
      ids.push(saved.asset.id);
    }
    return ids;
  }
  function recordSession(data) {
    if (data?.session?.id) {
      lastSession = data.session;
      queueMicrotask(showSentImages);
    }
    return data;
  }
  function wrapApi() {
    if (apiWrapped || typeof window.pixelWorksApi !== 'function') return;
    const native = window.pixelWorksApi;
    window.pixelWorksApi = async (path, payload) => {
      if (path !== '/api/pw-v0138/cafe' || !payload ||
          !(!payload.action || payload.action === 'message') || !queued.length) {
        const result = await native(path, payload);
        return path.startsWith('/api/pw-v0138/cafe') ? recordSession(result) : result;
      }
      if (busy) throw Error('Bildöverföringen pågår redan.');
      const files = [...queued], slug = payload.project;
      busy = true;
      notice('Laddar upp bilder till det valda spelet…');
      try {
        const ids = await upload(native, slug, files);
        const result = await native(path, {...payload, attachment_ids: ids});
        queued = []; notice('');
        return recordSession(result);
      } catch (error) {
        notice('Bilderna kunde inte skickas: ' + error.message);
        throw error;
      } finally { busy = false; }
    };
    apiWrapped = true;
  }
  const observer = new MutationObserver(() => { loadScriptUI(); enhance(); wrapApi(); });
  observer.observe(document.body, {subtree: true, childList: true});
  const check = setInterval(() => { loadScriptUI(); wrapApi(); if (apiWrapped && box) clearInterval(check); }, 200);
  setTimeout(() => clearInterval(check), 30000);
})();
