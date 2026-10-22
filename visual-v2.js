// Optional HUD-only layer: all existing server and gameplay actions stay with Pixel Works.
const dock = document.querySelector('#gameDock');
const dockDialog = document.querySelector('#dockDialog');
const dockContent = document.querySelector('#dockDialogContent');
const model = window.__PIXEL_WORKS_DEMO__?.model;
const ui = window.__PIXEL_WORKS_DEMO__?.ui;
const escapeHtml = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
// The top navigation reflects the currently open view, not the last clicked button.
function setDockActive(name='office') {
  dock?.querySelectorAll('.dock-item').forEach(button=>{
    const isActive=button.dataset.dock===name;
    button.classList.toggle('active',isActive);
    if(isActive)button.setAttribute('aria-current','page');
    else button.removeAttribute('aria-current');
  });
}
window.pixelWorksResetDock=()=>setDockActive('office');
function showDock(title, content) {
  dockDialog.classList?.toggle('pw-whiteboard-dialog',title.includes('Arbetsorder')||title.includes('Demo-uppdrag'));
  dockDialog.classList?.toggle('pw-staff-board-dialog',title.includes('Agenter')||title.includes('Personal'));
  dockContent.innerHTML = `<h2>${escapeHtml(title)}</h2><div>${content}</div><p class="dock-muted">Fakta kommer från valt projekt. Simulering är märkt som demo.</p><button type="button" class="dock-close" data-close>Stäng</button>`;
  dockContent.querySelector('[data-close]').addEventListener('click',()=>dockDialog.close());
  if (!dockDialog.open) dockDialog.showModal();
}
async function showOrders() {
  const slug = document.querySelector('#projectSelect')?.value;
  if(document.body.classList.contains('live-project') && window.pixelWorksApi && slug) {
    try {
      const {orders=[]} = await window.pixelWorksApi(`/api/projects/${encodeURIComponent(slug)}/orders`);
      // Real work orders, not the legacy demo mission cards. Superseded and
      // completed orders stay in each desk's history, never in the active list.
      const inactive=new Set(['done','superseded','archived','cancelled','rejected']);
      const active=orders.filter(o=>!inactive.has(o.status));
      const statusLabel={waiting:'Väntar på anställd',claimed:'Tilldelad',running:'Arbete pågår',review:'Behöver granskning',failed:'Behöver hjälp'};
      const waiting=active.filter(o=>o.status==='waiting').length;
      showDock(`📋 Arbetsorder (${active.length})`, `<p class="dock-muted">${waiting} väntar vid skrivbord · ${active.length-waiting} pågår eller behöver följas upp. Färdiga och ersatta jobb finns i historiken vid respektive bord.</p>` + (active.length ? active.slice(0,25).map(o=>`<div class="dock-row"><div><b>${escapeHtml(o.instruction?.slice(0,90)||'Arbetsorder')}</b><div class="dock-muted">${escapeHtml(o.station)} · ${escapeHtml(statusLabel[o.status]||o.status)}</div></div><button type="button" data-station="${escapeHtml(o.station)}">Visa arbetskö</button></div>`).join('') : '<p>Inga aktiva arbetsorder.</p>'));
      dockContent.querySelectorAll('[data-station]').forEach(b=>b.onclick=()=>{
        // Open the actual server-backed desk queue, not its "create new task" menu.
        // On a real project we must not fall back to the simulated board.
        dockDialog.close();
        window.pixelWorksStationOrders?.(slug,b.dataset.station,false,true);
      });
    } catch(e) { showDock('Arbetsorder',`<p>Kunde inte läsa arbetsorder: ${escapeHtml(e.message)}</p>`); }
  } else if(model) {
    const tasks=model.project.tasks || [];
    showDock('📋 Demo-uppdrag',tasks.map(t=>`<div class="dock-row"><div><b>${escapeHtml(t.title)}</b><div class="dock-muted">DEMO · ${escapeHtml(t.status)}</div></div></div>`).join('')||'Inga uppdrag ännu.');
  }
}
dock?.addEventListener('click', async e => {
  const button=e.target.closest('[data-dock]'); if(!button)return;
  const name=button.dataset.dock;
  setDockActive(name);
  switch(name){
    case 'office': dockDialog.open&&dockDialog.close();ui?.closeDrawer();break;
    case 'play': {
      // Reuse the real preview handler rather than inventing a demo or alternate URL.
      // A blocked pop-up is handled by the existing Pixel Works preview flow.
      const trigger=document.querySelector('#playProjectBtn');
      if(trigger)trigger.click();
      else console.warn('Spelpreview är ännu inte tillgänglig.');
      setDockActive('office');
      break;
    }
    case 'agents':document.querySelector('#hireBtn')?.click();break;
    case 'orders':await showOrders();break;
    case 'projects': {
      const options=[...document.querySelector('#projectSelect').options];
      showDock('📁 Välj spelprojekt',options.map(o=>`<div class="dock-row"><b>${escapeHtml(o.textContent)}</b><button type="button" data-project="${escapeHtml(o.value)}">Öppna</button></div>`).join('') + `<div class="dock-row"><button type="button" data-new-project>➕ Ny produktion</button><button type="button" data-delete-project>🗑 Ta bort valt projekt</button></div>`);
      dockContent.querySelector('[data-new-project]')?.addEventListener('click',()=>{dockDialog.close();document.querySelector('#newProjectBtn')?.click()});
      dockContent.querySelector('[data-delete-project]')?.addEventListener('click',()=>{dockDialog.close();document.querySelector('#removeProjectBtn')?.click()});
      dockContent.querySelectorAll('[data-project]').forEach(b=>b.onclick=()=>{const select=document.querySelector('#projectSelect');select.value=b.dataset.project;select.dispatchEvent(new Event('change',{bubbles:true}));dockDialog.close()});break;
    }
    case 'events': {
      const entries=[...document.querySelectorAll('.right-rail .real-job-events .real-event, .right-rail .event-feed .event-row')].slice(-25);
      showDock('🗄️ Händelser',entries.length?entries.map(row=>`<div class="dock-row">${escapeHtml(row.textContent.trim())}</div>`).join(''):'<p>Inga händelser att visa ännu.</p>');
      break;
    }
    case 'findings':document.querySelector('#deskBtn')?.click();break;
    case 'stats':document.querySelector('#officeBoard')?.click();break;
    case 'settings': {const codex=document.querySelector('#agentModeBadge')?.textContent?.trim()||'Ingen anslutningsstatus';const storage=document.querySelector('#storageLiveStatus')?.textContent?.trim()||'Ej kontrollerad';showDock('⚙️ Inställningar & diagnostik',`<div class="dock-row"><b>AI-motor</b><span>${escapeHtml(codex)}</span></div><div class="dock-row"><b>Lagring</b><span>${escapeHtml(storage)}</span></div><p class="dock-muted">Verklig AI-kvot visas först när leverantören tillhandahåller verifierad data.</p><button type="button" data-open-local>Öppna lokal studio</button>`);dockContent.querySelector('[data-open-local]').addEventListener('click',()=>{dockDialog.close();(document.querySelector('#localStudioBtn')||document.querySelector('#studioBtn'))?.click()});break;}
  }
});
dockDialog?.addEventListener('click',e=>{if(e.target===dockDialog)dockDialog.close()});
// Closing any menu with the X, Escape, overlay click or a command returns to Kontor.
// Works for dock menus, the older station dialog, personnel and project dialogs.
for (const id of ['dockDialog','localStudioDialog','gameDialog','taskDialog']) {
  document.querySelector('#'+id)?.addEventListener('close',()=>setDockActive('office'));
}

