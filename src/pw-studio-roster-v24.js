/* Pixel Works v2.4 — one playable studio roster, scroll repair and safe dismissals.
 * Reads the existing server-owned v0.13 roster. No identity merge, AI call or
 * migration runs when this module loads. Project history stays untouched. */
(() => {
  'use strict';
  if (window.__PW_STUDIO_ROSTER_V24__) return;
  window.__PW_STUDIO_ROSTER_V24__ = true;
  // The v0.13 module may create its dialog slightly later than main.js.
  const css = document.createElement('style');
  css.id = 'pw24-roster-style';
  css.textContent = `
    #pw13Dialog{box-sizing:border-box!important;width:min(930px,calc(100vw - 14px))!important;
      height:min(810px,90dvh)!important;max-height:90dvh!important;
      overflow:hidden!important;overscroll-behavior:contain;}
    #pw13Dialog::backdrop{overflow:hidden;overscroll-behavior:contain}
    #pw13Dialog .pw13-shell{height:100%;min-height:0;box-sizing:border-box;
      display:flex;flex-direction:column;overflow:hidden;}
    #pw13Dialog .pw13-shell>.pw13-head,
    #pw13Dialog .pw13-shell>.pw13-projects,
    #pw13Dialog .pw13-shell>.pw23-studio-links,
    #pw13Dialog .pw13-shell>.pw24-roster-tools,
    #pw13Dialog .pw13-shell>h3,
    #pw13Dialog .pw13-shell>p,
    #pw13Dialog .pw13-shell>.pw13-notice {flex-shrink:0;}
    #pw13Dialog .pw13-head {position:relative;gap:8px;padding-bottom:7px;}
    #pw13Dialog .pw13-head h2{font-size:20px}
    #pw13Dialog .pw13-shell>p{font-size:12px;line-height:1.35;margin:5px 0;}
    #pw13Dialog .pw13-shell>h3{margin:7px 0 3px;font-size:15px}
    #pw13Dialog .pw13-projects{display:flex;flex-wrap:nowrap;gap:4px;overflow-x:auto;
      overflow-y:hidden;min-height:45px;scrollbar-width:thin;padding:1px 0 3px;}
    #pw13Dialog .pw13-projects button{flex:0 0 auto;min-height:37px;margin:0;padding:5px 9px;font-size:12px}
    #pw13Dialog .pw23-studio-links {margin:4px 0;padding:6px 8px;}
    #pw13Dialog .pw23-studio-links small{display:none;}
    #pw13Dialog .pw23-studio-links button{min-height:36px;margin:0;padding:5px 9px;font-size:12px;}
    #pw13Dialog .pw13-staff{min-height:0!important;flex:1 1 auto!important;
      display:grid;grid-template-columns:repeat(2,minmax(0,1fr));
      grid-auto-rows:max-content;align-content:start;align-items:stretch;
      overflow-y:auto!important;overflow-x:hidden!important;
      overscroll-behavior:contain;-webkit-overflow-scrolling:touch;touch-action:pan-y;
      scrollbar-gutter:stable;padding:5px 6px 14px 3px;margin:4px 0 6px;}
    #pw13Dialog .pw13-staff .pw13-card{height:auto;min-height:130px;min-width:0;
      display:flex;flex-direction:column;gap:4px;overflow-wrap:anywhere;}
    #pw13Dialog .pw13-staff .pw13-card[hidden]{display:none!important;}
    #pw13Dialog .pw13-staff .pw13-card strong{font-size:15px;}
    #pw13Dialog .pw13-staff .pw13-card small{white-space:normal;line-height:1.4;}
    #pw13Dialog .pw24-identity{font-size:11px;color:#416073;display:block;line-height:1.4;}
    #pw13Dialog .pw13-assignment{margin-top:auto;}
    #pw13Dialog .pw13-assignment select{min-width:0;max-width:100%;}
    #pw13Dialog .pw24-roster-tools{display:flex;flex-wrap:wrap;align-items:end;gap:8px;
      padding:7px 9px;background:#dcebed;border:2px solid #96b4b6;margin:4px 0 3px;}
    #pw13Dialog .pw24-roster-tools label{font:700 12px system-ui,sans-serif;flex:1 1 165px;
      min-width:0;display:flex;flex-direction:column;gap:4px;}
    #pw13Dialog .pw24-roster-tools input,#pw13Dialog .pw24-roster-tools select{box-sizing:border-box;
      width:100%;min-height:42px;border:2px solid #7c9cac;border-radius:3px;padding:6px 8px;
      color:#16344c;background:white;font:14px system-ui,sans-serif;}
    #pw13Dialog .pw24-roster-count{width:100%;font-size:12px;color:#28495c;}
    #pw13Dialog .pw24-dismiss{border-color:#9a6061!important;background:#f9e0d9!important;
      color:#572b30!important;font-size:12px;min-height:38px!important;}
    #pw13Dialog .pw24-confirm{margin-top:8px;padding:9px;border:2px solid #bb8174;
      background:#fff1e6;color:#4d3134;}
    #pw13Dialog .pw24-confirm p{margin:0 0 5px;font-size:12px;}
    #pw13Dialog .pw24-confirm input{box-sizing:border-box;width:100%;min-height:42px;
      padding:7px;color:#233b4c;background:white;border:2px solid #b99a88;font:14px system-ui,sans-serif}
    #pw13Dialog .pw24-confirm button{min-height:40px!important;font-size:12px;}
    #pw13Dialog .pw24-inline-error{font-size:12px;color:#a43132;white-space:pre-wrap;}
    #pw13Dialog .pw24-empty{border:2px dashed #a5aeb3;padding:14px;color:#3b5665;background:#f7fcfd;}
    #pw13Dialog .pw13-shell>p.pw13-muted{margin:3px 0;font-size:11px}
    @media(max-width:630px){
      #pw13Dialog{width:calc(100vw - 8px)!important;height:94dvh!important;max-height:94dvh!important;
        border-width:4px!important;}
      #pw13Dialog .pw13-shell{padding:10px!important;}
      #pw13Dialog .pw13-head h2{font-size:17px;}
      #pw13Dialog .pw13-staff{grid-template-columns:1fr;gap:8px;}
      #pw13Dialog .pw13-shell>p{display:none;}
      #pw13Dialog .pw24-roster-tools{gap:6px;padding:5px;}
      #pw13Dialog .pw24-roster-tools label{flex-basis:120px;}
      #pw13Dialog .pw13-staff .pw13-card{min-height:0;}
    }
  `;
  document.head.append(css);
  const state = {rosterNode:null,loading:false,people:[],term:'',project:'all',muting:false};
  const norm = value => String(value??'').normalize('NFKC').toLocaleLowerCase('sv-SE');
  const api = (...args) => window.pixelWorksApi(...args);
  const el = (tag,cls,text) => {
    const e=document.createElement(tag);if(cls)e.className=cls;
    if(text!==undefined)e.textContent=text;return e;
  };
  function liveDialog(){return document.querySelector('#pw13Dialog');}
  function onNewRoster() {
    const d=liveDialog(),list=d?.querySelector('.pw13-staff');
    if(!d?.open || !list || list===state.rosterNode || state.loading || typeof window.pixelWorksApi!=='function')return;
    state.rosterNode=list;
    readRoster(list).catch(err=>{
      if(!list.isConnected)return;
      const warning=el('p','pw24-inline-error','⚠ Personalvyn kunde inte uppdateras: '+String(err.message||err));
      list.before(warning);
    });
  }
  async function readRoster(list){
    state.loading=true;
    try {
      const data=await api('/api/pw-v013/studio');
      if(!Array.isArray(data.staff) || !Array.isArray(data.projects))throw Error('Serverns personalregister saknas.');
      if(!list.isConnected||liveDialog()?.querySelector('.pw13-staff')!==list)return;
      state.people=data.staff.slice();
      renderControls(list,data);
    } finally {state.loading=false;}
  }
  function renderControls(list,data){
    const root=list.closest('.pw13-shell');if(!root)return;
    root.querySelector('.pw24-roster-tools')?.remove();
    const tools=el('div','pw24-roster-tools');tools.setAttribute('role','group');
    tools.setAttribute('aria-label','Filtrera hela studions personal');
    const nameLabel=el('label','', 'Sök anställd');
    const search=el('input');search.type='search';search.id='pw24-search';search.placeholder='Namn, yrke eller projekt';search.value=state.term;
    search.autocomplete='off';nameLabel.append(search);
    const projectLabel=el('label','', 'Projekt');
    const filter=el('select');filter.id='pw24-project';
    const all=el('option','', 'Alla projekt');all.value='all';filter.append(all);
    for(const p of data.projects){const option=el('option','',p.name);option.value=p.id;filter.append(option)}
    if([...filter.options].some(o=>o.value===state.project))filter.value=state.project;
    else state.project='all';
    projectLabel.append(filter);
    const count=el('div','pw24-roster-count');count.id='pw24-count';count.setAttribute('aria-live','polite');
    tools.append(nameLabel,projectLabel,count);
    list.before(tools);
    const header=root.querySelector('.pw13-head h2');
    if(header)header.textContent='🏢 Min studio · hela teamet';
    // A roster item has a stable studio identity. Names never identify people.
    const byId=new Map(data.staff.map(p=>[String(p.studio_id),p]));
    for(const card of list.querySelectorAll('.pw13-card')){
      const sid=card.id.replace(/^pw13-card-/,'');
      const person=byId.get(sid);
      if(!person)continue;
      card.dataset.pw24Id=sid;
      card.dataset.pw24Project=person.project_id;
      card.dataset.pw24Search=norm([person.name,person.role,person.project_name,person.role_type].join(' '));
      card.title=`${person.name} · ${person.project_name}\nStudio-ID: ${sid}\nProjektagent: ${person.agent_id}`;
      const ident=el('small','pw24-identity',`👤 Egen identitet · #${sid.slice(-7)} · ${person.project_name}`);
      card.querySelector('strong')?.after(ident);
      if(data.shared){
        const controls=card.querySelector('.pw13-assignment');
        if(controls){
          const button=el('button','pw24-dismiss',person.busy?'🔒 Arbetar · kan inte avskedas':'🚪 Avskeda…');
          button.type='button';button.disabled=!!person.busy;
          button.addEventListener('click',()=>showDismiss(card,person));
          controls.append(button);
        }
      }
    }
    const empty=el('p','pw24-empty','Inga anställda matchar sökningen.');empty.hidden=true;
    list.after(empty);
    const apply=()=>{
      const text=norm(state.term.trim());let visible=0;
      for(const card of list.querySelectorAll('.pw13-card')){
        const show=(state.project==='all'||card.dataset.pw24Project===state.project)&&
          (!text||String(card.dataset.pw24Search||'').includes(text));
        card.hidden=!show;
        if(show)visible++;
      }
      count.textContent=`${visible} av ${state.people.length} separata anställda · ${data.projects.length} spel · skrolla i personallistan nedanför`;
      empty.hidden=visible!==0;
    };
    search.addEventListener('input',()=>{state.term=search.value;apply();list.scrollTop=0});
    filter.addEventListener('change',()=>{state.project=filter.value;apply();list.scrollTop=0});
    apply();
  }
  function showDismiss(card,person){
    card.querySelector('.pw24-confirm')?.remove();
    const box=el('div','pw24-confirm');
    const title=el('p','',`Avskeda ${person.name} från ${person.project_name}? Historiska rapporter och spelkoden behålls. Inga AI-anrop startas.`);
    const label=el('label','',`Skriv ${person.name} för att bekräfta`);
    const input=el('input');input.type='text';input.autocomplete='off';input.spellcheck=false;
    const okay=el('button','pw24-dismiss','Bekräfta avsked');okay.type='button';
    const cancel=el('button','','Ångra');cancel.type='button';
    const error=el('p','pw24-inline-error');error.setAttribute('role','alert');
    label.append(input);box.append(title,label,okay,cancel,error);card.append(box);
    cancel.addEventListener('click',()=>box.remove());
    okay.addEventListener('click',async()=>{
      if(input.value.trim()!==person.name){error.textContent='Namnet stämmer inte. Inget har ändrats.';return;}
      okay.disabled=true;cancel.disabled=true;
      try{
        // Recheck the exact server identity; never dismiss someone by name.
        const fresh=await api('/api/pw-v013/studio');
        const match=fresh.staff?.find(p=>p.studio_id===person.studio_id&&p.project_id===person.project_id&&p.agent_id===person.agent_id);
        if(!match||match.busy)throw Error(match?'Medarbetaren har börjat arbeta.':'Personalposten ändrades. Öppna Min studio igen.');
        const result=await api('/api/projects/'+encodeURIComponent(person.project_id)+'/staff/dismiss',{
          agent_id:person.agent_id,approval:'DISMISS_STAFF'
        });
        if(result.dismissed!==person.agent_id)throw Error('Servern kunde inte bekräfta avskedet.');
        card.remove();state.people=state.people.filter(p=>p.studio_id!==person.studio_id);
        box.remove();
        const filter=liveDialog()?.querySelector('#pw24-search');
        filter?.dispatchEvent(new Event('input'));
        const feedback=el('div','pw24-inline-error',`✅ ${person.name} avskedad. Historiska rapporter behållna.`);
        const tools=liveDialog()?.querySelector('.pw24-roster-tools');tools?.append(feedback);
        // Refresh sprites from the authoritative server; don't create simulated staff.
        try {await window.pixelWorksRefreshLive?.();}
        catch(refreshError){feedback.textContent+=' ⚠ Uppdatera kontoret: '+String(refreshError.message||refreshError);}
      }catch(err){error.textContent='⚠ '+String(err.message||err);okay.disabled=false;cancel.disabled=false;}
    });
    input.focus({preventScroll:true});
  }
  let pending=false;
  const check=()=>{
    if(pending)return;pending=true;
    queueMicrotask(()=>{pending=false;onNewRoster()});
  };
  // Observe only the shared studio dialog after it exists. The game animates
  // other nodes continuously and should not trigger roster refresh work.
  const dialogObserver=new MutationObserver(check);
  function attachDialogObserver(){
    const current=liveDialog();if(!current)return false;
    dialogObserver.observe(current,{childList:true,subtree:true,attributes:true,attributeFilter:['open']});
    check();return true;
  }
  if(!attachDialogObserver()){
    const creationObserver=new MutationObserver(()=>{
      if(attachDialogObserver())creationObserver.disconnect();
    });
    creationObserver.observe(document.body,{childList:true,subtree:true});
  }
})();
