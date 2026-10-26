/* Pixel Works 0.12.11.8 – identity belongs to employees, not AI providers. */
(()=>{'use strict';
  const style=document.createElement('style');style.textContent=`
    #agentLayer .agent{isolation:isolate}
    #agentLayer .agent .agent-name{position:absolute!important;left:50%!important;top:-23px!important;transform:translateX(-50%)!important;z-index:25!important;white-space:nowrap;pointer-events:none}
    #agentLayer .agent.selected .agent-name{z-index:27!important}
  `;document.head.append(style);
  let busy=false;
  async function correct(){
    if(busy||!document.body.classList.contains('live-project'))return;
    const slug=document.querySelector('#projectSelect')?.value;
    if(!slug||!/^[-a-z0-9]{2,50}$/.test(slug))return;
    busy=true;
    try{
      const response=await fetch('/api/projects/'+slug+'/staff',{credentials:'same-origin'});
      if(!response.ok)return;
      const staff=(await response.json()).staff||[];
      for(const employee of staff){
        const node=[...document.querySelectorAll('#agentLayer .agent')].find(n=>n.dataset.id===employee.id);
        if(!node)continue;
        const label=node.querySelector('.agent-name');
        if(label&&label.textContent!==employee.name)label.textContent=employee.name;
        node.title=`${employee.name} · ${employee.role||'Medarbetare'}`;
        // Employee identity never comes from the station, current provider or
        // the neighbour standing beside them in a crowded break room.
      }
    }catch(_){/* Leave existing verified names displayed when offline. */}
    finally{busy=false}
  }
  setTimeout(correct,1400);setInterval(correct,3500);
})();


/* 0.12.11.9 – actionable station review indicators, independent of provider. */
(()=>{'use strict';
  const css=document.createElement('style');css.textContent=`
    #stationLayer .station{overflow:visible!important;position:absolute}
    #stationLayer .station .pw-review-alert{position:absolute!important;top:-25px;right:-14px;z-index:120;display:flex;align-items:center;justify-content:center;gap:3px;min-width:25px;height:25px;padding:0 5px;border:2px solid #742b32;border-radius:8px;background:#ffefba;color:#a31b21;box-shadow:2px 3px 0 #303047;font:900 13px/1 system-ui,sans-serif;cursor:pointer;pointer-events:auto}
    #stationLayer .station .pw-review-alert:hover,#stationLayer .station .pw-review-alert:focus-visible{background:#fff7dd;transform:scale(1.08);outline:2px solid #fff;outline-offset:1px}
  `;document.head.append(css);
  let busy=false,lastProject='';
  const validSlug=s=>/^[a-z0-9][a-z0-9-]{1,49}$/.test(s||'');
  const actionableReport=r=>r&&!r.archived&&!r.resolved_by&&!r.review_decision&&r.state==='review';
  function reviewCounts(orders,reports){
    const counts=new Map();const seen=new Set();
    const add=(station,key)=>{if(!station||seen.has(key))return;seen.add(key);counts.set(station,(counts.get(station)||0)+1)};
    for(const order of orders){
      if(order.status!=='review')continue;
      const linked=reports.find(r=>r.id===order.job_id||(r.order_id&&r.order_id===order.id));
      if(linked){if(actionableReport(linked))add(order.station,'report:'+linked.id);}
      else add(order.station,'order:'+order.id); // Missing report still needs attention.
    }
    for(const report of reports){
      if(!actionableReport(report))continue;
      const linked=orders.find(o=>o.id===report.order_id);
      if(linked&&['done','superseded','archived'].includes(linked.status))continue;
      add(linked?.station||report.station,'report:'+report.id);
    }
    return counts;
  }
  function paint(counts){
    for(const node of document.querySelectorAll('#stationLayer .station')){
      const station=node.dataset.id;const total=counts.get(station)||0;
      let marker=node.querySelector('.pw-review-alert');
      if(!total){marker?.remove();continue;}
      if(!marker){
        marker=document.createElement('button');marker.type='button';marker.className='pw-review-alert';
        marker.addEventListener('pointerdown',e=>e.stopPropagation());
        marker.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();
          // Reuse the existing work queue: no independent approval implementation.
          node.click();
        });
        node.append(marker);
      }
      marker.textContent='❗'+(total>1?String(total):'');
      marker.title=total+' ärende'+(total===1?'':'n')+' att granska – öppna bordets arbetskö';
      marker.setAttribute('aria-label',marker.title);
    }
  }
  async function refresh(){
    if(busy||!document.body.classList.contains('live-project'))return;
    const slug=document.querySelector('#projectSelect')?.value;
    if(!validSlug(slug)){paint(new Map());return;}
    busy=true;
    try{
      const [ordersResponse,reportsResponse]=await Promise.all([
        fetch('/api/projects/'+slug+'/orders',{credentials:'same-origin'}),
        fetch('/api/projects/'+slug+'/reports',{credentials:'same-origin'})
      ]);
      if(!ordersResponse.ok||!reportsResponse.ok)return; // Retain last known status offline.
      const [o,r]=await Promise.all([ordersResponse.json(),reportsResponse.json()]);
      if(slug!==document.querySelector('#projectSelect')?.value)return;
      lastProject=slug;paint(reviewCounts(o.orders||[],r.reports||[]));
    }catch(_){/* No fabricated status while backend is unreachable. */}
    finally{busy=false;}
  }
  document.querySelector('#projectSelect')?.addEventListener('change',()=>{lastProject='';paint(new Map());refresh()});
  window.addEventListener('pixelworks:gemini-review-changed',()=>setTimeout(refresh,100));
  setTimeout(refresh,1200);setInterval(refresh,3200);
})();

/* 0.12.11.10 – manually placing an employee at a worktable rechecks the
 * real queue even if the chief is present. Never fabricate an AI job. */
(()=>{'use strict';
  const original=window.pixelWorksMoveLive;
  if(typeof original!=='function'||typeof window.pixelWorksApi!=='function')return;
  const stations=new Set(['meeting','research','docs']);
  let outstanding=false;
  window.pixelWorksMoveLive=async function(slug,agentId,station){
    await original(slug,agentId,station);
    if(!stations.has(station)||outstanding)return;
    outstanding=true;
    try{
      const result=await window.pixelWorksApi('/api/pw-v0121110/dispatch',{project:slug,station,agent_id:agentId});
      const rail=document.querySelector('#pw116Activity, #realWorkerOverview, #pwUnifiedActivity, #realJobState');
      if(result.state==='blocked'&&rail){
        let hint=document.querySelector('#pwMeetingDispatchHint');
        if(!hint){hint=document.createElement('p');hint.id='pwMeetingDispatchHint';hint.setAttribute('role','status');rail.parentElement?.insertBefore(hint,rail);}
        hint.textContent='⚠ '+result.message;
      }else if(result.state==='started'){
        document.querySelector('#pwMeetingDispatchHint')?.remove();
        window.dispatchEvent(new Event('pixelworks:gemini-review-changed'));
      }
    }catch(e){
      const rail=document.querySelector('#pw116Activity,#realWorkerOverview,#realJobState');
      if(rail){let hint=document.querySelector('#pwMeetingDispatchHint');if(!hint){hint=document.createElement('p');hint.id='pwMeetingDispatchHint';rail.parentElement?.insertBefore(hint,rail);}hint.textContent='⚠ Kunde inte tilldela arbetet: '+e.message;}
    }finally{outstanding=false;}
  };
})();
