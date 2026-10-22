import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
const studio=readFileSync(new URL('./src/studio.js',import.meta.url),'utf8');
const local=readFileSync(new URL('./local.js',import.meta.url),'utf8');
assert.match(local,/window\.pixelWorksApi=api/);
for(const endpoint of ['/orders','/staff','/jobs','/dispatch/health']) {
  assert.ok(studio.includes(`window.pixelWorksApi(base+'${endpoint}')`),endpoint);
  assert.ok(!studio.includes(`fetch(base+'${endpoint}')`),`unauthenticated ${endpoint}`);
}
assert.match(studio,/if\(!this\.model\.project\.live\)\{const unread=/);
assert.match(local,/action:'read'\}\);await updateDeskBadge\(\)/);
assert.match(local,/action:'archive'\}\);await updateDeskBadge\(\)/);
console.log('Session-aware mission board and real-report badge contract OK');
