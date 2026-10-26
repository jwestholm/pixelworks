/* Pixel Works 0.13.2 – ONE COMPANY, bounded office population.
 * Existing agent/job UI is preserved. Roster is read-only until explicit
 * activation/transfer. No AI/network provider calls are started here. */
(() => {
'use strict';
if (window.__PW13_STUDIO__) return;
window.__PW13_STUDIO__ = true;
const esc = x => String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const $ = (s,r=document)=>r.querySelector(s);
const nameFor=(p,all)=>all.projects.find(x=>x.id===p)?.name||p;
const focus=()=>window.__PIXEL_WORKS_DEMO__?.model?.activeProjectId||$('#projectSelect')?.value;
let latest=null,loading=false,updating=false,lastScene='',initial=false;
const style=document.createElement('style');style.textContent=`
  body.live-project .right-rail{overflow-y:auto!important}
  body.live-project .right-rail #pw13-summary{flex:0 0 auto;order:-9;max-height:none}
  #pw13-summary{margin:7px 0;background:#173c50;color:#f3e9d8;border:2px solid #568d95;padding:10px;font:13px/1.45 system-ui,sans-serif}
  #pw13-summary h3{font-size:14px;color:#f9d389;margin:0 0 6px}
  #pw13-summary .pw13-small{font-size:11px;color:#c4e1de}
  #pw13-summary button{background:#eec776;border:2px solid #8a6b40;color:#183047;padding:7px 12px;font-weight:750;cursor:pointer;margin-top:7px}
  #pw13-summary b{color:white}
  /* Simple office HUD: do not repeat management panels already in the top menu. */
  body.live-project .right-rail #pw13-summary,
  body.live-project .right-rail #pw17-projectbar,
  body.live-project .right-rail #pw117Stats,
  body.live-project .right-rail #pw-people-state{display:none!important}
  body.live-project .right-rail #pw17-access.pw13-access-granted,
  body.live-project .right-rail #pw17-decisions.pw13-nothing-pending,
  body.live-project .right-rail .pw13-superseded-access{display:none!important}
  #pw13Production[hidden]{display:none!important}
  #pw13Production .pw13-plan-details>summary{list-style-position:inside;cursor:pointer;font-weight:800;color:#f5d180;outline-offset:4px;padding:3px 2px}
  #pw13Production .pw13-plan-details>summary:focus-visible{outline:2px solid #f5d180}
  #pw13Production .pw13-plan-body{padding:6px 0 2px}
  #pw13DeskStatus{display:flex;gap:7px;align-items:center;flex-wrap:wrap}
  #pw13OfficeRoster{position:absolute;inset:0;pointer-events:none;z-index:24}
  .pw13-avatar{position:absolute;pointer-events:auto;cursor:pointer;border:0;background:transparent;display:flex;flex-direction:column;align-items:center;gap:2px;min-width:58px;max-width:94px;transform:translate(-50%,-60%);font-size:11px;color:#fff;filter:drop-shadow(1px 2px 1px #08192c)}
  .pw13-avatar .pw13-pixel{width:20px;height:24px;background:linear-gradient(#e6bb86 0 42%,#6198aa 42%);border:2px solid #29324b;box-shadow:inset 4px 0 #bc8b79,5px 0 #28495a,-5px 0 #28495a;image-rendering:pixelated}
  .pw13-avatar .pw13-tag{padding:2px 5px;background:#163145;color:#fff6d0;border:1px solid #80b0bc;max-width:100%;white-space:nowrap;text-overflow:ellipsis;overflow:hidden}
  .pw13-avatar.pw13-busy .pw13-tag{border-color:#ffe389}
  .pw13-avatar:focus-visible,.pw13-group:focus-visible{outline:3px solid #f8d268;outline-offset:3px}
  .pw13-group{position:absolute;pointer-events:auto;transform:translate(-50%,-50%);border:1px solid #eac878;border-radius:4px;background:#16384ae8;color:#ffe8a5;box-shadow:2px 2px 0 #102031;padding:3px 6px;max-width:122px;white-space:nowrap;font:700 11px/1.2 system-ui,sans-serif;cursor:pointer}
  .pw13-group:hover{background:#28566c}
  #pw13Dialog{width:min(860px,96vw);max-height:88dvh;overflow:auto;box-sizing:border-box;padding:0;border:8px ridge #ac7a52;outline:3px solid #183251;box-shadow:9px 10px #101b2b;background:#f7f2e8;color:#1e3549;font:14px/1.5 system-ui,sans-serif}
  #pw13Dialog::backdrop{background:#061324d2}
  #pw13Dialog .pw13-shell{padding:18px 20px;background:linear-gradient(130deg,#fff9e9,#e6f1f3)}
  #pw13Dialog h2{font:800 23px/1.25 system-ui;margin:0;color:#17354c}
  #pw13Dialog h3{margin:15px 0 6px}
  #pw13Dialog p{margin:9px 0}
  #pw13Dialog .pw13-head{display:flex;align-items:center;justify-content:space-between;gap:12px;border-bottom:3px solid #cfae89;padding-bottom:12px}
  #pw13Dialog button{background:#f3cc7e;color:#1b3249;border:2px solid #99713a;padding:8px 12px;margin:3px;cursor:pointer;font-weight:700;min-height:40px;border-radius:3px}
  #pw13Dialog button:disabled{opacity:.45;cursor:not-allowed}
  #pw13Dialog .pw13-close{background:#385a78;color:white;border-color:#243b54}
  #pw13Dialog button:focus-visible,#pw13Dialog select:focus-visible{outline:3px solid #2776ac;outline-offset:2px}
  #pw13Dialog .pw13-notice{background:#ffebbb;border:1px solid #c89b41;padding:12px;margin:12px 0}
  #pw13Dialog .pw13-staff{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
  #pw13Dialog .pw13-card{background:#fff;border:2px solid #b1c0c5;padding:11px;box-shadow:2px 3px 0 #d2d2c7}
  #pw13Dialog .pw13-card strong{font-size:15px}
  #pw13Dialog .pw13-card small{display:block;color:#526c7e}
  #pw13Dialog .pw13-card select{max-width:100%;min-width:160px;min-height:39px;color:#1e3447;background:white;border:2px solid #9db0bf;padding:5px}
  #pw13Dialog .pw13-card .pw13-assignment{display:flex;align-items:center;flex-wrap:wrap;gap:4px;margin-top:8px}
  #pw13Dialog [role=status]{min-height:22px;white-space:pre-wrap;color:#884626}
  #pw13Dialog .pw13-muted{font-size:12px;color:#526b7c}
  @media(max-width:630px){#pw13Dialog .pw13-staff{grid-template-columns:1fr}#pw13Dialog .pw13-shell{padding:12px}}
`;document.head.append(style);
const dialog=document.createElement('dialog');dialog.id='pw13Dialog';dialog.setAttribute('aria-label','Pixel Works gemensamma studio');document.body.append(dialog);
const safeApi=(p,data)=>{
  if (typeof window.pixelWorksApi!=='function') throw Error('Studion är ännu inte ansluten till servern.');
  // Shared-studio routes have their own authorization. They are never a bypass
  // for old project-prefixed API requests.
  return window.pixelWorksApi(p,data);
};
const notify=text=>window.__PIXEL_WORKS_DEMO__?.ui?.toast?.(text);
function shiftFocus(slug){
  const app=window.__PIXEL_WORKS_DEMO__;
  if(!app?.model?.projects?.some(p=>p.id===slug))return;
  const selection=$('#projectSelect');
  if(selection && selection.value!==slug){selection.value=slug;selection.dispatchEvent(new Event('change',{bubbles:true}));}
  else if(app.model.activeProjectId!==slug){app.model.switchProject(slug);app.ui?.renderAll();}
  // Never change focus to a project as an accidental side effect of polling.
}
function ensurePanel(){
  let panel=$('#pw13-summary');
  if(panel)return panel;
  const rail=$('.right-rail');if(!rail)return null;
  panel=document.createElement('section');panel.id='pw13-summary';
  // Place at top, but don't hide the existing activity, decisions or stat panels.
  rail.prepend(panel);
  panel.addEventListener('click',event=>{
    if(event.target.closest('[data-pw13-open]'))open();
    const b=event.target.closest('[data-pw13-focus]');if(b)shiftFocus(b.dataset.pw13Focus);
  });
  return panel;
}
// A physical office has finite desks. A legacy project may have a full starter
// team of its own; those are NOT additional bodies in a shared office until the
// owner activates shared-studio mode. Never draw every project employee on the
// same coordinates: one outside representative per unoccupied desk, with an
// accessible group counter for the rest. No persisted coordinates are changed.
function drawScene(data){
  const app=window.__PIXEL_WORKS_DEMO__,stage=$('#officeStage');
  let layer=$('#pw13OfficeRoster');
  if(!stage||!app?.model?.project?.live){if(layer)layer.replaceChildren();return;}
  if(!layer){layer=document.createElement('div');layer.id='pw13OfficeRoster';stage.append(layer);}
  const project=focus();
  const outsiders=data.staff.filter(p=>p.project_id!==project);
  const locals=data.staff.filter(p=>p.project_id===project);
  const signature=JSON.stringify([!!data.shared,project,
    ...locals.map(p=>[p.studio_id,p.station]),
    ...outsiders.map(p=>[p.studio_id,p.name,p.project_id,p.station,p.busy])]);
  if(layer.dataset.signature===signature)return;
  layer.dataset.signature=signature;
  layer.replaceChildren();
  // Before opt-in these people belong to SEPARATE legacy offices. Show them
  // only in Min studio's inventory rather than pretending to share the room.
  if(!data.shared)return;
  const anchors={lead:[18,48],code:[42,51],research:[66,49],qa:[83,66],
    docs:[26,78],meeting:[60,66],art:[10,70],music:[82,86],voice:[39,74],cafe:[54,88]};
  const stationOf=p=>Object.hasOwn(anchors,p.station)?p.station:'cafe';
  const grouped=new Map();
  for(const person of outsiders){const desk=stationOf(person);
    if(!grouped.has(desk))grouped.set(desk,[]);
    grouped.get(desk).push(person);
  }
  const localCount={};for(const person of locals){const desk=stationOf(person);
    localCount[desk]=(localCount[desk]||0)+1;
  }
  for(const [desk,people] of grouped){
    // Consistent representative: show active work first, then alphabetical.
    people.sort((a,b)=>Number(b.busy)-Number(a.busy)||String(a.name).localeCompare(String(b.name),'sv'));
    const xy=anchors[desk],vacant=!(localCount[desk]||0);
    const representative=vacant?people[0]:null;
    if(representative){
      const node=document.createElement('button');node.type='button';
      node.className='pw13-avatar'+(representative.busy?' pw13-busy':'');
      node.dataset.studioId=representative.studio_id;
      node.style.left=xy[0]+'%';node.style.top=xy[1]+'%';
      node.title=representative.name+' · '+representative.role+' · '+representative.project_name+'. Visa i Min studio.';
      node.setAttribute('aria-label',node.title);
      const pix=document.createElement('span');pix.className='pw13-pixel';
      const tag=document.createElement('span');tag.className='pw13-tag';tag.textContent=representative.name;
      node.append(pix,tag);node.onclick=()=>open(representative.studio_id);
      layer.append(node);
    }
    const hidden=people.length-(representative?1:0);
    if(hidden>0){
      const counter=document.createElement('button');counter.type='button';counter.className='pw13-group';
      counter.dataset.station=desk;counter.dataset.count=String(hidden);
      counter.textContent=(desk==='cafe'?'☕ ':'👥 ')+(representative?'+':'')+hidden+' '+(hidden===1?'kollega':'kollegor');
      // Raise the group badge above the work area so it cannot form a column
      // of overlapping nameplates or obscure the underlying station button.
      counter.style.left=(xy[0]+(representative?6:0))+'%';counter.style.top=(xy[1]-10)+'%';
      counter.title=people.map(p=>p.name+' ('+p.project_name+')').slice(0,7).join(', ')+
        (people.length>7?' …':'')+'. Klicka för att öppna studions personal.';
      counter.setAttribute('aria-label',hidden+' kollegor vid '+desk+'. '+counter.title);
      counter.onclick=()=>open();layer.append(counter);
    }
  }
}
function renderPanel(data){
  // The top-bar 'Min studio' button remains the single entry to roster and
  // cross-project administration. No redundant paragraph panel on the HUD.
  drawScene(data);
}
async function refresh(force=false){
  if(loading||!window.pixelWorksApi||(!force && document.hidden))return;
  loading=true;
  try{
    const data=await safeApi('/api/pw-v013/studio');
    if(!data||!Array.isArray(data.staff))return;
    latest=data;renderPanel(data);
    // Do not reset an open person's project selector during polling.
  }catch(e){if(!initial)console.warn('Studioöversikt ej tillgänglig:',e.message);}
  finally{loading=false;initial=true;}
}
function renderDialog(data,selected){
  if(!data)return;
  dialog.innerHTML='';
  const body=document.createElement('div');body.className='pw13-shell';
  const head=document.createElement('header');head.className='pw13-head';
  head.innerHTML=`<div><h2>🏢 Välkommen till Pixel Works</h2><div>En studio · ${data.project_count} spel · ${data.staff_count} personalposter</div></div>`;
  const exit=document.createElement('button');exit.type='button';exit.className='pw13-close';exit.textContent='✕ Stäng';exit.onclick=()=>dialog.close();head.append(exit);body.append(head);
  const intro=document.createElement('p');intro.textContent='Här ser du hela teamet. Välj ett spel att fokusera på eller flytta en ledig medarbetare till en annan produktion. Spelkod, Game Bible och rapporter stannar alltid i sina respektive projekt.';body.append(intro);
  if(!data.shared){
    const info=document.createElement('div');info.className='pw13-notice';
    info.innerHTML='<b>Gemensam studio är inte aktiverad</b><p>Dina befintliga spel och deras personal bevaras. Om du aktiverar delad personal börjar framtida spel utan automatiskt anställda. Befintliga anställda flyttas bara när du själv väljer det. Gamla startteam kan innehålla flera olika anställda med samma namn; de slås inte ihop automatiskt.</p>';
    const enable=document.createElement('button');enable.textContent='🏢 Aktivera gemensam studio';enable.type='button';
    enable.onclick=async()=>{
      // Button itself is the explicit opt-in; no extra native permission dialog.
      enable.disabled=true;updating=true;
      try{await safeApi('/api/pw-v013/studio/enable',{approval:'ENABLE_SHARED_STUDIO_V013'});await reloadDialog();notify('Gemensam studio aktiverad.');}
      catch(e){showStatus(e.message);enable.disabled=false;}finally{updating=false;}
    };info.append(enable);body.append(info);
  }
  if(data.pending_transfer){
    const row=document.createElement('div');row.className='pw13-notice';row.innerHTML='<b>⚠ Avbrutet personalbyte</b><p>Servern har en journal från en ofullständig flytt. Ingen ny flytt tillåts innan kontroll och återställning. Spelets kod och rapporter rörs inte.</p>';
    const repair=document.createElement('button');repair.textContent='↩ Återställ personalfiler från journal';
    let repairConfirmed=false;repair.onclick=async()=>{
      if(!repairConfirmed){repairConfirmed=true;repair.textContent='⚠ Bekräfta återställning av personalfiler';return;}
      updating=true;try{await safeApi('/api/pw-v013/studio/repair',{approval:'RESTORE_STUDIO_TRANSFER_V013'});await reloadDialog();}catch(e){showStatus(e.message)}finally{updating=false;}};
    row.append(repair);body.append(row);
  }
  const h=document.createElement('h3');h.textContent='🎮 Projekt';body.append(h);
  const projects=document.createElement('div');projects.className='pw13-projects';
  for(const p of data.projects){const button=document.createElement('button');button.type='button';button.textContent=(focus()===p.id?'✓ ':'🎮 ')+p.name;
    button.onclick=()=>{shiftFocus(p.id);dialog.close();};projects.append(button);}
  body.append(projects);
  const title=document.createElement('h3');title.textContent='👥 Personalen – ett gemensamt kontor';body.append(title);
  const roster=document.createElement('div');roster.className='pw13-staff';
  for(const person of data.staff){
    const card=document.createElement('article');card.className='pw13-card';card.id='pw13-card-'+person.studio_id;
    const ident=document.createElement('strong');ident.textContent=(person.busy?'🔵 ':'☕ ')+person.name;
    const info=document.createElement('small');info.textContent=person.role+' · '+(person.busy?'Arbetar':'Tillgänglig')+' · '+person.project_name;
    card.append(ident,info);
    if(person.conflict){const error=document.createElement('p');error.textContent='⚠ Samma personal-ID finns i flera spel. Manuell kontroll krävs.';card.append(error);}
    const actions=document.createElement('div');actions.className='pw13-assignment';
    const focusButton=document.createElement('button');focusButton.type='button';focusButton.textContent='🎮 Visa spelet';
    focusButton.onclick=()=>{shiftFocus(person.project_id);dialog.close()};actions.append(focusButton);
    if(data.shared){
      const dropdown=document.createElement('select');dropdown.setAttribute('aria-label','Välj projekt för '+person.name);
      for(const p of data.projects){const opt=document.createElement('option');opt.value=p.id;opt.textContent=p.name;if(person.project_id===p.id)opt.selected=true;dropdown.append(opt)}
      dropdown.disabled=person.busy||person.conflict;
      const move=document.createElement('button');move.type='button';move.textContent='↗ Tilldela';move.disabled=person.busy||person.conflict||data.projects.length<2;
      move.onclick=async()=>{
        if(dropdown.value===person.project_id){showStatus('Den anställda arbetar redan i valt projekt.');return;}
        const destination=data.projects.find(p=>p.id===dropdown.value);
        if(!destination)return;
        if(move.dataset.confirmed!==destination.id){
          move.dataset.confirmed=destination.id;
          move.textContent='✓ Bekräfta: '+person.name+' → '+destination.name;return;
        }
        updating=true;move.disabled=true;
        try{await safeApi('/api/pw-v013/studio/transfer',{studio_id:person.studio_id,target_project:destination.id,approval:'ASSIGN_STUDIO_EMPLOYEE_V013'});
          await window.pixelWorksRefreshLive?.();await reloadDialog(person.studio_id);notify(person.name+' tilldelad '+destination.name);}
        catch(e){showStatus(e.message);move.disabled=false;}finally{updating=false;}
      };
      dropdown.onchange=()=>{move.dataset.confirmed='';move.textContent='↗ Tilldela';};
      actions.append(dropdown,move);
    }
    card.append(actions);roster.append(card);
  }
  body.append(roster);
  if(!data.staff.length){const empty=document.createElement('p');empty.textContent='Studion saknar anställda. Öppna Personal för att anställa till valt projekt.';body.append(empty);}
  const foot=document.createElement('p');foot.className='pw13-muted';foot.textContent='Tekniska AI-motorer syns i personalprofilen. Studieöversikten gör inga AI-anrop. Projektens filer och Game Bible blandas aldrig.';body.append(foot);
  const status=document.createElement('p');status.id='pw13-status';status.setAttribute('role','status');body.append(status);
  dialog.append(body);
  if(selected){const node=$('#pw13-card-'+selected,dialog);if(node)node.scrollIntoView({block:'nearest'});}
}
function showStatus(message){const node=$('#pw13-status');if(node)node.textContent='⚠ '+message;else notify(message);}
async function reloadDialog(selection){
  const data=await safeApi('/api/pw-v013/studio');latest=data;renderPanel(data);renderDialog(data,selection);
}
function open(selected){if(!latest){refresh(true).then(()=>{if(latest)open(selected)});return;}
  renderDialog(latest,selected);if(!dialog.open)dialog.showModal();
}
window.pixelWorksOpenStudio=open;
// Project focus is a view filter, not a different office skin.
function unifyRoom(){
  const ui=window.__PIXEL_WORKS_DEMO__?.ui;
  if(!ui||typeof ui.renderProjectHeader!=='function'||ui.renderProjectHeader.__pw13)return;
  const old=ui.renderProjectHeader.bind(ui);
  const combined=function(){
    const result=old();const stage=$('#officeStage');
    if(stage){stage.dataset.room='0';const sign=stage.querySelector('.project-wallboard');
      if(sign)sign.textContent='PIXEL WORKS · STUDION';}
    const title=$('#projectTitle');if(title&&window.__PIXEL_WORKS_DEMO__?.model?.project?.live)
      title.textContent='Fokusprojekt: '+window.__PIXEL_WORKS_DEMO__.model.project.title;
    return result;
  };
  combined.__pw13=true;ui.renderProjectHeader=combined;combined();
}
// A prominent entry point in the game's own navigation bar.
const studioNav=$('#gameDock');
if(studioNav && !$('#pw13StudioNav')){
  const b=document.createElement('button');b.id='pw13StudioNav';b.type='button';b.className='dock-item';
  b.innerHTML='<span>🏢</span>Min studio';b.title='Hela företaget: personal från alla spel och deras tilldelningar';
  b.onclick=()=>open();studioNav.append(b);
}
const version=$('.brand-title .version');if(version)version.textContent='v0.13.5';
// Simple polling; the CURRENT project never changes from a network response.
setInterval(()=>{unifyRoom();refresh(false);},6000);
window.addEventListener('pixelworks:project-changed',()=>{if(latest)renderPanel(latest)});
window.addEventListener('pixelworks:project-created',()=>setTimeout(()=>refresh(true),450));
setTimeout(()=>{unifyRoom();refresh(true);},900);
// v0.13.5: project-scoped automatic production; optional plan editor on errors.
const planBox=document.createElement('section');planBox.id='pw13Production';
planBox.setAttribute('aria-label','Produktionsplan och tilldelade arbetsordrar');
planBox.style.cssText='margin:7px 0;padding:11px;border:2px solid #628f9c;background:#163548;color:#f7eedd;font:12px/1.4 system-ui,sans-serif;flex:0 0 auto;order:-7';
const railPlan=$('.right-rail');if(railPlan)railPlan.insertBefore(planBox,$('#pw17-decisions')||railPlan.firstChild);
let loadedPlan=null,loadedSlug='',lastPlanCheck=0,planBusy=false,confirmReport='';
const jobState={handoff:'📨 Designunderlag lämnat vidare',draft:'📝 Väntar på planbeslut',ready:'🟢 Beroenden uppfyllda',dependency:'⏳ Väntar på tidigare steg',
  unassigned:'👥 Saknar medarbetare',waiting:'⏳ Väntar',running:'🔵 Arbetar',
  done:'✅ Avslutat',review:'🟡 Behöver granskas',failed:'🔴 Misslyckades',
  archived:'📦 Arkiverat',claimed:'🔵 Tilldelat'};
const deskName={art:'Grafikstudio',code:'Programmering',qa:'Testning',docs:'Dokumentation',
  meeting:'Mötesrum',research:'Forskning',music:'Musikstudio',voice:'Röststudio'};
function paintPlan(result){
  if(!result||!planBox)return;
  const slug=focus();if(slug!==loadedSlug)return;
  const tasks=result.orders||[];
  const drafts=result.draft_plans||[];
  const leadReport=!tasks.length&&Boolean(result.last_lead_report);
  // No persistent empty panel: the activity feed already says that the team is idle.
  if(!tasks.length&&!drafts.length&&!leadReport){
    planBox.hidden=true;planBox.replaceChildren();return;
  }
  const wasOpen=planBox.querySelector('details')?.open||false;
  planBox.hidden=false;
  const counts=tasks.reduce((acc,t)=>(acc[t.state]=(acc[t.state]||0)+1,acc),{});
  const busy=(counts.running||0)+(counts.claimed||0);
  const waiting=(counts.ready||0)+(counts.waiting||0)+(counts.dependency||0);
  const help=(counts.unassigned||0)+(counts.failed||0)+(counts.review||0)+drafts.length;
  const completed=(counts.done||0)+(counts.handoff||0);
  const label=help?'👔 Produktion · '+help+' behöver hjälp':
    busy?'👔 Produktion · '+busy+' arbetar':
    waiting?'👔 Produktion · '+waiting+' väntar':
    leadReport?'👔 Fortsätt produktionen':
    completed?'👔 Produktion · '+completed+' klara':
    '👔 Produktion · '+tasks.length+' uppdrag';
  planBox.innerHTML='<details class="pw13-plan-details" '+(wasOpen?'open':'')+'><summary>'+esc(label)+'</summary><div class="pw13-plan-body"></div></details>';
  const content=planBox.querySelector('.pw13-plan-body');
  if(tasks.length){
    const statuses=document.createElement('div');statuses.style.cssText='opacity:.8;margin:4px 0 8px';
    statuses.textContent='Uppdragsöversikt · '+tasks.length+' steg';content.append(statuses);
    const list=document.createElement('div');list.style.cssText='max-height:200px;overflow:auto';
    list.innerHTML=tasks.map(t=>
      '<div style="border-left:3px solid '+(t.state==='done'?'#65cfa2':t.state==='ready'?'#eac474':'#7299b2')+
      ';background:#22465b;margin:5px 0;padding:7px">'+
      '<b>'+esc(t.title)+'</b><br><small>'+esc(deskName[t.station]||t.station)+' · '+esc(t.assignee)+'</small><br>'+
      '<small>'+esc(jobState[t.state]||t.state)+(t.reason?': '+esc(t.reason):'')+'</small></div>').join('');
    content.append(list);
  }
  for(const draft of drafts){
    const btn=document.createElement('button');btn.type='button';
    btn.textContent='✏️ Redigera plan ('+draft.steps.length+' uppdrag)';
    btn.style.cssText='display:block;width:100%;margin:8px 0;padding:9px;background:#f4d27e;color:#1a364c;font-weight:800;cursor:pointer;border:2px solid #95723e';
    btn.onclick=()=>openPlanEditor(draft);content.append(btn);
  }
  if(tasks.some(t=>t.state==='unassigned'||(t.reason||'').includes('personal'))){
    const hire=document.createElement('button');hire.type='button';
    hire.textContent='👥 Hitta personal i Min studio';
    hire.style.cssText='margin-top:5px;background:#f0d288;color:#1a3848;border:2px solid #986d35;padding:7px;cursor:pointer;font-weight:800';
    hire.onclick=()=>$('#pw13StudioNav')?.click();content.append(hire);
  }
  if(leadReport){
    const choices=document.createElement('select');
    choices.setAttribute('aria-label','Välj chefsrapport att fortsätta från');
    choices.style.cssText='max-width:100%;width:100%;background:#fff9e8;color:#17364a;padding:6px;margin:4px 0';
    for(const r of result.lead_reports||[result.last_lead_report]){
      const opt=document.createElement('option');opt.value=r.id;
      opt.textContent=r.title+' · '+(r.date||'');choices.append(opt);
    }
    content.append(choices);
    const button=document.createElement('button');button.type='button';
    button.style.cssText='margin-top:7px;padding:8px;background:#eac574;color:#17364a;border:2px solid #916935;cursor:pointer;font-weight:700';
    button.textContent='▶ Fortsätt från chefsrapporten';
    button.onclick=async()=>{
      if(planBusy||!choices.value||focus()!==slug)return;
      planBusy=true;button.disabled=true;
      try{
        const answer=await safeApi('/api/pw-v0133/from-report',{project:slug,report_id:choices.value});
        notify(answer.message||'Chefen arbetar vidare med rapporten.');
        await refreshPlan(true);
      }catch(e){notify('Kunde inte skapa chefsuppdrag: '+e.message);button.disabled=false;}
      finally{planBusy=false;confirmReport='';}
    };
    content.append(button);
  }
}

async function refreshPlan(force=false){
  const slug=focus();if(!slug||!railPlan||!window.pixelWorksApi)return;
  if(!force&&Date.now()-lastPlanCheck<6500)return;
  lastPlanCheck=Date.now();loadedSlug=slug;
  try{
    const data=await safeApi('/api/pw-v0133/production?project='+encodeURIComponent(slug));
    if(focus()!==slug)return;
    loadedPlan=data;paintPlan(data);
  }catch(e){if(!loadedPlan)planBox.textContent='Produktionsstatus kunde inte hämtas.';}
}
window.addEventListener('pixelworks:project-changed',()=>{loadedPlan=null;confirmReport='';refreshPlan(true)});
setInterval(()=>refreshPlan(false),7000);setTimeout(()=>refreshPlan(true),1300);
// A single review of the whole production plan, not per-worker permission prompts.
const planDlg=document.createElement('dialog');planDlg.id='pw13PlanEditor';
planDlg.setAttribute('aria-label','Granska arbetsledarens produktionsplan');
planDlg.style.cssText='border:7px ridge #a67e57;max-width:92vw;width:min(900px,92vw);max-height:90vh;overflow:auto;background:#fffaf0;color:#17344c;padding:0;box-shadow:8px 9px #142337;font:14px/1.4 system-ui,sans-serif';
const planStyle=document.createElement('style');planStyle.textContent=`
#pw13PlanEditor::backdrop{background:#05172cd8}
#pw13PlanEditor .pw-plan-shell{padding:16px 20px}
#pw13PlanEditor h2{font-size:22px;color:#173a54;margin:0 0 6px}
#pw13PlanEditor .pw-plan-head{display:flex;justify-content:space-between;gap:12px;align-items:center;border-bottom:3px solid #c8a875;padding-bottom:10px}
#pw13PlanEditor .pw-plan-step{background:#f6f1e9;border:2px solid #b8c4c7;border-left:5px solid #538ba2;margin:9px 0;padding:11px;display:grid;gap:7px}
#pw13PlanEditor .pw-plan-row{display:grid;grid-template-columns:1fr 1fr;gap:8px}
#pw13PlanEditor label{font-size:12px;font-weight:750;display:block}
#pw13PlanEditor input,#pw13PlanEditor select,#pw13PlanEditor textarea{box-sizing:border-box;width:100%;font:13px system-ui;padding:7px;border:1px solid #91a4ad;color:#172c40;background:#fff;min-height:37px}
#pw13PlanEditor textarea{min-height:66px;resize:vertical}
#pw13PlanEditor button{background:#f1d081;color:#17364b;border:2px solid #986d38;padding:8px 12px;min-height:39px;font-weight:800;cursor:pointer;margin:2px}
#pw13PlanEditor button:disabled{opacity:.5;cursor:wait}
#pw13PlanEditor .pw-plan-deps{display:flex;gap:7px;flex-wrap:wrap;background:#e4ecec;padding:7px}
#pw13PlanEditor .pw-plan-deps label{display:flex;gap:4px;align-items:center;font-size:12px}
#pw13PlanEditor .pw-plan-deps input{width:auto;min-height:0}
#pw13PlanEditor [role=status]{white-space:pre-wrap;margin:8px 0;min-height:19px;color:#9d4128}
@media(max-width:590px){#pw13PlanEditor .pw-plan-row{grid-template-columns:1fr}}
`;document.head.append(planStyle);document.body.append(planDlg);
let editProject='',editId='',editRevision=0,editSteps=[],editLoading=false;
function gatherPlan(){
 const stored=new Map(editSteps.map(x=>[x.id,x]));
 for(const row of planDlg.querySelectorAll('[data-plan-step]')){
   const step=stored.get(row.dataset.planStep);if(!step)continue;
   step.title=row.querySelector('[data-edit-title]').value;
   step.instruction=row.querySelector('[data-edit-instruction]').value;
   step.priority=Number(row.querySelector('[data-edit-priority]').value);
   step.assigned_agent_id=row.querySelector('[data-edit-agent]').value||null;
   const local=[...row.querySelectorAll('[data-edit-dep]:checked')].map(x=>x.value);
   const external=(step.depends_on_order_ids||[]).filter(id=>!stored.has(id));
   step.depends_on_order_ids=[...external,...local];
 }
}
function openPlanEditor(draft){
 if(focus()!==loadedSlug||draft.project!==focus())return;
 editProject=draft.project;editId=draft.id;editRevision=draft.revision;
 editSteps=draft.steps.map(x=>({...x,depends_on_order_ids:[...x.depends_on_order_ids],staff_choices:[...x.staff_choices]}));
 drawPlanEditor();planDlg.showModal();
}
function drawPlanEditor(){
 planDlg.innerHTML='<div class="pw-plan-shell"><div class="pw-plan-head"><div><h2>👔 Produktionsplan – granska och fördela</h2><small>'+esc(editProject)+' · '+editSteps.length+' arbetsordrar · utkast</small></div><button type="button" data-close>✕ Stäng</button></div>'+ 
 '<p>Chefen tog fram planen med Codex. Justera vem som gör vad och vilka uppgifter som måste vara klara först. <b>Studion arbetar automatiskt inom redan godkänd studioåtkomst. Här kan du frivilligt ändra planen om något behöver korrigeras.</b></p>'+ 
 '<div data-plan-rows>'+editSteps.map((step,i)=>{
   const prev=editSteps.slice(0,i);
   const external=(step.depends_on_order_ids||[]).filter(id=>!editSteps.some(t=>t.id===id));
   return '<section class="pw-plan-step" data-plan-step="'+esc(step.id)+'"><div style="display:flex;justify-content:space-between;align-items:center;gap:7px"><b>'+ (i+1)+'. '+esc(deskName[step.station]||step.station)+'</b><span><button type="button" data-move="up" '+(i===0?'disabled':'')+' aria-label="Flytta upp uppdrag">↑</button><button type="button" data-move="down" '+(i===editSteps.length-1?'disabled':'')+' aria-label="Flytta ned uppdrag">↓</button></span></div>'+ 
   '<label>Uppdragets namn<input data-edit-title maxlength="100" value="'+esc(step.title)+'"></label>'+ 
   '<label>Arbetsinstruktion<textarea data-edit-instruction maxlength="1800">'+esc(step.instruction)+'</textarea></label>'+ 
   (step.staff_choices.length?'':'<small style="color:#a44b1d">⚠ Ingen behörig person är knuten till det här spelet för denna station. Öppna Min studio och tilldela personal innan uppdraget kan utföras.</small>')+ 
   '<div class="pw-plan-row"><label>Ansvarig<select data-edit-agent><option value="">Ingen ännu – vänta på personal</option>'+step.staff_choices.map(p=>'<option value="'+esc(p.id)+'" '+(p.id===step.assigned_agent_id?'selected':'')+'>'+esc(p.name)+' – '+esc(p.role)+'</option>').join('')+'</select></label>'+ 
   '<label>Prioritet<select data-edit-priority>'+[[1,'Hög'],[2,'Normal'],[3,'Låg']].map(([n,t])=>'<option value="'+n+'" '+(n===step.priority?'selected':'')+'>'+t+'</option>').join('')+'</select></label></div>'+ 
   '<div><b style="font-size:12px">Vänta tills dessa uppdrag är klara:</b><div class="pw-plan-deps">'+(prev.length?prev.map(p=>'<label><input type="checkbox" data-edit-dep value="'+esc(p.id)+'" '+(step.depends_on_order_ids.includes(p.id)?'checked':'')+'> '+esc(p.title)+'</label>').join(''):'<small>Inga tidigare uppdrag.</small>')+(external.length?'<small>Extern referens behålls.</small>':'')+'</div></div></section>';
 }).join('')+'</div><div role="status" id="pw13PlanMessage"></div><div style="display:flex;flex-wrap:wrap;gap:6px;justify-content:flex-end"><button type="button" data-save>Spara utkast</button><button type="button" data-release style="background:#78d5ad;color:#12344b">▶ Starta produktionen</button></div></div>';
 if(editSteps.some(step=>!step.staff_choices.length)){
   const notice=document.createElement('button');notice.type='button';notice.textContent='👥 Öppna Min studio och bemanna';
   notice.onclick=()=>{planDlg.close();$('#pw13StudioNav')?.click()};
   planDlg.querySelector('.pw-plan-head').append(notice);
 }
 planDlg.querySelector('[data-close]').onclick=()=>planDlg.close();
 for(const row of planDlg.querySelectorAll('[data-plan-step]')){
   for(const b of row.querySelectorAll('[data-move]'))b.onclick=()=>{
     gatherPlan();const idx=editSteps.findIndex(x=>x.id===row.dataset.planStep);
     const dest=idx+(b.dataset.move==='up'?-1:1);if(dest<0||dest>=editSteps.length)return;
     [editSteps[idx],editSteps[dest]]=[editSteps[dest],editSteps[idx]];
     // Cyclic/forward dependencies are deliberately NOT silently removed.
     // The server will explain any now-invalid dependency at save time.
     drawPlanEditor();
   };
 }
 planDlg.querySelector('[data-save]').onclick=()=>commitPlan(false);
 planDlg.querySelector('[data-release]').onclick=()=>commitPlan(true);
}
async function commitPlan(release){
 if(editLoading)return;
 gatherPlan();
 if(focus()!==editProject){planDlg.close();notify('Projektet har ändrats. Öppna rätt produktionsplan.');return;}
 const message=planDlg.querySelector('#pw13PlanMessage');
 editLoading=true;planDlg.querySelectorAll('button').forEach(b=>b.disabled=true);
 try{
   const result=await safeApi('/api/pw-v0133/plan/'+(release?'release':'save'),{
     project:editProject,plan_id:editId,revision:editRevision,
     steps:editSteps.map(x=>({id:x.id,title:x.title,instruction:x.instruction,
       priority:x.priority,assigned_agent_id:x.assigned_agent_id,
       depends_on_order_ids:x.depends_on_order_ids}))});
   notify(result.message||'Planen har uppdaterats.');
   if(release){planDlg.close();}else{editRevision=result.revision;}
   await refreshPlan(true);
   if(!release && planDlg.open){drawPlanEditor();}
 }catch(e){message.textContent='Kunde inte spara planen: '+e.message;
   planDlg.querySelectorAll('button').forEach(b=>b.disabled=false);
 }finally{editLoading=false;}
}
window.addEventListener('pixelworks:project-changed',()=>{if(planDlg.open)planDlg.close()});
// A new game's first playable code is created by the server. Older empty games
// may request the same fixed template explicitly, without AI cost or overwrite.
const starterCard=document.createElement('section');starterCard.id='pw13Starter';
starterCard.style.cssText='margin:7px 0;padding:9px;border:2px solid #7796a2;background:#19384b;color:#f4e6c6;font:12px/1.45 system-ui,sans-serif;flex:0 0 auto;order:-6';
if(railPlan)railPlan.insertBefore(starterCard,planBox.nextSibling);
let starterBusy=false;
async function refreshStarter(){
 const slug=focus();if(!slug||!window.pixelWorksApi)return;
 try{
  const state=await safeApi('/api/pw-v0134/bootstrap?project='+encodeURIComponent(slug));
  if(slug!==focus())return;
  starterCard.replaceChildren();
  if(state.can_bootstrap){
   const title=document.createElement('strong');title.textContent='🎮 Spelet saknar första spelbara grund';starterCard.append(title);
   const info=document.createElement('p');info.textContent='Skapa en liten HTML5-startprototyp med Game Bible-koppling och lokal Git-grund. Ingen AI-kvot används.';info.style.margin='5px 0';starterCard.append(info);
   const button=document.createElement('button');button.type='button';button.textContent='🕹️ Skapa spelbar grund';
   button.style.cssText='background:#efcc76;border:2px solid #987340;color:#123249;padding:8px;cursor:pointer;font-weight:800';
   button.onclick=async()=>{
     if(starterBusy||focus()!==slug)return;
     starterBusy=true;button.disabled=true;button.textContent='Skapar spelbar grund…';
     try{const result=await safeApi('/api/pw-v0134/bootstrap',{project:slug,approval:'CREATE_PLAYABLE_START_V0134'});
       notify('Startprototyp skapad – öppna Spela för att testa.');
       await refreshStarter();
     }catch(e){notify('Ingen spelkod ändrades: '+e.message);button.disabled=false;button.textContent='🕹️ Försök skapa spelbar grund';}
     finally{starterBusy=false;}
   };
   starterCard.append(button);
  }else if(state.playable){
   const message=document.createElement('span');message.textContent='🎮 En spelbar startsida finns i detta projekt. Prova 🎮 Spela.';starterCard.append(message);
  }else{
   starterCard.style.display='none';return;
  }
  starterCard.style.display='block';
 }catch(_){starterCard.style.display='none';}
}
window.addEventListener('pixelworks:project-changed',()=>refreshStarter());
window.addEventListener('pixelworks:project-created',()=>setTimeout(refreshStarter,750));
setTimeout(refreshStarter,1200);
// v0.13.6: context-first right rail. Keep functionality behind existing menus.
function simplifyRail(){
  const access=$('#pw17-access');
  if(access)access.classList.toggle('pw13-access-granted',
    Boolean(access.textContent.includes('Studioarbete tillåtet')));
  // The old yellow banner can survive even when studio access is already granted.
  // Hide only that redundant exact message; never mask a genuine revoked-access error.
  const rail=$('.right-rail');
  if(rail){
    const granted=Boolean(access?.classList.contains('pw13-access-granted'));
    for(const node of rail.querySelectorAll('button,div,section')){
      if(node.closest('#pw17-access'))continue;
      const text=(node.textContent||'').trim().replace(/^🔒\s*/, '');
      if(text==='Studioåtkomst behövs')node.classList.toggle('pw13-superseded-access',granted);
    }
  }
  const decisions=$('#pw17-decisions');
  if(decisions){
    const actions=[...decisions.children].filter(el=>el.tagName==='BUTTON');
    const isLoading=decisions.textContent.includes('Hämtar aktuell arbetskö');
    decisions.classList.toggle('pw13-nothing-pending',!actions.length&&!isLoading&&
      !decisions.textContent.includes('⚠'));
    // Only one immediate action in the main view. Other buttons remain intact
    // and accessible in an optional native HTML details disclosure.
    if(actions.length>1){
      const more=document.createElement('details');more.className='pw13-more-decisions';
      const summary=document.createElement('summary');summary.textContent='Fler åtgärder ('+(actions.length-1)+')';
      summary.style.cssText='cursor:pointer;color:#f5d180;font-weight:750;margin:5px 0';
      more.append(summary);for(const b of actions.slice(1))more.append(b);
      decisions.append(more);
    }
  }
}
setInterval(simplifyRail,1300);setTimeout(simplifyRail,1250);
window.addEventListener('pixelworks:studio-access-changed',()=>setTimeout(simplifyRail,350));
const label=$('.brand-title .version');if(label)label.textContent='v0.13.9';
})();
