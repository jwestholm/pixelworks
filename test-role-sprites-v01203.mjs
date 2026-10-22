import { readFileSync,existsSync } from 'node:fs';
import assert from 'node:assert/strict';
const root=new URL('.',import.meta.url);
const html=readFileSync(new URL('index.html',root),'utf8');
const css=readFileSync(new URL('visual-v2.css',root),'utf8');
const ui=readFileSync(new URL('src/ui.js',root),'utf8');
assert.ok(html.indexOf('id="gameDock"')<html.indexOf('</header>'),'navigation must be in header');
assert.match(css,/body \.top-statuses\{display:none!important;/);
assert.match(ui,/role_type/);
assert.match(ui,/sprite-role-\$\{roleKey\}/);
for(const role of ['programmer','qa','artist','musician','voice','research','lead','writer','allround']) {
 for(let variant=0;variant<4;variant++)for(const pose of ['idle','walk','working','cafe']) {
  const name=`agent-${role}-${variant}-${pose}.png`;
  assert.ok(existsSync(new URL(`assets/office-v2/${name}`,root)),name);
  assert.ok(css.includes(name),name);
 }
}
console.log('Role sprites and compact header: PASS');
