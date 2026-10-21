import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
const studio=readFileSync(new URL('./src/studio.js',import.meta.url),'utf8');
const server=readFileSync(new URL('./backend/server.py',import.meta.url),'utf8');
assert.match(studio,/board\(\)\{if\(this\.model\.project\.live\)\{this\.liveBoard\(\);return;\}/);
for(const endpoint of ['/orders','/staff','/jobs','/dispatch/health'])assert.ok(studio.includes("base+'"+endpoint+"'"));
assert.match(studio,/Endast jobb med status köad\/pågår räknas som aktiva/);
assert.match(server,/Spelet är ännu inte byggt: index\.html saknas/);
console.log('Live mission board contract OK');
