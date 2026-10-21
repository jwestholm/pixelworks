import assert from 'node:assert/strict';
import {planRoute,destinationForStation} from './src/navigation.js';
const boxes=[{left:35,right:47,top:41,bottom:55},{left:47,right:62,top:78,bottom:90},{left:56,right:67,top:57,bottom:66}];
const test=planRoute({x:40,y:91},{x:43,y:55},boxes);
assert.ok(test.length>=2,'must find route around center tables');
for(let i=1;i<test.length;i++){
 const a=test[i-1],b=test[i];
 for(let t=0;t<=1;t+=.05){const x=a.x+(b.x-a.x)*t,y=a.y+(b.y-a.y)*t;assert.ok(!boxes.some(o=>x>o.left&&x<o.right&&y>o.top&&y<o.bottom),`walk intersects furniture at ${x},${y}`);}
}
assert.deepEqual(planRoute({x:10,y:50},{x:90,y:50},[{left:0,right:100,top:30,bottom:95}]),[]);
assert.ok(destinationForStation({id:'code',x:42,y:45}).y>45);
console.log('PASS: A* routes around furniture, blocked routes fail closed, station approach');
