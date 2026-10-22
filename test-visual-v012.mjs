import { readFileSync, existsSync } from 'node:fs';
import assert from 'node:assert/strict';
const read = f => readFileSync(new URL(f,import.meta.url),'utf8');
const html=read('./index.html'),css=read('./visual-v2.css'),js=read('./visual-v2.js'), ui=read('./src/ui.js');
assert.match(html,/id="gameDock"/);
for(const n of ['office','agents','orders','projects','events','findings','stats','settings'])assert.match(html,new RegExp('data-dock="'+n+'"'));
for(const n of ['lead','code','research','qa','cafe','meeting','docs','music','voice','art']){
 assert.ok(existsSync(new URL('./assets/office-v2/desk-'+n+'.png', import.meta.url))); 
 assert.match(css,new RegExp('desk-'+n+'\\.png'));
}
for(let i=0;i<8;i++)for(const pose of ['idle','working','walk'])assert.ok(existsSync(new URL('./assets/office-v2/agent-'+i+'-'+pose+'.png', import.meta.url)));
assert.match(ui,/sprite-role-/);
assert.match(css,/body\.live-project \.right-rail \.real-session-panel/);
assert.match(css,/body:not\(\.live-project\) \.right-rail \.event-panel/);
assert.match(css,/credit-pill\{display:none!important/);
assert.match(js,/window\.pixelWorksApi/);
console.log('Visual v0.12.0: contracts PASS');
