/* Pixel Works v2.3 — studio identity and source-project help.
 * An employee's name is NOT an ID. Old report IDs are preserved.
 * Read-only until the owner explicitly presses an existing help action. */
(() => {
  'use strict';
  if (window.__PW_AGENT_HELP_BRIDGE_V23__) return;
  window.__PW_AGENT_HELP_BRIDGE_V23__ = true;
  const api = (...args) => window.pixelWorksApi(...args);
  const active = () => window.__PIXEL_WORKS_DEMO__?.model?.activeProjectId || '';
  const norm = text => String(text || '').normalize('NFKC').trim().toLocaleLowerCase('sv-SE');
  const model = () => window.__PIXEL_WORKS_DEMO__?.model;
  const key = (slug, id) => `${slug}\u0000${id}`;
  const state = {busy:false, loading:false, last:null};
  const style = document.createElement('style');
  style.textContent = `
    #pw23HelpDialog{box-sizing:border-box;width:min(780px,calc(100vw - 16px));max-height:90dvh;overflow:auto;
      padding:18px;border:7px ridge #a8794c;background:#f8f4e7;color:#20354b;font:14px/1.5 system-ui,sans-serif}
    #pw23HelpDialog::backdrop{background:rgba(5,16,32,.75)}
    #pw23HelpDialog h2{font-size:22px;color:#1e415b;margin:0 0 8px}
    #pw23HelpDialog p{line-height:1.45}
    #pw23HelpDialog button{min-height:44px;cursor:pointer;font:700 14px system-ui,sans-serif;
      border:2px solid #9c7946;background:#f1d28f;color:#1d3650;padding:9px 12px;margin:3px}
    #pw23HelpDialog button:focus-visible{outline:3px solid #2479ac;outline-offset:2px}
    #pw23HelpDialog .pw23-head{display:flex;align-items:start;justify-content:space-between;gap:12px}
    #pw23HelpDialog .pw23-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:14px 0}
    #pw23HelpDialog .pw23-card{min-width:0;background:white;border:2px solid #bec6c0;padding:12px;overflow-wrap:anywhere}
    #pw23HelpDialog .pw23-card small{display:block;color:#425e6d}
    #pw23HelpDialog .pw23-warning{border-left:4px solid #ba8744;background:#fff1d2;padding:10px}
    #pw23HelpDialog .pw23-muted{color:#4d6170;font-size:12px}
    #pw23HelpDialog [role=status]{white-space:pre-wrap;color:#883b26}
    @media(max-width:590px){#pw23HelpDialog{padding:10px}#pw23HelpDialog .pw23-list{grid-template-columns:1fr}}
    #pw13Dialog .pw23-studio-links{margin:8px 0;padding:10px;background:#dbecef;border:2px solid #8baebb}
    #pw13Dialog .pw23-studio-links button{min-height:44px}
    #pw13Dialog .pw23-studio-links small{display:block;color:#345268;line-height:1.4;margin-top:4px}
  `;
  document.head.append(style);
  const dlg = document.createElement('dialog');dlg.id='pw23HelpDialog';dlg.setAttribute('aria-label','Hjälpärenden i hela studion');document.body.append(dlg);

  function renderShell(title, summary='') {
    dlg.replaceChildren();
    const head=document.createElement('header');head.className='pw23-head';
    const h=document.createElement('h2');h.textContent=title;
    const close=document.createElement('button');close.type='button';close.textContent='✕ Stäng';close.onclick=()=>dlg.close();
    head.append(h,close);dlg.append(head);
    if(summary){const p=document.createElement('p');p.className='pw23-muted';p.textContent=summary;dlg.append(p)}
    if(!dlg.open)dlg.showModal();
  }
  function reportLink(slug,c,counts) {
    const name=c.agent_name||'Tidigare medarbetare';
    const card=document.createElement('article');card.className='pw23-card';
    const h=document.createElement('strong');h.textContent='❗ '+name;
    const project=document.createElement('small');project.textContent='Projekt: '+(c.project_name||slug)+' · Arbetsrapport: '+c.id;
    const why=document.createElement('p');why.textContent=c.friendly_reason||c.reason||'Arbetet behöver granskas.';
    const status=document.createElement('small');status.textContent='Originalagent-ID: '+(c.agent_id||'saknas')+' · '+(c.state||'hjälp');
    card.append(h,project,why,status);
    const count=counts.get(key(slug,c.agent_id))||0;
    const button=document.createElement('button');button.type='button';
    button.textContent=count>1?'📨 Öppna projektets beslutsinkorg':'💬 Öppna just detta hjälpärende';
    button.onclick=()=>{
      dlg.close();
      if(count===1 && typeof window.pixelWorksHelpLive==='function') {
        // The existing backend verifies report ownership and will only act on
        // this project's unresolved report. No project switch is required.
        window.pixelWorksHelpLive(slug,c.agent_id);
      } else {
        const selection=document.querySelector('#projectSelect');
        if(selection && selection.value!==slug){selection.value=slug;selection.dispatchEvent(new Event('change',{bubbles:true}))}
        if(typeof window.pixelWorksOpenDecisionContext==='function')window.pixelWorksOpenDecisionContext({kind:'help',employee:name});
        else window.pixelWorksHelpLive?.(slug,c.agent_id);
      }
    };
    card.append(button);return card;
  }
  async function snapshot() {
    if(typeof window.pixelWorksApi!=='function')throw Error('Studions serveranslutning är inte klar.');
    const studio=await api('/api/pw-v013/studio');
    if(!Array.isArray(studio.projects)||!Array.isArray(studio.staff))throw Error('Studiopersonal kunde inte läsas.');
    const responses=await Promise.allSettled(studio.projects.map(async p=>({p,cases:(await api('/api/projects/'+encodeURIComponent(p.id)+'/help')).cases})));
    const errors=responses.filter(x=>x.status==='rejected').length;
    const cases=responses.filter(x=>x.status==='fulfilled').flatMap(x=>(Array.isArray(x.value.cases)?x.value.cases:[]).map(c=>({
      ...c,project_id:x.value.p.id,project_name:x.value.p.name
    })));
    return {studio,cases,errors};
  }
  function showList(data,{name='',intro=''}={}) {
    const cases=data.cases.filter(c=>!name||norm(c.agent_name)===norm(name));
    const persons=data.studio.staff.filter(p=>!name||norm(p.name)===norm(name));
    const ids=new Set(persons.map(p=>key(p.project_id,p.agent_id)));
    const unidentified=cases.filter(c=>!ids.has(key(c.project_id,c.agent_id))).length;
    const duplicateNames=new Map();for(const p of data.studio.staff){const n=norm(p.name);duplicateNames.set(n,(duplicateNames.get(n)||0)+1)}
    const dupCount=[...duplicateNames.values()].filter(n=>n>1).length;
    renderShell('💌 Hjälp i hela studion',`${data.studio.project_count} projekt · ${data.studio.staff_count} personalposter · ${cases.length} öppna hjälpärenden`);
    if(intro){const p=document.createElement('p');p.className='pw23-warning';p.textContent=intro;dlg.append(p)}
    if(dupCount||unidentified){const p=document.createElement('p');p.className='pw23-warning';p.textContent=
      `${dupCount} namn förekommer på flera anställningsposter i olika projekt. ${unidentified?unidentified+' hjälpärende(n) har ett äldre ID som inte finns i ursprungsprojektets nuvarande personalregister. ':''}`+
      'Ett namn är inte en unik identitet. Välj rätt projekt och rapport; inga personer eller rapporter slås ihop automatiskt.';
      dlg.append(p)}
    if(data.errors){const p=document.createElement('p');p.setAttribute('role','status');p.textContent='⚠ '+data.errors+' projekt kunde inte läsas. Listan kan vara ofullständig.';dlg.append(p)}
    if(!cases.length){const p=document.createElement('p');p.textContent='Inga öppna hjälpärenden hittades'+(name?' för '+name:'')+'.';dlg.append(p)}
    else {const counts=new Map();for(const c of cases){const k=key(c.project_id,c.agent_id);counts.set(k,(counts.get(k)||0)+1)}
      const list=document.createElement('div');list.className='pw23-list';
      for(const c of cases.sort((a,b)=>String(b.created_at||'').localeCompare(String(a.created_at||''))))list.append(reportLink(c.project_id,c,counts));
      dlg.append(list)}
    const footer=document.createElement('p');footer.className='pw23-muted';footer.textContent='Projektens arbetsordrar, rapporter och spelkod ligger kvar i sitt ursprungsprojekt. Bara ett uttryckligt knapptryck i ett hjälpärende kan starta en åtgärd.';dlg.append(footer);
  }
  async function openStudioHelp(options={}) {
    if(state.loading)return;
    state.loading=true;renderShell('💌 Hjälp i hela studion','Läser enbart verkliga, öppna hjälpärenden…');
    try {const data=await snapshot();state.last=data;showList(data,options)}
    catch(err){renderShell('⚠ Kunde inte läsa studiobeslut');const p=document.createElement('p');p.textContent=String(err.message||err);p.setAttribute('role','status');dlg.append(p)}
    finally{state.loading=false}
  }
  window.pixelWorksStudioHelpAll=openStudioHelp;
  function presentStaffDialog() {
    const studioDlg=document.querySelector('#pw13Dialog');if(!studioDlg?.open)return;
    const container=studioDlg.querySelector('.pw13-shell');if(!container||container.querySelector('.pw23-studio-links'))return;
    const panel=document.createElement('div');panel.className='pw23-studio-links';
    const button=document.createElement('button');button.type='button';button.textContent='💌 Alla hjälpärenden i studion';
    button.onclick=()=>{studioDlg.close();openStudioHelp()};
    const copy=document.createElement('small');copy.textContent='Alla projekt · se vilken Gunnar som behöver hjälp. Inga rapporter flyttas eller kopplas om.';
    panel.append(button,copy);
    const projects=container.querySelector('.pw13-projects');projects?.after(panel);
  }
  // Studio dialog is rebuilt by the existing app. Inject one shared button only
  // into each fresh render; avoid competing with its project selection logic.
  const watcher=new MutationObserver(()=>presentStaffDialog());
  watcher.observe(document.body,{childList:true,subtree:true});
  setInterval(presentStaffDialog,1800);

  async function decideAgent(slug,id,visible) {
    if(state.busy||!slug||slug!==active())return;
    state.busy=true;
    const name=visible?.name||model()?.getAgent?.(id)?.name||'';
    try {
      const data=await snapshot();if(slug!==active())return;
      const exact=data.cases.filter(c=>c.project_id===slug&&String(c.agent_id)===String(id));
      if(exact.length===1){window.pixelWorksHelpLive?.(slug,id);return}
      // Same name across project boundaries is NOT proof of shared identity.
      const similar=data.cases.filter(c=>name&&norm(c.agent_name)===norm(name));
      if(exact.length>1||similar.length){showList(data,{name,intro:'Det finns ett eller flera äldre hjälpärenden för namnet '+name+'. Välj uttryckligen rätt projekt och rapport; ingen automatisk namnkoppling görs.'});return}
      const roster=await api('/api/projects/'+encodeURIComponent(slug)+'/staff');if(slug!==active())return;
      if(Array.isArray(roster.staff)&&roster.staff.some(a=>String(a.id)===String(id))){
        if(typeof window.pixelWorksTalkLive==='function')window.pixelWorksTalkLive(slug,id);
        else window.__PIXEL_WORKS_DEMO__?.ui?.selectAgent?.(id);
      }else{
        renderShell('⚠ Personalposten har ändrats');const msg=document.createElement('p');msg.textContent=(name||'Den anställda')+' finns inte längre med detta ID i '+slug+'. Öppna Min studio och välj rätt projektpost; ingen namnmatchning sker automatiskt.';dlg.append(msg);
      }
    }catch(err){renderShell('⚠ Kunde inte öppna personalärendet');const msg=document.createElement('p');msg.textContent=String(err.message||err);dlg.append(msg)}
    finally{state.busy=false}
  }
  window.pixelWorksTalkOrHelpLive=decideAgent;
  // Central click capture, supersedes earlier v2.2's name matching entirely.
  window.addEventListener('click',event=>{
    const node=event.target?.closest?.('#agentLayer .agent');const m=model();
    if(!node||!m?.project?.live||node.dataset.wasDragged==='1')return;
    const slug=active(),id=node.dataset.id;if(!slug||!m.getAgent?.(id))return;
    event.preventDefault();event.stopImmediatePropagation();
    decideAgent(slug,id,m.getAgent(id));
  },true);
})();
