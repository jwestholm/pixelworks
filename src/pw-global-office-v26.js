/* Pixel Works v2.6 — 1 GLOBAL STUDIO, 1 sprite per current registered employee.
 * UI projection only: real project job identities and records remain intact.
 * No writes, AI calls, synthetic job events or implicit project changes. */
(() => {
  'use strict';
  if (window.__PW_GLOBAL_OFFICE_V26__) return;
  window.__PW_GLOBAL_OFFICE_V26__ = true;
  const css=document.createElement('style');
  css.id='pw26-global-office-css';
  css.textContent=`
    /* Fix the v2.4 nested scrolling trap. One scroll surface, reachable on touch. */
    #pw13Dialog{box-sizing:border-box!important;display:block!important;
      height:min(820px,calc(100dvh - 18px))!important;
      max-height:calc(100dvh - 18px)!important;
      overflow-x:hidden!important;overflow-y:auto!important;
      overscroll-behavior:contain;scrollbar-gutter:stable;touch-action:pan-y;}
    #pw13Dialog .pw13-shell{box-sizing:border-box!important;display:block!important;
      height:auto!important;min-height:100%!important;overflow:visible!important;}
    #pw13Dialog .pw13-staff{display:grid!important;
      grid-template-columns:repeat(2,minmax(0,1fr))!important;
      grid-auto-rows:max-content!important;align-content:start!important;
      height:auto!important;max-height:none!important;min-height:0!important;
      flex:none!important;overflow:visible!important;scrollbar-gutter:auto!important;
      touch-action:auto!important;padding-bottom:18px!important;}
    #pw13Dialog .pw25-box{max-height:none!important;overflow:visible!important;}
    #pw13Dialog .pw24-roster-tools{position:sticky;top:0;z-index:7;
      box-shadow:0 3px 0 #90aeb4;}
    #pw13Dialog .pw26-highlight{outline:3px solid #d28a24;outline-offset:-3px;background:#fff0c9!important;}
    @media(max-width:630px){
      #pw13Dialog{height:calc(100dvh - 8px)!important;max-height:calc(100dvh - 8px)!important;}
      #pw13Dialog .pw13-staff{grid-template-columns:1fr!important;}
      #pw13Dialog .pw24-roster-tools{position:static;}
    }
    /* Do not render the old local-project sprites or the v0.13 group counters.
       Only after the global register AND the current roster are available. */
    body.pw26-global-office #agentLayer{visibility:hidden!important;}
    body.pw26-global-office #pw13OfficeRoster{display:none!important;}
    #pw26GlobalAgents{position:absolute;inset:0;z-index:26;pointer-events:none;overflow:visible;}
    #pw26GlobalAgents[hidden]{display:none!important;}
    #pw26GlobalAgents .pw26-person{pointer-events:auto;appearance:none;border:0;padding:0;
      /* Buttons receive an opaque UA background in Firefox/Chromium unless
         explicitly cleared. Preserve the role-specific sprite background-image:
         NEVER use the background shorthand here. */
      background-color:transparent!important;
      color:inherit;cursor:pointer;isolation:isolate;
      transition:left 1.05s linear,top 1.05s linear;}
    #pw26GlobalAgents .pw26-person.walking{transition:left 1.05s linear,top 1.05s linear!important;}
    #pw26GlobalAgents .pw26-person:hover{filter:drop-shadow(0 0 6px #fce5aa);z-index:41!important;}
    #pw26GlobalAgents .pw26-person:focus-visible{outline:3px solid #ffd47c;outline-offset:4px;z-index:41!important;}
    #pw26GlobalAgents .pw26-person .agent-name{pointer-events:none;max-width:112px;
      overflow:hidden;text-overflow:ellipsis;}
    #pw26GlobalAgents .pw26-person .agent-status{pointer-events:none;}
    #pw26GlobalAgents .pw26-person.pw26-on-break .agent-status{background:#ebbd63;}
    #pw26GlobalAgents .pw26-person.pw26-on-break{animation-delay:var(--pw-anim-phase,0s);}
    #pw26-global-count{position:absolute;right:9px;bottom:10px;z-index:27;
      border:2px solid #8ad5c8;background:#153e50df;color:#fff3d1;
      font:700 11px/1.3 system-ui,sans-serif;padding:5px 8px;border-radius:5px;
      pointer-events:none;box-shadow:2px 2px 0 #0c2937;}
    @media(prefers-reduced-motion:reduce){
      #pw26GlobalAgents .pw26-person{transition:none!important;animation:none!important;}
    }
  `;
  document.head.append(css);
  const $=(selector,root=document)=>root.querySelector(selector);
  const anchors={lead:[18,51],code:[42,55],research:[65,53],qa:[82,66],
    docs:[27,80],meeting:[60,68],art:[12,72],music:[82,86],voice:[39,77],cafe:[54,86]};
  // Dispersed, non-overlapping visual slots; never persisted as employee station.
  const places=[[12,51],[23,57],[35,50],[46,58],[58,51],[69,55],[82,54],
    [17,69],[28,70],[39,70],[51,70],[63,72],[76,73],[30,87],[66,86],
    [11,85],[44,87],[87,85],[55,59],[72,62],[19,84],[89,68],[37,61],[58,85]];
  const roleKey={lead:'lead',programmer:'programmer',qa:'qa',artist:'artist',
    musician:'musician',voice:'voice',research:'research',writer:'writer',
    creative:'writer',docs:'writer',allround:'allround'};
  const hash=value=>{let n=2166136261;for(const ch of String(value))n=Math.imul(n^ch.charCodeAt(0),16777619)>>>0;return n;};
  const state={layer:null,counter:null,people:new Map(),lastKey:'',fetching:false,serial:0,
    registered:false,walkIndex:0};
  function activeLive(){return !!window.__PIXEL_WORKS_DEMO__?.model?.project?.live;}
  function stopVisual(){
    document.body.classList.remove('pw26-global-office');
    if(state.layer)state.layer.hidden=true;
    if(state.counter)state.counter.hidden=true;
    state.registered=false;
  }
  function ensureLayer(){
    const stage=$('#officeStage');if(!stage)return false;
    if(state.layer?.parentElement!==stage){
      state.layer=document.createElement('div');state.layer.id='pw26GlobalAgents';stage.append(state.layer);
      state.lastKey='';state.people.clear();
    }
    if(state.counter?.parentElement!==stage){
      state.counter=document.createElement('div');state.counter.id='pw26-global-count';stage.append(state.counter);
    }
    return true;
  }
  function title(p){return `${p.name} · ${p.role||'Anställd'} · ${p.project_name||p.project_id}\nStudio-ID: ${p.studio_id}\n${p.busy?'Arbetar i tilldelat projekt':'Ledig i studion'} · Klicka för personalprofil`;}
  function setPos(node,x,y,walking=false){
    node.style.left=Math.max(7,Math.min(92,x))+'%';
    node.style.top=Math.max(42,Math.min(91,y))+'%';
    node.classList.toggle('walking',!!walking);
    if(walking){
      clearTimeout(node._pw26Stop);
      node._pw26Stop=setTimeout(()=>{if(node.isConnected)node.classList.remove('walking');},1130);
    }
  }
  function officeSlot(p,index,staff){
    if(!Object.hasOwn(anchors,p.station)||p.station==='cafe')return places[index%places.length];
    const xy=anchors[p.station];
    const deskPeers=staff.filter(x=>x.station===p.station);
    const i=deskPeers.findIndex(x=>x.studio_id===p.studio_id);
    // Each visible employee is separate, even if several share one workstation.
    const column=(i%5)-2,row=Math.floor(i/5);
    return [xy[0]+column*4.5,xy[1]+row*7+(i%2)*3];
  }
  function createPerson(p,index,people){
    const node=document.createElement('button');node.type='button';
    node.className='agent pw26-person';
    node.dataset.studioId=p.studio_id;
    node.dataset.projectId=p.project_id;
    node.dataset.agentId=p.agent_id;
    const kind=roleKey[String(p.role_type||'').toLowerCase()]||'allround';
    const variant=hash(p.studio_id)%4;
    const station=p.busy&&(p.station in anchors)?p.station:'cafe';
    node.classList.add('sprite-role-'+kind,'sprite-variant-'+variant,'activity-'+station,p.busy?'working':'idle');
    node.style.setProperty('--pw-anim-phase',(-((hash(p.studio_id)>>8)%350)/100).toFixed(2)+'s');
    node.style.setProperty('--agent-color','#5bb9ba');
    node.style.setProperty('--hair','#344a5e');
    node.style.setProperty('--status-color',p.busy?'#61d2a7':'#edcf89');
    for(const cls of ['agent-name','agent-shadow','agent-body','agent-head','agent-prop','agent-status']){
      const part=document.createElement('span');part.className=cls;
      if(cls==='agent-name')part.textContent=p.name;
      node.append(part);
    }
    node.title=title(p);node.setAttribute('aria-label',title(p).replaceAll('\n',' · '));
    setPos(node,...officeSlot(p,index,people));
    node.addEventListener('click',event=>{
      if(node._pw26JustDragged){event.preventDefault();event.stopPropagation();node._pw26JustDragged=false;return;}
      openPerson(p.studio_id);
    });
    enableDrag(node,p);
    return node;
  }
  function enableDrag(node,p){
    // Preserve the familiar drag-to-workstation interaction. Only a deliberate
    // drop invokes the original authorized project adapter; visual wandering
    // never calls the backend. No cross-project assignment by accident.
    node.addEventListener('pointerdown',event=>{
      if(event.button!==0||p.busy)return;
      const stage=$('#officeStage');if(!stage)return;
      const rect=stage.getBoundingClientRect();
      const initial={x:node.style.left,y:node.style.top};
      const start={x:event.clientX,y:event.clientY};
      let dragged=false;
      node.setPointerCapture?.(event.pointerId);
      const move=ev=>{
        if(Math.hypot(ev.clientX-start.x,ev.clientY-start.y)>9)dragged=true;
        if(!dragged)return;
        node.classList.add('dragging');
        node.style.left=Math.max(7,Math.min(92,100*(ev.clientX-rect.left)/rect.width))+'%';
        node.style.top=Math.max(42,Math.min(91,100*(ev.clientY-rect.top)/rect.height))+'%';
      };
      const finish=ev=>{
        node.removeEventListener('pointermove',move);
        node.removeEventListener('pointerup',finish);
        node.removeEventListener('pointercancel',finish);
        node.classList.remove('dragging');
        if(!dragged)return;
        node._pw26JustDragged=true;
        setTimeout(()=>{node._pw26JustDragged=false;},550);
        node.style.left=initial.x;node.style.top=initial.y;
        if(ev.type!=='pointerup')return;
        const ui=window.__PIXEL_WORKS_DEMO__?.ui;
        const station=ui?.stationAt?.(ev.clientX,ev.clientY);
        if(!station?.dataset?.id || typeof window.pixelWorksMoveLive!=='function')return;
        Promise.resolve(window.pixelWorksMoveLive(p.project_id,p.agent_id,station.dataset.id))
          .then(()=>{window.__PIXEL_WORKS_DEMO__?.ui?.toast?.(p.name+' → '+station.dataset.id);return refresh();})
          .catch(err=>{window.__PIXEL_WORKS_DEMO__?.ui?.toast?.('Kan inte flytta '+p.name+': '+String(err.message||err));});
      };
      node.addEventListener('pointermove',move);
      node.addEventListener('pointerup',finish);
      node.addEventListener('pointercancel',finish);
    });
  }
  // Clicking a sprite opens the SAME global personnel dialog, never a new
  // project-specific conversation window with an unknown agent ID.
  function openPerson(id){
    const nav=$('#pw13StudioNav');
    if(nav)nav.click();
    else return;
    let attempts=0;
    function focusCard(){
      const dialog=$('#pw13Dialog'),card=$('#pw13-card-'+id);
      if(!dialog?.open||!card){if(attempts++<12)setTimeout(focusCard,90);return;}
      const project=$('#pw24-project',dialog),search=$('#pw24-search',dialog);
      if(project&&project.value!=='all'){project.value='all';project.dispatchEvent(new Event('change',{bubbles:true}));}
      if(search&&search.value){search.value='';search.dispatchEvent(new Event('input',{bubbles:true}));}
      dialog.querySelectorAll('.pw26-highlight').forEach(el=>el.classList.remove('pw26-highlight'));
      card.classList.add('pw26-highlight');
      card.scrollIntoView({block:'center',behavior:'instant'});
      card.querySelector('strong')?.setAttribute('tabindex','-1');
    }
    setTimeout(focusCard,80);
  }
  function draw(data,projectCount){
    if(!ensureLayer()||!activeLive())return stopVisual();
    // A v2.5 snapshot is immutable. Refuse fake visual certainty if its source
    // roster no longer matches. Show current valid staff only, never invent them.
    const staff=[...data].sort((a,b)=>String(a.studio_id).localeCompare(String(b.studio_id)));
    if(!staff.length)return stopVisual();
    const key=JSON.stringify(staff.map(p=>[p.studio_id,p.name,p.role,p.role_type,p.project_id,p.agent_id,p.project_name,p.station,p.busy]));
    if(state.lastKey!==key){
      state.lastKey=key;
      state.layer.replaceChildren();state.people.clear();
      staff.forEach((p,index)=>{const node=createPerson(p,index,staff);state.people.set(p.studio_id,{node,person:p,slot:officeSlot(p,index,staff),move:0});state.layer.append(node);});
    }
    state.layer.hidden=false;
    document.body.classList.add('pw26-global-office');
    state.counter.hidden=false;
    const projectLabel=Number.isInteger(projectCount) && projectCount>=0
      ? `${projectCount} spel` : 'spelantal okänt';
    state.counter.textContent=`🏢 ${staff.length} anställda · ${projectLabel} · 1 studio`;
    state.registered=true;
  }
  async function refresh(){
    if(!activeLive()){stopVisual();return;}
    if(state.fetching||typeof window.pixelWorksApi!=='function')return;
    state.fetching=true;const seq=++state.serial;
    try{
      const [registry,studio]=await Promise.all([
        window.pixelWorksApi('/api/pw-v025/global-staff'),
        window.pixelWorksApi('/api/pw-v013/studio')
      ]);
      if(seq!==state.serial||!activeLive())return stopVisual();
      if(!registry?.registered||!Array.isArray(studio?.staff))return stopVisual();
      const valid=new Set((registry.staff||[]).map(p=>p.studio_id));
      // Register includes current source roster, and studio_id provides identity.
      const observed=studio.staff.filter(p=>valid.has(p.studio_id));
      draw(observed,Array.isArray(studio.projects)?studio.projects.length:null);
      if(registry.needs_reconciliation&&state.counter){state.counter.title='Personregistret och dagens personal behöver synkroniseras. Öppna Min studio.';}
      else if(state.counter)state.counter.title='Alla synliga personer hämtas från serverns globala personregister.';
    }catch(error){
      // Preserve last server-confirmed state during a transient offline period.
      if(!state.registered)stopVisual();
      console.warn('Global kontorspersonal kunde inte uppdateras:',String(error.message||error));
    }finally{state.fetching=false;}
  }
  function takeWalk(){
    if(!state.registered||!activeLive()||document.hidden||matchMedia('(prefers-reduced-motion: reduce)').matches)return;
    const idle=[...state.people.values()].filter(p=>!p.person.busy&&p.node.isConnected);
    if(!idle.length)return;
    // One idle sprite strolls at a time, outside the backend scheduler.
    const person=idle[(state.walkIndex++)%idle.length];
    person.move++;
    const [x,y]=person.slot;
    const offsets=[[4,2],[-3,3],[4,-3],[-4,-1],[0,0]];
    const [dx,dy]=offsets[person.move%offsets.length];
    setPos(person.node,x+dx,y+dy,true);
  }
  // Start only after the real web app and project roster are loaded.
  setTimeout(refresh,650);
  setInterval(refresh,10000);
  setInterval(takeWalk,1700);
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh();});
  window.addEventListener('pixelworks:project-changed',()=>setTimeout(refresh,250));
  window.addEventListener('pixelworks:studio-changed',()=>setTimeout(refresh,250));
})();
