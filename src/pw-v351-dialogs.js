/* Pixel Works 3.5.1 — shared game dialog navigation.
 * Existing V3 views keep their own state/permissions and renderers. This layer
 * centralizes transitions, back, focus and visual navigation; no AI calls.
 */
(() => {
  'use strict';
  if (window.__PW351_DIALOGS__) return;
  window.__PW351_DIALOGS__ = true;
  const keys = ['personal','uppdrag','chefen','beslut'];
  const ids = {personal:'pw3Dialog',uppdrag:'pw33Dialog',chefen:'pw34Dialog',beslut:'pwReviewDlg'};
  const labels = {personal:'👥 Personal',uppdrag:'📋 Uppdrag',chefen:'👔 Chefen',beslut:'💌 Beslut'};
  const messages = {personal:'Ditt team och rekrytering',uppdrag:'Arbetsorder och riktiga resultat',chefen:'Rekommendationer, inga automatiska starter',beslut:'Granska teamets förslag'};
  const $ = (sel,el=document) => el.querySelector(sel);
  const style=document.createElement('link');style.id='pw351-style';style.rel='stylesheet';
  style.href='./src/pw-v351-dialogs.css';document.head.append(style);
  let active = null, history = [], transitioning = false;
  let restoreFocus = null;
  const draft = {uppdrag:""};
  const dialogs = new Map();
  const esc = s => String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function dialog(kind){return document.getElementById(ids[kind]);}
  function opened(kind){return !!dialog(kind)?.open;}
  function current(){return keys.find(opened)||null;}
  function visibleLabel(){return current()||active||'personal';}
  function saveDraft(kind){
    if(kind==='uppdrag'){const field=$('#pw33Instruction',dialog(kind));if(field)draft.uppdrag=field.value;}
  }
  function closeV3(){for(const key of keys){const el=dialog(key);if(el?.open)el.close();}}
  function focusOffice(){const target=restoreFocus?.isConnected?restoreFocus:$('#gameDock [data-dock="office"]')||$('#pw3Open');if(target?.focus)target.focus({preventScroll:true});}
  function closeAll(){transitioning=true;history=[];active=null;closeV3();transitioning=false;focusOffice();}
  function go(kind, push=true, personId=null, view='crew'){
    if(!keys.includes(kind))return false;
    const from=current();
    if(from===kind)return true;
    if(!restoreFocus){const el=document.activeElement;if(el instanceof HTMLElement && !el.closest('dialog'))restoreFocus=el;}
    if(push&&from)history.push(from);
    if(from)saveDraft(from);
    if(history.length>12)history=history.slice(-12);
    transitioning=true;closeV3();transitioning=false;active=kind;
    const api = {personal:()=>window.pixelWorksRecruitV3?.open(view),
      uppdrag:()=>window.pixelWorksV3Tasks?.open(personId||undefined),
      chefen:()=>window.pixelWorksV3Chief?.open(),
      beslut:()=>window.pixelWorksOpenDecisionContext?.({kind:'all',label:'Teamets resultat och beslut'})};
    try{const result=api[kind]?.();if(result===undefined&&kind==='beslut'&&!dialog(kind))return false;
      if(result&&typeof result.then==='function')result.then(()=>{
        if(kind==='uppdrag'){const field=$('#pw33Instruction',dialog(kind));if(field&&!field.value&&draft.uppdrag)field.value=draft.uppdrag;}
      }).catch(e=>console.warn('Pixel Works dialog:',e.message));}
    catch(e){console.warn('Pixel Works dialog:',e.message);return false;}
    queueMicrotask(refresh);
    return true;
  }
  function back(){if(history.length){const prev=history.pop();go(prev,false)}else closeAll();}
  function makeNav(kind){
    const bar=document.createElement('nav');bar.className='pw351-navigation';bar.setAttribute('aria-label','Pixel Works huvudvyer');bar.dataset.pw351Nav=kind;
    const backBtn=document.createElement('button');backBtn.type='button';backBtn.className='pw351-back';backBtn.dataset.pw351Back='';backBtn.textContent=history.length?'◀ Tillbaka':'◀ Kontoret';backBtn.addEventListener('click',back);
    const group=document.createElement('div');group.className='pw351-menu';group.setAttribute('role','group');group.setAttribute('aria-label','Byt del av studion');
    for(const item of keys){const btn=document.createElement('button');btn.type='button';btn.textContent=labels[item];btn.dataset.pw351To=item;btn.setAttribute('aria-current',item===kind?'page':'false');btn.addEventListener('click',()=>go(item));group.appendChild(btn)}
    const office=document.createElement('button');office.type='button';office.dataset.pw351Office='';office.className='pw351-home';office.hidden=history.length===0;office.textContent='🏠 Kontor';office.addEventListener('click',closeAll);
    bar.append(backBtn,group,office);return bar;
  }
  function updateNav(kind){
    const el=dialog(kind);if(!el||!el.open)return;
    const old=$(':scope > .pw351-navigation',el)||$('.pwr-shell > .pw351-navigation',el);
    if(old){const b=$('[data-pw351-back]',old);if(b)b.textContent=history.length?'◀ Tillbaka':'◀ Kontoret';const home=$('[data-pw351-office]',old);if(home)home.hidden=history.length===0;return}
    // V3 render() replaces innerHTML on updates; insert only between its
    // existing header and body. Do not touch forms, audio players or offers.
    let parent=el,head=$(':scope > header,:scope > .pw3-head',el);
    if(kind==='beslut'){parent=$('.pwr-shell',el);head=$(':scope > .pwr-head',parent);}
    if(!parent||!head)return;
    head.after(makeNav(kind));
  }
  let scheduled=false;
  function refresh(){if(scheduled)return;scheduled=true;queueMicrotask(()=>{scheduled=false;const now=current();if(now){active=now;updateNav(now);} });}
  function attach(kind){
    const el=dialog(kind);if(!el||dialogs.has(kind))return;
    dialogs.set(kind,el);
    const observer=new MutationObserver(()=>{if(el.open)refresh()});
    observer.observe(el,{attributes:true,attributeFilter:['open'],childList:true,subtree:false});
    if(kind==='beslut'){
      const shell=$('.pwr-shell',el);
      if(shell)observer.observe(shell,{childList:true,subtree:false});
    }
    el.addEventListener('close',()=>{
      if(transitioning)return;
      // Native x or Esc returns to the office, rather than accidentally
      // uncovering a stale old project-specific modal.
      if(active===kind){active=null;history=[];focusOffice()}
    });
    if(kind!=='beslut')el.addEventListener('cancel',e=>{e.preventDefault();back()});
    if(el.open)updateNav(kind);
  }
  // Old buttons continue to exist while their views are migrated. Intercept
  // only navigation actions; never intercept Start, Hire or Approve.
  document.addEventListener('click',e=>{
    const target=e.target instanceof Element ? e.target.closest('[data-pw33-assign],#pw33ProfileStart,#pw33ChiefLink,#pw34ProfileChief,#pw34Review,#pw34Hire') : null;
    if(!target)return;
    let dest=null,personId=null,view='crew';
    if(target.matches('[data-pw33-assign],#pw33ProfileStart')){dest='uppdrag';personId=target.getAttribute('data-pw33-assign')||target.closest('[data-staff]')?.getAttribute('data-staff')||null;}
    else if(target.matches('#pw33ChiefLink,#pw34ProfileChief'))dest='chefen';
    else if(target.id==='pw34Review')dest='uppdrag';
    else if(target.id==='pw34Hire'){dest='personal';view='candidates'}
    if(!dest)return;
    e.preventDefault();e.stopImmediatePropagation();go(dest,true,personId,view);
  },true);
  for(const kind of keys)attach(kind);
  // The review dialog may be installed by another module during initialization.
  let polls=0;const timer=setInterval(()=>{for(const kind of keys)attach(kind);refresh();if(++polls>40||dialogs.size===keys.length)clearInterval(timer)},350);
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&dialog('beslut')?.open){/* Existing review logic owns cancel and audio cleanup. */}},false);
  window.pixelWorksGameDialog={go,back,close:closeAll,get active(){return current()},get history(){return [...history]}};
})();
