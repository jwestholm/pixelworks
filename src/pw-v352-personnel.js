/* v3.5.2 - visual CSS for the game's existing global personnel renderer.
   No independent state, AI provider calls, or extra dialogs. */
(() => {
 'use strict';
 if(document.getElementById('pw352-personnel-css'))return;
 const link=document.createElement('link');
 link.id='pw352-personnel-css';
 link.rel='stylesheet';
 link.href='./src/pw-v352-personnel.css?v=3.5.2';
 document.head.append(link);
})();
