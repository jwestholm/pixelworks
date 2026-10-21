// Local Studio Engine: same-origin only. Unavailable when opened without local server.
const $ = s => document.querySelector(s);
const esc = s => String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let token='', projects=[], info=null, current=null, jobId=null;
const LIVE_SESSION_KEY='pixelworks.activeCodexJob';
let livePollTimer=null, lastJobState='', lastEventCount=0, requestedStation='code';
let currentLiveJob=null;
window.pixelWorksCurrentJob=(slug,agentId)=>currentLiveJob?.project===slug&&(!agentId||currentLiveJob.agent_id===agentId)?currentLiveJob:null;
window.pixelWorksLatestEvent=events=>{const last=[...events].reverse().map(humanEvent).find(Boolean);return last?last.label+': '+last.detail:'Ingen tolkningsbar händelse ännu';};
let liveSpeechJobId=null,liveSpeechCount=0,liveSpeechInitialized=false,liveSpeechFresh=false;
const style=document.createElement('style');style.textContent=`
.local-dialog{width:min(690px,94vw);max-height:88vh;overflow:auto;background:#202842;color:#f3ebd4;border:4px solid #71849e;box-shadow:12px 12px 0 #101626;padding:22px;font-family:inherit;z-index:10000}
.local-dialog::backdrop{background:#070a19c9}.local-dialog h2{margin:0 0 10px;color:#f2cb79}.local-dialog h3{color:#9ce1c2}.local-dialog label{display:block;margin:12px 0 5px;font-weight:bold;font-size:13px}.local-dialog input,.local-dialog textarea,.local-dialog select{background:#121b2b;color:white;border:2px solid #7b89a2;padding:10px;box-sizing:border-box;width:100%;font:inherit}.local-dialog button{margin:6px 6px 5px 0;background:#d7b668;border:3px solid #715639;padding:10px;cursor:pointer;color:#1b2330;font-weight:bold}.local-dialog button.alt{background:#687b99;color:white}.local-dialog p,.local-dialog small{line-height:1.5}.local-dialog .log{background:#101827;color:#a6e6c5;padding:12px;max-height:200px;overflow:auto;white-space:pre-wrap;font:12px monospace}.local-dialog .error{color:#ffafaa}.local-dialog .state{padding:10px;background:#35445d}.local-dialog .line{border-top:1px solid #576781;padding:10px 0}`;
style.textContent+=`
.local-dialog{box-sizing:border-box;width:min(830px,calc(100vw - 26px));height:min(710px,calc(100dvh - 24px));max-height:calc(100dvh - 24px);padding:14px 18px;overflow:hidden;display:flex;flex-direction:column;gap:8px}
.local-dialog:not([open]){display:none}.local-dialog .local-shell-header{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-shrink:0}.local-dialog .local-shell-header h2{font-size:17px;margin:0}.local-dialog .local-shell-header button{margin:0;padding:5px 10px}.local-dialog .local-shell-info{font-size:11px;line-height:1.2;flex-shrink:0}.local-dialog .local-shell-body{min-height:0;flex:1;display:flex;flex-direction:column;gap:8px;overflow:hidden}.local-dialog .local-shell-body>h3{margin:3px 0}.local-dialog .local-shell-body>p{margin:4px 0;font-size:12px}.local-dialog .local-shell-body label{margin:4px 0;font-size:12px}.local-dialog .local-shell-body input,.local-dialog .local-shell-body select,.local-dialog .local-shell-body textarea{padding:7px}.local-dialog .local-shell-body button{padding:7px 11px;margin:2px 5px 2px 0}.local-dialog .local-screen{display:flex;flex-direction:column;gap:10px;min-height:0;flex:1}.local-dialog .local-actions{flex-shrink:0;display:flex;align-items:center;gap:8px;flex-wrap:wrap;border-top:2px solid #56677c;padding-top:8px}.local-dialog .local-cards{min-height:0;flex:1;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));grid-auto-rows:minmax(92px,1fr);gap:9px;overflow:hidden}.local-dialog .local-card{border:2px solid #71849e;padding:10px;background:#2c3854;display:flex;flex-direction:column;justify-content:space-between;min-width:0;gap:7px}.local-dialog .local-card small{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.local-dialog .local-card-actions{display:flex;gap:6px;flex-wrap:wrap}.local-dialog .local-pager{display:flex;align-items:center;gap:9px;justify-content:space-between;flex-shrink:0}.local-dialog .local-pager button:disabled{opacity:.45;cursor:not-allowed}.local-dialog .local-compact-form{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px 12px}.local-dialog .local-station-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:5px}.local-dialog .local-station-grid .task-ref{margin:0;border:1px solid #576781;padding:5px;min-width:0;font-size:11px}.local-dialog .local-note{font-size:11px;opacity:.9}.local-dialog .local-identity{display:flex;gap:12px;align-items:center;flex-wrap:wrap}.local-dialog .local-identity input{max-width:250px}.local-dialog .local-small-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}.local-dialog .local-skill-description{font-size:11px;line-height:1.3;max-height:3em;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}.local-dialog .local-card button{font-size:11px}.local-dialog .local-error{min-height:1em;color:#ffafaa}.local-dialog .local-shell-body:has(> .local-screen) > .local-screen{flex:1}.local-dialog .local-shell-body:not(:has(> .local-screen)){overflow:auto;scrollbar-gutter:stable}@media(max-width:650px){.local-dialog{padding:9px;width:calc(100vw - 12px)}.local-dialog .local-cards{grid-template-columns:1fr;grid-auto-rows:minmax(75px,1fr)}.local-dialog .local-station-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.local-dialog .local-compact-form{grid-template-columns:1fr}.local-dialog .local-shell-info{display:none}}
`;
style.textContent+=`
.station-builder .station-builder-top{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-shrink:0}.station-builder-top h3{margin:0}.station-builder-top span{font-size:12px;white-space:nowrap}.station-help{font-size:12px;line-height:1.3;margin:2px 0 6px}.station-task-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));grid-template-rows:repeat(2,minmax(0,1fr));gap:9px;flex:1;min-height:0}.local-dialog .station-task-tile{margin:0;min-width:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;font-size:13px;background:#334567;color:#ffeec0;border:3px solid #8ca6af}.station-task-tile:hover,.station-option.picked{background:#4d736d!important;border-color:#f4d587!important}.task-pixel-icon{width:36px;height:36px;flex:none;fill:currentColor;shape-rendering:crispEdges}.station-details{flex:1;min-height:0;display:flex;flex-direction:column;gap:7px;overflow:hidden}.station-details label{margin:0!important}.station-details textarea{resize:none;min-height:64px}.station-option-strip{display:flex;gap:6px;overflow-x:auto;max-width:100%;min-height:76px;padding-bottom:6px;flex-shrink:0}.local-dialog .station-option{flex:0 0 86px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:4px;margin:0;padding:5px;font-size:10px}.station-option .task-pixel-icon{width:25px;height:25px}.station-attach{cursor:pointer;border:2px dashed #a7b6b8;background:#283951;padding:10px;text-align:center;font-size:12px}.station-attach.active{background:#436960}.station-pending{display:flex;flex-wrap:wrap;gap:6px;max-height:48px;overflow:auto;font-size:11px}.station-pending span{background:#34495b;padding:3px}.station-pending button{padding:0 3px!important}.station-details details{font-size:11px}.station-ref-list{max-height:60px;overflow:auto}.station-queue{flex:1;min-height:0;overflow:auto}.station-queue .line{padding:5px 0}.station-builder .local-actions{margin-top:auto}.station-builder .local-pager button{padding:6px}@media(max-width:560px){.station-task-grid{grid-template-columns:repeat(2,minmax(0,1fr));grid-template-rows:repeat(3,minmax(0,1fr))}.station-task-tile .task-pixel-icon{width:25px;height:25px}}
`;
style.textContent+=`
/* v0.11.1.1: compact, 3-column station choices with pixel icons and no giant tiles. */
.local-dialog:has(.station-task-grid){height:min(510px,calc(100dvh - 24px))}
.station-task-grid{flex:1;grid-template-columns:repeat(3,minmax(0,1fr));grid-template-rows:repeat(3,minmax(0,76px));align-content:start;gap:6px}
.local-dialog .station-task-tile{min-height:0;padding:7px 5px;margin:0;gap:5px;font-size:11px;line-height:1.15;border-width:2px;justify-content:center;flex-direction:row;overflow:hidden}
.station-task-tile .task-pixel-icon{width:22px;height:22px;flex:none}
.station-task-tile span{text-align:left;overflow-wrap:anywhere}
@media(max-width:560px){.station-task-grid{grid-template-columns:repeat(2,minmax(0,1fr));grid-template-rows:repeat(5,minmax(0,64px))}.local-dialog:has(.station-task-grid){height:min(570px,calc(100dvh - 24px))}.local-dialog .station-task-tile{font-size:10px;padding:4px}}
`;
style.textContent+=`.task-ref{display:flex!important;align-items:center;gap:9px;font-weight:normal!important}.task-ref input{width:auto!important}.task-file{display:flex;align-items:center;gap:10px;padding:4px 10px;background:#31455a;margin-top:4px}.task-file span:nth-child(2){flex:1;overflow-wrap:anywhere}.task-file button{margin:0!important;padding:2px 8px!important}.task-attachments{border:2px solid #6c7e9e;padding:8px 12px;margin:12px 0}.task-attachments h3{margin:4px 0}.task-attachments .bible-drop{cursor:pointer;padding:14px}.bible-drop{border:3px dashed #bba46b;padding:23px;text-align:center;margin:12px 0;background:#2b3852}.bible-drop.active{background:#426d69}.bible-entries{max-height:35vh;overflow:auto}.bible-entries .line textarea{width:100%;min-height:60px}.bible-entries .line small{display:block}`;document.head.append(style);
const btn=document.createElement('button');btn.className='pixel-button secondary';btn.textContent='⚙ Lokal studio';btn.id='localStudioBtn';$('#studioBtn')?.after(btn);
const dialog=document.createElement('dialog');dialog.className='local-dialog';dialog.id='localStudioDialog';document.body.append(dialog);
const safeSlug=s=>s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,48);
function view(html){dialog.innerHTML=`<div class="local-shell-header"><h2>⚙ LOKAL STUDIO</h2><button type="button" id="localClose" class="alt" aria-label="Stäng">✕</button></div><small class="local-shell-info">Pixel Works v${info?.version||'okänd'} · autoarbete kräver aktivering</small><div class="local-shell-body">${html}</div>`;$('#localClose').onclick=()=>dialog.close();if(!dialog.open)dialog.showModal();}
async function api(path, payload){const r=await fetch(path,{method:payload?'POST':'GET',credentials:'same-origin',headers:{...(token?{'X-Pixelworks-Token':token}:{}),...(payload?{'Content-Type':'application/json'}:{})},...(payload?{body:JSON.stringify(payload)}:{})});const body=await r.json();if(!r.ok)throw Error(body.error||'HTTP '+r.status);return body;}
async function init(){try{info=await api('/api/bootstrap');token=info.token;const data=await api('/api/projects');projects=data.projects;await refreshLiveRoster();return true}catch(e){view(`<p>Spelet körs utan den lokala projektmotorn.</p><p>Starta med: <code>python3 backend/server.py</code> och öppna <b>http://127.0.0.1:8765</b>.</p><p class="error">${esc(e.message)}</p>`);return false;}}
async function refreshLiveRoster(){
  const staff={};
  for(const p of projects){try{staff[p.id]=(await api('/api/projects/'+p.id+'/staff')).staff;}catch(error){console.error('Kunde inte läsa personal för '+p.id,error);staff[p.id]=[];alert('Personal kunde inte läsas för '+p.name+': '+error.message+'\nInga personalfiler har ändrats.');}}
  if(window.pixelWorksApplyLive)window.pixelWorksApplyLive(projects,staff,Boolean(info.codex.execution_enabled));
  const version=document.querySelector('.brand-title .version');if(version)version.textContent='v'+(info.version||'okänd');const badge=document.querySelector('#agentModeBadge');if(badge){badge.textContent=info.codex.execution_enabled?'SKARPT · CODEX CLI HITTAD / INLOGGNING OKÄND':'SKARPT · CODEX SJUKSKRIVEN (CLI EJ NÅBAR)';badge.title='Kontorsuppdrag är inte verklig Codex-aktivitet förrän en Codex-session faktiskt har startats och rapporterat status.';}
}
window.pixelWorksMoveLive=async function(slug,agentId,station){
  await api('/api/projects/'+slug+'/station',{agent_id:agentId,station});
  if(station!=='cafe'){requestedStation=station;await stationOrders(slug,station,true);}
};
window.pixelWorksSkillsLive=async function(slug,agentId){
  try{
    const data=await api('/api/projects/'+slug+'/skills');
    const skills=data.skills[agentId];if(!skills)throw Error('Agentens skillprofil saknas');
    const entries=Object.entries(skills);
    let skillPage=0;
    function show(){
      const perPage=6,pages=Math.max(1,Math.ceil(entries.length/perPage));skillPage=Math.max(0,Math.min(skillPage,pages-1));
      const cards=entries.slice(skillPage*perPage,skillPage*perPage+perPage).map(([key,item])=>`<div class="local-card"><b>${esc(item.name)} · ${item.level}/5</b><span class="local-skill-description" title="${esc(item.instruction)}">${esc(item.instruction)}</span><button class="skillEdit" data-key="${esc(key)}">✎ Redigera</button></div>`).join('');
      view(`<section class="local-screen"><h3>★ SKILLS · ${esc(slug)}</h3><div class="local-note">Klicka på en skill för att redigera dess nivå och instruktion. Sparas per projekt och agent.</div><div class="local-cards" id="skillList">${cards}</div><div class="local-pager"><button class="alt" id="skillPrev" ${skillPage===0?'disabled':''}>◀ Föregående</button><span>Sida ${skillPage+1} / ${pages}</span><button class="alt" id="skillNext" ${skillPage>=pages-1?'disabled':''}>Nästa ▶</button></div><div class="local-actions"><button id="skillCustom">➕ Egen skill</button><button class="alt" id="skillClose">Stäng</button></div></section>`);
      $('#skillPrev').onclick=()=>{skillPage--;show()};$('#skillNext').onclick=()=>{skillPage++;show()};
      $('#skillCustom').onclick=()=>{view(`<h3>➕ NY SKILL</h3><label>Namn<input id="customName" maxlength="60" placeholder="Exempel: Phaser 3"></label><label>Nivå 0–5<input id="customLevel" type="number" value="3" min="0" max="5"></label><label>Instruktion<textarea id="customInstruction" rows="4" maxlength="3000" placeholder="Hur ska agenten arbeta med detta?"></textarea></label><p class="error" id="customError"></p><button id="customSave">Spara skill</button><button id="customBack" class="alt">Tillbaka</button>`);$('#customBack').onclick=show;$('#customSave').onclick=async()=>{try{const name=$('#customName').value.trim();const key='custom-'+name.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,45);if(key==='custom-')throw Error('Välj namn med bokstäver eller siffror');const r=await api('/api/projects/'+slug+'/skills',{agent_id:agentId,skill:key,name,level:Number($('#customLevel').value),instruction:$('#customInstruction').value});skills[key]=r.skill;entries.push([key,r.skill]);skillPage=Math.floor((entries.length-1)/perPage);show()}catch(e){$('#customError').textContent=e.message}}};
      $('#skillClose').onclick=()=>dialog.close();dialog.querySelectorAll('.skillEdit').forEach(b=>b.onclick=()=>edit(b.dataset.key));
    }
    function edit(key){
      const item=skills[key];
      view(`<h3>★ ${esc(item.name)}</h3><p>Projekt: ${esc(slug)} · ändringen sparas i management/SKILL_SETTINGS.json.</p><label>Skillnivå (spelprioritet 0–5)<input type="number" min="0" max="5" step="1" id="skillLevel" value="${item.level}"></label><label>Standardinstruktion<textarea id="skillInstruction" rows="8" maxlength="3000">${esc(item.instruction)}</textarea></label><p class="error" id="skillError"></p><button id="skillSave">💾 Spara för projektet</button><button class="alt" id="skillBack">Tillbaka</button>`);
      $('#skillBack').onclick=show;
      $('#skillSave').onclick=async()=>{try{const level=Number($('#skillLevel').value);const instruction=$('#skillInstruction').value;const r=await api('/api/projects/'+slug+'/skills',{agent_id:agentId,skill:key,level,instruction,...(key.startsWith('custom-')?{name:item.name}:{})});skills[key]=r.skill;const agent=window.__PIXEL_WORKS_DEMO__?.model.getAgent(agentId);if(agent){agent.skills[key]=r.skill.level;window.__PIXEL_WORKS_DEMO__.ui.renderDrawer(agent);}show();}catch(e){$('#skillError').textContent=e.message;}};
    }
    show();
  }catch(e){view('<h3>Skills kunde inte läsas</h3><p class="error">'+esc(e.message)+'</p>');}
};

// Arbetsorder: passiv projektkö, sorterad efter prioritet och manuell ordning.
let activeOrderStation=null, queueRun=null, studioAuto=null;
function dispatchOfficeStatus(message){
 const hint=document.querySelector('.office-hint-right');if(hint)hint.textContent='🤖 Autoarbete: '+message;
 const badge=document.querySelector('#studioAutoStatus');if(badge)badge.textContent=message;
}

function sortedOrders(items,station){return items.filter(o=>o.station===station).sort((a,b)=>a.priority-b.priority||items.indexOf(a)-items.indexOf(b));}
async function launchOrder(slug,order){
  const mandate=(await api('/api/projects/'+slug+'/mandate')).mandate;
  if(!mandate.enabled)throw Error('Godkänn projektmandatet i uppdragsfönstret innan du kör en hel kö.');
  const agents=(await api('/api/projects/'+slug+'/staff')).staff;
  const eligible=agents.filter(a=>a.provider==='codex'&&a.station===order.station&&(a.allowed_stations||Object.keys(STATION_FOCUS)).includes(order.station));
  if(eligible.length!==1)throw Error('Placera exakt en behörig Codex-agent vid stationen för köstart.');
  const r=await api('/api/jobs',{project:slug,station:order.station,instruction:order.instruction,attachment_ids:order.attachment_ids||[],order_id:order.id,agent_id:eligible[0].id,approval:'PROJECT_MANDATE'});
  jobId=r.job_id;currentLiveJob={id:jobId,project:slug,agent_id:eligible[0].id,agent_name:eligible[0].name,state:'queued',instruction:order.instruction,station:order.station,events:[]};
  sessionStorage.setItem(LIVE_SESSION_KEY,jobId);lastJobState='';liveSpeechFresh=true;liveSpeechInitialized=false;await pollLiveJob();await refreshOrderBadges(slug);
}
async function startQueue(slug,station){
  const all=(await api('/api/projects/'+slug+'/orders')).orders;
  const next=sortedOrders(all,station).find(o=>o.status==='waiting');
  if(!next){queueRun=null;announceLiveSpeech('Pappershögen är tom. Fikapaus!');return false;}
  queueRun={slug,station};
  await launchOrder(slug,next);
  announceLiveSpeech('Jag tar nästa arbetsorder!');
  return true;
}
// Opt-in dispatch while this browser tab remains open. The backend proposes a
// specific authorized employee; each execution still passes normal API checks.
async function stopStudioAuto(message='Autoarbete pausat'){
 studioAuto=null;
 dispatchOfficeStatus('⏸ '+message);
}
async function runStudioAuto(slug){
 if(!studioAuto||studioAuto.slug!==slug)return;
 try{
  const plan=await api('/api/projects/'+slug+'/dispatch');
  if(!plan.next){const reason=plan.workspace_busy?'Väntar på ledig arbetsyta':plan.waiting===0?'Inga väntande arbetsorder':(plan.blocked[0]?.reason||'Ingen tillgänglig behörig agent');await stopStudioAuto(reason);return;}
  const next=plan.next;
  // Server controls both station access and exclusive station ownership.
  await api('/api/projects/'+slug+'/station',{agent_id:next.agent_id,station:next.station});
  const result=await api('/api/jobs',{project:slug,station:next.station,agent_id:next.agent_id,
    instruction:next.instruction,order_id:next.order_id,attachment_ids:next.attachment_ids,
    approval:'PROJECT_MANDATE'});
  jobId=result.job_id;
  currentLiveJob={id:jobId,project:slug,agent_id:next.agent_id,agent_name:next.agent_name,
   station:next.station,instruction:next.instruction,state:'queued',events:[]};
  sessionStorage.setItem(LIVE_SESSION_KEY,jobId);lastJobState='';liveSpeechFresh=true;liveSpeechInitialized=false;
  dispatchOfficeStatus('🔴 '+next.agent_name+' arbetar vid '+next.station+' · session '+jobId);
  await refreshOrderBadges(slug);
  await pollLiveJob();
 }catch(error){await stopStudioAuto('Pausad: '+error.message);alert('Autoarbete pausat: '+error.message);}
}
async function studioAutoControls(slug){
 try{
  const plan=await api('/api/projects/'+slug+'/dispatch');
  const running=studioAuto?.slug===slug;
  const live=jobId?currentLiveJob:null;
  const jobMessage=live?.project===slug&&['queued','running'].includes(live.state)?`<p class="state">🔴 Verklig Codex-session: ${esc(live.agent_name||'Agent')} · ${esc(live.state)} · ${esc(live.id)}</p>`:'';
  const message=plan.next?'Nästa: '+plan.next.agent_name+' → '+plan.next.station+' (P'+plan.next.priority+')':
   plan.workspace_busy?'Arbetsytan är upptagen':plan.waiting+' väntande · '+(plan.blocked[0]?.reason||'Inga tillgängliga uppdrag');
  view(`<h3>🤖 STUDIO DISPATCH</h3><p>Välj <b>Självständig</b> eller <b>Specialist</b> på en anställd för att den ska kunna ta jobb. Stationsbehörigheter gäller alltid.</p><p class="state">${esc(message)}</p><p>Autoarbete körs endast medan den här webbläsarfliken är aktiv. Ett Codex-jobb per projekt; inga körningar återupptas automatiskt efter omstart.</p>${jobMessage}<p id="studioAutoStatus">${running?'▶ Autoarbete på':'⏸ Autoarbete av'}</p><button id="studioAutoToggle">${running?'⏸ Pausa nya jobb':'▶ Starta godkänd arbetskö'}</button><button id="studioLead" class="alt">👔 Arbetsledaren</button><button id="studioAutoBack" class="alt">Till kontoret</button>`);
  $('#studioAutoBack').onclick=()=>dialog.close();$('#studioLead').onclick=()=>leadStudio(slug);
  $('#studioAutoToggle').onclick=async()=>{
   if(studioAuto?.slug===slug){await stopStudioAuto();return studioAutoControls(slug);}
   const mandate=(await api('/api/projects/'+slug+'/mandate')).mandate;
   if(!mandate.enabled){alert('Ge först ett bestående projektmandat för Codex.');return;}
   if(!confirm('Starta automatiskt godkända arbetsorder i '+slug+'?\nEtt jobb i taget. Stoppa nya starter med Pausa.'))return;
   studioAuto={slug};dialog.close();dispatchOfficeStatus('⏳ söker behörig agent…');await runStudioAuto(slug);
  };
 }catch(e){view('<p class="error">'+esc(e.message)+'</p>');}
}

// Codex-arbetsledaren only proposes tasks; accepting one creates an ordinary work order.
async function leadStudio(slug){
 try{
  const staff=(await api('/api/projects/'+slug+'/staff')).staff.filter(a=>a.role_type==='lead'&&a.provider==='codex');
  const data=(await api('/api/projects/'+slug+'/lead')).plans;
  const latest=data.at(-1);
  const tasks=latest?.tasks||[];
  view(`<section class="local-screen"><h3>👔 ARBETSLEDAREN · ${esc(slug)}</h3>
   <p class="local-note">Codex läser Game Bible och skapar <b>förslag</b> – ingen kod körs eller ändras vid planering. Du godkänner varje arbetsorder.</p>
   ${staff.length?`<label>Välj arbetsledare<select id="leadAgent">${staff.map(a=>`<option value="${esc(a.id)}">${esc(a.name)}</option>`).join('')}</select></label>`:'<p class="error">Anställ eller ändra yrke till Arbetsledare (Codex) först.</p>'}
   <label>Vad vill du att studion ska uppnå?<textarea id="leadObjective" maxlength="1500" rows="3" placeholder="Exempel: Gör Bläck-Berit till en oförglömlig NPC med ett litet fiskäventyr."></textarea></label>
   <div class="local-actions"><button id="leadPlan" ${staff.length?'':'disabled'}>🧠 Be Codex planera</button><button id="leadBack" class="alt">Tillbaka</button></div>
   <p class="local-note" id="leadStatus">AI-planering kräver en uttrycklig knapptryckning. Molnmodeller är inte anslutna.</p>
   ${latest?`<h3>📋 Senaste plan · ${esc(latest.agent_name)}</h3><p>${esc(latest.summary||'Ingen sammanfattning')}</p><div class="station-queue">${tasks.map(x=>`<div class="line"><b>${esc(x.station)} · P${x.priority} · ${esc(x.state)}</b><p>${esc(x.instruction)}</p>${x.state==='proposed'?`<button data-lead="accept" data-task="${esc(x.id)}">✓ Godkänn arbetsorder</button><button class="alt" data-lead="reject" data-task="${esc(x.id)}">✕ Avvisa</button>`:''}</div>`).join('')}</div>`:''}</section>`);
  $('#leadBack').onclick=()=>studioAutoControls(slug);
  $('#leadPlan')?.addEventListener('click',async()=>{
   const objective=$('#leadObjective').value.trim();if(objective.length<10){$('#leadStatus').textContent='Beskriv målet med minst 10 tecken.';return;}
   if(!confirm('Be Codex planera detta mål i läsläge? Inga arbetsorder läggs i kön automatiskt.'))return;
   $('#leadPlan').disabled=true;$('#leadStatus').textContent='🧠 Codex planerar i läsläge…';
   try{await api('/api/projects/'+slug+'/lead',{action:'plan',objective,agent_id:$('#leadAgent').value,approval:'ASK_CODEX_TO_PLAN'});await leadStudio(slug);}
   catch(e){$('#leadStatus').textContent='⚠ '+e.message;$('#leadPlan').disabled=false;}
  });
  dialog.querySelectorAll('[data-lead]').forEach(b=>b.onclick=async()=>{
   try{const action=b.dataset.lead;if(action==='accept'&&!confirm('Lägg förslaget i projektets vanliga arbetskö?'))return;
    await api('/api/projects/'+slug+'/lead',{action,plan_id:latest.id,task_id:b.dataset.task,approval:'ACCEPT_LEAD_TASK'});
    await refreshOrderBadges(slug);await leadStudio(slug);
   }catch(e){alert('Kunde inte behandla förslaget: '+e.message)}
  });
 }catch(e){view('<p class="error">Arbetsledaren: '+esc(e.message)+'</p>')}
}
window.pixelWorksLeadStudio=leadStudio;

window.pixelWorksStudioDispatch=studioAutoControls;
// A station may eventually supply its own interface; shared work orders remain the only source of truth.
const TASK_CATALOG={
 code:[['Ny funktion','tool','Implementera en ny funktion i det befintliga spelet.'],['Ändra funktion','edit','Förbättra en befintlig funktion utan att skapa om spelet.'],['Buggfix','bug','Undersök och åtgärda ett avgränsat kodfel.'],['Prestanda','speed','Förbättra spelets prestanda och verifiera mätbart.'],['Spelsystem','game','Utveckla ett nytt sammanhängande spelsystem.'],['Eget uppdrag','plus','']],
 art:[['Skapa karaktär','person','Skapa en karaktär som passar spelets visuella stil.'],['Miljö och bakgrund','land','Skapa eller förbättra en spelmiljö och dess bakgrund.'],['Animation','spark','Lägg till eller förbättra animationer.'],['Grafik saknas','bug','Undersök varför grafiken inte visas och åtgärda orsaken.'],['Föremål','box','Skapa ett spelobjekt eller en resurs.'],['Event / scen','star','Skapa en visuell spelscen eller ett event.'],['HUD / menyer','grid','Förbättra spelets gränssnitt.'],['Eget uppdrag','plus','']],
 music:[['Bakgrundsmusik','music','Skapa eller integrera bakgrundsmusik som kan loopas.'],['Intromusik','play','Skapa eller integrera musik till spelets intro.'],['Segermusik','star','Skapa eller integrera ett segerljud.'],['Effektljud','spark','Skapa eller integrera ljud till spelarens handlingar.'],['Miljöljud','land','Skapa eller integrera miljöljud.'],['Ändra befintligt','edit','Ändra spelets befintliga ljud och uppspelning.'],['Ta bort ljud','trash','Ta bort det angivna ljudet och dess referenser på ett kontrollerat sätt.'],['Eget uppdrag','plus','']],
 qa:[['Felrapport','bug','Undersök följande fel, försök reproducera och åtgärda.'],['Vit skärm','blank','Spelet visar vit skärm. Kontrollera konsolfel och laddning och rätta orsaken.'],['Saknad grafik','eye','Spelets grafik saknas. Undersök bildreferenser och rendering.'],['Ljudproblem','music','Undersök varför ljud saknas eller fungerar fel.'],['Speltest','game','Provkör spelet och dokumentera upptäckta fel.'],['Prestanda','speed','Undersök hackningar och prestandaproblem.'],['Sparproblem','box','Undersök om spelets sparande och återläsning fungerar.'],['Eget fel','plus','']],
 voice:[['Karaktärsröst','person','Skapa eller integrera en röst till en karaktär.'],['Berättarröst','chat','Skapa eller integrera berättarröst till spelet.'],['Dialog','edit','Skriv och integrera karaktärsdialog.'],['Röstproblem','bug','Undersök fel i spelets röster och ljuduppspelning.'],['Eget uppdrag','plus','']],
 docs:[['Game Bible','book','Uppdatera Game Bible med verifierade spelbeslut.'],['Karaktärer','person','Dokumentera en karaktärs roll och interaktioner.'],['Spelmanual','book','Skapa eller uppdatera spelinstruktioner.'],['Ändringslogg','edit','Dokumentera senaste speländringar.'],['Eget uppdrag','plus','']],
 research:[['Spelidé','game','Undersök och utveckla en spelidé inom befintligt koncept.'],['Referenser','eye','Samla och analysera tillgängliga projektreferenser.'],['Balans','speed','Analysera och föreslå förbättrad spelbalans.'],['Eget uppdrag','plus','']],
 meeting:[['Nytt event','star','Planera ett nytt event som passar spelet.'],['Sidouppdrag','game','Planera ett sidouppdrag med tydlig spelmekanik.'],['Integration','tool','Samordna projektets existerande moduler.'],['Eget uppdrag','plus','']],
 lead:[['Planera produktion','book','Gör en prioriterad utvecklingsplan.'],['Fördela arbete','person','Föreslå arbetsorder och ansvariga utan att själv starta AI-jobb.'],['Granska resultat','eye','Granska befintliga rapporter och föreslå förbättringar.'],['Eget uppdrag','plus','']]
};
const TASK_OPTIONS={music:[['Jazz','music'],['Chiptune','game'],['Ambient','land'],['Orkester','star'],['Elektroniskt','spark'],['Rock','speed'],['Mysigt','heart'],['Spännande','bolt'],['Eget','plus']],art:[['Pixelart','grid'],['2D','game'],['Tecknat','star'],['Retro','play'],['Humor','heart'],['Mörkt','blank'],['Eget','plus']],qa:[['Vid uppstart','play'],['Vid klick','tool'],['Efter en stund','time'],['Slumpmässigt','spark'],['Eget','plus']]};
// Compact, offline pixel pictograms. SVGs are authored for Pixel Works; compatible with a future Pixelarticons adapter.
const TASK_PICTOGRAMS={music:['00110000','01111000','01001000','01001100','11001100','11001000','01100000','00000000'],bug:['01000100','00101000','01111100','11010110','11000110','01111100','00101000','01000100'],person:['00110000','01111000','01111000','00110000','01111000','11111100','11001100','00000000'],game:['01100110','11111111','11011011','11111111','11111111','11111111','01100110','00000000'],star:['00011000','00011000','11111111','01111110','00111100','01100110','11000011','00000000'],plus:['00011000','00011000','00011000','11111111','11111111','00011000','00011000','00000000'],book:['11111100','11000110','11000110','11000110','11000110','11000110','11111100','00000000'],eye:['00000000','00111100','01100110','11011011','11011011','01100110','00111100','00000000'],grid:['11111111','10011001','10011001','11111111','10011001','10011001','11111111','00000000'],heart:['01100110','11111111','11111111','11111111','01111110','00111100','00011000','00000000'],play:['11000000','11110000','11111100','11111111','11111100','11110000','11000000','00000000'],blank:['11111111','10000001','10111101','10100101','10111101','10000001','11111111','00000000'],box:['11111111','11000011','10100101','10011001','10100101','11000011','11111111','00000000'],land:['00000000','00011000','00111100','01111110','11111111','11011011','11000011','00000000'],edit:['00000011','00000111','00001110','00011100','00111000','01110000','11100000','00000000'],trash:['01111110','00111100','01111110','01100110','01100110','01100110','01111110','00000000'],tool:['01100110','01100110','00111100','00011000','00011000','00011000','00011000','00000000'],speed:['00011000','00111100','01100110','11000011','00011000','00110000','01100000','00000000'],spark:['10011001','01011010','00111100','11111111','00111100','01011010','10011001','00000000'],time:['00111100','01100110','11011011','11011011','11000011','01100110','00111100','00000000'],chat:['01111110','11000011','11000011','11000011','01111110','00011000','00110000','00000000'],bolt:['00110000','00110000','01111100','00111000','00111000','01100000','01100000','00000000']};
function taskIcon(key){const bits=TASK_PICTOGRAMS[key]||TASK_PICTOGRAMS.game;let shapes='';bits.forEach((line,y)=>{[...line].forEach((c,x)=>{if(c==='1')shapes+=`<rect x="${x*3}" y="${y*3}" width="3" height="3"/>`})});return `<svg class="task-pixel-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">${shapes}</svg>`;}
async function stationOrders(slug,station,placed=false){
 activeOrderStation=station;
 try{
  const all=(await api('/api/projects/'+slug+'/orders')).orders;
  const rows=sortedOrders(all,station),waiting=rows.filter(o=>o.status==='waiting');
  if(placed&&waiting.length){try{await startQueue(slug,station);return;}catch(e){view(`<p class="error">${esc(e.message)}</p><button id="backQueue">Visa kön</button>`);$('#backQueue').onclick=()=>stationOrders(slug,station);return;}}
  if(placed&&!waiting.length){await jobForm(slug,station);return;}
  const assets=(await api('/api/projects/'+slug+'/assets')).assets.filter(a=>a.station===station);
  const name=STATION_FOCUS[station]?.name||station, presets=TASK_CATALOG[station]||TASK_CATALOG.code;
  let page=0, step='choose', choice=null, selected=new Set(), custom='', draft='',pending=[],showHistory=false;
  function shell(inner,actions){view(`<section class="station-builder local-screen"><div class="station-builder-top"><h3>${esc(name)} · ${step==='choose'?'VÄLJ UPPDRAG':step==='details'?'SKAPA ARBETSORDER':'ARBETSKÖ'}</h3><span>📄 ${waiting.length} väntar</span></div>${inner}<div class="local-actions">${actions}</div></section>`);}
  function render(){
   if(step==='choose'){
    const max=9,pages=Math.max(1,Math.ceil(presets.length/max));page=Math.max(0,Math.min(page,pages-1));
    const cards=presets.slice(page*max,page*max+max).map((p,i)=>`<button type="button" class="station-task-tile" data-preset="${page*max+i}">${taskIcon(p[1])}<span>${esc(p[0])}</span></button>`).join('');
    shell(`<p class="station-help">Välj med ikoner – eller välj <b>Eget uppdrag</b> och skriv fritt.</p><div class="station-task-grid">${cards}</div><div class="local-pager"><button id="taskPrev" class="alt" ${page===0?'disabled':''}>◀ Fler val</button><span>${page+1} / ${pages}</span><button id="taskNext" class="alt" ${page===pages-1?'disabled':''}>Fler val ▶</button></div>`,`<button id="taskShowQueue" class="alt">📚 Arbetskö (${waiting.length})</button><button id="taskAuto" class="alt">🤖 Autoarbete</button><button id="taskExit" class="alt">Stäng</button>`);
    $('#taskPrev').onclick=()=>{page--;render()};$('#taskNext').onclick=()=>{page++;render()};$('#taskExit').onclick=()=>dialog.close();$('#taskAuto').onclick=()=>studioAutoControls(slug);$('#taskShowQueue').onclick=()=>{step='queue';render()};
    dialog.querySelectorAll('[data-preset]').forEach(b=>b.onclick=()=>{choice=presets[Number(b.dataset.preset)];draft=choice[2]||'';selected=new Set();step='details';render()});return;
   }
   if(step==='queue'){
    const visible=rows.filter(o=>showHistory||o.status!=='done');
    shell(`<div class="station-queue"><p>Avslutade uppdrag sparas i historiken, inte i den aktiva pappershögen.</p>${visible.map(o=>`<div class="line"><b>${o.priority===1?'🔴':o.priority===2?'🟡':'🟢'} P${o.priority} · ${esc(o.status)}</b><div>${esc(o.instruction)}</div>${o.attachment_ids?.length?`<small>📎 ${o.attachment_ids.length} bilagor</small>`:''}${o.status==='waiting'?`<div><button data-action="priority" data-id="${o.id}" data-priority="${o.priority===1?2:o.priority===2?3:1}">Prioritet</button><button data-action="move" data-id="${o.id}" data-direction="-1">↑</button><button data-action="move" data-id="${o.id}" data-direction="1">↓</button><button data-action="delete" data-id="${o.id}">Ta bort</button></div>`:''}</div>`).join('')||'<p>Inga aktiva arbetsorder.</p>'}</div>`,`<button id="queueBack">◀ Nytt uppdrag</button><button id="queueHistory" class="alt">${showHistory?'Dölj':'Visa'} historik</button><button id="queueClose" class="alt">Stäng</button><span class="local-error" id="queueError"></span>`);
    $('#queueBack').onclick=()=>{step='choose';render()};$('#queueClose').onclick=()=>dialog.close();$('#queueHistory').onclick=()=>{showHistory=!showHistory;render()};dialog.querySelectorAll('[data-action]').forEach(b=>b.onclick=async()=>{try{await api('/api/projects/'+slug+'/orders',{action:b.dataset.action,id:b.dataset.id,...(b.dataset.priority?{priority:Number(b.dataset.priority)}:{}),...(b.dataset.direction?{direction:Number(b.dataset.direction)}:{})});await refreshOrderBadges(slug);await stationOrders(slug,station);}catch(e){$('#queueError').textContent=e.message}});return;
   }
   const options=TASK_OPTIONS[station]||[];
   const pickers=options.length?`<div class="station-option-strip">${options.map(([label,icon])=>`<button type="button" data-style="${esc(label)}" class="station-option ${selected.has(label)?'picked':''}">${taskIcon(icon)}<span>${esc(label)}</span></button>`).join('')}</div>`:'';
   shell(`<div class="station-details"><p class="station-help"><b>${esc(choice?.[0]||'Eget uppdrag')}</b> · välj gärna fler egenskaper och skriv sedan vad du vill.</p>${pickers}<label>Din beskrivning<textarea id="stationInstructions" rows="3" maxlength="4000" placeholder="Berätta vad du vill skapa, ändra eller undersöka...">${esc(draft)}</textarea></label><div class="station-attach" id="stationDrop" tabindex="0" role="button">📎 Släpp filer här · klicka eller Ctrl+V</div><input type="file" id="stationFileInput" multiple hidden accept="image/*,audio/*,.pdf,.txt,.md,.json,.webm,.mp4,.mid,.midi"><div id="stationPending" class="station-pending" aria-live="polite"></div><details><summary>📚 Befintliga referenser (${assets.length})</summary><div class="station-ref-list">${assets.map(a=>`<label class="task-ref"><input type="checkbox" data-ref="${esc(a.id)}"><span>${esc(a.name)}</span></label>`).join('')||'Inga tidigare filer.'}</div></details><label>Prioritet <select id="stationPriority"><option value="1">🔴 P1 · Akut</option><option value="2" selected>🟡 P2 · Normal</option><option value="3">🟢 P3 · Låg</option></select></label><span id="stationError" class="local-error" role="status"></span></div>`,`<button id="stationBack" class="alt">◀ Tillbaka</button><button id="stationSave">📄 Lägg i arbetskö</button><button id="stationCancel" class="alt">Stäng</button>`);
   const ta=$('#stationInstructions'),picker=$('#stationFileInput'),drop=$('#stationDrop');
   function storeDraft(){draft=ta.value;}
   function displayPending(){$('#stationPending').innerHTML=pending.map((f,i)=>`<span>📎 ${esc(f.name)} <button type="button" data-remove="${i}" class="alt" aria-label="Ta bort ${esc(f.name)}">✕</button></span>`).join('');dialog.querySelectorAll('[data-remove]').forEach(b=>b.onclick=()=>{pending.splice(Number(b.dataset.remove),1);displayPending()})}
   function addFiles(files){for(const f of files){if(f.size>4*1024*1024){$('#stationError').textContent='Max 4 MB per fil: '+f.name;continue;}pending.push(f)}displayPending()}
   drop.onclick=()=>picker.click();drop.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();picker.click()}};drop.ondragover=e=>{e.preventDefault();drop.classList.add('active')};drop.ondragleave=()=>drop.classList.remove('active');drop.ondrop=e=>{e.preventDefault();drop.classList.remove('active');addFiles(e.dataTransfer.files)};
   // Listen on the full dialog: clipboard screenshots also work while the description field has focus.
   dialog.onpaste=e=>{if(!dialog.open)return;const images=[...(e.clipboardData?.items||[])].filter(i=>i.kind==='file').map(i=>i.getAsFile()).filter(f=>f&&f.type.startsWith('image/'));if(images.length){e.preventDefault();addFiles(images)}};
   picker.onchange=e=>{addFiles(e.target.files);picker.value=''};displayPending();
   dialog.querySelectorAll('[data-style]').forEach(b=>b.onclick=()=>{storeDraft();const label=b.dataset.style;if(label==='Eget'){const value=prompt('Egen egenskap (valfri):');if(value?.trim())selected.add(value.trim().slice(0,80));}else if(selected.has(label))selected.delete(label);else selected.add(label);render();});
   $('#stationBack').onclick=()=>{storeDraft();step='choose';render()};$('#stationCancel').onclick=()=>dialog.close();
   $('#stationSave').onclick=async()=>{const button=$('#stationSave');button.disabled=true;try{let instruction=ta.value.trim();if(selected.size)instruction+='\nValda egenskaper: '+[...selected].join(', ')+'.';if(instruction.length<10)throw Error('Beskriv uppdraget med minst 10 tecken.');const refs=[...dialog.querySelectorAll('[data-ref]:checked')].map(x=>x.dataset.ref);for(const file of pending){const encoded=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(String(reader.result).split(',')[1]);reader.onerror=reject;reader.readAsDataURL(file)});const uploaded=await api('/api/projects/'+slug+'/assets',{kind:'file',name:file.name,station,comment:instruction.slice(0,600),data:encoded});refs.push(uploaded.asset.id)}await api('/api/projects/'+slug+'/orders',{action:'create',station,instruction,priority:Number($('#stationPriority').value),attachment_ids:refs});await refreshOrderBadges(slug);await stationOrders(slug,station);}catch(e){$('#stationError').textContent=e.message;button.disabled=false}};
  }
  render();
 }catch(e){view(`<h3>Arbetsorder kan inte läsas</h3><p class="error">${esc(e.message)}</p>`);}
}
async function refreshOrderBadges(slug){
  if(!slug||!document.body.classList.contains('live-project'))return;
  try{
    const rows=(await api('/api/projects/'+slug+'/orders')).orders;
    for(const node of document.querySelectorAll('#stationLayer .station')){
      const count=rows.filter(o=>o.station===node.dataset.id&&o.status==='waiting').length;
      node.querySelector('.station-order-badge')?.remove();
      if(count){const badge=document.createElement('span');badge.className='station-order-badge';badge.textContent='❗📄 '+count;badge.title=count+' väntande arbetsorder – klicka för att öppna kön';node.append(badge);}
    }
  }catch(e){console.warn('Arbetsköindikator ej tillgänglig:',e.message)}
}
window.pixelWorksRefreshOrders=refreshOrderBadges;
window.pixelWorksStationOrders=stationOrders;
async function talkLive(slug,agentId){
  const render=async()=>{
    const staff=(await api('/api/projects/'+slug+'/staff')).staff;
    const agent=staff.find(a=>a.id===agentId);
    const jobs=(await api('/api/projects/'+slug+'/jobs')).jobs.filter(j=>j.agent_id===agentId);
    const record=jobs[0]||null;
    const events=(record?.events||[]).map(humanEvent).filter(Boolean);
    const name=agent?.name||'Okänd anställd';
    view(`<h3>☎ ARBETSSAMTAL · ${esc(name)}</h3><p>Motor: ${esc(agent?.provider||'okänd')} · <b>${esc(record?.state||'Ingen egen session')}</b></p>
      <div class="state"><b>Senaste egna uppdrag</b><p>${esc(record?.instruction||'Den här anställda har ingen registrerad Codex-session i den aktiva serverprocessen.')}</p></div>
      <h3>📡 Faktiska sessionshändelser · ${esc(name)}</h3><div class="log">${events.length?events.slice(-15).reverse().map(e=>esc(e.label+' – '+e.detail)).join('\n\n'):'Inga verifierade händelser för den här agenten.'}</div>
      <p class="local-note">Detta är en statusvy, inte en realtidschatt. Historiska sessioner från före serverstart syns via rapporterna.</p>
      <div class="local-actions"><button id="talkRefresh">↻ Uppdatera</button><button id="talkRaw" ${record?'':'disabled'}>Teknisk logg</button><button id="talkQueue">📄 Arbetsorder</button>${agent?.role_type==='lead'?'<button id="talkLead">👔 Planera arbete</button>':''}<button id="talkClose" class="alt">Stäng</button></div>`);
    $('#talkRefresh').onclick=render;
    $('#talkRaw').onclick=()=>{if(record){jobId=record.id;showJob();}};
    $('#talkQueue').onclick=()=>stationOrders(slug,agent?.station==='cafe'?'code':agent?.station||'code');
    $('#talkLead')?.addEventListener('click',()=>leadStudio(slug));
    $('#talkClose').onclick=()=>dialog.close();
  };await render();
}
window.pixelWorksTalkLive=talkLive;
async function offerRun(slug,station){
  const st=window.__PIXEL_WORKS_DEMO__?.model.getStation(station);
  const message=`Codex är placerad vid ${st?.name||station}. Vill du öppna uppdragsfönstret? Detta startar INGET automatiskt.`;
  await jobForm(slug);
}
async function hireScreen(slug,page=0){
  if(!info)await init();
  const roster=(await api('/api/projects/'+slug+'/staff')).staff;
  const pages=Math.max(1,Math.ceil(roster.length/4));page=Math.max(0,Math.min(page,pages-1));
  const cards=roster.slice(page*4,page*4+4).map(a=>`<div class="local-card"><div><b>👤 ${esc(a.name)}</b><br><small>${esc(a.role||'Utvecklare')} · ${esc(a.provider)} · ${esc(a.work_mode||'manual')}</small></div><div class="local-card-actions"><button data-edit-agent="${esc(a.id)}">⚙ Profil</button><button data-skill-agent="${esc(a.id)}">★ Skills</button></div></div>`).join('');
  view(`<section class="local-screen"><h3>👥 PERSONAL · ${esc(slug)}</h3><div class="local-identity"><label for="hireLiveName">Ny Codex-anställd</label><input id="hireLiveName" maxlength="35" value="Codex ${roster.length+1}" aria-label="Namn på ny agent"><button id="hireLiveYes">➕ Anställ agent</button></div><div class="local-note">${roster.length} anställda · samma lokala Codex CLI, separata roller. Högst ett skrivande uppdrag per projekt.</div><div class="local-cards">${cards||'<p>Ingen anställd ännu.</p>'}</div><div class="local-pager"><button class="alt" id="hirePrev" ${page===0?'disabled':''}>◀ Föregående</button><span>Sida ${page+1} / ${pages}</span><button class="alt" id="hireNext" ${page>=pages-1?'disabled':''}>Nästa ▶</button></div><div class="local-actions"><button id="hireAssignments">🔒 Stationsansvar</button><button class="alt" id="hireLiveBack">Stäng</button><span class="local-error" id="hireLiveError" role="status"></span></div></section>`);
  $('#hireLiveBack').onclick=()=>dialog.close();
  $('#hirePrev').onclick=()=>hireScreen(slug,page-1);$('#hireNext').onclick=()=>hireScreen(slug,page+1);
  $('#hireLiveYes').onclick=async()=>{try{const name=$('#hireLiveName').value.trim();if(!name)throw Error('Ange ett namn.');await api('/api/projects/'+slug+'/hire',{name,approval:'HIRE_CODEX_FOR_PROJECT'});await refreshLiveRoster();await hireScreen(slug,Math.floor(roster.length/4));}catch(e){$('#hireLiveError').textContent=e.message}};
  $('#hireAssignments').onclick=()=>stationAssignments(slug);
  dialog.querySelectorAll('[data-edit-agent]').forEach(b=>b.onclick=()=>editStaffProfile(slug,b.dataset.editAgent));
  dialog.querySelectorAll('[data-skill-agent]').forEach(b=>b.onclick=()=>window.pixelWorksSkillsLive(slug,b.dataset.skillAgent));
}
async function editStaffProfile(slug,id){
 const agents=(await api('/api/projects/'+slug+'/staff')).staff;const agent=agents.find(a=>a.id===id);if(!agent)return;
 const stationKeys=Object.keys(STATION_FOCUS),allowed=agent.allowed_stations||stationKeys;
 const roles=[['allround','🤖 Allroundare'],['programmer','💻 Programmerare'],['qa','🧪 QA-testare'],['artist','🎨 Grafiker'],['musician','🎵 Musiker'],['voice','🎙️ Röstproducent'],['writer','📖 Författare'],['research','🔬 Researcher'],['lead','👔 Arbetsledare']];
 view(`<section class="local-screen"><h3>⚙ REDIGERA ANSTÄLLNING · ${esc(agent.name)}</h3><div class="local-compact-form"><label>Namn<input id="profileName" maxlength="35" value="${esc(agent.name)}"></label><label>Anställd som<select id="profileRoleType">${roles.map(([id,label])=>`<option value="${id}" ${agent.role_type===id?'selected':''}>${label}</option>`).join('')}</select></label><label>Roll / titel<input id="profileRole" maxlength="60" value="${esc(agent.role||'Utvecklare')}"></label><label>Personlighet<input id="profilePersonality" maxlength="80" value="${esc(agent.personality||'Noggrann')}"></label><label>Arbetsbeteende<select id="profileMode"><option value="manual">Manuell</option><option value="specialist">Specialist (automation senare)</option><option value="autonomous">Självständig (automation senare)</option></select></label><label>Hemmabord<select id="profileHome">${stationKeys.map(st=>`<option value="${esc(st)}">${esc(STATION_FOCUS[st].name)}</option>`).join('')}</select></label></div><label>Egna arbetsinstruktioner<textarea id="profileInstructions" rows="2" maxlength="2000" placeholder="Exempel: Skriv tester för alla buggfixar.">${esc(agent.work_instructions||'')}</textarea></label><h3>🏢 Får arbeta vid</h3><div class="local-station-grid">${stationKeys.map(st=>`<label class="task-ref"><input type="checkbox" data-allowed="${esc(st)}" ${allowed.includes(st)?'checked':''}>${esc(STATION_FOCUS[st].name)}</label>`).join('')}</div><div class="local-note">Skillnivå är inte behörighet. Ändringar gäller nya arbetspass. Automatiska arbetslägen är ännu inte aktiverade.</div><div class="local-actions"><button id="profileSave">💾 Spara anställning</button><button id="profileSkills">★ Skills</button><button class="alt" id="profileBack">◀ Personal</button><span id="profileError" class="local-error" role="status"></span></div></section>`);
 $('#profileMode').value=agent.work_mode||'manual';$('#profileHome').value=agent.home_station||'code';$('#profileRoleType').value=agent.role_type||'allround';
 $('#profileBack').onclick=()=>hireScreen(slug);$('#profileSkills').onclick=()=>window.pixelWorksSkillsLive(slug,id);
 $('#profileSave').onclick=async()=>{try{await api('/api/projects/'+slug+'/staff/profile',{agent_id:id,name:$('#profileName').value,role:$('#profileRole').value,role_type:$('#profileRoleType').value,personality:$('#profilePersonality').value,work_instructions:$('#profileInstructions').value,home_station:$('#profileHome').value,work_mode:$('#profileMode').value,allowed_stations:[...dialog.querySelectorAll('[data-allowed]:checked')].map(n=>n.dataset.allowed)});await refreshLiveRoster();await hireScreen(slug);}catch(e){$('#profileError').textContent=e.message}};
}
async function stationAssignments(slug){
 const agents=(await api('/api/projects/'+slug+'/staff')).staff;
 const assignment=(await api('/api/projects/'+slug+'/assignments')).assignments;
 view(`<h3>🔒 STATIONSANSVAR</h3><p>Exklusiva stationer får bara användas av uttryckligen tilldelade anställda. Kontrolleras av servern.</p><label>Station<select id="ownerStation">${Object.entries(STATION_FOCUS).map(([k,v])=>`<option value="${esc(k)}">${esc(v.name)}</option>`).join('')}</select></label><label>Åtkomst<select id="ownerMode"><option value="open">Öppen – alla med behörighet</option><option value="exclusive">Exklusiv – endast ansvariga</option></select></label><div id="ownerCandidates"></div><p id="ownerError" class="error"></p><button id="ownerSave">💾 Spara ansvar</button><button class="alt" id="ownerBack">Personal</button>`);
 const render=()=>{const st=$('#ownerStation').value;const policy=assignment[st]||{mode:'open',agent_ids:[]};$('#ownerMode').value=policy.mode;$('#ownerCandidates').innerHTML=agents.map(a=>`<label class="task-ref"><input type="checkbox" data-owner="${esc(a.id)}" ${policy.agent_ids.includes(a.id)?'checked':''}>${esc(a.name)} · ${esc(a.role||'')}</label>`).join('')};
 $('#ownerStation').onchange=render;render();$('#ownerBack').onclick=()=>hireScreen(slug);
 $('#ownerSave').onclick=async()=>{try{const st=$('#ownerStation').value;await api('/api/projects/'+slug+'/assignments',{station:st,mode:$('#ownerMode').value,agent_ids:[...dialog.querySelectorAll('[data-owner]:checked')].map(n=>n.dataset.owner)});await stationAssignments(slug)}catch(e){$('#ownerError').textContent=e.message}};
}

async function home(){if(!await init())return;view(`<p class="state">Lagring: <b>${info.storage.verified?'SKARPT · VERIFIERAD':'EJ INITIERAD / EJ VERIFIERAD'}</b><br>Arbetsrot: <b>${esc(info.root)}</b><br>Codex CLI: <b>${info.codex.connected?esc(info.codex.codex_version||'hittad'):'ej installerad/hittad'}</b><br>Inloggning: ej kontrollerad · verklig kvot: okänt · inga uppdrag startas av att placera agenten</p><button id="setupRoot">📁 Skapa/verifiera ~/.pixelworks</button><button id="createLocal">✦ Skapa verklig projektmapp</button><h3>PROJEKT PÅ DISKEN</h3>${projects.length?projects.map(p=>`<div class="line"><b>${esc(p.name)}</b><br><small>${esc(p.id)} · ${esc(p.platform)} · ${esc(p.status)}</small><br><button class="hireLocal" data-id="${esc(p.id)}">♟ Anställ Codex</button><button class="openLocal" data-id="${esc(p.id)}">▶ Uppdrag / Codex</button></div>`).join(''):'<p>Inga lokala produktioner skapade än.</p>'}<small>Kontoret visar projekt från disken. Inga påhittade anställda visas när lokal backend är aktiv.</small>`);$('#setupRoot').onclick=async()=>{if(!confirm('Skapa och verifiera lokal projektrot: '+info.root+' ?'))return;try{await api('/api/setup',{approval:'CREATE_PIXELWORKS_HOME'});await home();}catch(e){view('<p class=\"error\">Lagring misslyckades: '+esc(e.message)+'</p><button id=\"retryLocal\">Tillbaka</button>');$('#retryLocal').onclick=home;}};$('#createLocal').onclick=createForm;document.querySelectorAll('.hireLocal').forEach(b=>b.onclick=()=>hireScreen(b.dataset.id));document.querySelectorAll('.openLocal').forEach(b=>b.onclick=()=>jobForm(b.dataset.id));}
function createForm(){view(`<h3>NY VERKLIG PRODUKTION</h3><p>Detta skapar mappar, dokument och ett lokalt Git-repository under den valda arbetsroten. Ingen AI körs.</p><label>Projektnamn<input id="localName" maxlength="90" placeholder="Rosa Grisens Äventyr"></label><label>Projekt-ID<input id="localSlug" maxlength="50" placeholder="rosa-grisens-aventyr"></label><label>Spelidé<textarea id="localIdea" rows="4" maxlength="3000" placeholder="Ett 2D-plattformsspel där en rosa gris samlar äpplen..."></textarea></label><label>Genre<input id="localGenre" value="Plattformsspel"></label><label>Plattform<select id="localPlatform"><option>Webbläsare</option><option>PC</option><option>Mobil</option></select></label><label>Prioritet<select id="localPriority"><option>Spelkänsla</option><option>Stabilitet</option><option>Grafik</option><option>Snabb leverans</option></select></label><label><input type="checkbox" id="localConsent" style="width:auto"> Jag godkänner att projektmappar och ett Git-repository skapas lokalt.</label><p id="localError" class="error"></p><button id="localCreate">Skapa projektmapp</button><button class="alt" id="localBack">Tillbaka</button>`);$('#localName').oninput=e=>{if(!$('#localSlug').dataset.edited)$('#localSlug').value=safeSlug(e.target.value)};$('#localSlug').oninput=e=>{e.target.dataset.edited='1'};$('#localBack').onclick=home;$('#localCreate').onclick=async()=>{if(!$('#localConsent').checked){$('#localError').textContent='Godkännande krävs.';return;}try{const r=await api('/api/projects',{slug:$('#localSlug').value,name:$('#localName').value,idea:$('#localIdea').value,genre:$('#localGenre').value,platform:$('#localPlatform').value,priority:$('#localPriority').value,approval:'CREATE_PROJECT_ON_DISK'});view(`<h3>Projektmappen är skapad ✓</h3><p><code>${esc(r.work)}</code></p><p>Git: ${r.git_initialized?'initierat':'git ej hittat'}</p><button id="nextLocal">Förbered Codex-uppdrag</button><button class="alt" id="homeLocal">Projektlistan</button>`);$('#nextLocal').textContent='Anställ Codex';$('#nextLocal').onclick=async()=>{await init();hireScreen(r.project.id);};$('#homeLocal').onclick=home;}catch(e){$('#localError').textContent=e.message;}};}
const STATION_FOCUS={
 code:{name:'Programmering',intro:'Fortsätt utveckla kodbasen och förbättra funktionaliteten.',prompt:'Fortsätt på det befintliga projektet i work/. Läs först README, befintlig kod och projektets GAME_BIBLE.md. Förbättra eller färdigställ nästa rimliga programmeringsuppgift utan att skapa ett nytt projekt. Testa det som går och rapportera kvarstående problem.'},
 art:{name:'Grafikverkstad',intro:'Gör spelet visuellt snyggare och mer sammanhängande.',prompt:'Fortsätt på det befintliga spelet i work/. Gör spelets grafik snyggare: förbättra sprites, färger, UI och visuellt uttryck enligt Studio Bible. Behåll spelmekaniken och skapa originalgrafik. Redovisa ändringarna och vad som återstår att granska.'},
 music:{name:'Musikstudio',intro:'Förbättra spelets musik, ljudeffekter och ljudupplevelse.',prompt:'Fortsätt på befintligt spel i work/. Förbättra musik och ljudeffekter inom tillgängliga verktyg, med tydlig ljudkontroll och utan externa assets med oklar licens. Om ljudgenerering inte är möjlig: dokumentera en konkret ljudplan och implementera säkert grundstöd.'},
 voice:{name:'Röststudio',intro:'Utveckla tal, dialoger och tillgängliga röstfunktioner.',prompt:'Fortsätt på den befintliga kodbasen i work/. Förbättra speltext, dialoger och röstfunktioner med hänsyn till tillgänglighet och rättigheter. Använd inte externa röst-API:er eller kostnadsbelagda tjänster utan särskilt godkännande.'},
 qa:{name:'QA-labb',intro:'Testa spelet och prioritera fel innan nya funktioner.',prompt:'Granska det befintliga spelet i work/. Kör säkra lokala tester som finns tillgängliga, hitta fel och dokumentera hur de återskapas. Rätta tydliga avgränsade buggar, men rapportera vad som inte kunde verifieras och föreslå nästa QA-steg.'},
 docs:{name:'Dokumentation',intro:'Förtydliga manualer och spelinstruktioner.',prompt:'Läs befintlig kod och Studio Bible. Uppdatera README, instruktioner, teknisk dokumentation och projektstatus för spelet som redan finns i work/. Skilj på implementerat, rapporterat och faktiskt testat.'},
 research:{name:'Research',intro:'Undersök alternativ och föreslå nästa utvecklingssteg.',prompt:'Undersök den befintliga kodbasen och projektets mål, föreslå förbättringar, risker och prioriteringar. Dokumentera fynd lokalt och gör inga nätverksanrop utan godkännande.'},
 meeting:{name:'Samordning',intro:'Se över integrationer och hur systemdelarna samarbetar.',prompt:'Fortsätt på projektet i work/. Granska hur dess befintliga moduler fungerar ihop, identifiera integrationsproblem och prioritera säkra förbättringar. Skapa inte en ny app; sammanfatta beslut, testresultat och nästa steg.'},
 lead:{name:'Planering',intro:'Planera det fortsatta arbetet i befintligt projekt.',prompt:'Läs Studio Bible och befintlig kodbas i work/. Skriv en konkret, prioriterad plan för nästa utvecklingssteg. Gör endast begränsade och välmotiverade kodändringar.'}
};
async function jobForm(slug,station=requestedStation){
  current=projects.find(p=>p.id===slug)||{id:slug};requestedStation=STATION_FOCUS[station]?station:'code';
  const focus={...STATION_FOCUS[requestedStation]};
  try {const roster=(await api('/api/projects/'+slug+'/staff')).staff;const agent=roster.find(a=>a.provider==='codex'&&a.station===requestedStation)||roster.find(a=>a.provider==='codex');const settings=(await api('/api/projects/'+slug+'/skills'));const key=settings.stations[requestedStation];const saved=settings.skills[agent?.id]?.[key];if(saved?.instruction)focus.prompt=saved.instruction;}catch(error){console.warn('Skillinställningar kunde inte hämtas, standardinstruktion används:',error);}
  const mandate=(await api('/api/projects/'+slug+'/mandate')).mandate;
  const available=(await api('/api/projects/'+slug+'/assets')).assets.filter(a=>a.station===requestedStation);
  view(`<h3>⚒ NYTT ARBETSPASS · ${esc(focus.name)}</h3><p><b>${esc(current.name||slug)}</b> · Fortsätt i den befintliga arbetsmappen</p><p>${esc(focus.intro)}</p><p class="state">📁 ${esc(info.root)}/projects/${esc(slug)}/work<br>Codex får bara skriva i projektets godkända arbetsyta. Ingen Git-push godkänns.</p><label>Vad vill du att Codex ska fokusera på?<textarea id="codexTask" rows="7">${esc(focus.prompt)}</textarea></label><section class="task-attachments"><h3>📎 MATERIAL TILL ${esc(focus.name).toUpperCase()}</h3><div class="bible-drop" id="taskDrop" tabindex="0">📥 Släpp bilder eller filer här · klicka för att välja · Ctrl+V för skärmbild</div><input type="file" id="taskFiles" multiple hidden accept="image/*,audio/*,.pdf,.txt,.md,.json,.webm,.mp4,.mid,.midi"><div id="taskPending" aria-live="polite"></div><label>Kommentar om materialet (valfritt)<textarea id="taskComment" rows="2" maxlength="2000" placeholder="Ex: Här syns att bakgrunden saknas. Varför?"></textarea></label><p><small>Filerna sparas i detta projekts Studio Bible-bibliotek och bifogas just detta uppdrag. Inget startar förrän du klickar Börja jobba.</small></p><div id="taskExisting">${available.length?'<b>Tidigare material vid samma bord:</b>':''}${available.map(a=>`<label class="task-ref"><input type="checkbox" data-asset="${esc(a.id)}"><span>${esc(a.name)} · ${esc((a.comment||'').slice(0,90))}</span></label>`).join('')}</div></section>${mandate.enabled?'<p class="state">✓ Projektmandat aktivt: skrivning begränsad till work/.</p>':'<label><input type="checkbox" id="runApprove" style="width:auto"> Godkänn skrivning i work/ för detta arbetspass.</label><button id="saveMandate" type="button">Ge bestående projektmandat</button>'}<p id="runError" class="error"></p><button id="runNow" ${info.codex.execution_enabled?'':'disabled'}>▶ BÖRJA JOBBA!</button><button class="alt" id="homeLocal">Tillbaka</button>${info.codex.execution_enabled?'':'<p class="error">Codex hittades inte på datorn.</p>'}`);
  $('#homeLocal').onclick=()=>dialog.close();
  const zone=$('#taskDrop'),picker=$('#taskFiles');let pending=[];
  function showPending(){const el=$('#taskPending');el.innerHTML=pending.map((f,i)=>`<div class="task-file">${f.type.startsWith('image/')?'<span>🖼️</span>':'<span>📄</span>'}<span>${esc(f.name)} (${Math.ceil(f.size/1024)} KB)</span><button type="button" class="alt" data-remove="${i}">✕</button></div>`).join('');el.querySelectorAll('[data-remove]').forEach(b=>b.onclick=()=>{pending.splice(Number(b.dataset.remove),1);showPending()})}
  function addFiles(files){for(const file of files){if(file.size>4*1024*1024){$('#runError').textContent='Max 4 MB per fil: '+file.name;continue}pending.push(file)}showPending()}
  zone.onclick=()=>picker.click();zone.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();picker.click()}};
  picker.onchange=e=>{addFiles(e.target.files);picker.value=''};
  zone.ondragover=e=>{e.preventDefault();zone.classList.add('active')};zone.ondragleave=()=>zone.classList.remove('active');zone.ondrop=e=>{e.preventDefault();zone.classList.remove('active');addFiles(e.dataTransfer.files)};
  dialog.onpaste=e=>{if(!dialog.open)return;const files=[...(e.clipboardData?.files||[])].filter(f=>f.type.startsWith('image/'));if(files.length){e.preventDefault();addFiles(files)}};
  if(!mandate.enabled)$('#saveMandate').onclick=async()=>{try{await api('/api/projects/'+slug+'/mandate',{enabled:true,approval:'ALLOW_CODEX_WORKSPACE_WRITE'});await jobForm(slug,station);}catch(e){$('#runError').textContent=e.message}};
  $('#runNow').onclick=async()=>{if(!mandate.enabled&&!$('#runApprove').checked){$('#runError').textContent='Godkänn skrivning för detta arbetspass först.';return;}try{const selected=[...dialog.querySelectorAll('[data-asset]:checked')].map(el=>el.dataset.asset);const comment=$('#taskComment').value.trim();for(const file of pending){const encoded=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(String(reader.result).split(',')[1]);reader.onerror=reject;reader.readAsDataURL(file)});const uploaded=await api('/api/projects/'+slug+'/assets',{kind:'file',name:file.name,station:requestedStation,comment,data:encoded});selected.push(uploaded.asset.id)}const staffRun=(await api('/api/projects/'+slug+'/staff')).staff.filter(a=>a.provider==='codex'&&a.station===requestedStation);if(staffRun.length!==1)throw Error('Placera exakt en Codex-agent vid '+requestedStation+' först.');const result=await api('/api/jobs',{project:slug,station:requestedStation,agent_id:staffRun[0].id,instruction:$('#codexTask').value,attachment_ids:selected,attachment_comment:comment,approval:mandate.enabled?'PROJECT_MANDATE':'STARTA_CODEX_I_WORK'});jobId=result.job_id;sessionStorage.setItem(LIVE_SESSION_KEY,jobId);lastEventCount=0;lastJobState='';liveSpeechFresh=true;liveSpeechInitialized=false;dialog.close();await pollLiveJob();}catch(e){$('#runError').textContent=e.message;}};
}
function humanEvent(line){
  try{
    const x=JSON.parse(line), type=x.type||'', item=x.item||{}, it=item.type||'';
    if(type==='thread.started')return {label:'Session öppnad',detail:'Codex har startat en ny arbetstråd.',kind:'info'};
    if(type==='turn.started')return {label:'Codex börjar arbeta',detail:'Ett verkligt arbetspass pågår.',kind:'working'};
    if(type==='turn.completed')return {label:'Arbetspass avslutat',detail:'Codex har avslutat sin tur. Resultatet måste granskas.',kind:'done'};
    if(type==='turn.failed')return {label:'Arbetspass misslyckades',detail:'Öppna råloggen för felsökning.',kind:'failed'};
    if(type==='item.started' && it==='command_execution')return {label:'Kör ett kommando',detail:String(item.command||'Kommando startat').slice(0,160),kind:'working'};
    if(type==='item.completed' && it==='command_execution')return {label:item.exit_code===0?'Kommando lyckades':'Kommando avslutat',detail:'Exitkod: '+(item.exit_code??'okänd'),kind:item.exit_code===0?'done':'info'};
    if(it==='agent_message' && type==='item.completed')return {label:'Codex rapporterar',detail:String(item.text||'').slice(0,320),kind:'info'};
    if(type==='item.completed' && it==='file_change')return {label:'Filer uppdaterade',detail:'Codex rapporterar filändringar. Kontrollera dem i arbetsmappen.',kind:'working'};
    if(type==='error')return {label:'Codex rapporterar fel',detail:String(x.message||'Okänt fel').slice(0,180),kind:'failed'};
  }catch{return {label:'Systemmeddelande',detail:String(line).slice(0,180),kind:'info'};}
  return null;
}
function ensureLivePanel(){
  let p=document.querySelector('#realSessionPanel');if(p)return p;
  p=document.createElement('section');p.id='realSessionPanel';p.className='pixel-panel real-session-panel';
  p.innerHTML='<div class="real-session-header"><b>📜 AKTIVITETSLOGG</b><span id="realJobState">Inget uppdrag</span></div><p id="realJobProject"></p><div id="realJobEvents" class="real-job-events"></div><button class="pixel-button compact" id="realJobDetails" type="button">📜 Visa fullständig logg</button>';
  const rail=document.querySelector('.right-rail');rail?.append(p);
  p.querySelector('#realJobDetails').onclick=showJob;
  return p;
}
// Välj en kort, sanningsenlig replik från riktiga Codex-händelser.
function liveSpeechForEvent(raw){
  let x;try{x=JSON.parse(raw)}catch{return null}
  const type=x.type||'',item=x.item||{},it=item.type||'';
  if(type==='turn.started')return ['Jag kikar på uppdraget…','info'];
  if(type==='item.started'&&it==='command_execution')return ['Jag undersöker projektet…','info'];
  if(type==='item.completed'&&it==='command_execution'&&Number(item.exit_code)!==0)return ['Oj! Ett kommando gav fel.','failed'];
  if(type==='item.completed'&&it==='file_change')return ['Jag har ändrat filer!','info'];
  if(type==='turn.failed'||type==='error')return ['Jag stötte på ett problem.','failed'];
  if(type==='turn.completed')return ['Jag är klar. Kolla rapporten!','done'];
  return null;
}
function announceLiveSpeech(message,kind='info'){
  window.pixelWorksLiveSpeech?.(message,kind,currentLiveJob?.agent_id||null);
}
function renderLiveState(result){
  currentLiveJob=result;
  const p=ensureLivePanel(),state=result.state||'okänt';
  const demo=window.__PIXEL_WORKS_DEMO__;if(demo?.model?.project?.live && demo.ui.selectedAgentId){const a=demo.model.getAgent(demo.ui.selectedAgentId);if(a)demo.ui.renderDrawer(a);}
  p.querySelector('#realJobState').textContent=({queued:'I kö',running:'ARBETAR',done:'Avslutat – granska',failed:'MISSLYCKADES'})[state]||state;
  p.querySelector('#realJobProject').textContent=(result.agent_name||'Okänd anställd')+' · Codex CLI · '+(result.project||'okänt')+' · Session '+(result.id||jobId);
  // Serverns råhändelser har ordning; annonsera bara NYA händelser.
  // Efter omladdning spelas inte gammal historik upp som färska repliker.
  const rawEvents=result.events||[];
  if(liveSpeechJobId!==result.id){liveSpeechJobId=result.id;liveSpeechCount=0;liveSpeechInitialized=false;}
  if(!liveSpeechInitialized){
    // Nystartat uppdrag (sessionen startade i denna vy) får sina första händelser.
    // Återupptagen session hoppar över historik för att undvika vilseledande bubblor.
    if(!liveSpeechFresh)liveSpeechCount=rawEvents.length;
    liveSpeechInitialized=true;
  }
  if(rawEvents.length<liveSpeechCount)liveSpeechCount=0;
  const fresh=rawEvents.slice(liveSpeechCount);
  liveSpeechCount=rawEvents.length;
  const candidates=fresh.map(liveSpeechForEvent).filter(Boolean);
  if(candidates.length){const last=candidates.at(-1);announceLiveSpeech(last[0],last[1]);}
  else if(lastJobState!==state){
    if(state==='queued')announceLiveSpeech('Jag väntar på min tur…');
    if(state==='running' && !fresh.length)announceLiveSpeech('Nu börjar jag jobba!');
    if(state==='done' && !fresh.length)announceLiveSpeech('Uppdraget avslutat. Granska mig!','done');
    if(state==='failed' && !fresh.length)announceLiveSpeech('Något gick fel. Läs rapporten.','failed');
  }
  const lines=rawEvents.map(humanEvent).filter(Boolean);
  const root=p.querySelector('#realJobEvents');root.replaceChildren();
  for(const event of lines.slice(-7).reverse()){const div=document.createElement('div');div.className='real-event '+event.kind;const b=document.createElement('b');b.textContent=(result.agent_name||'Okänd anställd')+' · '+event.label;const small=document.createElement('small');small.textContent=event.detail;div.append(b,small);root.append(div);}
  if(!lines.length)root.textContent='Väntar på första händelsen från Codex…';
  const badge=document.querySelector('#agentModeBadge');if(badge)badge.textContent=state==='running'?'🔴 SKARPT · CODEX ARBETAR':state==='done'?'✓ SKARPT · CODEX AVSLUTAD':state==='failed'?'⚠ SKARPT · CODEX FEL':'SKARPT · CODEX '+state.toUpperCase();
  const hint=document.querySelector('.office-hint-right');if(hint)hint.textContent='Codex-session: '+state+' · kontoret visar riktiga sessionsstatusar';
  const feedTitle=document.querySelector('.event-panel .demo-tag');if(feedTitle)feedTitle.textContent='';
  if(lastJobState!==state && ['done','failed'].includes(state)){p.querySelectorAll('.real-job-notice').forEach(n=>n.remove());const notice=document.createElement('div');notice.className='real-job-notice';notice.textContent=state==='done'?'📨 '+(result.agent_name||'Agenten')+' avslutade uppdraget. Granska resultatet.':'⚠ Codex-sessionen misslyckades. Läs felloggen.';p.append(notice);}
  if(lastJobState!==state){
    if(state==='running')window.pixelWorksAgentTravel?.(result.agent_id,result.station,'running');
    if(state==='done'||state==='failed')window.pixelWorksAgentTravel?.(result.agent_id,'cafe','idle');
  }
  lastJobState=state;
}
async function pollLiveJob(){
  if(!jobId)return;
  try{const result=await api('/api/jobs/'+jobId);renderLiveState(result);
    if(result.state==='done'||result.state==='failed'){
      updateDeskBadge();refreshOrderBadges(result.project);
      if(studioAuto?.slug===result.project){
        if(result.state==='done')setTimeout(()=>{if(studioAuto?.slug===result.project)runStudioAuto(result.project);},950);
        else stopStudioAuto('Pausad efter fel – granska rapporten');
      }
      if(queueRun?.slug===result.project && queueRun?.station===result.station){
        const resume=queueRun;queueRun=null;
        if(result.state==='done'){
          // A new queued job is started only in this active browser session following placement.
          setTimeout(()=>startQueue(resume.slug,resume.station).catch(e=>{announceLiveSpeech('Kön pausad: '+e.message,'failed');}),900);
        }else announceLiveSpeech('Arbetskön pausad efter fel. Granska rapporten.','failed');
      }
    }
    if(result.state==='running'||result.state==='queued'){clearTimeout(livePollTimer);livePollTimer=setTimeout(pollLiveJob,1800);}else{sessionStorage.removeItem(LIVE_SESSION_KEY);liveSpeechFresh=false;}
  }catch(e){const p=ensureLivePanel();p.querySelector('#realJobState').textContent='Session ej tillgänglig';p.querySelector('#realJobEvents').textContent='Kan inte hämta sessionen: '+e.message+' (backend-sessioner sparas ännu inte över serveromstart).';}
}
async function playProject(slug){
  if(!slug){view('<h3>Ingen produktion vald</h3><p>Välj ett projekt först.</p>');return;}
  const tab=window.open('about:blank','_blank');
  try{
    const result=await api('/api/projects/'+encodeURIComponent(slug)+'/preview');
    if(!result.ready)throw Error(result.reason||'Ingen index.html hittades i work/');
    const url=new URL(result.url,location.origin).href;
    // Servern kontrollerar startfilen. Ingen cross-origin fetch till preview här:
    // webbläsaren kan blockera fetch trots att adressen kan öppnas i en flik.
    if(tab){tab.opener=null;tab.location.replace(url);}else{
      view('<h3>Öppna spelet</h3><p>Webbläsaren blockerade den nya fliken.</p><p><a target="_blank" rel="noopener noreferrer" href="'+esc(url)+'">🎮 Öppna spelet</a></p>');
    }
  }catch(e){if(tab)tab.close();view('<h3>Spelstart misslyckades</h3><p class="error">'+esc(e.message)+'</p><p>Kontrollera att servern kör och att projektets work/index.html finns.</p>');}
}

async function reviewJob(){
  if(!jobId){view('<p>Ingen session att granska ännu.</p>');return;}
  try{
    const r=await api('/api/jobs/'+jobId);
    const messages=(r.events||[]).map(humanEvent).filter(e=>e&&e.label==='Codex rapporterar');
    const failures=(r.events||[]).map(humanEvent).filter(e=>e&&e.kind==='failed');
    view(`<h3>📋 GRANSKA ARBETSPASSET</h3><p><b>${esc(r.project||'Projekt')}</b> · Session ${esc(r.id||jobId)} · ${esc(r.state)}</p><div class="state"><b>Vad rapporterar Codex?</b><p>${esc(messages.at(-1)?.detail||'Ingen sammanfattning från agenten finns. Läs råloggen.')}</p></div><div class="state"><b>Verifieringsläge</b><p>En avslutad session är INTE samma sak som ett godkänt spelbygge. Kontrollera ändrade filer, kör spelet och granska tester i work/.</p><p>${failures.length?esc(failures.length+' rapporterade fel finns i händelserna.'):'Inga explicita fel identifierade i visade händelser; oberoende test ännu okänt.'}</p></div><p>Föreslagen granskning: öppna projektets work/, läs README och prova spelet. Skriv eventuella förbättringar vid relevant station.</p><button id="reviewPlay">🎮 SPELA / ÖPPNA APP</button><button id="reviewRaw">Visa teknisk logg</button><button class="alt" id="reviewClose">Till kontoret</button>`);
    $('#reviewPlay').onclick=()=>playProject(r.project);$('#reviewRaw').onclick=showJob;$('#reviewClose').onclick=()=>dialog.close();
  }catch(e){view('<p class="error">Granskning kunde inte läsas: '+esc(e.message)+'</p>');}
}
async function showJob(){
  if(!jobId){view('<p>Ingen verklig session är vald.</p>');return;}
  let result;try{result=await api('/api/jobs/'+jobId);}catch(e){view('<p class="error">'+esc(e.message)+'</p>');return;}
  view('<h3>CODEX · SESSION '+esc(jobId)+'</h3><p class="state">Status: '+esc(result.state)+'</p><p>Det här är teknisk rådata. Sammanfattningen visas direkt i spelets högra panel.</p><div class="log">'+esc((result.events||[]).slice(-60).join('\n')||'Inga händelser.')+'</div><button id="closeJobLog" class="alt">Tillbaka till spelet</button>');
  $('#closeJobLog').onclick=()=>dialog.close();
}

btn.onclick=home;
// Always-visible play affordance: also works after refreshing the page or finishing a job.
const playNav=document.createElement('button');
playNav.id='playProjectBtn';playNav.type='button';playNav.className='pixel-button';
playNav.textContent='🎮 Spela';playNav.title='Öppna projektets färdiga webbsida i en separat lokal förhandsvisning';
document.querySelector('.game-actions')?.appendChild(playNav);
playNav.addEventListener('click',()=>{
  const id=document.querySelector('#projectSelect')?.value;
  if(!projects.some(project=>project.id===id)){
    view('<h3>Inget skarpt projekt valt</h3><p>Välj en produktion som finns sparad på disk.</p>');return;
  }
  playProject(id);
});

// The real-production bridge used by the game's regular New Production wizard.
window.pixelWorksCreateLive = async function(d) {
  if(!token) { const ok=await init(); if(!ok) throw Error('Lokala backend-servern saknas. Starta python3 backend/server.py och öppna localhost:8765.'); }
  const name=(d.name||'').trim();
  const slug=safeSlug(name);
  if(!name || slug.length<2) throw Error('Ange ett projektnamn på minst två tecken.');
  const root=info.root;
  if(!confirm('SKARPT: Skapa projekt, dokument och lokalt Git-repo under\n'+root+'/projects/'+slug+'\n\nDetta skriver filer på din dator. Fortsätt?')) throw Error('Avbrutet – inga projektfiler skapades.');
  const payload={slug,name,idea:d.description,genre:d.genre,platform:d.platform,priority:d.priority,creator:d.creator||{},weights:d.weights||{},areas:d.areas||[],approval:'CREATE_PROJECT_ON_DISK'};
  const created=await api('/api/projects',payload);
  if(!created.verified) throw Error('Backend kunde inte verifiera projektlagringen.');
  const checked=await api('/api/projects/'+slug);
  if(!checked.verified || checked.path!==created.path) throw Error('Projektfilerna kunde inte läsas tillbaka från disk.');
  current=checked.project;
  return checked;
};

async function refreshStorageBadge(){const badge=document.querySelector('#storageLiveStatus');if(!badge)return;try{const result=await api('/api/bootstrap');badge.textContent=result.storage.verified?'📁 SKARPT: LAGRING VERIFIERAD':'📁 LAGRING EJ INITIERAD';badge.style.borderColor=result.storage.verified?'#6ccf9a':'#f0ab77';}catch{badge.textContent='📁 OFFLINE: INGEN DISKLAGRING';badge.style.borderColor='#e78e81';}}
refreshStorageBadge();

async function autoloadLive(){try{info=await api('/api/bootstrap');token=info.token;projects=(await api('/api/projects')).projects;await refreshLiveRoster();await updateDeskBadge();if(projects.length)await refreshOrderBadges(window.__PIXEL_WORKS_DEMO__?.model.activeProjectId||projects[0].id);}catch(e){console.info('Lokal studio offline. DEMO-världar visas.',e.message);}}
setTimeout(async()=>{await autoloadLive();const saved=sessionStorage.getItem(LIVE_SESSION_KEY);if(saved){jobId=saved;pollLiveJob();}},0);

window.pixelWorksRefreshLive=async()=>{await init();};
window.pixelWorksEditStaffLive=async (slug,id)=>{if(!info)await init();await editStaffProfile(slug,id)};
window.pixelWorksHireLive=async slug=>{if(!info)await init();await hireScreen(slug);};


// Real project inbox. No demo entries and no automatic permission grants.
async function liveInbox(){
  const slug=document.querySelector('#projectSelect')?.value;
  if(!projects.some(p=>p.id===slug))return;
  try{
    const data=await api('/api/projects/'+slug+'/reports');
    const reports=data.reports.filter(x=>!x.archived);
    view('<h3>📬 DITT SKRIVBORD · RIKTIGA RAPPORTER</h3>'+
      (reports.length?reports.map(r=>'<div class="line"><b>'+esc(r.read?'📄':'❗')+' '+esc(r.title)+'</b><br><small>'+esc(r.created_at)+' · '+esc(r.state)+' · verifierat: NEJ</small><br><button data-report="'+esc(r.id)+'">Läs rapport</button></div>').join(''):'<p>Inga nya verkliga Codex-rapporter ännu.</p>')+
      '<button class="alt" id="leaveInbox">Till kontoret</button>');
    $('#leaveInbox').onclick=()=>dialog.close();
    dialog.querySelectorAll('[data-report]').forEach(b=>b.onclick=()=>showLiveReport(slug,b.dataset.report));
  }catch(e){view('<p class="error">Rapporter kunde inte läsas: '+esc(e.message)+'</p>');}
}
async function showLiveReport(slug,rid){
  try{
    const found=(await api('/api/projects/'+slug+'/reports')).reports.find(r=>r.id===rid);
    if(!found)throw Error('Rapporten finns inte längre');
    await api('/api/projects/'+slug+'/reports/'+rid,{action:'read'});
    view('<h3>📄 '+esc(found.title)+'</h3><div class="state"><small>'+esc(found.created_at)+' · session '+esc(rid)+'</small><p>'+esc(found.summary)+'</p></div><p>Status: '+esc(found.state)+' · Exitkod: '+esc(found.exit_code??'okänd')+'</p><p><b>Verifiering: NEJ.</b> Codex rapport har ännu inte oberoende testats.</p><button id="fromReportPlay">🎮 Spela och granska</button><button id="fromReportArchive">Arkivera rapport</button><button class="alt" id="fromReportBack">Till rapporter</button>');
    $('#fromReportPlay').onclick=()=>playProject(slug);
    $('#fromReportArchive').onclick=async()=>{await api('/api/projects/'+slug+'/reports/'+rid,{action:'archive'});await liveInbox();};
    $('#fromReportBack').onclick=liveInbox;
  }catch(e){view('<p class="error">'+esc(e.message)+'</p>');}
}
async function updateDeskBadge(){
  const slug=document.querySelector('#projectSelect')?.value;
  if(!projects.some(p=>p.id===slug))return;
  try{const {reports}=await api('/api/projects/'+slug+'/reports');const unread=reports.filter(r=>!r.read&&!r.archived).length;
    const alert=document.querySelector('#deskAlert');if(alert)alert.hidden=!unread;
    const count=document.querySelector('#mailCount');if(count){count.hidden=!unread;count.textContent=unread;}
  }catch(e){console.warn('Rapportstatus saknas:',e.message);}
}
['#deskBtn','#officeDesk'].forEach(sel=>document.querySelector(sel)?.addEventListener('click',event=>{
  const slug=document.querySelector('#projectSelect')?.value;
  if(projects.some(p=>p.id===slug)){event.stopImmediatePropagation();event.preventDefault();liveInbox();}
},true));
document.querySelector('#projectSelect')?.addEventListener('change',()=>setTimeout(updateDeskBadge,150));
setInterval(updateDeskBadge,6500);


// Studio Bible / station inbox – actual files in studio-bible, no automatic Codex execution.
const bibleButton=document.createElement('button');bibleButton.className='pixel-button secondary';bibleButton.textContent='📖 Game Bible';bibleButton.id='bibleButton';btn.after(bibleButton);
async function activeSlug(){if(!info && !await init())return null;const choice=document.querySelector('#projectSelect');const slug=choice?.value||window.__PIXEL_WORKS_DEMO__?.model?.project?.id;return projects.some(p=>p.id===slug)?slug:(projects[0]?.id||null)}
async function bibleView(slug,station=null){
 const response=await api('/api/projects/'+slug+'/assets');const assets=response.assets.filter(a=>!station||a.station===station);
 view(`<h3>📖 STUDIO BIBLE · ${esc(slug)}</h3><p>Projektlokalt material. Släpp filer på ett bord eller lägg till här. Material startar aldrig Codex automatiskt.</p><div class="bible-drop" id="bibleDrop" tabindex="0">📥 Släpp filer här eller klistra in en bild (Ctrl+V)</div><input id="bibleFiles" type="file" multiple accept="image/png,image/jpeg,image/webp,image/gif,audio/mpeg,audio/wav,audio/ogg,audio/midi,.mid,.midi,.pdf,.txt,.md,.json,.webm,.mp4"><label>Arbetsstation<select id="bibleStation">${Object.keys(STATION_FOCUS).map(k=>`<option value="${k}" ${station===k?'selected':''}>${esc(STATION_FOCUS[k].name)}</option>`).join('')}</select></label><label>Kommentar / instruktion<textarea id="bibleComment" rows="3"></textarea></label><button id="bibleSaveFiles">Spara material</button><button id="bibleSaveNote">Spara idé / anteckning</button><p class="error" id="bibleError"></p><h3>📌 Projektmaterial (${assets.length})</h3><div class="bible-entries">${assets.map(a=>`<div class="line"><b>${esc(a.name)}</b> · ${esc(a.station)} · ${esc(a.status)}<small>${esc(a.file||'Anteckning')} ${a.size?'('+Math.round(a.size/1024)+' kB)':''}</small><textarea rows="2" data-comment="${a.id}">${esc(a.comment||'')}</textarea><select data-status="${a.id}">${['idea','reference','approved','rejected'].map(st=>`<option ${st===a.status?'selected':''}>${st}</option>`).join('')}</select><button data-update="${a.id}">Spara</button><button data-delete="${a.id}" class="alt">Ta bort</button></div>`).join('')||'<p>Inget material ännu.</p>'}</div>`);
 const stationSelect=$('#bibleStation');let pending=[];
 const collect=files=>{pending=[...files];$('#bibleError').textContent=pending.length+' fil(er) valda.';};
 $('#bibleFiles').onchange=e=>collect(e.target.files);
 const zone=$('#bibleDrop');zone.ondragover=e=>{e.preventDefault();zone.classList.add('active')};zone.ondragleave=()=>zone.classList.remove('active');zone.ondrop=e=>{e.preventDefault();zone.classList.remove('active');collect(e.dataTransfer.files)};
 zone.onpaste=e=>{const files=[...e.clipboardData.items].filter(i=>i.kind==='file').map(i=>i.getAsFile()).filter(Boolean);if(files.length){e.preventDefault();collect(files)}};
 const save=async()=>{try{for(const file of pending){if(file.size>4*1024*1024)throw Error('Max 4 MB per fil: '+file.name);const b64=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result.split(',')[1]);reader.onerror=reject;reader.readAsDataURL(file)});await api('/api/projects/'+slug+'/assets',{kind:'file',name:file.name,station:stationSelect.value,comment:$('#bibleComment').value,data:b64});}await bibleView(slug,station);}catch(e){$('#bibleError').textContent=e.message}};
 $('#bibleSaveFiles').onclick=()=>{if(!pending.length){$('#bibleError').textContent='Välj en fil först.';return;}save()};
 $('#bibleSaveNote').onclick=async()=>{try{await api('/api/projects/'+slug+'/assets',{kind:'note',name:'Idé / instruktion',station:stationSelect.value,comment:$('#bibleComment').value});await bibleView(slug,station)}catch(e){$('#bibleError').textContent=e.message}};
 dialog.querySelectorAll('[data-update]').forEach(b=>b.onclick=async()=>{const id=b.dataset.update;try{await api('/api/projects/'+slug+'/assets',{kind:'update',action:'edit',id,comment:dialog.querySelector('[data-comment="'+id+'"]').value,status:dialog.querySelector('[data-status="'+id+'"]').value});await bibleView(slug,station)}catch(e){$('#bibleError').textContent=e.message}});
 dialog.querySelectorAll('[data-delete]').forEach(b=>b.onclick=async()=>{if(!confirm('Ta bort denna referens från Game Bible?'))return;try{await api('/api/projects/'+slug+'/assets',{kind:'update',action:'delete',id:b.dataset.delete});await bibleView(slug,station)}catch(e){$('#bibleError').textContent=e.message}});
}
bibleButton.onclick=async()=>{try{const slug=await activeSlug();if(slug)await bibleView(slug);else view('<p>Skapa ett projekt först.</p>')}catch(e){view('<p class="error">'+esc(e.message)+'</p>')}};
// Drop files onto a station; do not intercept agent dragging.
const office=document.querySelector('#stationLayer');if(office){office.addEventListener('dragover',e=>{if(e.dataTransfer.types.includes('Files'))e.preventDefault()});office.addEventListener('drop',async e=>{if(!e.dataTransfer.files?.length)return;e.preventDefault();const st=e.target.closest('.station');if(!st)return;try{const slug=await activeSlug();await bibleView(slug,st.dataset.id);const fileInput=$('#bibleFiles');fileInput.files=e.dataTransfer.files;fileInput.dispatchEvent(new Event('change'));}catch(error){view('<p class="error">'+esc(error.message)+'</p>')}})}

const orderBadgeStyle=document.createElement("style");orderBadgeStyle.textContent=`.station{overflow:visible!important}.station-order-badge{position:absolute;z-index:30;right:-8px;top:-24px;min-width:35px;padding:3px 5px;background:#ffe6a1;border:2px solid #623c49;color:#3a2439;box-shadow:2px 2px 0 #2b203f;font-size:11px;font-weight:900;white-space:nowrap;pointer-events:none}`;document.head.append(orderBadgeStyle);
