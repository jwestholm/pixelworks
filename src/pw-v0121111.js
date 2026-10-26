/* Pixel Works 0.12.11.11: worker names and observable status, never adapters. */
(() => {
  'use strict';
  let pending = false;
  const css = document.createElement('style');
  css.textContent = `#pw-people-state{margin:8px 7px;border:1px solid #59879a;background:#102d44;color:#e4edf1;padding:8px;font-size:12px}#pw-people-state summary{cursor:pointer;font-weight:bold;color:#f4d27c}#pw-people-state .pw-person-line{padding:6px 0;border-top:1px solid #38546b;line-height:1.5}#pw-people-state .pw-person-line:first-child{margin-top:7px}#pw-people-state .pw-person-work{color:#a5d8e6;font-size:11px;display:block}`;
  document.head.appendChild(css);
  async function refresh(){
    if(pending || !document.body.classList.contains('live-project') || !window.pixelWorksApi)return;
    const slug=document.querySelector('#projectSelect')?.value;
    if(!slug)return;
    const panel=document.querySelector('#pw116Activity')?.parentElement || document.querySelector('.right-rail');
    if(!panel)return;
    pending=true;
    try {
      const data=await window.pixelWorksApi('/api/projects/'+encodeURIComponent(slug)+'/staff-status');
      if(document.querySelector('#projectSelect')?.value!==slug)return;
      let box=panel.querySelector('#pw-people-state');
      if(!box){box=document.createElement('details');box.id='pw-people-state';box.open=false;
        const summary=document.createElement('summary');box.appendChild(summary);panel.prepend(box);}
      const active=data.workers.filter(x=>x.state==='working').length;
      const waiting=data.workers.filter(x=>x.state==='waiting'||x.state==='blocked').length;
      box.querySelector('summary').textContent=`👥 Personal · ${active} arbetar · ${waiting} väntar`;
      const previous=box.querySelector('.pw-people-list');if(previous)previous.remove();
      const list=document.createElement('div');list.className='pw-people-list';
      for(const row of data.workers){
        const item=document.createElement('div');item.className='pw-person-line';
        const title=document.createElement('b');title.textContent=({working:'🔵 ',blocked:'🔴 ',waiting:'🟡 ',idle:'☕ '})[row.state]||'• ';
        title.textContent+=(row.name||'Medarbetare')+' · '+({working:'Arbetar',blocked:'Väntar på hjälp',waiting:'Redo för uppdrag',idle:'Ledig'})[row.state];
        const detail=document.createElement('span');detail.className='pw-person-work';detail.textContent=row.message||'';
        item.append(title,detail);list.appendChild(item);
      }
      box.appendChild(list);
    }catch(_){ /* Keep the last verified status during a temporary backend failure. */ }
    finally{pending=false;}
  }
  setInterval(refresh,5000);setTimeout(refresh,1800);
})();
