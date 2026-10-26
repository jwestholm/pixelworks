/* 0.12.11.13: Google-governed quotas and truthful manual assignment feedback.
 * Never perform cloud requests while drawing this diagnostic UI. */
(()=>{'use strict';
let token='',busy=false;
const $=(selector,root=document)=>root.querySelector(selector);
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function api(route,payload){
  if(window.pixelWorksApi)return window.pixelWorksApi(route,payload);
  if(!token){const b=await fetch('/api/bootstrap');if(!b.ok)throw Error('Servern svarar inte');token=(await b.json()).token}
  const r=await fetch(route,{method:payload?'POST':'GET',headers:{'X-Pixelworks-Token':token,...(payload?{'Content-Type':'application/json'}:{})},credentials:'same-origin',...(payload?{body:JSON.stringify(payload)}:{})});
  const result=await r.json();if(!r.ok)throw Error(result.error||'HTTP '+r.status);return result;
}
const style=document.createElement('style');style.textContent=`
#pw12LimitRow{background:#203c4f;border:2px solid #7c9ca8;margin:12px 0;padding:10px;color:#f3f1da}
#pw12LimitRow label{display:inline-block;margin:8px 6px 8px 0}
#pw12LimitRow select{width:auto;max-width:100%}
#pw12LimitRow button{margin:5px 0}
#pwMeetingDispatchHint{background:#523947;color:#fff0cf;border:2px solid #cba275;padding:8px;margin:6px;line-height:1.5}
#pw-people-state{flex-shrink:0}`;document.head.append(style);
async function showCapacity(box){
  const line=$('[data-capacity-info]',box);
  try{
    const d=await api('/api/pw-v0121112/capacity');if(!box.isConnected)return;
    line.textContent=`Registrerade Gemini-anrop idag: ${d.used_today}. Ingen lokal dygnsgräns. Google bestämmer aktuell RPM/TPM/RPD-kvot; återstående kvot: okänd.`;
    if(d.paused){
      const until=Number(d.paused_until_epoch);
      const when=Number.isFinite(until)&&until>0?' Till '+new Date(until*1000).toLocaleTimeString('sv-SE',{hour:'2-digit',minute:'2-digit'})+'.':
        d.paused_until_day?' Paus till Googles dygnskvot återställs.':'';
      line.textContent+=' Paus efter Googles svar: '+String(d.pause_reason||'Se status').slice(0,160)+when;
    }
    if(!d.verified)line.textContent+=' Anslutningen behöver verifieras.';
  }catch(e){if(line)line.textContent='Kunde inte läsa status: '+e.message;}
}
function addCapacity(){
  const root=$('#pw12Body');if(!root||$('#pw12LimitRow',root)||!$('#pw12Panel')?.open)return;
  const title=$('#pw12Title')?.textContent||'';
  if(!title.includes('Gemini'))return;
  const box=document.createElement('section');box.id='pw12LimitRow';
  box.innerHTML=`<h3>⚡ Arbetskapacitet</h3>
    <p data-capacity-info>Hämtar anropsstatistik…</p>
    <p>Google hanterar gränserna per projekt och modell (RPM, TPM, RPD). Ett verkligt kvotfel pausar nya anrop tillfälligt. Pixel Works uppgraderar aldrig automatiskt till en betald modell.</p>`;
  root.append(box);showCapacity(box);
}
const panel=$('#pw12Panel');if(panel){
  const body=$('#pw12Body',panel);
  if(body)new MutationObserver(()=>addCapacity()).observe(body,{childList:true});
  new MutationObserver(()=>addCapacity()).observe(panel,{attributes:true,attributeFilter:['open']});
  setTimeout(addCapacity,500);
}
// Initial/periodic status text – no API calls beyond local read-only endpoints.
// Help text remains available even after the old manager wrote misleading logs.
window.addEventListener('pixelworks:studio-access-changed',()=>setTimeout(addCapacity,150));
})();
