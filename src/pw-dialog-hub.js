/* Pixel Works – one context-aware entry to existing project decisions.
   Reuses the ONE review dialog and its verified server actions. No duplicate
   modals, API keys, local decisions or background agent calls are introduced.
*/
(() => {
  'use strict';
  if (window.__PW_DIALOG_HUB__) return;
  window.__PW_DIALOG_HUB__ = true;
  const selectors = [
    {root:'#pw138Cafe', target:'.pw138-sheet', section:'cafe'},
    {root:'#pw18Desk', target:'.pw18-paper', section:'station'},
    {root:'#localStudioDialog', target:'.local-shell-body', section:'report'},
    {root:'#agentDrawerContent', target:'.agent-detail', section:'agent'},
    {root:'#pw13Dialog', target:'.pw13-shell', section:'studio'}
  ];
  const live = () => document.body.classList.contains('live-project');
  const current = () => window.__PIXEL_WORKS_DEMO__?.model?.activeProjectId || document.querySelector('#projectSelect')?.value;
  let snapshot = {project:'', items:[]};
  const css=document.createElement('style');
  css.textContent=`
    .pwd-context{display:flex;align-items:center;justify-content:space-between;gap:9px;flex-wrap:wrap;
      margin:10px 0;padding:9px 11px;border:2px solid #abbbbf;border-left:5px solid #4b8d89;
      border-radius:4px;background:#f0f7f1;color:#243f4e;font:650 12px/1.4 system-ui,sans-serif;
      box-shadow:0 2px 0 #c1d2cd;box-sizing:border-box;max-width:100%;}
    .pwd-context strong{font-size:13px}.pwd-context small{display:block;color:#4a5e69;margin-top:2px;font-size:11px}
    .pwd-context button{flex:0 0 auto;min-height:42px;border:2px solid #2e5868;border-radius:4px;
      background:#37697a;color:#fff!important;font:800 13px system-ui,sans-serif;padding:8px 12px;
      cursor:pointer;max-width:100%;white-space:normal;}
    .pwd-context button:focus-visible{outline:3px solid #ebbc69;outline-offset:2px}
    #pw138Cafe .pwd-context,#pw18Desk .pwd-context,#localStudioDialog .pwd-context{color:#243f4e}
    #agentDrawerContent .pwd-context{margin:7px 0 13px}
    @media(max-width:480px){.pwd-context button{flex:1 1 100%}}
  `;
  document.head.append(css);

  function context(section, root){
    if(section==='agent'){
      const id=window.__PIXEL_WORKS_DEMO__?.ui?.selectedAgentId;
      const agent=window.__PIXEL_WORKS_DEMO__?.model?.project?.agents?.find(a=>a.id===id);
      return {kind:'all', employee:agent?.name||'',label:agent?.name?agent.name+' · Ärenden':'Personal · Ärenden'};
    }
    if(section==='station'){
      const shell=root.querySelector('.pw18-paper');
      const station=(shell?.className.match(/\bpw18-(music|voice|art|qa|code|docs|research|meeting)\b/)||[])[1]||'';
      const kind=station==='music'||station==='voice'?'audio':station==='art'?'image':'all';
      const names={music:'Musikstudion',voice:'Röststudion',art:'Grafikstudion',qa:'Testning',code:'Programmering',docs:'Dokumentation',research:'Forskning',meeting:'Mötesrummet'};
      return {kind,station:station||'',label:(names[station]||'Arbetsstation')+' · Resultat och beslut'};
    }
    if(section==='cafe'){
      // Only a view preference. No inference turns a discussion into an order.
      const draft=root.querySelector('#pw139Owner')?.value||root.querySelector('#pw138Note')?.value||'';
      const recent=[...root.querySelectorAll('.pw138-speech p')].slice(-3).map(x=>x.textContent).join(' ');
      const text=(draft+' '+recent).toLocaleLowerCase('sv-SE');
      const sound=/\b(ljud|musik|sound|audio|ljudeffekt|röst|soundtrack)/i.test(text);
      const picture=/\b(bild|bilder|grafik|sprite|illustration|animation)/i.test(text);
      return {kind:sound&&!picture?'audio':picture&&!sound?'image':'all',label:'Fikarummet · Teamets förslag'};
    }
    return {kind:'all',label:section==='report'?'Rapporter · Resultat och beslut':'Studio · Resultat och beslut'};
  }
  function matches(item, ctx){
    if(ctx.kind!=='all'&&item.kind!==ctx.kind)return false;
    if(ctx.employee&&String(item.employee||'').toLocaleLowerCase('sv-SE')!==ctx.employee.toLocaleLowerCase('sv-SE'))return false;
    if(ctx.station&&item.station!==ctx.station)return false;
    return true;
  }
  function updateBar(bar, section, root){
    const ctx=context(section,root);
    const items=snapshot.project===current()?snapshot.items:[];
    const relevant=items.filter(item=>matches(item,ctx));
    const waiting=relevant.filter(x=>x.status==='waiting').length;
    const total=items.filter(x=>x.status==='waiting').length;
    const title=bar.querySelector('strong');
    const details=bar.querySelector('small');
    title.textContent=ctx.kind==='audio'?'🎧 Lyssna och välj':ctx.kind==='image'?'🖼 Granska bilder':'💌 Teamets resultat och beslut';
    details.textContent=waiting?`${waiting} beslut här · ${total} väntar i hela studion`:
      total?`${total} beslut i studion · öppna för att hitta dem`:'Samma inkorg för hjälp, ljud, bilder och granskning';
    bar.querySelector('button').textContent=waiting?`Öppna ${waiting} ärenden →`:'Öppna inkorgen →';
    bar.dataset.pwdContext=section;
  }
  function attach({root:selector,target,section}){
    const root=document.querySelector(selector);if(!root)return;
    const place=()=>{
      if(!live())return;
      const inner=root.querySelector(target);
      if(!inner||inner.querySelector(':scope > .pwd-context'))return;
      const bar=document.createElement('section');bar.className='pwd-context';bar.setAttribute('aria-label','Studions gemensamma ärenden');
      const description=document.createElement('div');
      description.innerHTML='<strong>💌 Teamets resultat och beslut</strong><small>Samma inkorg i hela studion</small>';
      const button=document.createElement('button');button.type='button';button.textContent='Öppna inkorgen →';
      button.addEventListener('click',()=>{
        if(typeof window.pixelWorksOpenDecisionContext==='function'){
          const ctx=context(section,root);
          window.pixelWorksOpenDecisionContext(ctx);
        }
      });
      bar.append(description,button);
      // Put navigation just below the existing dialog's header without taking
      // over its controls. The existing modal stays open behind the review.
      const anchor=inner.querySelector(':scope > .pw138-head,:scope > .pw18-head,:scope > .agent-detail-head');
      if(anchor)anchor.after(bar);else inner.prepend(bar);
      updateBar(bar,section,root);
    };
    const update=()=>{const bar=root.querySelector(target+' > .pwd-context');if(bar)updateBar(bar,section,root)};
    new MutationObserver(()=>{if(root.querySelector(target+' > .pwd-context'))return;place();}).observe(root,{childList:true});
    root.addEventListener('input',e=>{if(section==='cafe'&&e.target.matches?.('#pw139Owner,#pw138Note'))update();});
    window.addEventListener('pixelworks:decision-snapshot',update);
    document.querySelector('#projectSelect')?.addEventListener('change',()=>queueMicrotask(update));
    place();
  }
  const installed=new Set();
  const attachNew=()=>{
    for(const spec of selectors){
      if(installed.has(spec.root)||!document.querySelector(spec.root))continue;
      attach(spec);installed.add(spec.root);
    }
  };
  attachNew();
  // Some legacy dialogs are created after the module imports. Attach when
  // those elements actually exist, instead of depending on script order.
  let attempts=0;
  const discovery=setInterval(()=>{
    attachNew();attempts++;
    if(installed.size===selectors.length||attempts>=120)clearInterval(discovery);
  },500);
  window.addEventListener('pixelworks:decision-snapshot',event=>{
    const detail=event.detail||{};
    snapshot={project:detail.project||'',items:Array.isArray(detail.items)?detail.items:[]};
  },{capture:true});
})();
