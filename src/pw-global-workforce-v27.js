/* Pixel Works v2.7 – opt-in global workforce cutover. No AI/network writes on view. */
(() => {
  'use strict';
  if(window.__PW_WORKFORCE_V27__)return;
  window.__PW_WORKFORCE_V27__=true;
  const css=document.createElement('style');
  css.id='pw27-css';
  css.textContent=`
    #pw13Dialog .pw27-workforce{border:2px solid #678d99;background:#ebf4ef;color:#213e4f;
      margin:10px 0;padding:12px 14px;font:13px/1.45 system-ui,sans-serif;}
    #pw13Dialog .pw27-workforce strong{color:#1c4a59}
    #pw13Dialog .pw27-workforce p{margin:5px 0 9px}
    #pw13Dialog .pw27-workforce button{background:#eac77e;color:#243d48;border:2px solid #977346;
      min-height:40px;padding:7px 12px;font-weight:800}
    #pw13Dialog .pw27-workforce .pw27-projects{display:flex;gap:7px;flex-wrap:wrap}
    #pw13Dialog .pw27-workforce .pw27-projects span{border:1px solid #7b9ba1;
      background:white;padding:4px 8px}
    #pw13Dialog .pw27-warn{color:#983d2e!important;white-space:pre-wrap}
    body.pw27-workforce-active #pw13Dialog .pw25-box{display:none!important}
    #pw27Confirm{box-sizing:border-box;width:min(620px,calc(100vw - 12px));
      max-height:calc(100dvh - 15px);overflow:auto;background:#fff9ec;color:#233c4f;
      border:7px ridge #a67b56;padding:15px;box-shadow:6px 8px 0 #12283a;
      font:14px/1.5 system-ui,sans-serif}
    #pw27Confirm::backdrop{background:#0d263eb8}
    #pw27Confirm .pw27-people{max-height:36dvh;overflow-y:auto;background:#fff;
      border:1px solid #91a9ab;padding:9px;white-space:pre-line}
    #pw27Confirm button{cursor:pointer;min-height:43px;border:2px solid #9a7646;
      background:#f0c779;color:#233849;padding:8px 11px;font-weight:800;margin:8px 5px 0 0}
    #pw27Confirm button:disabled{opacity:.5}
    #pw27Confirm button.pw27-cancel{background:#476784;color:#fff}
    #pw27Confirm [role=alert]{color:#983d2e;white-space:pre-wrap}
    @media(max-width:630px){#pw13Dialog .pw27-workforce{padding:8px}#pw27Confirm{border-width:4px;padding:9px}}
  `;document.head.append(css);
  const $=(q,root=document)=>root.querySelector(q);
  const request=(path,data)=>window.pixelWorksApi(path,data);
  const base='/api/pw-v027/workforce';
  const modal=document.createElement('dialog');modal.id='pw27Confirm';
  modal.setAttribute('aria-label','Aktivera global arbetsstyrka');document.body.append(modal);
  let lastRoster=null,loading=false;
  const el=(tag,txt)=>{const n=document.createElement(tag);if(txt!==undefined)n.textContent=txt;return n;};
  function approval(data,panel){
    const heading=el('h2','🏢 Aktivera gemensam arbetsstyrka');
    const intro=el('p','Alla anställda tillhör Pixel Works. Varje person får en enda aktiv projekttilldelning åt gången. Den gamla arbetsmotorn får deras uppgifter via en adapter. Inga gamla projektfiler eller arbetsrapporter tas bort.');
    const explanation=el('p','Det här ändrar vilken personaldatabas som används för NYA uppdrag. Vänta tills arbetspass är avslutade. Andra projekts bakgrundsproduktion pausas inte automatiskt.');
    const list=el('div');list.className='pw27-people';list.textContent=data.people.map(p=>
      `${p.name} · ${p.project_id} · ${p.studio_id}`).join('\n');
    const ok=el('button','✅ Använd global personal för uppdrag');
    const cancel=el('button','Tillbaka');cancel.className='pw27-cancel';
    const error=el('p');error.setAttribute('role','alert');
    modal.replaceChildren(heading,intro,explanation,list,ok,cancel,error);
    cancel.onclick=()=>modal.close();
    ok.onclick=async()=>{
      ok.disabled=cancel.disabled=true;
      try{
        const answer=await request(base+'/activate',{
          approval:'ACTIVATE_GLOBAL_WORKFORCE_V27',
          expected_ids:data.people.map(p=>p.studio_id).sort()});
        if(!answer.active)throw Error('Servern har inte bekräftat aktiveringen');
        modal.close();await draw(panel);window.pixelWorksRefreshLive?.();
      }catch(exc){error.textContent='⚠ '+String(exc.message||exc);ok.disabled=cancel.disabled=false;}
    };
    modal.showModal();
  }
  async function draw(panel){
    if(!panel.isConnected)return;
    loading=true;
    try{
      const data=await request(base);
      if(!panel.isConnected)return;
      panel.replaceChildren();
      const active=!!data.active;
      document.body.classList.toggle('pw27-workforce-active',active);
      panel.append(el('strong',active?'🟢 GLOBAL ARBETSSTYRKA AKTIV':'🏢 Nästa steg: global arbetsstyrka'));
      panel.append(el('p',active
        ?`${data.count} anställda. En person har ett beständigt studio-ID, en aktiv projekttilldelning och kan byta spel utan att anställas igen.`
        :`${data.count} registrerade personer. Projektens gamla personalfiler styr fortfarande nya AI-uppdrag tills du aktiverar bytet.`));
      if(active){
        const counts=new Map(data.projects.map(p=>[p.id,0]));
        for(const p of data.people)if(!p.dismissed&&counts.has(p.project_id))counts.set(p.project_id,counts.get(p.project_id)+1);
        const projectList=el('div');projectList.className='pw27-projects';
        data.projects.forEach(p=>projectList.append(el('span',`${p.name}: ${counts.get(p.id)} tilldelade`)));
        panel.append(projectList);
        panel.append(el('p','Välj en person längre ned och använd Tilldela för att byta spel. Det ändrar inte hennes identitet. Historiska arbetsrapporter finns kvar i ursprungsprojektet.'));
        panel.append(el('p','⚠ Bakgrundsjobben i andra spel är fortfarande aktiva där en chef har tillstånd. Det styr vi centralt i nästa steg.'));
      }else if(data.registered){
        const button=el('button','🔁 Granska och aktivera global personal');button.type='button';
        button.addEventListener('click',()=>approval(data,panel));panel.append(button);
      }else{
        const note=el('p','Registrera personalen i panelen ovan först (v2.5).');panel.append(note);
      }
    }catch(error){panel.replaceChildren(el('strong','⚠ Global personal kunde inte läsas'),
      el('p',String(error.message||error)));}
    finally{loading=false;}
  }
  function attach(){
    const dialog=$('#pw13Dialog');const roster=$('.pw13-staff',dialog);
    if(!dialog?.open||!roster||lastRoster===roster||loading)return;
    lastRoster=roster;
    const panel=el('section');panel.className='pw27-workforce';
    panel.setAttribute('aria-label','Global arbetsstyrka');
    // Put beneath conversion progress, above employee filters and cards.
    const before=$('.pw24-roster-tools',dialog)||roster;
    before.before(panel);draw(panel);
  }
  let pending=false;
  const schedule=()=>{if(pending)return;pending=true;queueMicrotask(()=>{pending=false;attach()})};
  function boot(){
    const dialog=$('#pw13Dialog');if(!dialog)return false;
    new MutationObserver(schedule).observe(dialog,{childList:true,subtree:true,attributes:true,attributeFilter:['open']});
    schedule();return true;
  }
  if(!boot())new MutationObserver((obs)=>{if(boot())obs.disconnect()}).observe(document.body,{childList:true,subtree:true});
})();
