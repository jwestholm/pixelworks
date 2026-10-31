/* Pixel Works 3.5 A+B first playable slice.
 * All scenery, dialogue bubbles, and clock are purely visual simulations.
 * No requests, no provider calls, no writes to project/crew state.
 */
(() => {
  'use strict';
  if (window.__PW35_WORLD__) return;
  window.__PW35_WORLD__ = true;
  const $ = (selector, root=document) => root.querySelector(selector);
  const characterIds = new Set(['chef','joppe','siv','nisse','mira','vera','lova']);
  const phrases = {
    chef: ['Jag ser över dagens plan.', 'Vi behöver bara ett bra nästa steg.'],
    joppe: ['Tjaba! Nu blir det åka av!', 'Den där grejen kan bli riktigt frän.'],
    siv: ['Jag har skrivit en liten checklista.', 'Vi bör precisera det där lite.'],
    nisse: ['En prototyp går fort, hehe.', 'Den håller nog. Vi testar!'],
    mira: ['En pixel till, sen sitter det!', 'Färgerna behöver lite kärlek.'],
    vera: ['Psst! Jag hör en ny melodi.', 'Tänk om knappen sa plong?'],
    lova: ['Det där låter som början på en saga.', 'Även kaffemaskinen har en historia.']
  };
  const DAY_LENGTH_MS = 12 * 60 * 1000; // Simulated, synced by device clock; never a real work schedule.
  const SETTINGS = 'pw35-ambience-v1';
  let settings = { preview:'auto', chatter:true, motion:true };
  try {
    const saved = JSON.parse(localStorage.getItem(SETTINGS) || '{}');
    if (['auto','day','dusk','night'].includes(saved.preview)) settings.preview=saved.preview;
    if (typeof saved.chatter==='boolean') settings.chatter=saved.chatter;
    if (typeof saved.motion==='boolean') settings.motion=saved.motion;
  } catch (_) { /* Storage can be unavailable; fall back to visual defaults. */ }
  const store = () => { try { localStorage.setItem(SETTINGS,JSON.stringify(settings)); } catch (_){} };
  const motionOff = () => !settings.motion || !!window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  let stage=null,root=null,clock=null,phase='',tick=0,personSequence=0,knownPeople=null;
  const css=document.createElement('link');css.rel='stylesheet';css.href='./src/pw-v35-world.css';css.id='pw35-styles';document.head.appendChild(css);

  function simulatedHour() {
    // Every device sees approximately the same clock without network or back-end mutations.
    const ms = ((Date.now() % DAY_LENGTH_MS) + DAY_LENGTH_MS) % DAY_LENGTH_MS;
    return ms / DAY_LENGTH_MS * 24;
  }
  function selectedHour(){ return settings.preview==='day'?12:settings.preview==='dusk'?18.6:settings.preview==='night'?23.5:simulatedHour() }
  function phaseAt(h) {
    if(h>=5&&h<8)return 'dawn';
    if(h>=8&&h<17.5)return 'day';
    if(h>=17.5&&h<20)return 'dusk';
    return 'night';
  }
  function make(tag,cls,attrs={}){
    const el=document.createElement(tag);el.className=cls;
    for(const [name,value] of Object.entries(attrs))el.setAttribute(name,value);
    return el;
  }
  function ensureScene(){
    const nowStage=$('#officeStage');
    if(!nowStage){stage=null;return false;}
    stage=nowStage;
    if(root?.parentElement!==stage){root=null;knownPeople=null;}
    if(!root){
      root=make('div','pw35-atmosphere',{id:'pw35-atmosphere','aria-hidden':'true'});
      const sky=make('div','pw35-sky');
      const star=make('div','pw35-stars');
      const clouds=make('div','pw35-clouds');
      const sun=make('div','pw35-sun');
      const moon=make('div','pw35-moon');
      sky.append(star,clouds,sun,moon);
      const shine=make('div','pw35-lightshaft');
      const tint=make('div','pw35-room-tint');
      const lamps=make('div','pw35-lamps');
      for(const [x,y] of [[24,53],[47,52],[69,53],[82,68],[35,72]]){
        const lamp=make('span','pw35-lamp');lamp.style.left=x+'%';lamp.style.top=y+'%';lamps.append(lamp);
      }
      root.append(sky,shine,tint,lamps);
      stage.append(root);
    }
    if(!clock||clock.parentElement!==stage){
      clock=make('section','pw35-clock',{id:'pw35-clock','aria-label':'Spelkontorets simulerade dygn'});
      const line=make('div','pw35-clock-line');
      line.innerHTML='<span id="pw35-phase">☀️ Dag</span><span id="pw35-time">12:00</span><span class="pw35-demo">SPELTID · DEMO</span>';
      const control=make('div','pw35-clock-buttons');
      const cycle=make('button','pw35-btn',{type:'button',id:'pw35-phase-button','aria-label':'Växla mellan automatiskt speldygn, dag, solnedgång och natt'});
      const talk=make('button','pw35-btn',{type:'button',id:'pw35-chatter-button','aria-label':'Slå på eller av fiktiva pratbubblor'});
      const motion=make('button','pw35-btn',{type:'button',id:'pw35-motion-button','aria-label':'Slå på eller av kontorets dekorativa rörelser'});
      cycle.addEventListener('click',()=>{
        const list=['auto','day','dusk','night'];settings.preview=list[(list.indexOf(settings.preview)+1)%list.length];
        store();renderSky();
      });
      talk.addEventListener('click',()=>{
        settings.chatter=!settings.chatter;store();updateControls();
        if(!settings.chatter)removeBubbles();
      });
      motion.addEventListener('click',()=>{settings.motion=!settings.motion;store();updateControls();if(!settings.motion)removeBubbles()});
      control.append(cycle,talk,motion);clock.append(line,control);stage.append(clock);
    }
    return true;
  }
  function updateControls(){
    const previewLabel={auto:'🕒 Auto',day:'☀️ Dag',dusk:'🌇 Kväll',night:'🌙 Natt'};
    const btn=$('#pw35-phase-button',clock),talk=$('#pw35-chatter-button',clock),motion=$('#pw35-motion-button',clock);
    if(btn){btn.textContent=previewLabel[settings.preview];btn.title='Välj ljusläge (visuellt, ingen påverkan på uppdrag)';}
    if(talk){talk.textContent=settings.chatter?'💬 Prat på':'💬 Prat av';talk.setAttribute('aria-pressed',String(settings.chatter));}
    if(motion){motion.textContent=settings.motion?'🍃 Rörelse på':'⏸ Rörelse av';motion.setAttribute('aria-pressed',String(settings.motion));}
    stage?.classList.toggle('pw35-motion-off',motionOff());
  }
  function renderSky(){
    if(!ensureScene())return;
    const h=selectedHour();phase=phaseAt(h);
    stage.dataset.pw35Phase=phase;
    const sky=$('.pw35-sky',root),sun=$('.pw35-sun',root),moon=$('.pw35-moon',root);
    const daytime=h>=5.5&&h<19;
    const sunP=Math.max(0,Math.min(1,(h-5.5)/13.5));
    const nightHour=h<5.5?h+24:h;
    const moonP=Math.max(0,Math.min(1,(nightHour-19)/10.5));
    sun.style.left=(8+sunP*84)+'%';
    sun.style.top=(70-50*Math.sin(Math.PI*sunP))+'%';
    moon.style.left=(8+moonP*84)+'%';
    moon.style.top=(70-43*Math.sin(Math.PI*moonP))+'%';
    sun.style.opacity=daytime?'1':'0';
    moon.style.opacity=daytime?'0':'1';
    sky.setAttribute('data-time',String(Math.floor(h)));
    const label={dawn:'🌅 Morgon',day:'☀️ Dag',dusk:'🌇 Solnedgång',night:'🌙 Natt'}[phase];
    $('#pw35-phase',clock).textContent=label;
    $('#pw35-time',clock).textContent=String(Math.floor(h)).padStart(2,'0')+':'+String(Math.floor((h%1)*60)).padStart(2,'0');
    updateControls();
  }
  function removeBubbles(){document.querySelectorAll('#pw3OfficeAgents .pw35-speech').forEach(e=>e.remove())}
  function getEmployees(){return [...document.querySelectorAll('#pw3OfficeAgents .pw3-person[data-person-id]')].filter(n=>n.isConnected)}
  function hasModal(){return !!document.querySelector('dialog[open]')}
  function decorateEmployee(n){
    const ident=n.dataset.characterId;
    if(!characterIds.has(ident))return;
    if(n.dataset.pw35Ready==='true')return;
    n.dataset.pw35Ready='true';
    // Preserve the office position when animations are disabled; old v3 timers
    // may continue changing inline left/top, but CSS holds the visual position.
    n.style.setProperty('--pw35-home-x',n.style.left||'50%');
    n.style.setProperty('--pw35-home-y',n.style.top||'55%');
    n.style.setProperty('--pw35-talk',`url("./assets/characters/${ident}/${ident}-talk.png")`);
    n.style.setProperty('--pw35-celebrate',`url("./assets/characters/${ident}/${ident}-celebrate.png")`);
    // Preserve real status semantics. Ambient talking is not 'working'.
    n.title=(n.title||n.getAttribute('aria-label')||'Anställd')+' · Fiktiva småanimationer';
  }
  function celebrate(n){
    if(motionOff())return;
    n.classList.add('pw35-celebrating');
    setTimeout(()=>n.classList.remove('pw35-celebrating'),2700);
  }
  function inspectCrew(){
    if(!document.body.classList.contains('pw3-active'))return;
    const arr=getEmployees();arr.forEach(decorateEmployee);
    const current=new Set(arr.map(n=>n.dataset.personId));
    if(knownPeople!==null){
      for(const n of arr){if(!knownPeople.has(n.dataset.personId))celebrate(n)}
    }
    knownPeople=current;
  }
  function speak(){
    inspectCrew();
    if(!settings.chatter||motionOff()||document.hidden||hasModal())return;
    const employees=getEmployees();if(!employees.length)return;
    const n=employees[personSequence++%employees.length],ident=n.dataset.characterId;
    if(n.classList.contains('walking')||n.classList.contains('working')||n.classList.contains('pw35-celebrating'))return;
    const lines=phrases[ident];if(!lines)return;
    if(n.querySelector('.pw35-speech'))return;
    n.classList.add('pw35-talking');
    const bubble=make('span','pw35-speech',{role:'note','aria-label':'Simulerat småprat'});
    bubble.textContent=lines[Math.floor(personSequence/Math.max(1,employees.length))%lines.length]+' · DEMO';
    n.append(bubble);
    setTimeout(()=>{n.classList.remove('pw35-talking');bubble.remove()},3200);
  }
  function start(){
    ensureScene();renderSky();
    setTimeout(inspectCrew,950);
    setInterval(()=>{if(!document.hidden){renderSky();inspectCrew();}},3500);
    setInterval(speak,9000);
    document.addEventListener('visibilitychange',()=>{if(!document.hidden)renderSky()});
    window.addEventListener('pixelworks:v3-office-refresh',()=>{renderSky();inspectCrew()});
  }
  window.pixelWorksV35={phaseAt, get mode(){return settings.preview}, get ambience(){return phase}, preview(mode){
    if(!['auto','day','dusk','night'].includes(mode))return false;
    settings.preview=mode;store();renderSky();return true;
  },refresh:()=>{renderSky();inspectCrew()}};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
