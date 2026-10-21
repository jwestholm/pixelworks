// Layout-based A* for the visible office. Navigation affects sprites only, never starts tools.
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const STEP=2;
export function planRoute(start,end,obstacles, opts={}) {
  const lowY=opts.minY??33, highY=opts.maxY??94;
  const width=50, height= Math.floor((highY-lowY)/STEP)+1;
  const key=(x,y)=>y*width+x;
  const fromCell=p=>({x:clamp(Math.round(p.x/STEP),4,47),y:clamp(Math.round((p.y-lowY)/STEP),0,height-1)});
  const coords=c=>({x:c.x*STEP,y:lowY+c.y*STEP});
  const blocked=(x,y)=>{if(x<4||x>47||y<0||y>=height)return true;const p=coords({x,y});return obstacles.some(o=>p.x>=o.left && p.x<=o.right && p.y>=o.top && p.y<=o.bottom);};
  const nearest=(p)=>{const at=fromCell(p);if(!blocked(at.x,at.y))return at;for(let r=1;r<25;r++){let best=null,dist=Infinity;for(let dy=-r;dy<=r;dy++)for(let dx=-r;dx<=r;dx++){if(Math.max(Math.abs(dx),Math.abs(dy))!==r)continue;const x=at.x+dx,y=at.y+dy;if(!blocked(x,y)){const d=dx*dx+dy*dy;if(d<dist){best={x,y};dist=d;}}}if(best)return best;}return null;};
  const origin=nearest(start),goal=nearest(end);if(!origin||!goal)return [];
  const startKey=key(origin.x,origin.y),goalKey=key(goal.x,goal.y),cost=new Map([[startKey,0]]),came=new Map(),open=[{...origin,f:0}];
  const distance=(x,y)=>Math.hypot(x-goal.x,y-goal.y);
  let attempts=0;
  while(open.length && attempts++<5000){open.sort((a,b)=>a.f-b.f);const c=open.shift(),ck=key(c.x,c.y);if(ck===goalKey){const result=[coords(c)];let id=ck;while(came.has(id)){id=came.get(id);result.push(coords({x:id%width,y:Math.floor(id/width)}));}result.reverse();const simplified=[];for(let i=0;i<result.length;i++){const prev=result[i-1],next=result[i+1];if(prev&&next&&Math.sign(result[i].x-prev.x)===Math.sign(next.x-result[i].x)&&Math.sign(result[i].y-prev.y)===Math.sign(next.y-result[i].y))continue;simplified.push(result[i]);}return simplified;}
    for(const [dx,dy] of [[0,1],[1,0],[0,-1],[-1,0],[1,1],[-1,1],[1,-1],[-1,-1]]){const x=c.x+dx,y=c.y+dy;if(blocked(x,y)||(dx&&dy&&(blocked(c.x+dx,c.y)||blocked(c.x,c.y+dy))))continue;const id=key(x,y),next=(cost.get(ck)??Infinity)+Math.hypot(dx,dy);if(next<(cost.get(id)??Infinity)){came.set(id,ck);cost.set(id,next);const f=next+distance(x,y);const present=open.findIndex(n=>n.x===x&&n.y===y);if(present>=0)open.splice(present,1);open.push({x,y,f});}}
  }
  return [];
}
export function furnitureObstacles(stage, stations){
  const r=stage.getBoundingClientRect();if(!r.width||!r.height)return [];
  return [...stations].map(el=>{const b=el.getBoundingClientRect();const pad=9;return {left:100*(b.left-r.left+pad)/r.width,right:100*(b.right-r.left-pad)/r.width,top:100*(b.top-r.top+pad)/r.height,bottom:100*(b.bottom-r.top-pad)/r.height};});
}
export function destinationForStation(station,seat=0){
  const x=station.x+(seat%3-1)*3.5;
  // Stop at the front/side of furniture, never inside its footprint.
  const below=station.id==='cafe'?station.y+7:station.y+10;
  return {x:clamp(x,8,93),y:clamp(below,34,93)};
}
