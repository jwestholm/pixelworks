/* Pixel Works v3 – player-owned recruitment gameplay. DEMO: no provider calls. */
(() => {
'use strict';
if(window.__PW_RECRUIT_V3__)return;
window.__PW_RECRUIT_V3__=true;
const $=(sel,root=document)=>root.querySelector(sel);
const esc=(s)=>String(s??'').replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]));
const api=(url,data)=>{if(!window.pixelWorksApi)throw Error('Pixel Works-servern är inte ansluten');return window.pixelWorksApi(url,data)};
const URL='/api/pw-v3/crew';
let data=null,tab='crew',selected='mira',role='artist',detail=null,notice='',busy=false,officeKey='',loadBusy=false;
const manualRoleByPerson=new Map(); // only player overrides; candidates default to their best role
const roles={'programmer':'Programmerare','artist':'Pixelgrafiker','musician':'Ljudproducent','qa':'QA-testare','writer':'Berättare','research':'Researcher','allround':'Allroundare'};
const colors=['#f3ca83','#6cd6cb','#f48a91'];
const places=[[18,49],[31,57],[43,49],[54,59],[66,52],[81,58],[16,69],[28,71],[40,73],[52,71],[65,72],[80,70],[25,85],[40,86],[58,86],[74,86]];
const css=document.createElement('style');css.id='pw3-style';css.textContent=`
#pw3Open{position:fixed;z-index:80;bottom:20px;left:86px;background:#f4cb77;color:#24384b;
 border:3px solid #6d4731;padding:10px 15px;font:900 13px system-ui;box-shadow:4px 4px #142b38;cursor:pointer}
#pw3Open:hover{background:#ffe6a0}
#gameDock #pw3Open{position:static;display:flex;align-items:center;justify-content:center;min-height:53px;box-shadow:none;font-size:12px;width:auto;z-index:auto}
body.pw3-active #pw13StudioNav{display:none!important}
#pw3Dialog{border:6px solid #845335;outline:4px solid #2d4858;box-shadow:12px 12px #101a29;
 border-radius:5px;padding:0;width:min(1100px,calc(100vw - 28px));height:min(825px,calc(100dvh - 22px));
 max-height:calc(100dvh - 22px);overflow-y:auto;overscroll-behavior:contain;scrollbar-gutter:stable;
 background:#f6efda;color:#283e4b;font:14px/1.42 system-ui;box-sizing:border-box}
#pw3Dialog:not([open]){display:none}#pw3Dialog::backdrop{background:#081624cf}
#pw3Dialog *{box-sizing:border-box}#pw3Dialog h2{font-size:22px;margin:0;color:#fff5d2;line-height:1.1}
#pw3Dialog h3{color:#31516a;margin:8px 0;font-size:17px}#pw3Dialog small{font-size:12px}
#pw3Dialog button,#pw3Dialog select,#pw3Dialog textarea{font:inherit}
#pw3Dialog button{cursor:pointer;min-height:41px;border:2px solid #725033;background:#edc779;
 color:#2b3441;font-weight:800;padding:8px 13px;box-shadow:2px 2px 0 #c9b393;border-radius:3px}
#pw3Dialog button:hover:not(:disabled){filter:brightness(1.08)}#pw3Dialog button:disabled{opacity:.48;cursor:not-allowed}
#pw3Dialog button.pw3-blue{background:#285875;border-color:#173d57;color:#fff3d2}
#pw3Dialog button.pw3-green{background:#78c59e;color:#142f31;border-color:#478878}
#pw3Dialog button.pw3-plain{background:#e8e8da;border-color:#92a19f}
#pw3Dialog button:focus-visible,#pw3Dialog input:focus-visible,#pw3Dialog select:focus-visible,
#pw3Dialog textarea:focus-visible{outline:3px solid #388aba;outline-offset:2px}
#pw3Dialog input,#pw3Dialog select,#pw3Dialog textarea{width:100%;padding:10px;border:2px solid #8ba7a9;
 background:#fffdf4;color:#24384c;min-height:42px}
#pw3Dialog textarea{resize:vertical;min-height:100px}
#pw3Dialog .pw3-head{background:#203b52;border-bottom:5px solid #ba8b54;color:#fff5d2;
 padding:16px 20px;display:flex;justify-content:space-between;align-items:center;gap:10px;position:sticky;top:0;z-index:12}
#pw3Dialog .pw3-sub{color:#bde8df;font-size:12px;margin-top:5px}
#pw3Dialog .pw3-head button{background:#dfe4db;min-width:47px;font-size:20px;padding:6px}
#pw3Dialog .pw3-body{padding:19px 22px 35px}
#pw3Dialog .pw3-tabs{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 12px}
#pw3Dialog .pw3-tabs button.active{background:#347d83;color:white;border-color:#265d6a}
#pw3Dialog .pw3-notice{background:#fef1bd;border:2px solid #ba9955;padding:12px 14px;margin-bottom:14px}
#pw3Dialog .pw3-notice.good{background:#e1f4e9;border-color:#6aa98f}
#pw3Dialog .pw3-error{border-left:4px solid #b84d44;color:#992e26;padding:9px;margin:9px 0;background:#fff2ea}
#pw3Dialog .pw3-grid{display:grid;grid-template-columns:minmax(240px,34%) minmax(0,1fr);gap:18px}
#pw3Dialog .pw3-portrait-card{background:linear-gradient(160deg,#fff3d2,#e4d3a6);padding:15px;
 border:6px ridge #946344;box-shadow:4px 5px 0 #baa47f;min-width:0}
#pw3Dialog .pw3-portrait{display:grid;place-items:center;min-height:225px;background:radial-gradient(circle,#d6eadc,#a5bfb3);
 border:5px solid #385767;margin-bottom:12px}
#pw3Dialog .pw3-portrait svg{width:min(100%,205px);height:205px;image-rendering:pixelated}
#pw3Dialog .pw3-tag{background:#254a5b;color:#fff3d0;display:inline-block;padding:4px 8px;font:800 11px system-ui;margin:3px 0}
#pw3Dialog .pw3-quote{font:italic 600 15px/1.35 Georgia,serif;color:#344f56;margin:8px 0}
#pw3Dialog .pw3-row{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap}
#pw3Dialog .pw3-card{background:#fffdf7;border:2px solid #adc0b8;padding:13px 15px;margin-bottom:12px;min-width:0}
#pw3Dialog .pw3-card strong{color:#264b5d}
#pw3Dialog .pw3-label{font:900 12px system-ui;text-transform:uppercase;letter-spacing:.5px;margin:8px 0}
#pw3Dialog .pw3-pill{display:inline-block;margin:3px 4px 3px 0;padding:5px 9px;
 border:1px solid #8db9b0;background:#e5f3eb;border-radius:5px;font-weight:700;font-size:12px}
#pw3Dialog .pw3-pill.warn{background:#fff0d3;border-color:#d0ad67}
#pw3Dialog .pw3-pill.deny{background:#fde8e7;border-color:#d3aaa5}
#pw3Dialog .pw3-bars{display:grid;grid-template-columns:1fr 1fr;gap:7px 15px}
#pw3Dialog .pw3-bar{display:grid;grid-template-columns:1fr 82px;gap:8px;align-items:center;font-size:12px}
#pw3Dialog .pw3-track{height:11px;background:#d7ded5;border:1px solid #6f8b83;overflow:hidden}
#pw3Dialog .pw3-fill{height:100%;background:#3e9f8e}
#pw3Dialog .pw3-steps{display:flex;justify-content:space-between;gap:8px;align-items:center;
 flex-wrap:wrap;padding:12px;margin-top:12px;border-top:3px solid #c7a46d;background:#f1e4c2}
#pw3Dialog .pw3-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
#pw3Dialog .pw3-list article{background:#fffdf6;border:2px solid #9cb3b2;padding:12px;display:flex;gap:12px;min-width:0;align-items:center}
#pw3Dialog .pw3-list svg{width:73px;height:85px;flex-shrink:0}
#pw3Dialog .pw3-list button{margin:7px 5px 0 0}
#pw3Dialog .pw3-good{color:#28745c;font-weight:850}#pw3Dialog .pw3-bad{color:#a23f35;font-weight:800}
#pw3Dialog .pw3-interview{background:#e7efe6;border:3px solid #77a49c;padding:14px;margin:12px 0}
#pw3Dialog .pw3-demo{background:#214459;color:#fff5d6;font-weight:900;padding:5px 9px;font-size:11px;display:inline-block}
#pw3Dialog .pw3-gorilla{display:grid;place-items:center;padding:12px;background:#d2e4cb;border:4px solid #517768}
#pw3Dialog .pw3-gorilla svg{width:192px;height:192px;image-rendering:pixelated}
#pw3Dialog .pw3-muted{color:#557078;font-size:12px}
body.pw3-active #agentLayer,body.pw3-active #pw13OfficeRoster,body.pw3-active #pw26GlobalAgents,
body.pw3-active #pw26-global-count{display:none!important;visibility:hidden!important}
body.pw3-active #localStudioBtn{display:none!important}
body.pw3-active #pw13StudioNav{opacity:.98}
#pw3OfficeAgents{position:absolute;inset:0;display:block!important;opacity:1!important;visibility:visible!important;pointer-events:none;z-index:52}
#pw3OfficeAgents .pw3-person{display:block!important;visibility:visible!important;opacity:1!important;width:48px;height:68px}
/* Even a missing/rejected sprite file must never make an employee invisible. */
#pw3OfficeAgents .pw3-person.pw3-sprite-missing{background-image:none!important;background:linear-gradient(110deg,var(--pw3-skin,#e9bc89) 0 45%,var(--pw3-shirt,#60a6b1) 45% 100%) center 13px/31px 39px no-repeat!important;outline:2px solid #263c50;outline-offset:-6px}
#pw3OfficeAgents .pw3-person.pw3-sprite-missing:before{content:attr(data-initial);position:absolute;left:8px;top:5px;width:29px;height:25px;display:grid;place-items:center;background:var(--pw3-hair,#3e3547);border:2px solid #21364a;color:#fff5d2;font:900 13px/1 ui-monospace,monospace}
#pw3OfficeAgents .pw3-person.pw3-sprite-missing .agent-name{top:-17px}
#pw3OfficeAgents .pw3-person{pointer-events:auto;appearance:none;border:0;padding:0;
 background-color:transparent!important;color:inherit;cursor:pointer;isolation:isolate;
 transition:top 1s ease,left 1s ease}
#pw3OfficeAgents .pw3-person:focus-visible{outline:3px solid #ffedaa;outline-offset:4px}
#pw3OfficeAgents .pw3-person:hover{filter:drop-shadow(0 0 8px #ffdda4);z-index:60!important}
#pw3OfficeAgents .pw3-person .agent-name{background:#203e4b;color:#fdf6dd;max-width:100px;
 text-overflow:ellipsis;overflow:hidden;white-space:nowrap}
#pw3-count{position:absolute;bottom:10px;right:10px;z-index:40;border:2px solid #8dd0bd;
 background:#173c4b;color:#fff7c5;padding:6px 9px;font:bold 11px system-ui;pointer-events:none}
@media(max-width:720px){#pw3Dialog{width:100vw;height:100dvh;max-height:100dvh;outline:0;border:0;border-radius:0}
 #pw3Dialog .pw3-body{padding:12px 12px 24px}#pw3Dialog .pw3-head{padding:13px}
 #pw3Dialog .pw3-grid{grid-template-columns:1fr}#pw3Dialog .pw3-portrait{min-height:155px}
 #pw3Dialog .pw3-portrait svg{height:145px;width:145px}#pw3Dialog .pw3-list{grid-template-columns:1fr}
 #pw3Dialog .pw3-bars{grid-template-columns:1fr}#pw3Dialog .pw3-steps{position:static}
 #pw3Open{left:10px;bottom:8px;z-index:50;padding:8px 11px}}
@media(prefers-reduced-motion:reduce){#pw3OfficeAgents .pw3-person{animation:none!important;transition:none!important}}

#pw3Dialog .pw31-policies{background:#f8e9d7;border:2px solid #cdb095;margin:9px 0 15px;padding:10px 12px}#pw3Dialog .pw31-policies summary{cursor:pointer;font-weight:800;color:#755147}#pw3Dialog .pw31-policylist{margin:8px 0}
/* v3.1: Game-style character dossier, less duplicated administration. */
#pw3Dialog .pw31-nav{display:flex;gap:12px;justify-content:space-between;align-items:end;flex-wrap:wrap;margin:4px 0 13px;background:#eee0b9;padding:10px 13px;border:2px solid #b89a70}
#pw3Dialog .pw31-navigate{display:flex;gap:10px;align-items:center}
#pw3Dialog .pw31-navigate button{min-width:48px}
#pw3Dialog .pw31-role{display:grid;gap:3px;min-width:min(310px,100%);font-size:12px}
#pw3Dialog .pw31-role select{min-height:42px}
#pw3Dialog .pw31-grid{grid-template-columns:minmax(270px,37%) minmax(0,1fr);align-items:start}
#pw3Dialog .pw31-character{padding:12px 14px;background:linear-gradient(145deg,#faeed1,#d8e6cf);border-color:#9a7950}
#pw3Dialog .pw31-character .pw3-portrait{min-height:183px;margin-bottom:8px;background:radial-gradient(circle,#d4e6dc,#93b3ac)}
#pw3Dialog .pw31-character .pw3-portrait svg{width:160px;height:173px;filter:drop-shadow(6px 6px #28405531)}
#pw3Dialog .pw31-name{margin:0;font-size:24px;color:#244a56}
#pw3Dialog .pw31-character .pw3-quote{font-size:14px;margin:6px 0 9px}
#pw3Dialog .pw31-bio{padding:10px;background:#fffaf0;border:2px solid #b6c1ac;font-size:12px}
#pw3Dialog .pw31-bio p{margin:7px 0}#pw3Dialog .pw31-story{font-style:italic;line-height:1.45}
#pw3Dialog .pw31-facts{display:flex;flex-wrap:wrap;gap:5px}
#pw3Dialog .pw31-facts span{background:#dceae5;border:1px solid #99b3a9;padding:4px 6px;font-weight:750}
#pw3Dialog .pw31-persona,#pw3Dialog .pw31-allskills{background:#f0f4eb;border:1px solid #aac1b6;margin-top:9px;padding:8px 10px}
#pw3Dialog .pw31-persona summary,#pw3Dialog .pw31-allskills summary{cursor:pointer;font-weight:800;color:#235c66}
#pw3Dialog .pw31-persona p{font-size:12px;line-height:1.4}
#pw3Dialog .pw31-work .pw3-card{margin-bottom:10px}
#pw3Dialog .pw31-work h3{font-size:16px;margin:0 0 7px}
#pw3Dialog .pw31-rating{display:flex;align-items:center;gap:16px;margin:6px 0 12px}
#pw3Dialog .pw31-stars{color:#bb7936;font-size:25px;letter-spacing:2px;white-space:nowrap}
#pw3Dialog .pw31-skillheadline{display:flex;align-items:center;gap:5px;flex-wrap:wrap;margin-top:7px}
#pw3Dialog .pw31-skillheadline>b{font-size:12px;margin-right:7px}
#pw3Dialog .pw31-warning{background:#fff0ca;border-left:4px solid #b77c29;padding:9px;font-size:12px}
#pw3Dialog .pw31-audition{background:#eef3eb;border-color:#77afa2}
#pw3Dialog .pw31-audition p{font-size:12px;margin:5px 0 10px}
#pw3Dialog .pw31-audition label{display:grid;gap:4px;font-size:12px}
#pw3Dialog .pw31-interview-actions{display:flex;align-items:center;flex-wrap:wrap;gap:9px;margin-top:9px}
#pw3Dialog .pw31-interview-actions button{margin:0}
#pw3Dialog .pw31-audition .pw3-demo{font-size:10px}
#pw3Dialog .pw31-empty{font-style:italic;color:#50716e;margin:12px 0 2px}
#pw3Dialog .pw31-answer{padding:9px 12px;margin:10px 0 0;background:#fffdf5}
#pw3Dialog .pw31-answer h4{margin:7px 0;color:#254f61;font-size:13px}
#pw3Dialog .pw31-answer .pw3-gorilla svg{width:85px;height:85px}
#pw3Dialog .pw31-scoreline{font-size:11px;color:#66706c}
#pw3Dialog .pw31-bottom{position:sticky;bottom:0;z-index:9;margin-bottom:0;background:#f1e4be;border:2px solid #c4a06b;box-shadow:0 -3px 12px #253e5140}
#pw3Dialog .pw31-bottom .pw3-green{min-height:46px;font-size:15px}
#pw3Dialog .pw31-hint{font-size:12px;font-weight:700}
@media(max-width:720px){#pw3Dialog .pw31-grid{grid-template-columns:1fr;gap:10px}
 #pw3Dialog .pw31-character .pw3-portrait{min-height:140px}
 #pw3Dialog .pw31-character .pw3-portrait svg{width:136px;height:144px}
 #pw3Dialog .pw31-bottom{position:sticky;bottom:0;padding:9px}
 #pw3Dialog .pw31-bottom .pw3-green{width:100%}#pw3Dialog .pw31-nav{align-items:stretch}
 #pw3Dialog .pw31-role{min-width:100%}}

/* v3.2 fixed character-atlas sprite contract; one character identity across roles. */
#pw3OfficeAgents .pw3-person{background-color:transparent!important;background-image:var(--pw3-idle)!important;
 background-size:192px 68px!important;background-repeat:no-repeat!important;background-position:0 0;
 image-rendering:pixelated;animation:pw32-steps 2.9s steps(4,end) infinite!important}
#pw3OfficeAgents .pw3-person.walking{background-image:var(--pw3-walk)!important;
 animation:pw32-steps .55s steps(4,end) infinite!important}
#pw3OfficeAgents .pw3-person.working:not(.walking){background-image:var(--pw3-working)!important;
 animation:pw32-steps .85s steps(4,end) infinite!important}
@keyframes pw32-steps{to{background-position:-192px 0}}
#pw3Dialog .pw32-best{background:#d8efdc;border-left:5px solid #3b936e;padding:9px 11px;margin:8px 0;color:#234e3d;font-size:13px}
#pw3Dialog .pw32-story{margin:9px 0;background:#fff9e6;border:2px dashed #a98d5c;padding:9px 11px}
#pw3Dialog .pw32-story summary,#pw3Dialog .pw32-prompt summary{font-weight:800;cursor:pointer}
#pw3Dialog .pw32-prompt{background:#e7f1f0;padding:11px;margin:14px 0;border:2px solid #8bb3af}
#pw3Dialog .pw32-prompt pre{white-space:pre-wrap;overflow-wrap:anywhere;color:#1b3b44;background:#fff;padding:12px;max-height:290px;overflow:auto;font:12px/1.5 ui-monospace,monospace}
@media(prefers-reduced-motion:reduce){#pw3OfficeAgents .pw3-person{animation:none!important}}
`;document.head.append(css);
const modal=document.createElement('dialog');modal.id='pw3Dialog';modal.setAttribute('aria-label','Pixel Works rekrytering');document.body.append(modal);
modal.addEventListener('cancel',e=>{e.preventDefault();returnToOffice()});
const button=document.createElement('button');button.id='pw3Open';button.type='button';button.textContent='🏢 Personal & rekrytering';button.onclick=()=>open('crew');(document.querySelector('#gameDock')||document.body).append(button);
// Unique portrait silhouettes, hair, expressions and props per character.
// Inline SVG artwork remains local, sharp at pixel scale and transparent.
function portrait(c){
 const id=c.id||'chef', [skin,shirt,hair]=c.colors||colors;
 const r=(x,y,w,h,color)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${color}"/>`;
 const dark='#203546',light='#fff5d5';
 const face={chief:[30,23,36,49],joppe:[29,25,38,46],siv:[31,24,34,48],nisse:[28,29,40,45],mira:[30,23,36,48],vera:[30,27,38,46],lova:[29,26,38,48]}[id]||[30,24,36,48];
 let art=r(17,87,62,13,dark)+r(22,79,52,21,shirt)+r(22,83,10,17,shirt)+r(64,83,10,17,shirt);
 art+=r(39,74,19,13,skin)+r(face[0]-3,face[1]-2,face[2]+6,face[3]+4,dark);
 art+=r(...face,skin)+r(23,51,7,10,skin)+r(67,51,7,10,skin);
 // Hair and accessories are not recolors: each candidate has a recognizable silhouette.
 const hairShapes={
 chief:()=>r(28,18,40,12,hair)+r(31,12,31,8,hair)+r(29,22,7,8,hair)+r(48,88,5,12,'#d79e5e')+r(42,79,12,7,light),
 joppe:()=>r(25,16,50,13,'#e75f58')+r(20,27,53,7,'#e75f58')+r(58,11,11,8,'#f2c767')+r(24,39,6,15,hair)+r(67,39,6,15,hair)+r(25,84,45,7,'#4268a3'),
 siv:()=>r(27,15,43,16,hair)+r(60,9,16,19,hair)+r(68,12,12,14,'#9aaabc')+r(26,28,6,49,hair)+r(65,27,7,41,hair)+r(27,82,45,6,'#d6c9ed'),
 nisse:()=>r(23,22,51,13,hair)+r(25,14,15,12,hair)+r(44,18,16,10,hair)+r(26,34,6,16,hair)+r(29,61,38,15,'#654b3b')+r(41,84,14,16,'#d9ac54'),
 mira:()=>r(27,13,42,17,hair)+r(62,9,17,26,hair)+r(74,29,9,31,hair)+r(26,27,7,37,hair)+r(64,29,7,35,hair)+r(71,12,8,8,'#f4d86b')+r(29,87,38,8,'#ffd6a1'),
 vera:()=>r(24,10,33,21,hair)+r(53,16,18,13,'#dd6dce')+r(24,26,7,29,'#475f8d')+r(67,25,7,30,'#475f8d')+r(18,31,9,20,'#e6ca5b')+r(71,31,9,20,'#e6ca5b')+r(24,25,51,5,'#e6ca5b')+r(39,88,15,5,light),
 lova:()=>r(25,14,51,17,hair)+r(24,27,9,51,hair)+r(66,28,10,55,hair)+r(69,50,9,8,'#f1d783')+r(71,62,8,8,'#f1d783')+r(24,82,14,16,'#a7d5bc'),
 };
 art+=(hairShapes[id]||hairShapes.chief)();
 const eyeY=id==='nisse'?49:id==='siv'?46:47;
 art+=r(36,eyeY,6,5,dark)+r(56,eyeY,6,5,dark);
 if(id==='siv')art+=r(32,43,15,12,'#425967')+r(51,43,15,12,'#425967')+r(47,47,4,3,'#425967')+r(35,46,9,6,skin)+r(54,46,9,6,skin)+r(37,48,4,3,dark)+r(56,48,4,3,dark)+r(31,57,9,2,'#b88f80')+r(56,57,9,2,'#b88f80');
 else if(id==='mira')art+=r(33,57,3,3,'#d37e73')+r(40,56,3,3,'#d37e73')+r(61,57,3,3,'#d37e73')+r(52,63,11,3,'#af6c7a');
 else if(id==='nisse')art+=r(40,62,17,4,'#f1e2cd')+r(50,62,9,4,'#3e2e2d');
 else if(id==='joppe')art+=r(40,62,21,3,'#774b51')+r(44,64,12,3,'#f7ecd7');
 else if(id==='vera')art+=r(40,61,16,4,'#9a596a')+r(37,38,5,3,'#b3e5dd');
 else if(id==='lova')art+=r(39,60,19,4,'#b16c67')+r(42,62,11,4,light)+r(77,53,3,4,'#f9db7f');
 else art+=r(42,62,13,4,'#a66966');
 const svg=`<svg viewBox="0 0 96 100" role="img" aria-label="Pixelporträtt av ${esc(c.name)}" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges">${art}</svg>`;
 return svg;
}
function gorilla(){return `<svg viewBox="0 0 32 32" role="img" aria-label="Fiktiv 32 gånger 32 pixlad gorilla" xmlns="http://www.w3.org/2000/svg">
 <rect width="32" height="32" fill="#cbd9bb"/><path d="M4 10h5V5h4V3h8v2h4v5h4v15h-5v4H8v-4H4z" fill="#444751"/>
 <rect x="3" y="12" width="6" height="11" fill="#3c414b"/><rect x="23" y="12" width="6" height="11" fill="#3c414b"/>
 <rect x="9" y="12" width="14" height="15" fill="#8b8586"/><rect x="11" y="18" width="10" height="8" fill="#b9ada0"/>
 <rect x="10" y="12" width="5" height="3" fill="#151e2a"/><rect x="17" y="12" width="5" height="3" fill="#151e2a"/>
 <rect x="12" y="15" width="2" height="2" fill="white"/><rect x="18" y="15" width="2" height="2" fill="white"/>
 <rect x="14" y="21" width="2" height="2" fill="#31343c"/><rect x="18" y="21" width="2" height="2" fill="#31343c"/>
 <rect x="13" y="25" width="7" height="2" fill="#413137"/><rect x="15" y="26" width="3" height="2" fill="#fff1d8"/>
 </svg>`}
function categorise(candidate){let skills=Object.entries(candidate.skills||{});
 const labels=data.skills||{};return {best:skills.filter(([k,v])=>v>=4).map(([k])=>labels[k]||k),
   ok:skills.filter(([k,v])=>v===2||v===3).map(([k])=>labels[k]||k),
   bad:skills.filter(([k,v])=>v<=1).map(([k])=>labels[k]||k).concat(candidate.weakness||'')};}
function pills(arr,extra=''){return arr.map(v=>`<span class="pw3-pill ${extra}">${esc(v)}</span>`).join('')}
function rating(c,r){return c.skills[data.role_skill[r]]||0}
function recommendedRoles(c){
 const wanted=c.recommended_role;
 if(wanted && roles[wanted])return [[wanted,roles[wanted]]];
 const list=Object.entries(roles).sort((a,b)=>rating(c,b[0])-rating(c,a[0]));
 return list.slice(0,1);
}

function chooseCandidate(id){
 const c=data?.candidates?.find(item=>item.id===id);
 if(!c)return;
 selected=id;
 role=manualRoleByPerson.get(id)||recommendedRoles(c)[0]?.[0]||'allround';
}
function staffByChar(id){return data.people.find(x=>x.character_id===id)}
function badge(c,r){const value=rating(c,r);return value>=4?'🌟 Mycket lämplig':value>=2?'👍 Kan fungera':'⚠️ Svag matchning'}
function skillBars(c){return `<div class="pw3-bars">${Object.entries(c.skills||{}).map(([k,v])=>`<div class="pw3-bar"><span>${esc(data.skills[k]||k)} <b>${v}/5</b></span><span class="pw3-track"><span class="pw3-fill" style="display:block;width:${v*20}%"></span></span></div>`).join('')}</div>`}
function roleOptions(selectedRole){return Object.entries(roles).map(([k,v])=>`<option value="${k}" ${selectedRole===k?'selected':''}>${esc(v)}</option>`).join('')}
function returnToOffice(){
  if(modal.open)modal.close();
  for(const sel of ['#localStudioDialog','#pw13Dialog','#dockDialog']){
    const old=$(sel);if(old?.open)old.close();
  }
  // The office is the canonical landing surface after recruiting.
  const office=document.querySelector('#gameDock [data-dock="office"],.dock-item[data-dock="office"],[data-dock="office"]');
  if(office)office.click();
}
function shell(content){modal.innerHTML=`<header class="pw3-head"><div><h2>🏢 Pixel Works • Personalbyrån</h2><div class="pw3-sub">Ett kontor · unika karaktärer · sex rekryteringskandidater</div></div><button id="pw3Close" aria-label="Stäng" type="button">✕</button></header><main class="pw3-body">${content}</main>`;$('#pw3Close',modal).onclick=returnToOffice;if(notice){const n=$('#pw3Message',modal);if(n)n.textContent=notice;}}
function tabs(){return `<nav class="pw3-tabs" aria-label="Personalbyråns flikar"><button id="pw3Team" class="${tab==='crew'?'active':''}">👥 Mitt team (${data.people.length})</button><button id="pw3Candidates" class="${tab==='candidates'?'active':''}">🔎 Rekrytera (6 kandidater)</button></nav>`}
function bindTabs(){const a=$('#pw3Team',modal),b=$('#pw3Candidates',modal);if(a)a.onclick=()=>{tab='crew';detail=null;render()};if(b)b.onclick=()=>{tab='candidates';detail=null;chooseCandidate(selected);render()}}
function render(){if(!data)return;shell(data.enabled?tabs()+(detail?.startsWith('pw3-')?profileView(detail):(tab==='crew'?teamView():candidateView())):startView());bindTabs();bindEvents()}
function startView(){return `<div class="pw3-notice"><h3>✨ Börja om – ett nytt personalläge</h3>
 <p>Vi lämnar de gamla projektanställningarna bakom oss och börjar med <b>Chefen</b> som första kollega. Sedan får du välja bland sex nya personer. De gamla projekten, arbetsrapporterna, AI-adaptrarna och deras filer <b>raderas inte</b>.</p>
 <p><strong>Viktigt:</strong> den gamla automatiska AI-schemaläggaren pausas när du aktiverar v3. Intervjuer och nya anställda är DEMO tills vi anslutit den nya arbetspipelinen.</p>
 <button id="pw3Activate" class="pw3-green">🏢 Starta nya personalstudion</button><p id="pw3Message" role="status" class="pw3-error"></p></div>`}
function teamView(){
 const people=data.people||[];
 const team=people.map(p=>{
   const c=p.character||{};
   const best=p.person_id==='pw3-chef'?'Arbetsledare · allround':(recommendedRoles(c)[0]?.[1]||p.role_name||'Allroundare');
   const strongest=Object.entries(c.skills||{}).sort((a,b)=>b[1]-a[1]).slice(0,2)
     .map(([key,score])=>`<span class="pw352-skill">${esc(data.skills?.[key]||key)} <b>${score}/5</b></span>`).join('');
   return `<article class="pw352-person-card" data-person-id="${esc(p.person_id)}">
     <div class="pw352-card-top"><div class="pw352-avatar">${portrait(c)}</div><div class="pw352-card-intro">
       <span class="pw352-kicker">ANSTÄLLD · ${esc(p.role_name)}</span>
       <h3>${esc(p.name)}</h3>
       <span class="pw352-best">🌟 Bäst lämpad som ${esc(best)}</span>
       <span class="pw352-bio">${esc(c.experience_years??'?')} års erfarenhet · ${esc(c.age??'?')} år</span>
     </div></div>
     <p class="pw352-speech">“${esc(c.speech_sample||c.quote||c.subtitle||'Redo för nästa äventyr!')}”</p>
     <div class="pw352-skills" aria-label="Styrkor">${strongest}</div>
     <div class="pw352-actions">
       <button type="button" data-staff="${esc(p.person_id)}" class="pw3-blue">👤 Visa person</button>
       <button type="button" data-pw33-assign="${esc(p.person_id)}" class="pw3-green">📋 Ge uppdrag</button>
     </div>
   </article>`;
 }).join('');
 return `<section class="pw352-team" aria-label="Pixel Works anställda">
   <div class="pw352-team-head"><div><span class="pw352-kicker">🏢 PIXEL WORKS / PERSONAL</span>
   <h3>Ditt team <span class="pw352-count">${people.length} anställda</span></h3>
   <p>En studio, flera spel. Varje person har sin egen stil och sin egen kompetens.</p></div>
   <button type="button" id="pw3GoRecruit" class="pw3-green">➕ Rekrytera</button></div>
   <div class="pw352-team-grid">${team||'<p class="pw3-notice">Ännu ingen personal.</p>'}</div>
   <details class="pw352-company-rules"><summary>⚙️ Företagsregler och behörigheter</summary>
   <p>Gemensamma regler gäller alla anställda, oavsett personlighet.</p>
   ${pills(data.denied||[],'deny')}</details>
   <p class="pw352-source">Personlighet och skills är spelvärden. Riktigt AI-arbete och tillgänglighet verifieras separat för varje uppdrag.</p>
   <p id="pw3Message" role="status" class="pw3-error"></p>
 </section>`;
}
function biography(c){return `<div class="pw31-bio"><div class="pw31-facts">
 <span>🎂 ${esc(c.age??'?')} år</span><span>🪪 ${esc(c.gender||'Ej angivet')} · ${esc(c.pronouns||'–')}</span>
 <span>🧰 ${esc(c.experience_years??'?')} års erfarenhet</span></div>
 <p><b>Tidigare:</b> ${esc(c.former_job||'Okänt')}</p>
 <p class="pw31-story">${esc(c.background||'Bakgrund kommer senare.')}</p>
 <p class="pw31-quirk">🎒 <b>Favorit:</b> ${esc(c.favorite||'Kaffe')}</p></div>`}
function candidateView(){
 const c=data.candidates.find(x=>x.id===selected)||data.candidates[0],hired=staffByChar(c.id);
 const options=data.interview_tasks?.[role]||[{id:'default',question:'Visa ett kort demo-arbetsprov'}];
 const current=data.interviews?.[c.id],score=rating(c,role),list=categorise(c);
 const alternatives=Object.entries(roles).filter(([r])=>r!==role).sort((a,b)=>rating(c,b[0])-rating(c,a[0]));
 const suggested=alternatives[0];
 return `<div class="pw31-nav"><div class="pw31-navigate"><button id="pw3PrevTop" class="pw3-plain" aria-label="Föregående kandidat">◀</button><span><b>Kandidat ${data.candidates.indexOf(c)+1} av ${data.candidates.length}</b></span><button id="pw3NextTop" class="pw3-plain" aria-label="Nästa kandidat">▶</button></div>
 <label class="pw31-role"><b>Vilken roll vill du tillsätta?</b><small class="pw353-role-hint">🌟 Rekommenderat: ${esc(recommendedRoles(c)[0][1])} · förvalt vid kandidatbyte</small><select id="pw3Role">${roleOptions(role)}</select></label></div>
 <div class="pw3-grid pw31-grid"><section class="pw3-portrait-card pw31-character">
 <div class="pw3-portrait">${portrait(c)}</div>
 <h3 class="pw31-name">${esc(c.name)}</h3><div class="pw32-best">🌟 <b>Bäst lämpad för:</b> ${recommendedRoles(c).map(([r,n])=>esc(n)).join(' & ')} · ${rating(c,recommendedRoles(c)[0][0])}/5</div><div class="pw3-tag">${esc(c.subtitle)}</div>
 <p class="pw3-quote">”${esc(c.quote)}”</p>
 ${biography(c)}
 ${c.career_highlight?`<details class="pw32-story"><summary>🎬 Hör en historia från förr</summary><p>${esc(c.career_highlight)}</p><p>${esc(c.office_rumour)}</p><small>☕ På kontoret: ${esc(c.office_habit)}</small></details>`:''}
 <details class="pw31-persona"><summary>🔒 Personlighet & egenheter</summary><p>${esc(c.voice)}</p><p>🗣️ <i>${esc(c.speech_sample||'')}</i></p><p>✨ ${esc(c.quirk)}</p><p>⚠️ ${esc(c.weakness)}</p></details>
 </section><section class="pw31-work"><div class="pw3-card pw31-fit"><div class="pw3-row"><h3>🎯 Passar som ${esc(roles[role])}?</h3><strong class="${score<2?'pw3-bad':'pw3-good'}">${badge(c,role)}</strong></div>
 <div class="pw31-rating"><div class="pw31-stars" aria-label="${score} av 5 i rollen">${'★'.repeat(score)}${'☆'.repeat(5-score)}</div><div>${score}/5 · <small>Spelvärde, inte AI-betyg</small></div></div>
 ${score<3?`<p class="pw31-warning">💡 Starkare som <b>${esc(suggested?.[1]||'annan specialist')}</b> (${rating(c,suggested?.[0]||role)}/5). Du får ändå välja själv.</p>`:''}
 <div class="pw31-skillheadline"><b>🌟 Styrkor</b>${pills(list.best.slice(0,3))}</div>
 <div class="pw31-skillheadline"><b>⚠️ Svagheter</b>${pills(list.bad.slice(0,2),'warn')}</div>
 <details class="pw31-allskills"><summary>📊 Se alla åtta färdigheter</summary>${skillBars(c)}</details>
 </div>
 <div class="pw3-card pw31-audition"><h3>🎤 Testa kandidaten</h3><p>Välj en uppgift och lyssna på <b>hur personen tänker och pratar</b>.</p>
 <label><b>Provuppdrag</b><select id="pw31InterviewTask">${options.map(o=>`<option value="${esc(o.id)}" ${current?.role===role&&current?.test_id===o.id?'selected':''}>${esc(o.question)}</option>`).join('')}</select></label>
 <div class="pw31-interview-actions"><button id="pw3Interview" class="pw3-blue">🎤 Genomför demo-intervju</button><span class="pw3-demo">DEMO · inga AI-anrop</span></div>
 ${current?.role===role?interviewCard(current):'<p class="pw31-empty">Ingen intervju för den här rollen än. Prova kandidaten!</p>'}
 </div></section></div>
 <div class="pw3-steps pw31-bottom"><span class="pw31-hint">${hired?'✅ Kandidaten är redan anställd.':'👔 Du fattar anställningsbeslutet – inte Chefen.'}</span>
 <button id="pw3Hire" class="pw3-green" ${hired?'disabled':''}>${hired?'✅ Redan anställd':'➕ Anställ som '+esc(roles[role])}</button></div>
 <p id="pw3Message" role="status" class="pw3-error"></p>`;
}
function interviewCard(v){return `<div class="pw3-interview pw31-answer"><span class="pw3-demo">🧪 DEMO · Förskrivet svar</span>
 <h4>❓ ${esc(v.question||'Provuppdrag')}</h4>
 ${(v.test_id==='gorilla'||(!v.test_id&&v.role==='artist'))?`<div class="pw3-gorilla">${gorilla()}<small>Statisk exempelbild, inte skapad av en AI</small></div>`:''}
 <p>💬 ”${esc(v.text)}”</p>
 <div class="pw31-scoreline">Rollens startvärde: <b>${v.score}/5</b> · Resultatet är inte verifierat.</div>
 ${v.test_id==='menu'?'<button id="pw3Beep" class="pw3-blue">▶ Lyssna på lokalt demo-ljud</button>':''}</div>`}
function profileView(pid){
 const p=data.people.find(x=>x.person_id===pid);if(!p){detail=null;return teamView()};
 const c=p.character;const best=pid==='pw3-chef'?'Arbetsledare · allround':(recommendedRoles(c)[0]?.[1]||'Allroundare');
 return `<div class="pw352-profile"><button id="pw3Back" class="pw3-plain">◀ Till teamet</button>
  <div class="pw352-profile-grid"><section class="pw352-profile-hero">
    <div class="pw352-profile-portrait">${portrait(c)}</div>
    <span class="pw352-kicker">EN AV VÅRA KOLLEGOR</span><h3>${esc(c.name)}</h3>
    <span class="pw352-best">🌟 Rekommenderad roll: ${esc(best)}</span>
    <p class="pw352-speech">“${esc(c.speech_sample||c.quote||'')}”</p>
    <p class="pw352-profile-facts">${esc(c.age??'?')} år · ${esc(c.experience_years??'?')} års erfarenhet</p>
    <p>🎭 ${esc(c.quirk||'Unik kollega')}</p>
    <details class="pw352-expand"><summary>📖 Bakgrund och personlig historia</summary>${biography(c)}<p>${esc(c.career_highlight||'')}</p></details>
  </section><section class="pw352-profile-work">
    <div class="pw352-work-head"><span class="pw352-kicker">DITT FÖRETAG BESTÄMMER</span><h3>Arbete & ansvar</h3>
      <p>Du kan ändra roll och arbetsbeskrivning. Karaktärsdrag och grundskills är fasta.</p></div>
    <label><b>Nuvarande arbetsroll</b><select id="pw3StaffRole" ${pid==='pw3-chef'?'disabled':''}>${pid==='pw3-chef'?'<option value="lead">Arbetsledare</option>':roleOptions(p.role)}</select></label>
    <label><b>Arbetsbeskrivning</b><textarea id="pw3WorkDescription" maxlength="1400" placeholder="Beskriv ansvar, rapportering och arbetsmetod...">${esc(p.work_description)}</textarea></label>
    <div class="pw352-profile-actions"><button id="pw3SaveStaff" class="pw3-green">💾 Spara</button><button type="button" id="pw33ProfileStart" class="pw3-blue">📋 Ge uppdrag</button>
      ${pid==='pw3-chef'?'<button type="button" id="pw34ProfileChief" class="pw3-plain">👔 Fråga Chefen</button>':'<button id="pw3Dismiss" class="pw3-plain">🚪 Avskeda…</button>'}</div>
    <details class="pw352-expand"><summary>⭐ Alla färdigheter</summary>${skillBars(c)}</details>
    <details class="pw352-expand"><summary>🔒 Fast personlighet och AI-instruktion</summary><p>${esc(c.voice)}</p><p>⚠️ ${esc(c.weakness)}</p><pre class="pw352-prompt">${esc(p.prompt_preview||'')}</pre></details>
    <small class="pw352-source">AI-motor väljs per uppdrag. Att öppna profilen startar inget AI-anrop.</small>
    <p id="pw3Message" role="status" class="pw3-error"></p>
  </section></div></div>`;
}
function bindEvents(){if(!data.enabled){const b=$('#pw3Activate',modal);if(b)b.onclick=()=>mutate('/activate',{approval:'START_NEW_STUDIO_CREW_V3'},'crew');return}
 $('#pw3GoRecruit',modal)?.addEventListener('click',()=>{tab='candidates';detail=null;chooseCandidate(selected);render()});
 modal.querySelectorAll('[data-staff]').forEach(x=>x.onclick=()=>{tab='candidates';detail=x.dataset.staff;render()});
 modal.querySelectorAll('[data-pw33-assign]').forEach(b=>b.onclick=()=>window.pixelWorksV3Tasks?.open(b.dataset.pw33Assign));
 if(detail?.startsWith('pw3-')){ $('#pw33ProfileStart',modal)?.addEventListener('click',()=>window.pixelWorksV3Tasks?.open(detail)); $('#pw34ProfileChief',modal)?.addEventListener('click',()=>window.pixelWorksV3Chief?.open()); const back=$('#pw3Back',modal);if(back)back.onclick=()=>{detail=null;tab='crew';render()};
 const p=data.people.find(p=>p.person_id===detail);$('#pw3SaveStaff',modal)?.addEventListener('click',()=>mutate('/profile',
 {person_id:detail,role:detail==='pw3-chef'?'lead':$('#pw3StaffRole',modal).value,work_description:$('#pw3WorkDescription',modal).value},'crew'));
 $('#pw3Dismiss',modal)?.addEventListener('click',()=>{if(confirm(`Avskeda ${p?.name}? Den nya personan lämnar studion. Historiska v3-data behålls.`))mutate('/dismiss',{person_id:detail,approval:'DISMISS_PERSON_V3'},'crew')});return}
 const c=data.candidates.find(x=>x.id===selected)||data.candidates[0];$('#pw3Role',modal)?.addEventListener('change',ev=>{role=ev.target.value;manualRoleByPerson.set(c.id,role);render()});
 for(const id of ['#pw3Prev','#pw3PrevTop'])$(id,modal)?.addEventListener('click',()=>{chooseCandidate(data.candidates[(data.candidates.indexOf(c)+data.candidates.length-1)%data.candidates.length].id);render()});
 for(const id of ['#pw3Next','#pw3NextTop'])$(id,modal)?.addEventListener('click',()=>{chooseCandidate(data.candidates[(data.candidates.indexOf(c)+1)%data.candidates.length].id);render()});
 $('#pw3Interview',modal)?.addEventListener('click',()=>mutate('/interview',{candidate_id:c.id,role,test_id:$('#pw31InterviewTask',modal)?.value},'candidates'));
 $('#pw3Hire',modal)?.addEventListener('click',()=>{if(confirm(`Anställa ${c.name} som ${roles[role]}? Detta är en DEMO-anställning utan AI-kostnad.`))mutate('/hire',{candidate_id:c.id,role,approval:'HIRE_PERSON_V3'},'candidates')});
 $('#pw3Beep',modal)?.addEventListener('click',()=>{try{const A=window.AudioContext||window.webkitAudioContext;if(!A)throw Error('Web Audio stöds inte');const ctx=new A();[392,588].forEach((hz,i)=>{const osc=ctx.createOscillator(),gain=ctx.createGain();osc.type='sine';osc.frequency.value=hz;gain.gain.setValueAtTime(.001,ctx.currentTime+i*.22);gain.gain.exponentialRampToValueAtTime(.17,ctx.currentTime+i*.22+.02);gain.gain.exponentialRampToValueAtTime(.001,ctx.currentTime+i*.22+.19);osc.connect(gain);gain.connect(ctx.destination);osc.start(ctx.currentTime+i*.22);osc.stop(ctx.currentTime+i*.22+.20)});setTimeout(()=>ctx.close(),800)}catch(err){showError(err.message)}});
}
function showError(message){notice='⚠ '+String(message||'Fel');const p=$('#pw3Message',modal);if(p){p.textContent=notice;p.hidden=false}}
async function mutate(suffix,fields,returnTab){if(busy)return;busy=true;const previous=detail;
 modal.querySelectorAll('button').forEach(b=>b.disabled=true);
 try{const result=await api(URL+suffix,{...fields,revision:data.revision});
   if(result?.people){data=result}else{data.revision=result.revision;data.interviews[fields.candidate_id]=result.interview}
   notice='';tab=returnTab;detail=suffix==='/profile'?previous:null;render();if(suffix==='/interview')$('#pw3Dialog .pw31-audition')?.scrollIntoView({block:'nearest'});updateOffice();window.dispatchEvent(new Event('pixelworks:v3-crew-changed'));
 }catch(e){showError(e.message);modal.querySelectorAll('button').forEach(b=>b.disabled=false)}finally{busy=false}}
async function load(){if(loadBusy)return;loadBusy=true;try{data=await api(URL);if(data.enabled)updateOffice();else{document.body.classList.remove('pw3-active');}
 }catch(e){showError(e.message)}finally{loadBusy=false}}
async function open(which='crew',personId=null){
 // Legacy dialogs must not stay as a second modal backdrop behind Personalbyrån.
 for(const sel of ['#localStudioDialog','#pw13Dialog','#dockDialog']){const old=$(sel);if(old?.open)old.close()}
 tab=which;detail=personId;notice='';if(tab==='candidates')chooseCandidate(selected);if(!modal.open)modal.showModal();
 modal.innerHTML='<div style="padding:35px;background:#f8f0dc;color:#23384c">Läser Personalbyrån…</div>';
 await load();if(data)render();else modal.innerHTML='<div style="padding:30px">Kan inte läsa personal från servern. Kontrollera att backend är omstartad. <button onclick="this.closest(\'dialog\').close()">Stäng</button></div>';}
window.pixelWorksRecruitV3={open,refresh:load,getWorkers:()=>data?.people?.map(p=>p.worker)||[]};
// Access via every former personnel button. One capture handler prevents old dialogs.
document.addEventListener('click',ev=>{
 const old=ev.target.closest('#hireBtn,#officeHire,#pw13StudioNav,[data-dock="agents"],.hireLocal');
 if(!old)return;ev.preventDefault();ev.stopImmediatePropagation();open('crew');
},true);
let layer=null,counter=null;
function ensureOffice(){
 const root=$('#officeStage');if(!root||!root.isConnected)return false;
 if(!layer||layer.parentElement!==root){layer=document.createElement('div');layer.id='pw3OfficeAgents';root.append(layer);officeKey=''}
 if(!counter||counter.parentElement!==root){counter=document.createElement('div');counter.id='pw3-count';root.append(counter)}
 if(!$('#pw353-move-notice',root)){const n=document.createElement('div');n.id='pw353-move-notice';n.setAttribute('role','status');n.hidden=true;root.append(n)}
 return true;
}
const spriteIds=new Set(['chef','joppe','siv','nisse','mira','vera','lova']);
const spritePath=(id,state)=>`./assets/characters/${id}/${id}-${state}.png`;
const spritePalette={chef:['#624833','#e5ba8d','#487991'],joppe:['#ab463b','#f3c79f','#6a98c0'],siv:['#59606a','#eecaaa','#7681aa'],nisse:['#5a4136','#d3a780','#d69668'],mira:['#29b8b6','#ecc79b','#ba72ad'],vera:['#6a4c9f','#dbb18d','#5a9cc0'],lova:['#ad694c','#e5b394','#b97883']};
// The browser may reject a sprite due to a missing file, CSP or a stale asset cache.
// In that case retain a distinct, clickable employee with a visible fallback.
function verifySprite(node,character){
 const image=new Image();image.onload=()=>{if(node.isConnected&&image.naturalWidth<48)node.classList.add('pw3-sprite-missing')};
 image.onerror=()=>{if(node.isConnected)node.classList.add('pw3-sprite-missing')};
 image.src=spritePath(character,'idle');
}
function rebuildOffice(people){
 officeKey=JSON.stringify(people.map(p=>[p.person_id,p.character_id,p.name,p.role,p.office_position]));
 layer.replaceChildren();
 people.forEach((p,i)=>{
  const node=document.createElement('button');node.type='button';node.className='agent pw3-person idle activity-cafe';
  const character=spriteIds.has(p.character_id)?p.character_id:'chef';
  const [hair,skin,shirt]=spritePalette[character]||spritePalette.chef;
  node.dataset.personId=p.person_id;node.dataset.characterId=character;
  node.dataset.initial=String(p.name||character).slice(0,1).toUpperCase();
  node.style.setProperty('--pw3-hair',hair);node.style.setProperty('--pw3-skin',skin);node.style.setProperty('--pw3-shirt',shirt);
  for(const animation of ['idle','walk','working','cafe'])node.style.setProperty('--pw3-'+animation,`url("${spritePath(character,animation)}")`);
  node.setAttribute('aria-label',p.name+' · '+p.role_name);
  node.title=p.name+' · '+p.role_name+' · v3-anställd';node.style.setProperty('--pw-anim-phase',(-i*.23)+'s');
  node.style.setProperty('--status-color','#ecd58c');
  const home=p.office_position||{x:places[i%places.length][0],y:places[i%places.length][1]};
  node.style.left=home.x+'%';node.style.top=home.y+'%';
  node.style.setProperty('--pw35-home-x',home.x+'%');node.style.setProperty('--pw35-home-y',home.y+'%');
  node.dataset.pinned=p.office_position?'true':'false';node.dataset.stationId=p.office_position?.station_id||'';
  const name=document.createElement('span');name.className='agent-name';name.textContent=p.name;node.append(name);
  for(const cls of ['agent-shadow','agent-head','agent-body','agent-prop','agent-status']){const part=document.createElement('span');part.className=cls;node.append(part)}
  node.onclick=()=>{if(node.dataset.dragged==='yes'){node.dataset.dragged='';return;}open('crew',p.person_id)};
  node.addEventListener('pointerdown',startOfficeDrag);layer.append(node);
  verifySprite(node,character);
 });
}
let activeDrag=null;
const clamp=(n,min,max)=>Math.max(min,Math.min(max,n));
function roomCoords(clientX,clientY){
 const rect=$('#officeStage').getBoundingClientRect();
 return {x:clamp((clientX-rect.left)/rect.width*100,5,95),
         y:clamp((clientY-rect.top)/rect.height*100,40,91)};
}
function nearestDesk(clientX,clientY){
 let winner=null,dist=Infinity;
 for(const st of document.querySelectorAll('#stationLayer .station[data-id]')){
   const r=st.getBoundingClientRect(),cx=r.left+r.width/2,cy=r.top+r.height*.55;
   const delta=Math.hypot(clientX-cx,clientY-cy);
   if(delta<Math.max(70,r.width*.68)&&delta<dist){winner=st;dist=delta}
 }
 return winner;
}
function startOfficeDrag(ev){
 if(ev.button!==0||!ev.isPrimary||activeDrag||!data?.enabled)return;
 const node=ev.currentTarget;
 activeDrag={node,id:node.dataset.personId,pointer:ev.pointerId,
   x:ev.clientX,y:ev.clientY,original:{x:parseFloat(node.style.left),y:parseFloat(node.style.top)},
   dragging:false};
 node.setPointerCapture(ev.pointerId);
 node.addEventListener('pointermove',moveOfficeDrag);
 node.addEventListener('pointerup',finishOfficeDrag);
 node.addEventListener('pointercancel',cancelOfficeDrag);
}
function moveOfficeDrag(ev){
 const ctx=activeDrag;if(!ctx||ev.pointerId!==ctx.pointer)return;
 if(!ctx.dragging&&Math.hypot(ev.clientX-ctx.x,ev.clientY-ctx.y)<8)return;
 ctx.dragging=true;
 const node=ctx.node,xy=roomCoords(ev.clientX,ev.clientY);
 node.classList.add('pw353-dragging');node.classList.remove('walking');
 node.style.left=xy.x+'%';node.style.top=xy.y+'%';
 document.querySelectorAll('.pw353-drop-target').forEach(e=>e.classList.remove('pw353-drop-target'));
 nearestDesk(ev.clientX,ev.clientY)?.classList.add('pw353-drop-target');
 ev.preventDefault();
}
function clearDrag(){
 const ctx=activeDrag;if(!ctx)return;
 const node=ctx.node;
 node.removeEventListener('pointermove',moveOfficeDrag);
 node.removeEventListener('pointerup',finishOfficeDrag);
 node.removeEventListener('pointercancel',cancelOfficeDrag);
 node.classList.remove('pw353-dragging');
 document.querySelectorAll('.pw353-drop-target').forEach(e=>e.classList.remove('pw353-drop-target'));
 try{if(node.hasPointerCapture(ctx.pointer))node.releasePointerCapture(ctx.pointer)}catch(_){/* node rerendered */}
 activeDrag=null;
}
function cancelOfficeDrag(ev){
 const ctx=activeDrag;if(!ctx||ev.pointerId!==ctx.pointer)return;
 ctx.node.style.left=ctx.original.x+'%';ctx.node.style.top=ctx.original.y+'%';
 ctx.node.dataset.dragged=ctx.dragging?'yes':'';clearDrag();
}
async function finishOfficeDrag(ev){
 const ctx=activeDrag;if(!ctx||ev.pointerId!==ctx.pointer)return;
 if(!ctx.dragging){clearDrag();return;}
 const node=ctx.node,desk=nearestDesk(ev.clientX,ev.clientY);
 let xy=roomCoords(ev.clientX,ev.clientY);
 if(desk){const r=desk.getBoundingClientRect();xy=roomCoords(r.left+r.width*.5,r.top+r.height*.85)}
 node.dataset.dragged='yes';
 node.style.left=xy.x+'%';node.style.top=xy.y+'%';
 node.style.setProperty('--pw35-home-x',xy.x+'%');node.style.setProperty('--pw35-home-y',xy.y+'%');
 node.dataset.pinned='true';
 const pid=ctx.id,old=ctx.original;
 clearDrag();
 try{
   const saved=await api(URL+'/place',{person_id:pid,x:xy.x,y:xy.y,station_id:desk?.dataset.id||null,revision:data.revision});
   if(!saved?.people)throw Error('Servern bekräftade inte placeringen');
   data=saved;updateOffice();
   document.dispatchEvent(new CustomEvent('pixelworks:v3-office-placed',{detail:{person_id:pid,station_id:desk?.dataset.id||null}}));
 }catch(error){
   // Never pretend a move has persisted when LAN or another browser disagrees.
   node.style.left=old.x+'%';node.style.top=old.y+'%';
   node.style.setProperty('--pw35-home-x',old.x+'%');node.style.setProperty('--pw35-home-y',old.y+'%');
   notice='⚠ Placeringen sparades inte: '+error.message;
   try{data=await api(URL);updateOffice()}catch(_){}
   const toast=$('#pw353-move-notice');if(toast){toast.textContent=notice;toast.hidden=false;setTimeout(()=>toast.hidden=true,6500)}
 }
}
function updateOffice(){
 if(!data?.enabled||!Array.isArray(data.people))return;
 // Live-project refresh and older room renderers may replace the stage's children.
 // Repair independently of registry revision; never duplicate global characters.
 if(!ensureOffice())return;
 const people=data.people;
 const signature=JSON.stringify(people.map(p=>[p.person_id,p.character_id,p.name,p.role,p.office_position]));
 if(!activeDrag&&(signature!==officeKey||layer.children.length!==people.length||
   [...layer.children].some((node,i)=>node.dataset.personId!==people[i].person_id)))rebuildOffice(people);
 counter.textContent=`🏢 ${people.length} anställda · 1 studio`;
 document.body.classList.add('pw3-active');
}
async function poll(){if(document.hidden||loadBusy)return;const viewing=modal.open;
 try{const fresh=await api(URL);if(!data||fresh.revision!==data.revision||fresh.enabled!==data.enabled){data=fresh;if(viewing&&tab==='crew'&&!detail)render()}
 updateOffice();}
 catch(_){updateOffice()} }
// The v3 roster must survive F5 hydration, live project polling and DOM rebuilds.
setTimeout(async()=>{await load();updateOffice();},700);
setInterval(poll,9000);
setInterval(()=>{if(data?.enabled&&!document.hidden)updateOffice()},1800);
window.addEventListener('pixelworks:v3-office-refresh',updateOffice);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)updateOffice()});
let walk=0;setInterval(()=>{if(!data?.enabled||!layer||document.hidden||matchMedia('(prefers-reduced-motion:reduce)').matches)return;
 const nodes=[...layer.children].filter(n=>n.dataset.pinned!=='true'&&!n.classList.contains('pw353-dragging'));if(nodes.length<2)return;const node=nodes[(walk++)%nodes.length],i=[...layer.children].indexOf(node),xy=places[i%places.length];
 const dx=((walk%3)-1)*2,dy=walk%2?2:-2;node.style.left=(xy[0]+dx)+'%';node.style.top=(xy[1]+dy)+'%';
 node.classList.add('walking');setTimeout(()=>{if(node.isConnected)node.classList.remove('walking')},1050)
},2600);
})();
