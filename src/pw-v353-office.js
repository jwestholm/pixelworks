/* Pixel Works 3.5.3 — office art layers only. No AI, files or gameplay calls. */
(() => {
 'use strict';
 if(window.__PW353_OFFICE__)return; window.__PW353_OFFICE__=true;
 const style=document.createElement('link');style.rel='stylesheet';style.href='./src/pw-v353-office.css';style.id='pw353OfficeCSS';document.head.append(style);
 function ensure(){
   const stage=document.getElementById('officeStage');if(!stage)return;
   if(stage.querySelector('#pw353OfficeDecor'))return;
   const root=document.createElement('div');root.id='pw353OfficeDecor';root.setAttribute('aria-hidden','true');
   root.innerHTML='<div class="pw353-window-glass pw353-w1"></div><div class="pw353-window-glass pw353-w2"></div><div class="pw353-window-glass pw353-w3"></div><div class="pw353-rug pw353-rug-main"></div><div class="pw353-rug pw353-rug-meet"></div><div class="pw353-coffee-steam">♨</div>';
   // Keep decoration below the clickable employee and workstation layers.
   stage.insertBefore(root,stage.firstChild);
 }
 function refresh(){
   ensure();
   // Distinguish the installed UI layer from the legacy engine version.
   const brand=document.querySelector('.brand-title');
   if(brand&&!document.getElementById('pw353Version')){
     const badge=document.createElement('small');badge.id='pw353Version';
     badge.textContent=' · UI 3.5.3';badge.title='Grafik och kontorsinteraktioner (backendversion visas separat)';
     brand.append(badge);
   }
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',refresh,{once:true});else refresh();
 window.addEventListener('pixelworks:v3-office-refresh',refresh);
 setInterval(()=>{if(!document.hidden)refresh()},5000);
 window.pixelWorksV353Office={refresh};
})();
