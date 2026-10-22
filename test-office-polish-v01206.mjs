import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const root=new URL('.',import.meta.url);
const css=readFileSync(new URL('./visual-v2.css',root),'utf8');
const local=readFileSync(new URL('./local.js',root),'utf8');
const uiSource=readFileSync(new URL('./src/ui.js',root),'utf8');
const html=readFileSync(new URL('./index.html',root),'utf8');
// No fixed manager overlay may obscure the office tip. Explicit approval still exists.
assert.doesNotMatch(local,/chiefDispatchHealth/);
assert.match(local,/chief-mandate-button/);
assert.match(local,/health\?\.state==='mandate_required'/);
assert.match(local,/ALLOW_CODEX_WORKSPACE_WRITE/);
assert.match(local,/function askChiefMandatePermission\(/);
assert.doesNotMatch(local,/const ok=confirm\('Tillåt behöriga Codex-anställda/);
assert.match(css,/#realWorkerOverview \.chief-mandate-button/);
// Version banner and server must match.
assert.match(html,/v0\.12\.0\.9/);
// Exercise the *actual* UI renderAgents method with fake existing nodes,
// rather than merely looking for a hash function in source.
function agentNode(id){
 const style={values:new Map(),setProperty(key,value){this.values.set(key,value)}};
 return {dataset:{id,bound:'1'},style,classList:{toggle(){}},setAttribute(){}};
}
const nodes=[agentNode('lead-1'),agentNode('coder-1'),agentNode('artist-1')];
const agentLayer={querySelectorAll(){return nodes}};
const context={document:{querySelector(selector){return selector==='#agentLayer'?agentLayer:null}},window:{},console};
const source=uiSource.replace(/^import\s+.*?;\s*$/gm,'').replace('export class GameUI','class GameUI');
vm.runInNewContext(source+'\nthis.GameUI=GameUI;',context);
const agents=nodes.map((node,i)=>({id:node.dataset.id,name:node.dataset.id,role:'Agent',x:20+i*20,y:60,status:'idle',station:'cafe'}));
const model={activeProjectId:'project-a',project:{agents},getAgent(id){return agents.find(a=>a.id===id)}};
const ui=new context.GameUI(model);
ui.renderAgents();
const phases=nodes.map(n=>n.style.values.get('--pw-anim-phase'));
assert.equal(new Set(phases).size,3,`expected unique animation phases, got ${phases}`);
ui.renderAgents();
assert.deepEqual(nodes.map(n=>n.style.values.get('--pw-anim-phase')),phases,'phase must not change on polling/render');
assert.match(css,/animation-delay:var\(--pw-anim-phase,0s\)/);
assert.match(css,/@media\(prefers-reduced-motion:reduce\)/);
console.log('PASS: no overlaid manager panel, visible manager approval, stable per-agent desynchronization');
