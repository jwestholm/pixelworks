/* Pixel Works v2.5 – one studio identity registry, explicit lossless conversion.
 * Never performs migrations automatically, never dismisses staff, no AI calls. */
(() => {
  'use strict';
  if (window.__PW_GLOBAL_STAFF_V25__) return;
  window.__PW_GLOBAL_STAFF_V25__ = true;
  const css=document.createElement('style');
  css.id='pw25-registry-css';
  css.textContent=`
    #pw13Dialog .pw25-box{background:#e8f1ee;border:2px solid #7aa2a1;color:#1c4050;
      padding:8px 10px;margin:5px 0 7px;flex:0 0 auto;max-height:27vh;overflow:auto;
      font:13px/1.5 system-ui,sans-serif;overscroll-behavior:contain}
    #pw13Dialog .pw25-box[hidden],#pw25-confirm[hidden]{display:none!important}
    #pw13Dialog .pw25-box strong{color:#1b4050}
    #pw13Dialog .pw25-box p{margin:3px 0 7px;font-size:12px}
    #pw13Dialog .pw25-box button{min-height:38px;margin:3px 6px 2px 0;font-size:12px}
    #pw13Dialog .pw25-warning{color:#82382e;white-space:pre-wrap}
    #pw25-confirm{box-sizing:border-box;width:min(620px,calc(100vw - 16px));
      max-height:calc(100dvh - 20px);overflow:auto;background:#fbf7e9;color:#21394e;
      border:7px ridge #a47b55;padding:17px;box-shadow:8px 8px 0 #152337;
      font:14px/1.5 system-ui,sans-serif}
    #pw25-confirm::backdrop{background:#081b30bb}
    #pw25-confirm h2{margin:0 0 9px;color:#233f50}
    #pw25-confirm .pw25-list{border:1px solid #8eabbb;background:white;padding:9px;
      max-height:34vh;overflow:auto;line-height:1.7;white-space:pre-line}
    #pw25-confirm button{min-height:44px;padding:8px 12px;margin:8px 5px 0 0;
      background:#e9bc74;color:#1b3046;border:2px solid #896944;font-weight:800;cursor:pointer}
    #pw25-confirm button:disabled{opacity:.5}
    #pw25-confirm .pw25-cancel{background:#536d87;color:white;border-color:#344658}
    #pw25-confirm .pw25-error{white-space:pre-wrap;color:#912c27}
    @media(max-width:640px){#pw13Dialog .pw25-box{max-height:18vh;padding:5px 7px}
      #pw13Dialog .pw25-box p{display:none}#pw25-confirm{border-width:4px;padding:10px}}
  `;
  document.head.append(css);
  const path='/api/pw-v025/global-staff';
  let observed=null,loading=false,last=null;
  const q=(s,p=document)=>p.querySelector(s);
  const create=(type,cl,txt)=>{const node=document.createElement(type);if(cl)node.className=cl;if(txt!==undefined)node.textContent=txt;return node;};
  const request=(path,data)=>window.pixelWorksApi(path,data);
  const modal=document.createElement('dialog');modal.id='pw25-confirm';
  modal.setAttribute('aria-label','Skapa globalt personregister');document.body.append(modal);
  function projectSummary(data){
    const projects=new Map((data.projects||[]).map(p=>[p.id,p.name]));
    return (data.staff||[]).map(p=>`${p.name} · ${projects.get(p.project_id)||p.project_id} · ${p.studio_id}`).join('\n');
  }
  async function draw(panel){
    if(!panel.isConnected)return;
    loading=true;
    try{
      const data=await request(path);
      if(!panel.isConnected)return;
      last=data;
      panel.replaceChildren();
      const intro=create('strong','',data.registered?'🏢 Global personalstyrka registrerad':'🏢 Konvertera till en global personalstyrka');panel.append(intro);
      const msg=create('p','',data.registered?
        `${data.people_count} personer har beständiga studio-ID:n. Projektens gamla personalfiler används fortfarande som adapter medan jobbmotor och historik migreras.`:
        `${data.current_count} personer i ${data.projects?.length||0} projekt kan få beständiga identiteter i Min studio. Inga avskedas, slås ihop eller byter projekt.`);
      panel.append(msg);
      if(!data.registered){
        const act=create('button','','👥 Granska och skapa personregister');
        act.type='button';act.addEventListener('click',()=>showConfirm(data));panel.append(act);
      }else{
        const count=create('small','',`Register: ${data.registry_created_at||'okänt datum'} · Säkerhetskopia: ${data.backup_ref||'okänt'}`);
        panel.append(count);
        if(data.needs_reconciliation){
          const warning=create('p','pw25-warning',`⚠ Personalen har ändrats efter registreringen: ${data.new_count} nya, ${data.missing_count} saknas, ${data.changed_assignments.length} projektbyten. Gamla uppdrag är inte raderade. Uppdatering av personregistret kommer i nästa steg.`);
          panel.append(warning);
        }
      }
      const note=create('p','','Personallistan är global, men AI-arbete sker ännu i tilldelat projekt. Byt projekt utan att registrerade personer försvinner ur Min studio.');panel.append(note);
    }catch(error){
      if(!panel.isConnected)return;
      panel.replaceChildren(create('strong','','⚠ Globalt personregister kunde inte läsas'));
      panel.append(create('p','pw25-warning',String(error.message||error)));
    }finally{loading=false;}
  }
  function showConfirm(data){
    const heading=create('h2','','👥 Konvertera personalen i Min studio');
    const text=create('p','','Det här skapar ett separat, beständigt personregister och säkerhetskopierar befintliga personal- och kompetensfiler. Alla är kvar. Inga AI-anrop eller avskedningar görs.');
    const caption=create('p','','Följande personer registreras var för sig även om namnen är lika:');
    const names=create('div','pw25-list',projectSummary(data));
    const note=create('p','','Gamla projektlokala personalfiler behålls till dess att hela uppdragsmotorn har migrerats. Gör inte manuell rensning av dem.');
    const approve=create('button','','✅ Skapa register med säkerhetskopia');approve.type='button';
    const cancel=create('button','pw25-cancel','Avbryt');cancel.type='button';
    const error=create('div','pw25-error');error.setAttribute('role','alert');
    modal.replaceChildren(heading,text,caption,names,note,approve,cancel,error);
    cancel.onclick=()=>modal.close();
    approve.onclick=async()=>{
      approve.disabled=true;cancel.disabled=true;
      try{
        const ids=data.staff.map(p=>p.studio_id).sort();
        const result=await request(path+'/activate',{approval:'CREATE_GLOBAL_STAFF_V25',expected_ids:ids});
        if(!result.registered)throw Error('Servern bekräftade inte registreringen.');
        modal.close();const panel=q('#pw13Dialog .pw25-box');if(panel)await draw(panel);
      }catch(exc){error.textContent='⚠ '+String(exc.message||exc);approve.disabled=false;cancel.disabled=false;}
    };
    if(!modal.open)modal.showModal();
  }
  function attach(){
    const d=q('#pw13Dialog'),roster=d?.querySelector('.pw13-staff');
    if(!d?.open||!roster||roster===observed||loading)return;
    observed=roster;
    const panel=create('section','pw25-box');panel.setAttribute('aria-label','Globalt personalregister');
    const before=d.querySelector('.pw24-roster-tools')||roster;
    before.before(panel);
    draw(panel);
  }
  let queued=false;
  const check=()=>{if(queued)return;queued=true;queueMicrotask(()=>{queued=false;attach()})};
  const observer=new MutationObserver(check);
  function boot(){
    const node=q('#pw13Dialog');if(!node)return false;
    observer.observe(node,{childList:true,subtree:true,attributes:true,attributeFilter:['open']});
    check();return true;
  }
  if(!boot()){
    const initObserver=new MutationObserver(()=>{if(boot())initObserver.disconnect()});
    initObserver.observe(document.body,{childList:true,subtree:true});
  }
})();
