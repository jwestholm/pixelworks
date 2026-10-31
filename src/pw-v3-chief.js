/* Pixel Works 3.4 — Chefen recommends; the player always approves real runs. */
(()=>{'use strict';
if(window.__PW_V34_CHIEF__)return;window.__PW_V34_CHIEF__=true;
const $=(q,r=document)=>r.querySelector(q);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const api=(u,d)=>{if(typeof window.pixelWorksApi!=='function')throw Error('Pixel Works backend saknas');return window.pixelWorksApi(u,d)};
const categories=[['coding','💻 Programmering'],['art','🎨 Grafik/pixelart'],['music','🎵 Musik/ljud'],['qa','🧪 QA/testning'],['writing','✍️ Story/dialog'],['research','🔎 Research'],['design','🎮 Speldesign'],['planning','📋 Planering']];
let projects=[],project='',category='coding',provider='codex',task='',proposal=null,notification='',loading=false,chosen='',more=false;
const style=document.createElement('style');style.textContent=`
#pw34Dialog{width:min(930px,calc(100vw - 24px));max-height:calc(100dvh - 20px);margin:auto;overflow-y:auto;overscroll-behavior:contain;border:7px ridge #a3754a;background:#f3edda;color:#173847;padding:0;box-shadow:7px 8px 0 #091b25;font:14px/1.45 system-ui,sans-serif}
#pw34Dialog:not([open]){display:none}#pw34Dialog::backdrop{background:#071624d9}
#pw34Dialog *{box-sizing:border-box}#pw34Dialog header{position:sticky;top:0;z-index:3;padding:14px 18px;display:flex;justify-content:space-between;align-items:center;gap:12px;background:#243e4f;color:#fff4d7;border-bottom:4px solid #b9854d}
#pw34Dialog header h2{font-size:24px;margin:0;color:inherit}#pw34Dialog header small{display:block;color:#c7e1e2}
#pw34Dialog .pw34-body{padding:16px 20px 28px}#pw34Dialog .pw34-head{background:#e4efeb;border:2px solid #83a6a3;padding:14px;display:flex;gap:14px;align-items:center}
#pw34Dialog .pw34-face{min-width:60px;height:66px;display:grid;place-items:center;font-size:36px;background:#2b4e5a;border:3px solid #a87e4b;box-shadow:3px 3px #1d3845}
#pw34Dialog h3{margin:5px 0 9px;color:#244f5b}#pw34Dialog p{margin:7px 0}#pw34Dialog .pw34-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
#pw34Dialog label{display:block;font-weight:800;margin-top:12px}#pw34Dialog select,#pw34Dialog textarea{width:100%;display:block;padding:10px;border:2px solid #789eaa;border-radius:2px;background:#fffefa;color:#193b4c;font:inherit;margin-top:5px}
#pw34Dialog textarea{min-height:110px;resize:vertical}#pw34Dialog button{border:2px solid #805d37;border-radius:2px;background:#f0ce89;color:#183748;padding:9px 13px;min-height:43px;cursor:pointer;font:800 13px system-ui}
#pw34Dialog button.primary{background:#277b77;border-color:#235c59;color:#fff}#pw34Dialog button:disabled{opacity:.45;cursor:not-allowed}
#pw34Dialog button:focus-visible,#pw34Dialog select:focus-visible,#pw34Dialog textarea:focus-visible{outline:3px solid #168ac5;outline-offset:2px}
#pw34Dialog .pw34-card{padding:12px;margin:11px 0;background:#fffdfa;border:2px solid #b4c0b3;border-left:6px solid #7ea697}
#pw34Dialog .pw34-card:first-of-type{border-left-color:#e2af57}#pw34Dialog .pw34-card.warn{background:#fff2d4;border-left-color:#c99643}#pw34Dialog .pw34-card.blocked{background:#f1eeeb;border-left-color:#9e898a}
#pw34Dialog .pw34-row{display:flex;justify-content:space-between;gap:10px;align-items:flex-start;flex-wrap:wrap}
#pw34Dialog .pw34-tag{background:#dbe8e2;border:1px solid #8da7a5;padding:2px 7px;display:inline-block;margin:3px 4px 0 0;font-size:12px}
#pw34Dialog .pw34-note{font-size:12px;color:#4b6570}#pw34Dialog .pw34-error{background:#ffe0dc;padding:10px;border-left:5px solid #bb514b;white-space:pre-wrap}#pw34Dialog .pw34-actions{display:flex;flex-wrap:wrap;gap:9px;margin:11px 0}
@media(max-width:650px){#pw34Dialog{inset:0;width:100vw;max-width:none;height:100dvh;max-height:100dvh;border:0;margin:0;box-shadow:none}#pw34Dialog header{padding:12px}#pw34Dialog .pw34-body{padding:12px}#pw34Dialog .pw34-grid{grid-template-columns:1fr}}
`;document.head.append(style);
const modal=document.createElement('dialog');modal.id='pw34Dialog';modal.setAttribute('aria-label','Chefens uppdragsfördelning');document.body.append(modal);
const dock=$('#gameDock');if(dock){const button=document.createElement('button');button.type='button';button.id='pw34Open';button.className='dock-item';button.innerHTML='<span>👔</span>Chefen';button.onclick=()=>open();dock.append(button)}
function options(source,selected){return source.map(([id,name])=>`<option value="${esc(id)}" ${id===selected?'selected':''}>${esc(name)}</option>`).join('')}
function projectOptions(){return projects.map(p=>`<option value="${esc(p.id)}" ${p.id===project?'selected':''}>${esc(p.name)}</option>`).join('')}
function rankedHTML(){if(!proposal)return '';
 const cards=more?proposal.ranked:proposal.ranked.slice(0,3);
 return `<div class="pw34-head"><div class="pw34-face" aria-hidden="true">👔</div><div><h3>Chefen har granskat bemanningen</h3><p>${esc(proposal.chief_message)}</p><small>${esc(proposal.note)}</small></div></div>
 ${proposal.hiring_recommended?`<div class="pw34-card warn">👥 <b>Rekryteringsförslag:</b> Vi har ingen anställd specialist på det här området. Du kan ändå ge jobbet till någon annan – eller anställa först.<div class="pw34-actions"><button type="button" id="pw34Hire">🔎 Se kandidater (du anställer)</button></div></div>`:''}
 ${proposal.category==='art'||proposal.category==='music'?`<div class="pw34-card warn">⚠️ Den nya v3-pipelinen kan ännu inte generera färdiga ${proposal.category==='art'?'bildfiler':'ljudfiler'}. Förslag här gäller text, koncept eller Codex-kod, inte färdig media.</div>`:''}
 ${!proposal.engine_available?`<div class="pw34-card warn">🟡 <b>${esc(proposal.provider.toUpperCase())} är inte körklar.</b> Du kan se rankningen men får inte starta förrän anslutning/Git är verifierad.</div>`:''}
 <h3>👥 Chefens rekommenderade personal</h3>${cards.map((p,i)=>`<article class="pw34-card ${p.can_start?'':'blocked'}" data-person="${esc(p.person_id)}"><div class="pw34-row"><div><b>${i+1}. ${esc(p.name)}</b><div>${esc(p.role_name)} · ${esc(p.fit)}</div><small class="pw34-note">${esc(p.skill_name)} ${esc(p.level)}/5 · fiktiv kompetens</small></div><button type="button" class="${p.can_start?'primary':''}" data-pw34-choose="${esc(p.person_id)}" ${p.can_start?'':'disabled'}>${p.can_start?'✅ Välj för uppdrag':'⏸ Kan inte starta'}</button></div><p>${esc(p.reason)}</p>${p.blockers.length?`<p class="pw34-note">⚠️ ${esc(p.blockers.join(' · '))}</p>`:''}</article>`).join('')}
 ${proposal.ranked.length>3?`<button id="pw34More">${more?'Visa färre':'Visa alla '+proposal.ranked.length+' anställda'}</button>`:''}
 <div class="pw34-card"><p><b>Viktigt:</b> Chefen föreslår bara. Inga AI-anrop har gjorts. Nästa steg öppnar det befintliga godkännandefönstret, där du själv kan ändra uppdraget och godkänna körningen.</p></div>`;
}
function render(){modal.innerHTML=`<header><div><h2>👔 Chefens skrivbord</h2><small>En studio · ett team · alla dina spel</small></div><button id="pw34Close" type="button" aria-label="Stäng chefsbordet">✕</button></header>
 <main class="pw34-body"><p>Beskriv jobbet så föreslår Chefen vem som bör göra det. <b>Rangordningen bygger på spelvärden</b> – ingen AI bedömer kandidaterna här.</p>
 <div class="pw34-grid"><label>🎮 Spel<select id="pw34Project">${projectOptions()}</select></label><label>🛠️ Arbetskategori<select id="pw34Category">${options(categories,category)}</select></label></div>
 <label>🧠 Arbetsverktyg<select id="pw34Provider">${options([['codex','Codex – isolerad kodarbetsyta'],['gemini','Gemini – text och koncept']],provider)}</select></label>
 <label>✉ Vad behöver göras?<textarea id="pw34Task" maxlength="3000" placeholder="Exempel: Felsök spelsparningen och skriv tester som visar problemet.">${esc(task)}</textarea></label>
 <div class="pw34-actions"><button type="button" class="primary" id="pw34Suggest" ${loading||!projects.length?'disabled':''}>👔 Be Chefen föreslå</button><button type="button" id="pw34Review" >💌 Se AI-resultat</button></div>
 ${notification?`<p class="pw34-error" role="alert">${esc(notification)}</p>`:''}${rankedHTML()}
 </main>`;
 $('#pw34Close',modal).onclick=()=>modal.close();$('#pw34Project',modal).onchange=e=>{project=e.target.value;proposal=null;notification='';render()};
 $('#pw34Category',modal).onchange=e=>{task=$('#pw34Task',modal).value;category=e.target.value;proposal=null;render()};
 $('#pw34Provider',modal).onchange=e=>{task=$('#pw34Task',modal).value;provider=e.target.value;proposal=null;render()};
 $('#pw34Task',modal).addEventListener('input',e=>{task=e.target.value;if(proposal){proposal=null;const c=$('#pw34Suggest',modal);c.textContent='👔 Uppdatera Chefens förslag';$('#pw34Hire',modal)?.remove();modal.querySelectorAll('.pw34-card,.pw34-head').forEach(el=>el.remove())}});
 $('#pw34Suggest',modal).onclick=suggest;$('#pw34Review',modal).onclick=()=>{modal.close();window.pixelWorksV3Tasks?.open()};
 $('#pw34Hire',modal)?.addEventListener('click',()=>{modal.close();window.pixelWorksRecruitV3?.open('candidates')});
 $('#pw34More',modal)?.addEventListener('click',()=>{more=!more;render()});
 modal.querySelectorAll('[data-pw34-choose]').forEach(b=>b.onclick=()=>choose(b.dataset.pw34Choose));
}
async function suggest(){if(loading)return;task=$('#pw34Task',modal).value.trim();
 if(task.length<15){notification='Beskriv uppdraget med minst 15 tecken.';render();return}
 loading=true;notification='';proposal=null;render();
 try{proposal=await api('/api/pw-v3/chief/recommend',{project,category,provider,instruction:task});more=false;}
 catch(e){notification=e.message||String(e)}finally{loading=false;render()}
}
async function choose(pid){const person=proposal?.ranked?.find(x=>x.person_id===pid);
 if(!person?.can_start||!window.pixelWorksV3Tasks?.prepare)return;
 modal.close();await window.pixelWorksV3Tasks.prepare({person_id:pid,project,provider,instruction:task});
}
async function open(){for(const id of ['#pw3Dialog','#pw33Dialog','#pw13Dialog','#localStudioDialog','#dockDialog']){const d=$(id);if(d?.open)d.close()}
 if(!modal.open)modal.showModal();modal.innerHTML='<header><h2>👔 Chefens skrivbord</h2></header><div class="pw34-body">Läser studions projekt…</div>';
 try{const data=await api('/api/projects');projects=data.projects||[];if(!projects.some(p=>p.id===project))project=projects[0]?.id||'';notification='';render()}
 catch(e){projects=[];notification='Kunde inte läsa projekten: '+(e.message||e);render()}
}
window.pixelWorksV3Chief={open};
})();
