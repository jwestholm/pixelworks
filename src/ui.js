import { planRoute, furnitureObstacles, destinationForStation } from './navigation.js';
const STATUS_LABELS = { idle:'LEDIG', working:'ARBETAR', blocked:'BLOCKERAD', done:'KLAR' };
const STATUS_COLORS = { idle:'#70a8ff', working:'#72df8d', blocked:'#ff6b6b', done:'#ffd45e' };
const EVENT_COLORS = { TASK_ASSIGNED:'#ff78b7', TASK_STARTED:'#65e8d8', AGENT_MESSAGE:'#70a8ff', FINDING_REPORTED:'#ae83ff', RESULT_VERIFIED:'#72df8d', TASK_COMPLETED:'#ffd45e', TASK_FAILED:'#ff6b6b', AGENT_IDLE:'#8e88a8' };
const skillName = { planning:'Planering', review:'Granskning', documentation:'Dokumentation', coding:'Kodning', testing:'Testning', research:'Research',music:'Musik',voice:'Röst',art:'Grafik' };
const taskStatusLabel = { todo:'TODO', working:'PÅGÅR', review:'GRANSKAS', done:'KLAR' };

export class GameUI {
  constructor(model) {
    this.model = model;
    this.selectedAgentId = null;
    this.drag = null;
    this.walks = new Map();
    this.routeSnapshot = new Map();
    this.lastFrame = 0;
    this.animFrame = null;
    this.nodes = {
      projectSelect: document.querySelector('#projectSelect'), projectTitle: document.querySelector('#projectTitle'), projectGoal: document.querySelector('#projectGoal'),
      stationLayer: document.querySelector('#stationLayer'), agentLayer: document.querySelector('#agentLayer'), fxLayer: document.querySelector('#fxLayer'), officeStage: document.querySelector('#officeStage'),
      taskList: document.querySelector('#taskList'), leadStrip: document.querySelector('#leadStrip'), eventFeed: document.querySelector('#eventFeed'),
      drawer: document.querySelector('#agentDrawer'), drawerContent: document.querySelector('#agentDrawerContent'), taskDialog: document.querySelector('#taskDialog'), taskAssignee: document.querySelector('#taskAssignee'),
      toastLayer: document.querySelector('#toastLayer'), pauseBtn: document.querySelector('#pauseSimBtn')
    };
    this.callbacks = {};
  }

  bind(callbacks) {
    this.callbacks = callbacks;
    this.nodes.projectSelect.addEventListener('change', e => callbacks.onProjectChange?.(e.target.value));
    document.querySelector('#newTaskBtn')?.addEventListener('click', () => this.openTaskDialog());
    document.querySelector('#closeDrawerBtn').addEventListener('click', () => this.closeDrawer());
    document.querySelector('#clearEventsBtn').addEventListener('click', () => callbacks.onClearEvents?.());
    this.nodes.pauseBtn.addEventListener('click', () => callbacks.onToggleSimulation?.());
    document.querySelector('#taskForm').addEventListener('submit', e => {
      e.preventDefault();
      const fd = new FormData(e.currentTarget);
      callbacks.onCreateTask?.(Object.fromEntries(fd.entries()));
      this.nodes.taskDialog.close();
      e.currentTarget.reset();
    });
  }

  renderAll() {
    this.renderProjectSwitcher(); this.renderProjectHeader(); this.renderStations(); this.renderAgents(); this.renderLead(); this.renderTasks(); this.renderEvents(); this.renderTaskAssignees();
    if (this.selectedAgentId) {
      const stillThere = this.model.getAgent(this.selectedAgentId);
      stillThere ? this.renderDrawer(stillThere) : this.closeDrawer();
    }
  }

  renderProjectSwitcher() {
    const current = this.model.activeProjectId;
    this.nodes.projectSelect.innerHTML = this.model.projects.map(p => `<option value="${p.id}" ${p.id===current?'selected':''}>${escapeHTML(p.title)}</option>`).join('');
  }
  renderProjectHeader() { this.nodes.projectTitle.textContent = this.model.project.title; this.nodes.projectGoal.textContent = this.model.project.goal;const room=this.nodes.officeStage;const n=this.model.projects.findIndex(x=>x.id===this.model.activeProjectId);room.dataset.room=String(n%4);let sign=room.querySelector('.project-wallboard');if(!sign){sign=document.createElement('div');sign.className='project-wallboard';room.appendChild(sign);}sign.textContent=this.model.project.title.toUpperCase()+(this.model.project.live?' · SKARPT':' · DEMO');document.body.classList.toggle('live-project',!!this.model.project.live); }

  renderStations() {
    this.nodes.stationLayer.innerHTML = this.model.stations.map(station => `
      <div class="station" role="button" tabindex="0" aria-label="Öppna ${station.name}" data-id="${station.id}" data-type="${station.type}" style="left:${station.x}%;top:${station.y}%;--station-color:${station.color}" title="${station.name}">
        <div class="station-base"></div><div class="station-top"></div><div class="station-screen"></div><div class="station-chair"></div><div class="station-instrument"></div><div class="station-accessory"></div><div class="station-label">${station.short}</div><span class="station-worker" hidden></span>
      </div>`).join('');
    this.nodes.stationLayer.querySelectorAll('.station').forEach(node=>{
      const open=()=>this.callbacks?.onStationClick?.(node.dataset.id);
      node.addEventListener('click',open);
      node.addEventListener('keydown',event=>{
        if(event.key==='Enter'||event.key===' '){event.preventDefault();open();}
      });
    });
  }

  renderAgents() {
    const existing = new Map([...this.nodes.agentLayer.querySelectorAll(".agent")].map(n=>[n.dataset.id,n]));
    for(const [id,node] of existing)if(!this.model.getAgent(id)){node.remove();this.walks.delete(id);}
    for(const agent of this.model.project.agents){
      let node=existing.get(agent.id);
      if(!node){this.nodes.agentLayer.insertAdjacentHTML("beforeend",this.agentHTML(agent));node=this.nodes.agentLayer.lastElementChild;}
      // Deterministic per-agent phase: agents must not blink, sip coffee or
      // work in perfect sync. Keep it stable across render/poll cycles.
      const phaseKey=String(this.model.activeProjectId||'')+':'+String(agent.id);
      let phaseHash=2166136261;
      for(let k=0;k<phaseKey.length;k++)phaseHash=Math.imul(phaseHash^phaseKey.charCodeAt(k),16777619)>>>0;
      const phaseSeconds=((phaseHash%379)/100).toFixed(2);
      node.style.setProperty('--pw-anim-phase',`-${phaseSeconds}s`);
      if(!this.walks.has(agent.id) && this.drag?.id!==agent.id){node.style.left=`${agent.x}%`;node.style.top=`${agent.y}%`;}
      node.classList.toggle("walking",this.walks.has(agent.id));
      for(const state of ['idle','working','blocked','done']) node.classList.toggle(state,agent.status===state);
      for(const activity of ['code','lead','research','qa','cafe','meeting','docs','voice','music','art']) node.classList.toggle('activity-'+activity,(agent.activity||agent.station)===activity);
      node.setAttribute('aria-label',`${agent.name}, ${agent.role}, ${STATUS_LABELS[agent.status]||'OKÄND'}`);
    }
    // Show the name of a *real assigned worker*, never guess from the desk's
    // profession or from how close a sprite happens to be. Simulated projects
    // use their own explicitly simulated worker state.
    for(const station of this.nodes.stationLayer?.querySelectorAll('.station') || []){
      const badge=station.querySelector('.station-worker');
      if(!badge)continue;
      const workers=this.model.project.agents.filter(agent=>
        agent.station===station.dataset.id && agent.status==='working' &&
        !this.walks.has(agent.id));
      const first=workers[0];
      badge.hidden=!first;
      badge.textContent=first ? `● ${first.name}${workers.length>1?` +${workers.length-1}`:''}` : '';
      badge.title=first ? `${workers.map(a=>a.name).join(', ')} arbetar här${this.model.project.live?'':' (demo)'}` : '';
    }
    this.nodes.agentLayer.querySelectorAll('.agent').forEach(node => {
      if (node.dataset.bound) return;
      node.dataset.bound = '1';
      node.addEventListener('click', e => {
        if (node.dataset.wasDragged === '1') { node.dataset.wasDragged='0'; return; }
        this.selectAgent(node.dataset.id);
      });
      node.addEventListener('pointerdown', e => this.startDrag(e, node));
    });
  }

  // Transition to a work location using collision-aware waypoints. Visual movement never runs Codex.
  walkTo(agentId, stationId, after) {
    const agent=this.model.getAgent(agentId),station=this.model.getStation(stationId);
    if(!agent||!station)return false;
    const node=this.nodes.agentLayer.querySelector(`[data-id="${CSS.escape(agentId)}"]`);
    if(!node)return false;
    const stage=this.nodes.officeStage;
    const obstacles=furnitureObstacles(stage,this.nodes.stationLayer.querySelectorAll('.station'));
    const start={x:parseFloat(node.style.left)||agent.x,y:parseFloat(node.style.top)||agent.y};
    const seat=this.model.project.agents.filter(a=>a.id!==agentId&&a.station===stationId).length;
    const destination=destinationForStation(station,seat);
    const path=planRoute(start,destination,obstacles);
    if(!path.length){this.toast('Ingen fri gångväg till stationen.');return false;}
    this.walks.set(agentId,{path,index:0,x:start.x,y:start.y,after,project:this.model.activeProjectId});
    node.classList.add('walking');this.animateWalks();return true;
  }
  animateWalks(){
    if(this.animFrame)return;
    const step=(stamp)=>{
      const dt=Math.min(0.065,Math.max(0.01,(stamp-(this.lastFrame||stamp))/1000));this.lastFrame=stamp;
      for(const [id,w] of [...this.walks]){
        if(w.project!==this.model.activeProjectId){this.walks.delete(id);continue;}
        const node=[...this.nodes.agentLayer.querySelectorAll('.agent')].find(n=>n.dataset.id===id);
        if(!node){this.walks.delete(id);continue;}
        let budget=16*dt; // percentage points per second, consistent across screen sizes
        while(budget>0 && w.index<w.path.length){const next=w.path[w.index],dx=next.x-w.x,dy=next.y-w.y,dist=Math.hypot(dx,dy);if(dist<=budget){w.x=next.x;w.y=next.y;budget-=dist;w.index++;}else{w.x+=dx/dist*budget;w.y+=dy/dist*budget;budget=0;}}
        node.style.left=w.x+'%';node.style.top=w.y+'%';
        if(w.index>=w.path.length){this.walks.delete(id);node.classList.remove('walking');const agent=this.model.getAgent(id);if(agent){agent.x=w.x;agent.y=w.y;}w.after?.();}
      }
      if(this.walks.size){this.animFrame=requestAnimationFrame(step);}else{this.animFrame=null;this.lastFrame=0;}
    };this.animFrame=requestAnimationFrame(step);
  }
  resetWalks(){this.walks.clear();if(this.animFrame)cancelAnimationFrame(this.animFrame);this.animFrame=null;this.lastFrame=0;}

  agentHTML(agent) {
    // Visual profession is independent of provider/skills. Cosmetic variants are stable per employee.
    const roleType = String(agent.role_type || agent.role || '').toLowerCase();
    const roleKey = roleType.includes('lead') || roleType.includes('arbetsled') || roleType.includes('projektled') ? 'lead'
      : roleType.includes('qa') || roleType.includes('test') ? 'qa'
      : roleType.includes('artist') || roleType.includes('grafik') || roleType.includes('designer') ? 'artist'
      : roleType.includes('music') || roleType.includes('musik') ? 'musician'
      : roleType.includes('voice') || roleType.includes('röst') ? 'voice'
      : roleType.includes('research') || roleType.includes('forsk') ? 'research'
      : roleType.includes('writer') || roleType.includes('creative') || roleType.includes('story') || roleType.includes('dokument') ? 'writer'
      : roleType.includes('program') || roleType.includes('utveckl') || roleType.includes('kod') ? 'programmer' : 'allround';
    const stableHash = [...String(agent.id || agent.name)].reduce((n,ch)=>((n*31+ch.charCodeAt(0))>>>0),7);
    // Future profile may set appearance_variant explicitly: 0/2 masculine, 1/3 feminine illustration families.
    const preferredVariant = Number(agent.appearance_variant);
    const spriteVariant = agent.appearance_variant !== undefined && Number.isInteger(preferredVariant) && preferredVariant >= 0 && preferredVariant < 4 ? preferredVariant : stableHash % 4;
    return `<div title="${escapeHTML(agent.role)}" class="agent sprite-role-${roleKey} sprite-variant-${spriteVariant} activity-${agent.activity||agent.station} ${agent.status} ${this.selectedAgentId===agent.id?'selected':''}" data-id="${agent.id}" style="left:${agent.x}%;top:${agent.y}%;--agent-color:${agent.color};--hair:${agent.hair};--status-color:${STATUS_COLORS[agent.status] || STATUS_COLORS.idle}" aria-label="${escapeHTML(agent.name)}, ${escapeHTML(agent.role)}, ${STATUS_LABELS[agent.status]}">
      <div class="agent-name">${escapeHTML(agent.name)}</div><div class="agent-shadow"></div><div class="agent-body"></div><div class="agent-head"></div><div class="agent-prop"></div><div class="agent-badge provider-mark ${agent.provider}" title="${agent.provider.toUpperCase()} · ${this.model.project.live?'SKARPT / STATUS SEPARAT':'DEMO'}">${({codex:"◎",claude:"✳",google:"G",microsoft:"▦"})[agent.provider]||"?"}</div><div class="agent-status"></div>
    </div>`;
  }

  startDrag(e, node) {
    if (e.button !== 0) return;
    e.preventDefault(); node.setPointerCapture(e.pointerId); node.classList.add('dragging');
    const stageRect = this.nodes.officeStage.getBoundingClientRect();
    const agent = this.model.getAgent(node.dataset.id);
    this.drag = { id:agent.id, node, stageRect, startX:e.clientX, startY:e.clientY, moved:false, origX:agent.x, origY:agent.y };
    const move = ev => this.moveDrag(ev);
    const end = ev => { node.removeEventListener('pointermove', move); node.removeEventListener('pointerup', end); node.removeEventListener('pointercancel', end); this.endDrag(ev); };
    node.addEventListener('pointermove', move); node.addEventListener('pointerup', end); node.addEventListener('pointercancel', end);
  }

  moveDrag(e) {
    if (!this.drag) return;
    const { node, stageRect } = this.drag;
    const x = Math.max(5,Math.min(95,((e.clientX-stageRect.left)/stageRect.width)*100));
    const y = Math.max(30,Math.min(94,((e.clientY-stageRect.top)/stageRect.height)*100));
    if (Math.hypot(e.clientX-this.drag.startX,e.clientY-this.drag.startY) > 4) this.drag.moved=true;
    node.style.left=`${x}%`; node.style.top=`${y}%`;
    const target = this.stationAt(e.clientX,e.clientY);
    document.querySelectorAll('.station').forEach(n => n.classList.toggle('drop-target', n.dataset.id===target?.dataset.id));
  }

  endDrag(e) {
    if (!this.drag) return;
    const { node, moved, id, origX, origY } = this.drag;
    node.classList.remove('dragging');
    node.style.left=origX+'%';node.style.top=origY+'%';
    document.querySelectorAll('.station').forEach(n => n.classList.remove('drop-target'));
    const target = this.stationAt(e.clientX,e.clientY);
    node.dataset.wasDragged = moved ? '1':'0';
    if (moved && target) this.callbacks.onMoveAgent?.(id,target.dataset.id);
    else this.renderAgents();
    this.drag=null;
  }

  stationAt(x,y) {
    const all = [...document.querySelectorAll('.station')];
    return all.find(node => { const r=node.getBoundingClientRect(); return x>=r.left-14 && x<=r.right+14 && y>=r.top-14 && y<=r.bottom+20; }) || null;
  }

  selectAgent(id) { this.selectedAgentId=id; this.renderAgents(); this.renderDrawer(this.model.getAgent(id)); this.nodes.drawer.classList.add('open'); this.nodes.drawer.setAttribute('aria-hidden','false'); }
  closeDrawer() { this.selectedAgentId=null; this.nodes.drawer.classList.remove('open'); this.nodes.drawer.setAttribute('aria-hidden','true'); this.nodes.drawerContent.replaceChildren(); this.renderAgents(); }

  renderDrawer(agent) {
    if (!agent) return;
    const currentTask = agent.currentTask ? this.model.getTask(agent.currentTask) : null;
    const liveJob = this.model.project.live ? window.pixelWorksCurrentJob?.(this.model.activeProjectId,agent.id) : null;
    const provider = this.model.project.providers[agent.provider];
    const stationOptions = this.model.stations.map(s=>`<option value="${s.id}" ${s.id===agent.station?'selected':''}>${s.name}</option>`).join('');
    const latest = this.model.projectEvents.find(e=>e.agentId===agent.id);
    this.nodes.drawerContent.innerHTML = `<div class="agent-detail">
      <div class="agent-detail-head"><div class="detail-avatar" style="--detail-color:${agent.color}">${agent.initials}</div><div><span class="eyebrow">AGENT // ${STATUS_LABELS[agent.status]}</span><h2>${escapeHTML(agent.name)}</h2><div class="agent-role">${escapeHTML(agent.role)}</div><div class="provider-line"><span class="provider-mark ${agent.provider}">${({codex:"◎",claude:"✳",google:"G",microsoft:"▦"})[agent.provider]||"?"}</span> Provider: <strong>${provider.label}</strong> · motorstatus: <strong>${escapeHTML(provider.engineState)}</strong> · real kvot: <strong>${provider.quota}</strong></div></div></div>
      <div class="detail-section"><h3>SKILLS</h3><div class="skill-row">${Object.entries(agent.skills).sort((a,b)=>b[1]-a[1]).map(([k,v])=>`<span class="skill">${skillName[k]||k} <strong>${'◆'.repeat(v)}</strong></span>`).join('')}</div></div>
      <div class="detail-section"><button id="talkAgentBtn" class="pixel-button compact">☏ Prata med ${escapeHTML(agent.name)}</button> <button id="skillsAgentBtn" class="pixel-button compact secondary">★ Skills</button> <button id="profileAgentBtn" class="pixel-button compact secondary">⚙ Profil</button></div><div class="detail-section"><h3>AKTUELLT UPPDRAG</h3>${liveJob?`<div class="task-card"><div class="task-title">${escapeHTML(liveJob.instruction||'Codex-uppdrag')}</div><div class="task-meta">SKARPT · ${escapeHTML(liveJob.state)} · ${escapeHTML(liveJob.station||'')}</div></div>`:currentTask?`<div class="task-card priority-${currentTask.priority}"><div class="task-title">${escapeHTML(currentTask.title)}</div><div class="task-details">${escapeHTML(currentTask.details)}</div><div class="task-meta"><span class="chip status-${currentTask.status}">${taskStatusLabel[currentTask.status]}</span><span class="chip sim">SIMULERAT</span></div></div>`:'<div class="task-details">Ingen aktiv tilldelning.</div>'}</div>
      <div class="detail-section"><h3>INSTRUKTION / FOKUS</h3><textarea class="focus-box" id="focusInput">${escapeHTML(agent.focus)}</textarea><div class="detail-actions"><button class="pixel-button compact" id="saveFocusBtn">Sätt fokus</button><select id="stationSelect">${stationOptions}</select><button class="pixel-button compact secondary" id="moveAgentBtn">Flytta</button></div></div>
      <div class="detail-section"><h3>EVIDENSSTATUS</h3><div class="evidence-grid"><div class="evidence-card"><span>Aktivitet</span><strong>${liveJob?'SKARPT · '+escapeHTML(liveJob.state):this.model.project.live?'INGEN AKTIV SESSION':'SIMULERAD'}</strong></div><div class="evidence-card"><span>Oberoende verifiering</span><strong>NEJ</strong></div></div></div>
      <div class="detail-section"><h3>SENASTE HÄNDELSE</h3><div class="last-event">${liveJob?.events?.length?escapeHTML(window.pixelWorksLatestEvent?.(liveJob.events)||'Codex-händelse mottagen'):latest?escapeHTML(latest.message):'Ingen händelse ännu.'}</div></div>
    </div>`;
    this.nodes.drawer.querySelector('#talkAgentBtn')?.addEventListener('click',()=>this.callbacks.onTalk?.(agent.id));
    this.nodes.drawer.querySelector('#profileAgentBtn')?.addEventListener('click',()=>{if(this.model.project.live)window.pixelWorksEditStaffLive?.(this.model.activeProjectId,agent.id);else this.callbacks.onTalk?.(agent.id);});
    this.nodes.drawer.querySelector('#skillsAgentBtn')?.addEventListener('click',()=>this.callbacks.onSkills?.(agent.id));
    this.nodes.drawer.querySelector('#saveFocusBtn')?.addEventListener('click',()=>this.callbacks.onFocus?.(agent.id,this.nodes.drawer.querySelector('#focusInput').value));
    this.nodes.drawer.querySelector('#moveAgentBtn')?.addEventListener('click',()=>this.callbacks.onMoveAgent?.(agent.id,this.nodes.drawer.querySelector('#stationSelect').value));
  }

  renderLead() {
    if (!this.nodes.leadStrip) return;
    const lead=this.model.getLead();
    if(!lead){this.nodes.leadStrip.innerHTML=`<div class="lead-card"><div><div class="lead-name">INGEN ANSTÄLLD</div><div class="lead-meta">Anställ Codex i ⚙ Lokal studio, sedan dra honom till en station.</div></div></div>`;return;}
    this.nodes.leadStrip.innerHTML=`<div class="lead-card"><div class="lead-avatar">${lead.initials}</div><div><div class="lead-name">${lead.name} · ${lead.role}</div><div class="lead-meta">planering ${lead.skills.planning||0}/5 · ${STATUS_LABELS[lead.status]}</div></div><div class="lead-actions"><button id="delegateBtn" class="pixel-button compact">Auto-delegera</button></div></div>`;
    this.nodes.leadStrip.querySelector('#delegateBtn').addEventListener('click',()=>this.callbacks.onAutoDelegate?.());
  }

  renderTasks() {
    if (!this.nodes.taskList) return;
    this.nodes.taskList.innerHTML=this.model.project.tasks.map(task=>{
      const agent=task.assignee?this.model.getAgent(task.assignee):null;
      return `<article class="task-card priority-${task.priority}" data-task="${task.id}"><div class="task-title">${escapeHTML(task.title)}</div><div class="task-details">${escapeHTML(task.details)}</div><div class="task-meta"><span class="chip ${agent?'':'status-todo'}">${agent?agent.name:'OTILLDELAD'}</span><span class="chip">${skillName[task.requiredSkill]||task.requiredSkill}</span><span class="chip sim">DEMO</span><select class="task-state-select" data-task-status="${task.id}" aria-label="Status för ${escapeHTML(task.title)}">${['todo','working','review','done'].map(s=>`<option value="${s}" ${s===task.status?'selected':''}>${taskStatusLabel[s]}</option>`).join('')}</select></div></article>`;
    }).join('') || '<div class="task-details">Inga uppdrag ännu.</div>';
    this.nodes.taskList.querySelectorAll('[data-task-status]').forEach(sel=>sel.addEventListener('change',()=>this.callbacks.onTaskStatus?.(sel.dataset.taskStatus,sel.value)));
  }

  renderEvents() {
    const events=this.model.projectEvents;
    this.nodes.eventFeed.innerHTML=events.map(ev=>`<div class="event-row" style="--event-color:${EVENT_COLORS[ev.type]||'#8e88a8'}"><div class="event-time">${new Date(ev.timestamp).toLocaleTimeString('sv-SE',{hour:'2-digit',minute:'2-digit',second:'2-digit'})}</div><div><div class="event-msg">${escapeHTML(ev.message)}</div><div class="event-type">${ev.type} · source=demo · ${ev.confidence}</div></div></div>`).join('') || '<div class="event-row"><div></div><div class="event-msg">Feed rensad. Nya demo-event visas här.</div></div>';
  }

  renderTaskAssignees() { this.nodes.taskAssignee.innerHTML='<option value="">Arbetsledaren väljer senare</option>'+this.model.project.agents.map(a=>`<option value="${a.id}">${a.name} · ${a.role}</option>`).join(''); }
  openTaskDialog() { this.renderTaskAssignees(); this.nodes.taskDialog.showModal(); setTimeout(()=>this.nodes.taskDialog.querySelector('input[name="title"]')?.focus(),0); }

  showSpeech(agent,message) {
    const node=document.createElement('div'); node.className='speech'; node.style.left=`${agent.x}%`; node.style.top=`${Math.max(35,agent.y-8)}%`; node.textContent=message; this.nodes.fxLayer.appendChild(node); setTimeout(()=>node.remove(),3100);
  }
  showAgentSpeech(agent,message,kind='info') {
    if(!agent || this.model.project.id!==this.model.activeProjectId)return false;
    const node=[...this.nodes.agentLayer.querySelectorAll('.agent')].find(n=>n.dataset.id===agent.id);
    if(!node)return false;
    const old=node.querySelector('.agent-speech');if(old)old.remove();
    const bubble=document.createElement('div');bubble.className='agent-speech speech-'+(kind==='failed'?'failed':kind==='done'?'done':'info');
    bubble.setAttribute('role','status');bubble.textContent=String(message).slice(0,95);
    node.appendChild(bubble);
    // Kan inte lämna kvar bubbla på borttagen eller återanvänd agentnod.
    const timeout=setTimeout(()=>bubble.remove(),4200);
    bubble.addEventListener('click',e=>{e.stopPropagation();clearTimeout(timeout);bubble.remove()});
    return true;
  }
  toast(message) { const node=document.createElement('div');node.className='toast';node.textContent=message;this.nodes.toastLayer.appendChild(node);setTimeout(()=>node.remove(),2400); }
  setSimulationPaused(paused) { this.nodes.pauseBtn.textContent=paused?'Starta simulering':'Pausa simulering'; }
}

function escapeHTML(value='') { return String(value).replace(/[&<>'"]/g, ch=>({ '&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;' }[ch])); }
