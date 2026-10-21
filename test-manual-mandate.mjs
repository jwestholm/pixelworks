import fs from 'node:fs'; import assert from 'node:assert/strict';
const s=fs.readFileSync(new URL('./local.js',import.meta.url),'utf8');
assert.match(s,/Arbetsordern är redan skapad/);
assert.match(s,/Godkänn lokalt skrivmandat/);
assert.match(s,/approval:'ALLOW_CODEX_WORKSPACE_WRITE'/);
assert.match(s,/if\(!chiefHere\).*?startQueue\(slug,station\)/s);
assert.match(s,/isolated:true,approval:'PROJECT_MANDATE'/);
console.log('Manuellt uppdrag + aktivt samtycke + isolerad Codex: OK');
