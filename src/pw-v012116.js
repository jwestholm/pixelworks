/* Pixel Works 0.12.11.6 – persons and tasks, not engine brands, in the office. */
(() => {
  'use strict';
  const $=(s,r=document)=>r.querySelector(s);
  const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let token='',busy=false,lastProject='',staff=[],jobs=[],reports=[];
  const css=document.createElement('style');css.textContent=`
    #realSessionPanel{display:none!important}
    #pw116Activity{background:#102d41;color:#e9f4ee;padding:12px;line-height:1.45;max-height:72vh;overflow:auto;border:2px solid #4e7784}
    #pw116Activity h3{margin:0 0 12px;font-size:14px;color:#f5cb72}
    .pw116-task{background:#234257;padding:10px;margin:7px 0;border-left:4px solid #5ed9cf;cursor:pointer}
    .pw116-task:focus-visible{outline:3px solid #fff}.pw116-task strong{display:block;color:white}
    .pw116-task small{display:block;color:#d2e4ef;margin:4px 0}
    .pw116-task button{font-size:12px;background:#f1ce80;color:#1d2b40;border:1px solid #784e34;padding:5px 8px;cursor:pointer}
    .pw116-idle{color:#b8e8c7}.pw116-error{color:#ffb7a9}
  `;document.head.append(css);
  async function api(path){if(!token){const b=await fetch('/api/bootstrap');if(!b.ok)throw Error('Servern svarar inte');token=(await b.json()).token}
    const r=await fetch(path,{headers:{'X-Pixelworks-Token':token},credentials:'same-origin'});
    const j=await r.json();if(!r.ok)throw Error(j.error||'HTTP '+r.status);return j;
  }
  function project(){return $('#projectSelect')?.value||''}
  function target(){let p=$('#pw116Activity');if(p)return p;const right=$('.right-rail');if(!right)return null;
    p=document.createElement('section');p.id='pw116Activity';p.setAttribute('aria-label','Studions aktivitetslogg');
    const old=$('#realSessionPanel');if(old)old.before(p);else right.append(p);return p;}
  const nameOf=(r)=>staff.find(s=>s.id===r.agent_id)?.name||r.agent_name||'Medarbetaren';
  // Never display the raw instruction in the office rail. It can contain the
  // complete Game Bible and material context. Full instructions stay in the job.
  const activityNames={code:'Arbetar med koden',docs:'Skriver dokumentation',
    research:'Undersöker spelprojektet',meeting:'Arbetar med en spelidé',
    art:'Arbetar med grafiken',music:'Komponerar musik',voice:'Arbetar med ljud och röster',
    qa:'Testar spelet',lead:'Planerar studions arbete'};
  function activityFor(station,queued=false){return queued?'Väntar på att börja':
    (activityNames[station]||'Arbetar med sitt uppdrag');}
  function taskFromReport(r){return r.state==='failed'?'Ett arbetsproblem behöver lösas':
    (activityNames[r.station]||'Förslag färdigt för granskning');}
  function render(){const panel=target();if(!panel)return;
    const live=jobs.filter(j=>['queued','running'].includes(j.state));
    const pending=reports.filter(r=>!r.archived&&!r.review_decision&&r.state==='review');
    const failed=reports.filter(r=>!r.archived&&!r.resolved_by&&!r.review_decision&&r.state==='failed');
    // A current active session takes precedence over historical reports for the same worker.
    const activePeople=new Set(live.map(j=>j.agent_id));
    const actionable=[...pending,...failed].filter(r=>!activePeople.has(r.agent_id)).slice(0,8);
    let html='<h3>📜 STUDIONS AKTIVITETER</h3>';
    if(!live.length&&!actionable.length)html+='<p class="pw116-idle">☕ Inga aktiva arbetsuppgifter</p>';
    for(const j of live){const person=nameOf(j),verb=j.state==='queued'?'väntar på sin tur':'arbetar';
      html+=`<div class="pw116-task" tabindex="0" data-person="${esc(j.agent_id)}"><strong>🔵 ${esc(person)} ${verb}</strong><small>${esc(activityFor(j.station,j.state==='queued'))}</small></div>`;}
    for(const r of actionable){const person=nameOf(r),review=r.state==='review';
      html+=`<div class="pw116-task" tabindex="0" data-report="${esc(r.id)}" data-person="${esc(r.agent_id)}"><strong>${review?'🟡':'🔴'} ${esc(person)} ${review?'har ett förslag att granska':'behöver hjälp'}</strong><small>${esc(taskFromReport(r)||r.title||'Öppna ärendet för detaljer')}</small><button type="button" data-open-report="${esc(r.id)}">${review?'Granska förslag':'Visa hjälp'}</button></div>`;}
    const legacy=$('#agentModeBadge');if(legacy)legacy.textContent=live.length?`${live.length} arbetar`:'Inga aktiva arbetsuppgifter';
    const hint=$('.office-hint-right');if(hint)hint.textContent=live.length?`${live.length} medarbetare arbetar`:'☕ Studion inväntar nästa uppdrag';
    panel.innerHTML=html;
    panel.querySelectorAll('[data-open-report]').forEach(b=>b.addEventListener('click',e=>{e.stopPropagation();openReport(b.dataset.openReport)}));
    panel.querySelectorAll('[data-report]').forEach(e=>{e.onclick=()=>openReport(e.dataset.report);e.onkeydown=k=>{if(k.key==='Enter')openReport(e.dataset.report)}});
    panel.querySelectorAll('[data-person]:not([data-report])').forEach(e=>{e.onclick=()=>openAgent(e.dataset.person);e.onkeydown=k=>{if(k.key==='Enter')openAgent(e.dataset.person)}});
  }
  function openAgent(id){const ui=window.__PIXEL_WORKS_DEMO__?.ui;if(ui?.selectAgent)ui.selectAgent(id)}
  function openReport(id){const r=reports.find(r=>r.id===id);if(!r)return;
    if(r.source==='gemini-api'&&window.pixelWorksGeminiReview){window.pixelWorksGeminiReview(project(),id);return;}
    if(r.state==='failed'&&window.pixelWorksHelpLive){window.pixelWorksHelpLive(project(),id);return;}
    const desk=$('#officeDesk');desk?.click();}
  function hookAgents(){const layer=$('#agentLayer');if(!layer||layer.dataset.pw116Bound)return;
    layer.dataset.pw116Bound='1';layer.addEventListener('click',event=>{
      const node=event.target.closest('.agent');if(!node||node.dataset.wasDragged==='1')return;
      const agentId=node.dataset.id;if(!agentId)return;
      const r=reports.find(r=>r.agent_id===agentId&&!r.archived&&!r.review_decision&&['review','failed'].includes(r.state));
      if(!r)return;
      event.stopImmediatePropagation();event.preventDefault();openReport(r.id);
    },true);
  }
  async function update(){if(busy||!document.body.classList.contains('live-project'))return;
    const slug=project();if(!/^[a-z0-9][a-z0-9-]{1,49}$/.test(slug))return;busy=true;
    try{if(lastProject!==slug){lastProject=slug;staff=[];jobs=[];reports=[]}
      const results=await Promise.allSettled([api('/api/projects/'+slug+'/staff'),api('/api/projects/'+slug+'/jobs'),api('/api/projects/'+slug+'/reports')]);
      if(slug!==project())return;
      if(results[0].status==='fulfilled')staff=results[0].value.staff||[];
      if(results[1].status==='fulfilled')jobs=results[1].value.jobs||[];
      if(results[2].status==='fulfilled')reports=results[2].value.reports||[];
      render();hookAgents();
    }catch(e){const p=target();if(p)p.textContent='⚠ Aktiviteterna kunde inte uppdateras: '+e.message}
    finally{busy=false}
  }
  // A chief's blocked report is actionable: retry its *existing* waiting
  // work order, without creating a duplicate or bypassing a busy work/ tree.
  async function retryRequest(data){
    if(!token){const bootstrap=await api('/api/bootstrap');token=bootstrap.token}
    const response=await fetch('/api/pw-v0121116/retry',{
      method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-Pixelworks-Token':token},
      body:JSON.stringify(data)});
    const payload=await response.json();
    if(!response.ok)throw Error(payload.error||'Omförsöket kunde inte startas');
    return payload;
  }
  function attachChiefRetry(){
    const dialog=$('#localStudioDialog');if(!dialog?.open)return;
    const detail=$('.pw-report-detail',dialog);
    if(!detail||$('#pw116Retry',detail))return;
    const match=$('.pw-report-tech',detail)?.textContent.match(/Session:\s*([0-9a-f]{12})/);
    if(!match)return;
    const r=reports.find(row=>row.id===match[1]);
    if(!r||r.source!=='studio-dispatch'||r.archived)return;
    const footer=$('.local-actions',detail);if(!footer)return;
    const box=document.createElement('div');box.id='pw116Retry';
    box.style.cssText='padding:10px;background:#f8e6b7;color:#3f3029;margin:10px 0;border:2px solid #9f774b';
    const title=document.createElement('strong');title.textContent='🔄 Försök starta arbetet igen';
    const message=document.createElement('p');message.style.cssText='font-size:12px;margin:7px 0';
    message.textContent='Arbetsordern finns kvar i kön. Om spelmappen fortfarande är upptagen kan du försöka igen när den blir ledig.';
    const select=document.createElement('select');select.hidden=true;
    select.setAttribute('aria-label','Välj arbetsorder');
    select.style.marginRight='8px';
    const button=document.createElement('button');button.type='button';button.textContent='🔄 Försök igen';
    const status=document.createElement('p');status.setAttribute('role','status');status.style.cssText='font-size:12px;margin:7px 0 0;white-space:pre-wrap';
    let sending=false;
    button.onclick=async()=>{
      if(sending)return;sending=true;button.disabled=true;
      status.textContent='Kontrollerar väntande arbetsorder och ledig arbetsplats…';
      try{
        const result=await retryRequest({project:project(),report_id:r.id,
          ...(select.hidden?{}:{order_id:select.value})});
        if(result.state==='choose'){
          select.replaceChildren();
          for(const row of result.orders||[]){const option=document.createElement('option');option.value=row.id;
            option.textContent=(row.station||'Arbetsstation')+' · '+row.id;select.append(option)}
          select.hidden=false;status.textContent='Välj arbetsorder och klicka Försök igen.';
        }else if(result.state==='started'){
          status.textContent='✅ '+(result.message||'Arbetet startades.');button.textContent='✅ Startat';
          await update();return;
        }else{
          status.textContent=result.message||'Arbetsordern väntar fortfarande. Försök igen när det blir ledigt.';
          if(result.state==='idle')button.textContent='✅ Ärendet färdigt';
        }
      }catch(error){status.textContent='⚠ '+error.message}
      finally{sending=false;if(button.textContent==='🔄 Försök igen')button.disabled=false}
    };
    box.append(title,message,select,button,status);footer.before(box);
  }
  const reportDialog=$('#localStudioDialog');
  if(reportDialog)new MutationObserver(attachChiefRetry).observe(reportDialog,{childList:true,subtree:true});
  // Hide the legacy engine-specific bar; preserve its technical log behind a future diagnostics view.
  const observer=new MutationObserver(()=>{const old=$('#realSessionPanel');if(old)old.hidden=true;hookAgents()});
  const rail=$('.right-rail');if(rail)observer.observe(rail,{childList:true});
  $('#projectSelect')?.addEventListener('change',()=>{lastProject='';update()});
  window.addEventListener('pixelworks:gemini-review-changed',()=>setTimeout(update,100));
  setTimeout(update,1300);setInterval(update,2800);
})();
