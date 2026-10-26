/* Pixel Works 0.12.11.7: human-first stamina & observed usage; Bible editorial review. */
(()=>{'use strict';
const $=(q,r=document)=>r.querySelector(q);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let token='',staff=[],jobs=[],reports=[],project='',busy=false;
const energy=new Map();const resting=new Set();let lastTick=Date.now();
const style=document.createElement('style');style.textContent=`
#agentLayer .pw117-stamina{position:absolute;left:-2px;right:-2px;top:-9px;height:5px;border:1px solid #16232a;background:#242c38;opacity:0;pointer-events:none;z-index:15}
#agentLayer .agent:hover .pw117-stamina,#agentLayer .agent:focus-within .pw117-stamina,#agentLayer .agent.pw117-tired .pw117-stamina{opacity:1}
#agentLayer .pw117-stamina>span{display:block;height:100%;background:#49dc80;width:var(--stamina)}
#agentLayer .agent.pw117-low .pw117-stamina>span{background:#f8be50}#agentLayer .agent.pw117-tired .pw117-stamina>span{background:#f36d69}
#pw117Stats{font:12px system-ui;color:#e7f1e6;background:#153646;border:1px solid #638e86;padding:9px;margin:8px 0}
#pw117Stats summary{cursor:pointer;color:#f3d394;font-weight:bold}#pw117Stats .pw117-row{display:flex;justify-content:space-between;gap:8px;padding:4px 0;border-bottom:1px solid #476076}
#pw117Chapter{width:min(850px,95vw);max-height:90vh;overflow:auto;padding:18px;background:#243749;color:#fff;border:5px ridge #b89568;box-sizing:border-box}
#pw117Chapter::backdrop{background:#06101de0}#pw117Chapter textarea{width:100%;height:23vh;box-sizing:border-box;background:#142c3d;color:#fff;padding:10px;resize:vertical}
#pw117Chapter button{padding:9px;margin:5px;background:#f5d083;color:#243347;font-weight:bold;border:2px solid #85603b;cursor:pointer}
#pw117Chapter [role=status]{min-height:2em;color:#f7cc88}`;document.head.append(style);
async function api(path,payload){if(!token){const b=await fetch('/api/bootstrap');if(!b.ok)throw Error('Servern svarar inte');token=(await b.json()).token}
 const r=await fetch(path,{method:payload?'POST':'GET',headers:{'X-Pixelworks-Token':token,...(payload?{'Content-Type':'application/json'}:{})},credentials:'same-origin',body:payload?JSON.stringify(payload):undefined});const data=await r.json();if(!r.ok)throw Error(data.error||'HTTP '+r.status);return data}
function usageOf(job){const u=job.usage_metadata||{};return Number(u.totalTokenCount??u.total_token_count??(Number(u.promptTokenCount||0)+Number(u.candidatesTokenCount||0)))||null}
function energyTick(){const now=Date.now(),mins=Math.min(1,(now-lastTick)/60000);lastTick=now;
 const active=new Set(jobs.filter(j=>['queued','running'].includes(j.state)).map(j=>j.agent_id));
 for(const a of staff){let e=energy.get(a.id)??100; e=Math.max(0,Math.min(100,e+(active.has(a.id)?-7:(a.station==='cafe'?15:4))*mins));energy.set(a.id,e);
  // Walk to the café only when genuinely idle. This is a gameplay choice,
  // not an API-quota reset; never interrupt a running job.
  if(e<18&&!active.has(a.id)&&a.station!=='cafe'&&!resting.has(a.id)&&typeof window.pixelWorksMoveLive==='function'){
    resting.add(a.id);window.pixelWorksMoveLive(project,a.id,'cafe').catch(()=>{}).finally(()=>resting.delete(a.id));
  }
 }
 for(const el of document.querySelectorAll('#agentLayer .agent')){const e=energy.get(el.dataset.id);if(e===undefined)continue;
 let bar=el.querySelector('.pw117-stamina');if(!bar){bar=document.createElement('span');bar.className='pw117-stamina';bar.innerHTML='<span></span>';el.append(bar)}
 bar.style.setProperty('--stamina',`${Math.round(e)}%`);el.classList.toggle('pw117-tired',e<24);el.classList.toggle('pw117-low',e>=24&&e<50);
 bar.title=`Spelork ${Math.round(e)} % – fiktiv spelstatistik, inte AI-kvot`;
 }
}
function stats(){let panel=$('#pw117Stats');const root=$('.right-rail');if(!root)return;
 if(!panel){panel=document.createElement('details');panel.id='pw117Stats';root.prepend(panel)}
 const current=jobs.filter(j=>['queued','running'].includes(j.state));const count=jobs.reduce((n,j)=>n+(usageOf(j)||0),0);
 const known=jobs.filter(j=>usageOf(j)!==null).length;
 const people=staff.map(p=>`<div class="pw117-row"><span>${esc(p.name)} · ${esc(p.role||'Medarbetare')}</span><span>❤️ ${Math.round(energy.get(p.id)??100)}% · ${current.some(j=>j.agent_id===p.id)?'Arbetar':'Ledig'}</span></div>`).join('');
 const expanded=panel.open;
 panel.innerHTML=`<summary>📊 Studiostatistik · ${current.length} arbetar · ☕ ${staff.length-current.length} lediga</summary>
 <p>❤️ Ork är en spelmekanik. ⚡ Token kommer från leverantörsrapporterade jobb, inte återstående kvot.</p>
 <div class="pw117-row"><b>⚡ Observerade token (senaste serverjobben)</b><b>${known?count.toLocaleString('sv-SE'):'Okänt'}</b></div>
 <div class="pw117-row"><span>Externa återstående kvoter</span><strong>Okänt</strong></div>${people}`;
 panel.open=expanded;
}
async function update(){if(busy||!document.body.classList.contains('live-project'))return;const slug=$('#projectSelect')?.value;
 if(!slug||!/^[a-z0-9-]{2,50}$/.test(slug))return;busy=true;
 try{if(project!==slug){project=slug;staff=[];jobs=[];reports=[];energy.clear()}
 const data=await Promise.allSettled([api(`/api/projects/${slug}/staff`),api(`/api/projects/${slug}/jobs`),api(`/api/projects/${slug}/reports`)]);
 if(slug!==$('#projectSelect')?.value)return;
 if(data[0].status==='fulfilled')staff=data[0].value.staff||[];
 if(data[1].status==='fulfilled')jobs=data[1].value.jobs||[];
 if(data[2].status==='fulfilled')reports=data[2].value.reports||[];
 stats();energyTick();
 }catch(err){/* Never synthesize quota when offline. */}finally{busy=false}}
const dialog=document.createElement('dialog');dialog.id='pw117Chapter';document.body.append(dialog);
function editor(data,slug,rid){dialog.innerHTML=`<h2>📖 Granska nytt Game Bible-kapitel: ${esc(data.title)}</h2>
 <p>AI har läst tidigare kapitel och förslaget. Kontrollera att inget viktigt försvunnit innan du inför hela den nya sidan.</p>
 <details><summary>Visa föregående kapitel</summary><textarea readonly>${esc(data.original)}</textarea></details>
 <h3>AI-redigerat kapitelutkast</h3><textarea readonly>${esc(data.draft)}</textarea>
 <p role="status" id="pw117Msg">Ingenting är ändrat förrän du väljer Inför kapitlet.</p>
 <button id="pw117Confirm">✅ Inför kapitlet</button><button id="pw117Cancel">Avbryt – behåll det gamla</button>`;
 $('#pw117Cancel',dialog).onclick=()=>dialog.close();
 $('#pw117Confirm',dialog).onclick=async()=>{const b=$('#pw117Confirm',dialog);b.disabled=true;$('#pw117Msg',dialog).textContent='Sparar kapitlet…';
 try{const res=await api('/api/pw-v012117/bible',{action:'confirm',project:slug,report_id:rid});$('#pw117Msg',dialog).textContent=res.message;window.dispatchEvent(new Event('pixelworks:gemini-review-changed'));setTimeout(()=>dialog.close(),950)}
 catch(err){b.disabled=false;$('#pw117Msg',dialog).textContent='⚠ '+err.message}};
 if(!dialog.open)dialog.showModal();}
// Capture the older approve button before its legacy append handler. Other
// review actions (revise, forward, reject) remain untouched.
document.addEventListener('click',async event=>{const button=event.target.closest?.('[data-pw115-action="approve"]');if(!button)return;
 event.preventDefault();event.stopImmediatePropagation();
 const modal=$('#pw115Review');
 const selected=reports.find(r=>r.id===modal?.dataset.reportId&&r.source==='gemini-api'&&
   !r.review_decision&&r.state==='review');
 if(!selected){const status=$('#pw115Message');if(status)status.textContent='⚠ Rapporten måste öppnas igen innan godkännande.';return;}
 const slug=$('#projectSelect')?.value;
 button.disabled=true;const status=$('#pw115Message');if(status)status.textContent=`${selected.agent_name||'Medarbetaren'} sammanför kapitlet…`;
 try{const data=await api('/api/pw-v012117/bible',{action:'prepare',project:slug,report_id:selected.id});if(modal?.open)modal.close();editor(data,slug,selected.id)}
 catch(err){if(status)status.textContent='⚠ '+err.message}finally{button.disabled=false}
},true);
setTimeout(update,1200);setInterval(update,3000);setInterval(energyTick,4000);
})();
