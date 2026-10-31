/* Pixel Works v2.8: one global staff view from every personnel entrance.
 * Project IDs are job allocations, never employment identities.
 * Merely opening the UI never writes project data or starts an agent. */
(()=>{'use strict';
if(window.__PW_GLOBAL_PEOPLE_V28__)return;window.__PW_GLOBAL_PEOPLE_V28__=true;
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const api=(path,body)=>window.pixelWorksApi(path,body);
const live=()=>!!window.__PIXEL_WORKS_DEMO__?.model?.project?.live;
const make=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n};
let lastRoster=null,lastFilter=null,seq=0;
const css=make('style');css.textContent=`
 #pw13Dialog .pw13-projects,#pw13Dialog .pw28-project-title{display:none!important}
 #pw13Dialog .pw28-project-jump{display:none!important}
 #pw13Dialog .pw28-global-banner{background:#e2f3e6;color:#1b4850;border:2px solid #6b9c8d;
   font:700 12px/1.5 system-ui,sans-serif;padding:10px;margin:7px 0}
 #pw13Dialog .pw28-global-banner.is-pending{background:#fff1cd;border-color:#cba76c;color:#69451e}
 #pw13Dialog .pw28-global-banner.is-error{background:#fff0e9;border-color:#c38a80;color:#853431}
 #pw13Dialog #pw28PeopleHeader .pw28-actions{display:flex;flex-wrap:wrap;gap:9px;margin:7px 0 10px}
 #pw13Dialog #pw28PeopleHeader button{background:#eace89;border:2px solid #a27d50;color:#1b394e;
   min-height:41px;padding:7px 12px;font-weight:800;cursor:pointer}
 #pw13Dialog #pw28PeopleHeader button:disabled{opacity:.45;cursor:not-allowed}
 #pw13Dialog .pw28-subtitle{margin:4px 0;font:700 12px system-ui,sans-serif;color:#476775}
 #pw13Dialog .pw28-role{color:#205369;font-weight:650}
 #pw28Recruit{box-sizing:border-box;width:min(540px,calc(100vw - 12px));max-height:90dvh;
  overflow:auto;background:#fff9e9;border:7px ridge #a67a55;padding:17px;color:#16384c;
  box-shadow:6px 7px 0 #132f46;font:14px/1.5 system-ui,sans-serif}
 #pw28Recruit::backdrop{background:#09223bd0}
 #pw28Recruit label{display:grid;gap:5px;font-weight:700;margin:12px 0}
 #pw28Recruit input,#pw28Recruit select{box-sizing:border-box;width:100%;min-height:44px;
  background:white;border:2px solid #93b0b5;color:#1c4053;padding:8px;font:inherit}
 #pw28Recruit button{margin:7px 7px 0 0;min-height:44px;background:#ebcb8f;border:2px solid #967349;
  color:#1b3b51;font-weight:800;padding:8px 12px;cursor:pointer}
 #pw28Recruit button:disabled{opacity:.5}
 #pw28Recruit [role=alert]{color:#a52a29;white-space:pre-wrap}
 @media(max-width:630px){#pw28Recruit{border-width:4px;padding:9px}
  #pw13Dialog #pw28PeopleHeader .pw28-actions{flex-direction:column}}
`;document.head.append(css);
const recruitDialog=make('dialog');recruitDialog.id='pw28Recruit';recruitDialog.setAttribute('aria-label','Anställ globalt');document.body.append(recruitDialog);
function resetFilter(d){if(!d?.open)return;const project=$('#pw24-project',d),q=$('#pw24-search',d);
 if(project&&project.value!=='all'){project.value='all';project.dispatchEvent(new Event('change',{bubbles:true}))}
 if(q&&q.value){q.value='';q.dispatchEvent(new Event('input',{bubbles:true}))}}
function open(){const nav=$('#pw13StudioNav');if(!nav){window.__PIXEL_WORKS_DEMO__?.ui?.toast?.('Globala personalvyn laddas fortfarande.');return}
 const old=$('#localStudioDialog');if(old?.open)old.close();const dock=$('#dockDialog');if(dock?.open)dock.close();
 nav.click();setTimeout(()=>resetFilter($('#pw13Dialog')),140)}
window.pixelWorksGlobalPeopleOpen=open;
// All entrances share the SAME global roster. Project selection is for work.
document.addEventListener('click',ev=>{if(!live())return;
 const button=ev.target.closest('[data-dock="agents"],#hireBtn,#officeHire,.hireLocal');
 if(!button)return;ev.preventDefault();ev.stopImmediatePropagation();open()},true);
const oldHire=window.pixelWorksHireLive;
window.pixelWorksHireLive=function(slug){if(!live())return oldHire?.(slug);return open()};
const local=$('#localStudioBtn');if(local){local.textContent='🔧 Projektverktyg';local.title='Teknik och projekt – personal finns i Min studio'}
function guard(d,enabled){for(const item of $$('.pw13-card .pw24-dismiss,.pw13-card .pw13-assignment select,.pw13-card .pw13-assignment button:not(.pw28-project-jump)',d)){
 if(item.dataset.pw28OriginalDisabled===undefined)item.dataset.pw28OriginalDisabled=item.disabled?'1':'0';
 item.disabled=!enabled||item.dataset.pw28OriginalDisabled==='1';
 if(!enabled)item.title='Aktivera global arbetsmotor innan personaländringar';}}
function decorate(d){for(const card of $$('.pw13-staff .pw13-card',d)){
 if(card.dataset.pw28Done)return;card.dataset.pw28Done='1';
 for(const button of $$('.pw13-assignment button',card)){
  if(button.textContent.includes('Visa spelet')){button.classList.add('pw28-project-jump');button.hidden=true;button.tabIndex=-1}
  if(button.textContent.trim()==='↗ Tilldela'){button.textContent='↗ Byt arbetsprojekt';
    button.title='Flytta arbetsuppgifterna till valt spel – anställningen är kvar i Pixel Works'}
 }
 const role=$(':scope > small',card);if(role)role.classList.add('pw28-role');}}
async function loadStatus(panel,serial){const banner=$('.pw28-global-banner',panel);
 try{
  const data=await api('/api/pw-v027/workforce');if(!panel.isConnected||seq!==serial)return;
  panel.dataset.globalActive=data.active?'yes':'no';
  banner.className='pw28-global-banner'+(data.active?'':' is-pending');
  banner.textContent=data.active?
   `🟢 GLOBAL ARBETSMOTOR AKTIV · ${data.count} anställda. Arbetsprojekt är en tilldelning – alla personer är anställda av Pixel Works.`:
   `🟡 AKTIVERING ÅTERSTÅR. De ${data.count} personerna är registrerade, men den gamla projektmotorn används fortfarande. Välj ”Granska och aktivera global personal” nedan.`;
  $('.pw28-recruit',panel).disabled=!data.active;
  $('.pw28-activate',panel).hidden=!!data.active;
  $('.pw28-activate',panel).onclick=()=>$('#pw13Dialog .pw27-workforce button')?.click();
  $('.pw28-subtitle',panel).textContent=`🏢 ${data.count} anställda · ${data.projects.length} spel · 1 studio`;
  const byID=new Map(data.people.map(p=>[p.studio_id,p]));const project=new Map(data.projects.map(p=>[p.id,p.name]));
  for(const card of $$('.pw13-staff .pw13-card',$('#pw13Dialog'))){const p=byID.get(card.id.replace(/^pw13-card-/,''));if(!p)continue;
   const label=$(':scope > small',card);if(label)label.textContent=`${p.role||'Anställd'} · ${p.busy?'Arbetar':'Ledig'} · Arbetsprojekt: ${project.get(p.project_id)||'Inget'}`;
   const identity=$('.pw24-identity',card);if(identity)identity.textContent=`🪪 Pixel Works-ID #${p.studio_id.slice(-7)} · anställd i studion`;
  }
  const filter=$('#pw24-project',$('#pw13Dialog'))?.closest('label');
  if(filter?.firstChild?.nodeType===Node.TEXT_NODE)filter.firstChild.textContent='Arbetsprojekt (valfritt filter)';
  guard($('#pw13Dialog'),!!data.active);
 }catch(e){if(!panel.isConnected||seq!==serial)return;
  banner.className='pw28-global-banner is-error';banner.textContent='⚠ Global personalstatus kunde inte verifieras: '+String(e.message||e);
  $('.pw28-recruit',panel).disabled=true;guard($('#pw13Dialog'),false);
 }}
function recruit(){const panel=$('#pw28PeopleHeader');if(panel?.dataset.globalActive!=='yes')return;
 const title=make('h2','', '➕ Ny anställd i Pixel Works');
 const intro=make('p','', 'Personen anställs i företaget. Välj första arbetsprojekt för att registrera personen i den nuvarande uppdragsmotorn. Ingen AI-session startas.');
 const nameLabel=make('label','', 'Namn');const name=make('input');name.maxLength=35;nameLabel.append(name);
 const projectLabel=make('label','', 'Första arbetsprojekt');const project=make('select');project.id='pw28HireProject';projectLabel.append(project);
 const save=make('button','', '➕ Anställ Codex-agent');const cancel=make('button','', 'Avbryt');const msg=make('p');msg.setAttribute('role','alert');
 recruitDialog.replaceChildren(title,intro,nameLabel,projectLabel,save,cancel,msg);cancel.onclick=()=>recruitDialog.close();
 save.disabled=true;
 api('/api/pw-v027/workforce').then(data=>{if(!recruitDialog.open)return;
  for(const p of data.projects){const opt=make('option','',p.name);opt.value=p.id;project.append(opt)}
  save.disabled=project.length===0;if(!project.length)msg.textContent='Skapa ett spel först.';
 }).catch(err=>{msg.textContent=String(err.message||err)});
 save.onclick=async()=>{if(!name.value.trim()||!project.value){msg.textContent='Ange namn och arbetsprojekt.';return}
  save.disabled=cancel.disabled=true;
  try{await api('/api/projects/'+encodeURIComponent(project.value)+'/hire',{name:name.value.trim(),approval:'HIRE_CODEX_FOR_PROJECT'});
   recruitDialog.close();const roster=$('#pw13Dialog');if(roster?.open)roster.close();await window.pixelWorksRefreshLive?.();open();
   window.dispatchEvent(new Event('pixelworks:studio-changed'));
  }catch(err){msg.textContent='⚠ '+String(err.message||err);save.disabled=cancel.disabled=false;}
 };recruitDialog.showModal();name.focus();}
let updating=false;
function onRoster(){const d=$('#pw13Dialog'),roster=$('.pw13-staff',d);if(!d?.open||!roster)return;
 if(lastRoster!==roster){lastRoster=roster;seq++;
  resetFilter(d);
  for(const h of $$('h3',d))if(h.textContent.trim()==='🎮 Projekt')h.classList.add('pw28-project-title');
  const heading=$('.pw13-head h2',d);if(heading)heading.textContent='🏢 Min studio · hela personalstyrkan';
  const intro=$('.pw13-head',d)?.nextElementSibling;
  if(intro?.tagName==='P')intro.textContent='En gemensam personalstyrka för alla spel. Byt spel via Projekt-menyn. Här ser du människor och deras aktuella arbetsprojekt.';
  const panel=make('section');panel.id='pw28PeopleHeader';const banner=make('div','pw28-global-banner','Kontrollerar arbetsmotorn …');
  const subtitle=make('p','pw28-subtitle','En studio · alla personer');const actions=make('div','pw28-actions');
  const recruitButton=make('button','pw28-recruit','➕ Anställ i studion');recruitButton.disabled=true;recruitButton.onclick=recruit;
  const activate=make('button','pw28-activate','✅ Aktivera global arbetsmotor');activate.hidden=true;
  actions.append(recruitButton,activate);panel.append(banner,subtitle,actions);
  ($('.pw24-roster-tools',d)||roster).before(panel);
  loadStatus(panel,seq);
 }
 decorate(d);
 const filter=$('#pw24-project',d);if(filter&&filter!==lastFilter){lastFilter=filter;resetFilter(d)}
 const panel=$('#pw28PeopleHeader',d);if(panel?.dataset.globalActive)guard(d,panel.dataset.globalActive==='yes');
}
let scheduled=false;
function schedule(){if(scheduled)return;scheduled=true;queueMicrotask(()=>{scheduled=false;onRoster()})}
function observe(){const d=$('#pw13Dialog');if(!d)return false;
 new MutationObserver(schedule).observe(d,{childList:true,subtree:true,attributes:true,attributeFilter:['open']});schedule();return true}
if(!observe())new MutationObserver(obs=>{if(observe())obs.disconnect()}).observe(document.body,{childList:true,subtree:true});
})();
