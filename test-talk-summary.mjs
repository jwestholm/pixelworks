import fs from 'node:fs';
import assert from 'node:assert/strict';
const s=fs.readFileSync(new URL('./local.js',import.meta.url),'utf8');
const section=s.slice(s.indexOf('async function talkLive('),s.indexOf('window.pixelWorksTalkLive=talkLive;'));
assert(section.includes('latestNote')); assert(section.includes('record.integrated'));assert(section.includes('🔧 Teknisk logg'));assert(!section.includes("events.slice(-15).reverse()"));
assert(s.includes("if(type==='item.started' && it==='command_execution')return null"));
assert(s.includes("if(type==='item.completed' && it==='file_change')return null"));
console.log('OK: talk summary separates agent output from technical events');
