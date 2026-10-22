import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const script=readFileSync(new URL('./visual-v2.js',import.meta.url),'utf8');
const handlers={};
const buttons=['office','agents','orders','projects','events','findings','stats','settings'].map(name=>{
  const attrs={};const classes=new Set(name==='office'?['active']:[]);
  return {dataset:{dock:name},classList:{toggle(c,on){if(on)classes.add(c);else classes.delete(c)},contains(c){return classes.has(c)}},setAttribute(k,v){attrs[k]=v},removeAttribute(k){delete attrs[k]},getAttribute(k){return attrs[k]}};
});
const docks={querySelectorAll:()=>buttons,addEventListener(type,fn){handlers['dock:'+type]=fn}};
const dialogs=Object.fromEntries(['dockDialog','localStudioDialog','gameDialog','taskDialog'].map(id=>[id,{open:true,addEventListener(type,fn){handlers[id+':'+type]=fn},close(){this.open=false;handlers[id+':close']?.()},showModal(){this.open=true}}]));
const nodes={'#gameDock':docks,'#dockDialogContent':{set innerHTML(v){this.html=v},querySelector(){return {addEventListener(){}}},querySelectorAll(){return []}},'#projectSelect':{value:'demo'}};
const document={body:{classList:{contains(){return false}}},querySelector(sel){return nodes[sel]||dialogs[sel.slice(1)]||null}};
const context=vm.createContext({document,window:{__PIXEL_WORKS_DEMO__:{model:{project:{tasks:[]}},ui:{closeDrawer(){}}}},console});
vm.runInContext(script,context);
// Open the settings menu using the real click handler, then close it.
const settings=buttons.find(b=>b.dataset.dock==='settings');
handlers['dock:click']({target:{closest:()=>settings}});
assert.equal(settings.classList.contains('active'),true);
handlers['dockDialog:close']();
assert.equal(buttons[0].classList.contains('active'),true);
assert.equal(buttons.filter(x=>x.classList.contains('active')).length,1);
// Check the close event on all dialog surfaces for a second navigation route.
for(const id of ['localStudioDialog','gameDialog','taskDialog']){
  buttons[1].classList.toggle('active',true);buttons[0].classList.toggle('active',false);
  handlers[id+':close']();
  assert.equal(buttons[0].getAttribute('aria-current'),'page');
  assert.equal(buttons[1].classList.contains('active'),false);
}
assert.match(readFileSync(new URL('./local.js',import.meta.url),'utf8'),/data-action="archive"/);
assert.match(readFileSync(new URL('./local.js',import.meta.url),'utf8'),/data-archive-yes/);
assert.match(readFileSync(new URL('./local.js',import.meta.url),'utf8'),/stationOrders\(slug,station,false,true\)/);
console.log('PASS Navigation reset and archive in-game confirmation');
