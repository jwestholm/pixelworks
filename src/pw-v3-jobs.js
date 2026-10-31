/* v3.3: real, per-job approved AI tasks for immutable personas, not legacy staff. */
(()=>{'use strict';
if(window.__PW_V33_TASKS__)return;window.__PW_V33_TASKS__=true;
const $=(q,r=document)=>r.querySelector(q);
const esc=s=>String(s??'').replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]));
const api=(path,data)=>{if(!window.pixelWorksApi)throw Error('Servern är inte ansluten');return window.pixelWorksApi(path,data)};
const base='/api/pw-v3/jobs',crewUrl='/api/pw-v3/crew';
let selection='',selectedProject='',provider='codex',view='assign',notice='',busy=false,models=null,projects=[],crew=null,chosenJob=null,feedbackDraft='';
const style=document.createElement('style');style.textContent=`
#pw33Dialog{width:min(900px,calc(100vw - 18px));max-height:calc(100dvh - 18px);overflow-y:auto;overscroll-behavior:contain;
 border:6px ridge #9f7046;background:#f6efd9;color:#213e4c;box-shadow:8px 8px #132536;padding:0;font:14px/1.45 system-ui}
#pw33Dialog:not([open]){display:none}#pw33Dialog::backdrop{background:#071825cc}
#pw33Dialog *{box-sizing:border-box}#pw33Dialog h2{font-size:23px;margin:0;color:#fff2d2}#pw33Dialog h3{margin:8px 0;color:#254b61}
#pw33Dialog header{position:sticky;top:0;background:#233f56;color:#fff;padding:14px 18px;border-bottom:4px solid #b8894e;z-index:3;display:flex;justify-content:space-between;align-items:center;gap:10px}
#pw33Dialog .pw33-body{padding:17px 20px 27px}#pw33Dialog .pw33-tabs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
#pw33Dialog button{border:2px solid #855c36;border-radius:3px;background:#f0cf84;color:#263a4a;min-height:42px;font:800 13px system-ui;padding:8px 13px;cursor:pointer}
#pw33Dialog button.primary{background:#267677;border-color:#205958;color:#fff}#pw33Dialog button.secondary{background:#e4e8dd;border-color:#7b9a98}
#pw33Dialog button:disabled{opacity:.5;cursor:not-allowed}
#pw33Dialog button:focus-visible,#pw33Dialog select:focus-visible,#pw33Dialog textarea:focus-visible{outline:3px solid #228fbc;outline-offset:2px}
#pw33Dialog select,#pw33Dialog textarea{display:block;width:100%;border:2px solid #8ba5a1;background:#fffdf4;color:#203c4a;padding:10px;margin:5px 0 14px;font:inherit;min-height:45px}
#pw33Dialog textarea{min-height:128px;resize:vertical}
#pw33Dialog .pw33-card{background:#fffdf5;border:2px solid #9fb5b1;padding:14px;margin:12px 0}
#pw33Dialog .pw33-summary{background:#e5efeb;border-left:5px solid #468f86;padding:10px 13px;margin:13px 0}
#pw33Dialog .pw33-warn{background:#fff1c4;border-left:5px solid #c38e36;padding:10px 13px;margin:13px 0}
#pw33Dialog .pw33-error{background:#ffe8e5;border-left:5px solid #c24b3e;padding:10px 13px;white-space:pre-wrap;margin:12px 0}
#pw33Dialog .pw33-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
#pw33Dialog .pw33-job{border:2px solid #b0beb5;background:white;margin:8px 0;padding:13px}
#pw33Dialog .pw33-job summary{cursor:pointer;font-weight:800}
#pw33Dialog .pw33-job pre{background:#163b50;color:#f9f6e5;padding:12px;white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.5 ui-monospace,monospace;max-height:38vh;overflow-y:auto}
#pw33Dialog .pw33-meta{color:#506b73;font-size:12px}#pw33Dialog .pw33-actions{display:flex;flex-wrap:wrap;gap:8px;padding:9px 0}
#pw33Dialog .pw33-result{white-space:pre-wrap;overflow-wrap:anywhere;background:#eef5ef;padding:12px;border:1px solid #8ba49a;max-height:40vh;overflow:auto}
#pw33Dialog label{display:block;font-weight:800}#pw33Dialog .pw33-status{font-size:12px;padding:5px 8px;background:#174455;color:#fff6d9;display:inline-block;margin:4px 0}
@media(max-width:650px){#pw33Dialog{width:100vw;max-width:none;height:100dvh;max-height:100dvh;margin:0;inset:0;border:0;box-shadow:none}
 #pw33Dialog .pw33-body{padding:12px}#pw33Dialog .pw33-row{grid-template-columns:1fr}#pw33Dialog header{padding:11px 12px}}
`;document.head.append(style);
const modal=document.createElement('dialog');modal.id='pw33Dialog';modal.setAttribute('aria-label','Verkliga AI-uppdrag');document.body.append(modal);
const dock=$('#gameDock');if(dock){const button=document.createElement('button');button.id='pw33Open';button.type='button';button.className='dock-item';button.innerHTML='<span>🧠</span>AI-uppdrag';button.onclick=()=>open();dock.append(button)}
function statusText(j){return {queued:'⏳ Köad',running:'🔵 Arbetar',review:'💌 Ditt beslut krävs',done:'✅ Godkänt',failed:'🔴 Misslyckades',rejected:'❌ Avvisat',interrupted:'⏸ Avbrutet vid omstart'}[j.state]||j.state}
function roleName(p){return p?.role_name||p?.role||'Okänd roll'}
function projectName(slug){return projects.find(x=>x.id===slug)?.name||slug}
function header(){return `<header><div><h2>🧠 AI-uppdrag</h2><small>Riktiga motorer · unika karaktärer · godkännande före körning och integration</small></div><button id="pw33Close" aria-label="Stäng och återgå till kontoret">✕</button></header>`}
function options(items,value,label,val){return items.map(item=>`<option value="${esc(val(item))}" ${val(item)===value?'selected':''}>${esc(label(item))}</option>`).join('')}
function assignHTML(){const people=crew?.people||[];const person=people.find(p=>p.person_id===selection)||people[0];
 const health=models?.providers||{},current=health[provider]||{};const score=person?.character?.skills?.[(crew?.role_skill||{})[person?.role]]??0;
 return `<div class="pw33-card"><h3>✉ Ge en anställd ett uppdrag</h3><p>Chefen får planera och föreslå. <b>Du väljer vem, vilket spel och vilken motor som faktiskt får köras.</b></p>
 <div class="pw33-row"><label>👤 Anställd<select id="pw33Person">${options(people,person?.person_id,p=>p.name+' · '+roleName(p),p=>p.person_id)}</select></label>
 <label>🎮 Arbetsprojekt<select id="pw33Project">${options(projects,selectedProject,p=>p.name,p=>p.id)}</select></label></div>
 <div class="pw33-row"><label>🧠 AI-motor<select id="pw33Provider"><option value="codex" ${provider==='codex'?'selected':''}>Codex · isolerad kodarbetsyta</option><option value="gemini" ${provider==='gemini'?'selected':''}>Gemini · textförslag</option></select></label>
 <div class="pw33-summary"><b>${esc(person?.name||'Anställd saknas')}</b><br>${esc(roleName(person))} · Rollskill ${score}/5 (spelvärde)<br><small>🔒 ${esc(person?.character?.voice||'')}</small></div></div>
 <div class="${current.available?'pw33-summary':'pw33-warn'}">${current.available?'🟢 Verifierad motor tillgänglig':'🟡 Motorn kan inte starta just nu'} · ${esc(current.model||'okänd')}<br><small>Kvot: ${esc(current.quota||'okänt')}. ${esc(current.pause_reason||'')} Ingen automatisk modelluppgradering.</small></div>
 <label>📝 Uppdrag till ${esc(person?.name||'den anställda')}<textarea id="pw33Instruction" maxlength="3000" placeholder="Beskriv ett tydligt uppdrag. Ex: Fixa felaktig sparning, skriv tester och redovisa ändrade filer."></textarea></label>
 <div class="pw33-warn">${provider==='codex'?'<b>Codex:</b> Kan ändra filer i en isolerad Git-worktree. Inget införs i huvudspelet innan du godkänner resultatet. Projektets Git måste redan vara rent och committat.':'<b>Gemini:</b> Endast textförslag. Den kan inte ändra spelkod, generera verifierade bilder eller skriva i Game Bible från detta uppdrag.'}<br><small>Personligheten påverkar uttryckssättet, aldrig verktygsbehörighet eller säkerhetsregler.</small></div>
 <button id="pw33Start" class="primary" ${current.available&&person&&projects.length?'':'disabled'}>▶ Godkänn och starta ${esc(provider.toUpperCase())}</button></div>`}
function jobsHTML(){const jobs=models?.jobs||[];return `<h3>📋 Arbetsrapporter (${jobs.length})</h3>${jobs.length?jobs.map(j=>`<article class="pw33-job"><div class="pw33-row"><div><b>${esc(j.name)} · ${esc(projectName(j.project))}</b><div class="pw33-meta">${esc(j.provider)} · ${esc(j.model)} · ${esc(j.created_at||'')}</div></div><div><span class="pw33-status">${statusText(j)}</span></div></div>
 <p><b>Uppdrag:</b> ${esc(j.task)}</p><small>${esc(j.note||'')} · Rapport: ${j.verified?'Verifierad':'Inte oberoende verifierad'} · ${j.integrated?'Införd':'Inte införd'}</small>
 ${(j.answer||j.error)?`<details><summary>📄 Visa resultat / fel</summary><div class="pw33-result">${esc(j.answer||j.error)}</div></details>`:''}
 ${j.provider==='codex'&&j.changed_files?`<details><summary>📂 Ändrade filer i isolerad Git-arbetsyta</summary><pre>${esc(j.changed_files)}</pre><small>Filnamn och Git-status är ingen kvalitetsverifiering. Granska koden innan du godkänner integrationen.</small></details>`:''}
 ${j.state==='review'?`<div class="pw33-actions"><button class="primary" data-pw33-decision="approve" data-id="${esc(j.id)}">${j.provider==='codex'?'✅ Ja – inför kod lokalt':'✅ Ja – godkänn textförslag'}</button><button data-pw33-decision="reject" data-id="${esc(j.id)}">❌ Nej</button><button class="secondary" data-pw33-decision="later" data-id="${esc(j.id)}">🤔 Kanske</button></div>`:''}
 </article>`).join(''):'<div class="pw33-summary">Inga AI-uppdrag har startats från den nya personalstudion.</div>'}`}
function render(){modal.innerHTML=header()+`<main class="pw33-body"><nav class="pw33-tabs"><button class="${view==='assign'?'primary':''}" id="pw33AssignTab">✉ Nytt uppdrag</button><button class="secondary" id="pw33ChiefLink">👔 Fråga Chefen</button><button class="${view==='jobs'?'primary':''}" id="pw33JobsTab">💌 Granska (${(models?.jobs||[]).filter(j=>j.state==='review').length})</button></nav>
 ${notice?`<p class="pw33-error" role="alert">${esc(notice)}</p>`:''}
 ${!crew?.enabled?'<div class="pw33-warn">Aktivera Pixel Works v3 och anställ först. Inga gamla personer importeras automatiskt.</div>':view==='assign'?assignHTML():jobsHTML()}</main>`;
 $('#pw33Close',modal).onclick=()=>modal.close();$('#pw33ChiefLink',modal).onclick=()=>{modal.close();window.pixelWorksV3Chief?.open()};$('#pw33AssignTab',modal).onclick=()=>{view='assign';render()};$('#pw33JobsTab',modal).onclick=()=>{view='jobs';render()};
 $('#pw33Person',modal)?.addEventListener('change',e=>{selection=e.target.value;const text=$('#pw33Instruction',modal)?.value||'';render();$('#pw33Instruction',modal).value=text});
 $('#pw33Project',modal)?.addEventListener('change',e=>selectedProject=e.target.value);
 $('#pw33Provider',modal)?.addEventListener('change',e=>{const text=$('#pw33Instruction',modal)?.value||'';provider=e.target.value;render();$('#pw33Instruction',modal).value=text});
 $('#pw33Start',modal)?.addEventListener('click',start);
 modal.querySelectorAll('[data-pw33-decision]').forEach(b=>b.onclick=()=>decide(b.dataset.id,b.dataset.pw33Decision));
}
async function refresh(){const [overview,people,projectData]=await Promise.all([api(base),api(crewUrl),api('/api/projects')]);
 models=overview;crew=people;projects=projectData.projects||[];
 if(!crew.people?.some(p=>p.person_id===selection))selection=crew.people?.[0]?.person_id||'';
 if(!projects.some(p=>p.id===selectedProject))selectedProject=projects[0]?.id||'';
 updateOfficeStatus();}
async function open(personId){if(personId&&typeof personId==='string')selection=personId;notice='';
 for(const node of ['#pw3Dialog','#pw13Dialog','#localStudioDialog','#dockDialog']){const d=$(node);if(d?.open)d.close()}
 if(!modal.open)modal.showModal();modal.innerHTML=header()+'<div class="pw33-body">Läser uppdragslistan…</div>';
 try{await refresh();render()}catch(e){notice='Kunde inte läsa AI-uppdrag: '+e.message;render()}}
function setError(error){notice='⚠ '+(error?.message||String(error));render()}
async function start(){if(busy)return;const text=$('#pw33Instruction',modal)?.value?.trim();
 if(!text||text.length<15){notice='Beskriv arbetet med minst 15 tecken.';render();return}
 const who=crew.people.find(p=>p.person_id===selection);if(!who)return setError('Välj person först');
 if(!confirm('Starta ett RIKTIGT '+provider.toUpperCase()+'-uppdrag för '+who.name+' i '+projectName(selectedProject)+'?\n\n'+
  (provider==='codex'?'Codex får ändra isolerade projektfiler; du godkänner eventuell integration separat.':'Gemini gör ett verkligt API-anrop och förbrukar kvot.')))return;
 busy=true;try{await api(base+'/start',{person_id:selection,project:selectedProject,provider,instruction:text,approval:'START_V3_REAL_JOB'});
  view='jobs';notice='✅ Uppdraget är köat. Resultatet behöver ditt beslut.';await refresh();render();
 }catch(e){setError(e)}finally{busy=false}}
async function decide(id,action){if(busy)return;const job=models.jobs.find(j=>j.id===id);if(!job)return;
 const choice=action==='approve'?'Ja':action==='reject'?'Nej':'Kanske';let feedback='';
 if(action==='reject')feedback=prompt('Feedback till '+job.name+' (frivilligt):','')??null;
 if(feedback===null)return;
 if(action==='approve'&&!confirm((job.provider==='codex'?'Föra in arbetets Git-ändringar i spelet':'Godkänna textförslaget (utan att ändra spelet)')+'?'))return;
 busy=true;try{const r=await api(base+'/decision',{job_id:id,action,feedback,approval:'PLAYER_V3_REVIEW_DECISION'});
  notice=r.message||'Beslut sparat';await refresh();render();
 }catch(e){setError(e)}finally{busy=false}}
function updateOfficeStatus(){const live=(models?.jobs||[]).filter(j=>j.state==='running'||j.state==='queued');
 const latest=new Map();for(const job of live){if(!latest.has(job.person_id))latest.set(job.person_id,job)}
 for(const node of document.querySelectorAll('#pw3OfficeAgents [data-person-id]')){
  const job=latest.get(node.dataset.personId);node.classList.toggle('working',!!job);node.classList.toggle('idle',!job);
  node.title=job?node.getAttribute('aria-label')+' · 🔵 VERKLIGT jobb i '+projectName(job.project):node.getAttribute('aria-label');
  node.style.setProperty('--status-color',job?'#49cb83':'#ecd58c');
 }}
// v3.4 uses this prefill path; NEVER starts AI itself. The v3.3 confirmation
// and backend validation remain mandatory, even for Chief recommendations.
async function prepare(proposal){
 if(!proposal||typeof proposal!=='object')return;
 await open(proposal.person_id);
 if(crew?.people?.some(p=>p.person_id===proposal.person_id))selection=proposal.person_id;
 if(projects.some(p=>p.id===proposal.project))selectedProject=proposal.project;
 if(['codex','gemini'].includes(proposal.provider))provider=proposal.provider;
 view='assign';notice='👔 Chefens förslag – granska uppdraget och godkänn själv innan någon AI körs.';
 render();const textarea=$('#pw33Instruction',modal);if(textarea)textarea.value=String(proposal.instruction||'').slice(0,3000);
}
window.pixelWorksV3Tasks={open,refresh,prepare};
window.addEventListener('pixelworks:v3-crew-changed',()=>{if(modal.open)refresh().then(render).catch(()=>{});else refresh().catch(()=>{})});
setInterval(async()=>{if(document.hidden||busy)return;try{const before=JSON.stringify((models?.jobs||[]).map(j=>[j.id,j.state]));
 const state=await api(base);models=state;updateOfficeStatus();if(modal.open&&view==='jobs'&&before!==JSON.stringify(state.jobs.map(j=>[j.id,j.state])))render();
 }catch(_){ /* Read-only polling never creates provider calls */}},3500);
})();
