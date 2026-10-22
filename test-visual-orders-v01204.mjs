import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const source=readFileSync(new URL('./visual-v2.js',import.meta.url),'utf8');
const original=readFileSync(new URL('./local.js',import.meta.url),'utf8');
assert.match(original,/async function stationOrders\(slug,station,placed=false,openQueue=false\)/);
assert.match(original,/step=openQueue\?'queue':'choose'/);
let rendered='', queueRequest=null;
const dockDialog={open:false,showModal(){this.open=true},close(){this.open=false},addEventListener(){}};
const dockContent={
 set innerHTML(s){rendered=s;},get innerHTML(){return rendered;},
 querySelector(){return {addEventListener(){}};},
 querySelectorAll(){const stations=[...rendered.matchAll(/data-station="([a-z]+)"/g)];return stations.map(m=>({dataset:{station:m[1]},onclick:null}));}
};
const dock={addEventListener(){},querySelectorAll(){return []}};
// Store button objects to simulate user clicking "Visa arbetskö".
let realButtons=[];
dockContent.querySelectorAll=function(){realButtons=[...rendered.matchAll(/data-station="([a-z]+)"/g)].map(m=>({dataset:{station:m[1]},onclick:null}));return realButtons};
const document={body:{classList:{contains(){return true}}},querySelector(s){return {'#gameDock':dock,'#dockDialog':dockDialog,'#dockDialogContent':dockContent,'#projectSelect':{value:'test-project'}}[s]||null}};
const window={__PIXEL_WORKS_DEMO__:{model:{project:{tasks:[]}},ui:{callbacks:{onStationClick(){throw new Error('Must not use demo board')}}}},pixelWorksApi:async()=>({orders:[
 {id:'1',station:'code',status:'running',instruction:'Ny funktion'},
 {id:'2',station:'meeting',status:'superseded',instruction:'Gammalt försök'},
 {id:'3',station:'qa',status:'waiting',instruction:'Ny felrapport'},
 {id:'4',station:'meeting',status:'review',instruction:'Väntar på granskning'},
 {id:'5',station:'code',status:'done',instruction:'Avslutat'},
 {id:'6',station:'qa',status:'failed',instruction:'Behöver hjälp'}
 ]}),pixelWorksStationOrders:(...args)=>queueRequest=args};
const ctx=vm.createContext({document,window,console});
vm.runInContext(source,ctx,{filename:'visual-v2.js'});
await vm.runInContext('showOrders()',ctx);
assert.match(rendered,/Arbetsorder \(4\)/);
assert.match(rendered,/1 väntar vid skrivbord/);
assert.doesNotMatch(rendered,/Gammalt försök/);
assert.doesNotMatch(rendered,/Avslutat/);
assert.match(rendered,/Arbete pågår/);
assert.match(rendered,/Behöver granskning/);
assert.match(rendered,/Behöver hjälp/);
assert.equal(realButtons.length,4);
realButtons.find(b=>b.dataset.station==='qa').onclick();
assert.deepEqual(queueRequest,['test-project','qa',false,true]);
assert.equal(dockDialog.open,false);
console.log('PASS Visual orders: real active statuses and direct station queue navigation');
