import { PROJECTS, STATIONS } from './data.js';

const clone = value => JSON.parse(JSON.stringify(value));

export class GameModel {
  constructor() {
    this.projects = clone(PROJECTS);
    this.economies = {};
    this.mailboxes = {};
    this.stationNotes = {};
    this.decisions = {};
    this.projects.forEach(project => { this.economies[project.id] = { credits:48000, lastTick:Date.now() }; this.mailboxes[project.id]=[]; this.stationNotes[project.id]=[]; this.decisions[project.id]=[]; });
    this.stations = clone(STATIONS);
    this.activeProjectId = this.projects[0].id;
    this.events = {};
    this.projects.forEach(project => {
      this.events[project.id] = project.seedEvents.map(([type, message, agentId], index) => this.makeEvent(type, message, agentId, null, index + 1, project.id));
    });
    this.projects.forEach(project => project.agents.filter(a=>!a.currentTask && a.status==='idle').forEach((a,i)=>this.seatAtCafe(a, i, project)));
  }

  loadLiveProjects(data) {
    this.projects = data.map(p=>({id:p.id,title:p.name,goal:p.idea,genre:p.genre,platform:p.platform,providers:{codex:{label:'Codex',engineState:'EJ KONTROLLERAD',quota:'okänt'}},leadId:null,agents:[],tasks:[],seedEvents:[],live:true}));
    this.events={};this.economies={};this.mailboxes={};this.stationNotes={};this.decisions={};
    for(const p of this.projects){this.events[p.id]=[];this.economies[p.id]={credits:0,lastTick:Date.now()};this.mailboxes[p.id]=[];this.stationNotes[p.id]=[];this.decisions[p.id]=[];}
    this.activeProjectId=this.projects[0]?.id||null;
  }
  setLiveStaff(projectId,staff,available){
    const project=this.projects.find(p=>p.id===projectId);
    if(!project)return;
    project.agents=staff.map((a,i)=>{
      const st=this.getStation(a.station)||this.getStation('cafe');
      return {...a,initials:a.name.slice(0,2).toUpperCase(),color:'#68dcd1',hair:'#2a4057',x:this.getStation('cafe').x-9+i*5,y:this.getStation('cafe').y+8,activity:'cafe',status:available?'idle':'blocked',currentTask:null,engineAvailable:available};
    });
    project.providers.codex.engineState=available?'HITTAD · INLOGGNING OKÄND':'SJUKSKRIVEN · CLI EJ NÅBAR';
    project.leadId=project.agents[0]?.id||null;
  }
  get economy() { return this.economies[this.activeProjectId]; }
  get mailbox() { return this.mailboxes[this.activeProjectId]; }
  get notes() { return this.stationNotes[this.activeProjectId]; }
  get project() { return this.projects.find(p => p.id === this.activeProjectId) || {id:"none",title:"Inga projekt",goal:"Skapa en produktion",agents:[],tasks:[],providers:{},leadId:null}; }
  get projectEvents() { return this.events[this.activeProjectId] ?? []; }
  getAgent(id) { return this.project.agents.find(a => a.id === id); }
  getTask(id) { return this.project.tasks.find(t => t.id === id); }
  getStation(id) { return this.stations.find(s => s.id === id); }
  getLead() { return this.getAgent(this.project.leadId); }

  switchProject(projectId) {
    if (!this.projects.some(p => p.id === projectId)) return;
    this.activeProjectId = projectId;
  }

  makeEvent(type, message, agentId = null, taskId = null, seedOffset = 0, projectId = this.activeProjectId) {
    const d = new Date(Date.now() - seedOffset * 95000);
    return {
      id: `ev-${Math.random().toString(36).slice(2,8)}`,
      projectId,
      agentId,
      taskId,
      type,
      source: 'demo',
      confidence: 'simulated',
      timestamp: d.toISOString(),
      message,
    };
  }

  addEvent(type, message, agentId = null, taskId = null) {
    const event = this.makeEvent(type, message, agentId, taskId);
    this.events[this.activeProjectId].unshift(event);
    if (["FINDING_REPORTED","TASK_COMPLETED","TASK_FAILED"].includes(type)) { this.mailbox.unshift({id:event.id,title:type==="TASK_COMPLETED"?"Uppdrag avslutat":type==="TASK_FAILED"?"Problem upptäckt":"Nytt fynd",message,agentId,at:event.timestamp,read:false,source:"demo"}); this.mailboxes[this.activeProjectId]=this.mailbox.slice(0,60); }
    this.events[this.activeProjectId] = this.events[this.activeProjectId].slice(0, 80);
    return event;
  }

  clearEvents() { this.events[this.activeProjectId] = []; }

  seatAtCafe(agent,index=0,project=this.project) {
    const cafe=this.getStation('cafe');
    agent.station='cafe';agent.activity='cafe';agent.status='idle';
    agent.x=cafe.x + [-11,-5,5,11,0][index%5];
    agent.y=cafe.y + (index%2 ? 8 : -2);
  }

  sendIdleToCafe() {
    let count=0;
    this.project.agents.forEach(agent=>{if(!agent.currentTask && agent.status==='idle'){if(agent.station!=='cafe')this.seatAtCafe(agent,count);count++;}});
  }

  moveAgent(agentId, stationId) {
    const agent = this.getAgent(agentId);
    const station = this.getStation(stationId);
    if (!agent || !station) return null;
    agent.station = station.id;
    const seat = this.project.agents.filter(a=>a.id!==agent.id && a.station===station.id).length;
    agent.x = station.x + ((seat%3)-1)*6;
    agent.y = station.y + 8 + Math.floor(seat/3)*5;
    agent.activity = station.type;
    agent.status = station.type === 'cafe' || station.type === 'meeting' ? 'idle' : 'working';
    if(station.type==='cafe')this.seatAtCafe(agent,seat);
    this.addEvent('AGENT_MESSAGE', `${agent.name} flyttade till ${station.name}.`, agent.id, agent.currentTask);
    return { agent, station };
  }

  setAgentFocus(agentId, focus) {
    const agent = this.getAgent(agentId);
    if (!agent) return;
    agent.focus = focus.trim() || agent.focus;
    this.addEvent('AGENT_MESSAGE', `${agent.name} uppdaterade fokus: “${agent.focus}”`, agent.id, agent.currentTask);
  }

  assignTask(taskId, agentId) {
    const task = this.getTask(taskId);
    const agent = this.getAgent(agentId);
    if (!task || !agent) return;
    const old = this.project.agents.find(a => a.currentTask === task.id);
    if (old && old.id !== agent.id) old.currentTask = null;
    task.assignee = agent.id;
    task.status = task.status === 'done' ? 'done' : 'working';
    agent.currentTask = task.id;
    if(agent.station==='cafe') {const target=({music:'music',voice:'voice',art:'art',coding:'code',testing:'qa',research:'research',documentation:'docs',planning:'lead',review:'meeting'})[task.requiredSkill]||'code'; this.moveAgent(agent.id,target);}
    agent.status = task.status === 'done' ? 'done' : 'working';
    this.addEvent('TASK_ASSIGNED', `${this.getLead().name} tilldelade “${task.title}” till ${agent.name}.`, agent.id, task.id);
  }

  createTask({ title, details, priority, assignee }) {
    const skillMap = { 'research':'research', 'test':'testing', 'qa':'testing', 'kod':'coding', 'implement':'coding', 'dokument':'documentation', 'plan':'planning', 'gransk':'review' };
    const haystack = `${title} ${details}`.toLowerCase();
    const requiredSkill = Object.entries(skillMap).find(([needle]) => haystack.includes(needle))?.[1] || 'planning';
    const task = {
      id: `task-${Date.now().toString(36)}`,
      title: title.trim(),
      details: details.trim() || 'Inget ytterligare acceptanskriterium angivet.',
      priority,
      assignee: assignee || null,
      status: assignee ? 'working' : 'todo',
      requiredSkill,
    };
    this.project.tasks.unshift(task);
    if (assignee) this.assignTask(task.id, assignee);
    else this.addEvent('TASK_ASSIGNED', `Nytt otilldelat uppdrag skapades: “${task.title}”.`, this.project.leadId, task.id);
    return task;
  }

  updateTaskStatus(taskId, status) {
    const task = this.getTask(taskId);
    if (!task) return;
    task.status = status;
    const agent = task.assignee ? this.getAgent(task.assignee) : null;
    if (agent) {agent.status = status === 'done' ? 'done' : status === 'todo' ? 'idle' : 'working';if(status==='done'||status==='todo'){agent.currentTask=null;agent.status='idle';this.sendIdleToCafe();}}
    const type = status === 'done' ? 'TASK_COMPLETED' : status === 'review' ? 'FINDING_REPORTED' : 'TASK_STARTED';
    this.addEvent(type, `“${task.title}” → ${status.toUpperCase()} (DEMO).`, task.assignee, task.id);
  }


  addProject({title,goal,genre,platform='Webbläsare',priority,areas}) {
    const id=`world-${Date.now().toString(36)}`;
    const base=clone(PROJECTS[0]);
    base.id=id; base.title=title.trim().slice(0,42)||'Ny produktion'; base.goal=goal.trim(); base.genre=genre; base.platform=genre==='Spel'?platform:'Ej tillämplig'; base.priorityFocus=priority;
    base.agents=base.agents.map(a=>({...a,id:`${id}-${a.id}`,currentTask:null,status:'idle',activity:a.station}));
    base.leadId=`${id}-nova`;
    base.tasks=areas.map((area,i)=>({id:`${id}-task-${i}`,title:area,details:`Planera och leverera: ${area}. Mål: ${goal.slice(0,100)}`,priority:i===0?'high':'normal',assignee:null,status:'todo',requiredSkill:({Grafik:'art',Kodning:'coding',Testning:'testing',Dokumentation:'documentation',Design:'art',Research:'research',Ljud:'music',Röster:'voice',Planering:'planning'})[area]||'coding'}));
    base.seedEvents=[]; base.agents.forEach((a,i)=>this.seatAtCafe(a,i,base)); this.projects.push(base); this.economies[id]={credits:48000,lastTick:Date.now()};this.mailboxes[id]=[];this.stationNotes[id]=[];this.decisions[id]=[];this.events[id]=[];this.activeProjectId=id;
    this.addEvent('TASK_ASSIGNED',`Ny produktion skapad: ${base.title}. ${base.tasks.length} områden väntar på delegering.`,base.leadId);
    return base;
  }
  hireAgent({name,provider,role,skill}) {
    const templates={music:{music:5,art:2,review:2},voice:{voice:5,music:2,documentation:2},art:{art:5,coding:2,review:2},coding:{coding:5,testing:2,review:2},research:{research:5,review:3,documentation:2},testing:{testing:5,review:3,coding:2},planning:{planning:5,review:4,documentation:2},documentation:{documentation:5,research:2,review:3}};
    const colors={codex:'#54d3a4',claude:'#db946f',google:'#7dafff',microsoft:'#d9aa57'};
    const agent={id:`hire-${Date.now().toString(36)}`,name:name.trim().slice(0,26)||'Ny kollega',initials:(name.trim()||'NK').slice(0,2).toUpperCase(),role,provider,skills:templates[skill]||templates.coding,status:'idle',station:({music:'music',voice:'voice',art:'art',testing:'qa'})[skill]||'meeting',activity:({music:'music',voice:'voice',art:'art',testing:'qa'})[skill]||'meeting',x:54+Math.random()*7,y:79,focus:`Fokusera på ${skill}. Vänta på uppdrag från arbetsledaren.`,color:colors[provider]||'#fff',hair:'#35304d',currentTask:null};
    this.project.agents.push(agent);this.seatAtCafe(agent,this.project.agents.filter(a=>a.station==='cafe').length);this.addEvent('AGENT_MESSAGE',`${agent.name} anställd som ${role} (${provider.toUpperCase()}).`,agent.id);return agent;
  }
  setSkill(agentId,skill,level){const a=this.getAgent(agentId);if(!a)return; a.skills[skill]=Math.max(0,Math.min(5,Number(level)));this.addEvent('AGENT_MESSAGE',`${a.name}: ${skill} ändrad till ${a.skills[skill]} i DEMO.`,agentId);}
  queueInstruction(agentId,text,mode='later') {const a=this.getAgent(agentId);if(!a||!text.trim())return;const t=this.createTask({title:text.trim().slice(0,90),details:mode==='instead'?'Prioriterat om enligt chefens instruktion':'Köat efter aktuellt arbete',priority:mode==='instead'?'high':'normal',assignee:''});if(mode==='instead'){if(a.currentTask){const old=this.getTask(a.currentTask);if(old){old.status='todo';old.assignee=null;}}this.assignTask(t.id,a.id);}this.addEvent('AGENT_MESSAGE',`${a.name} fick instruktion (${mode==='instead'?'byt fokus':'gör senare'}): ${text.trim()}`,a.id,t.id);}
  readMail(id){const letter=this.mailbox.find(x=>x.id===id);if(letter)letter.read=true;return letter;}
  deleteMail(id){this.mailboxes[this.activeProjectId]=this.mailbox.filter(x=>x.id!==id);}
  requestDecision({title,message,agentId=null,action='repo_write'}){
    const id=`decision-${Date.now()}-${Math.random().toString(36).slice(2,6)}`;
    this.mailbox.unshift({id,title,message,agentId,at:new Date().toISOString(),read:false,source:'demo',decision:true,action,outcome:null});
    this.addEvent('AGENT_MESSAGE',`Beslutsfråga på skrivbordet: ${title}`,agentId); return id;
  }
  respondDecision(id,answer){const l=this.mailbox.find(x=>x.id===id&&x.decision); if(!l||l.outcome!==null)return false;
    l.outcome=answer?'approved':'denied';l.read=true; this.addEvent('AGENT_MESSAGE',`Chefen svarade ${answer?'JA':'NEJ'} på ”${l.title}”. Endast DEMO, ingen extern åtgärd.`,l.agentId); return true;
  }
  addStationNote(stationId,text,agentId=null){const st=this.getStation(stationId);if(!st||!text.trim())return null;
    const assigned=agentId?this.getAgent(agentId):null;const task=this.createTask({title:text.trim().slice(0,90),details:`Ändringslapp på ${st.name}: ${text.trim()}`,priority:'normal',assignee:assigned?.id||''});
    task.requiredSkill=st.skill||'planning';this.notes.unshift({id:`note-${Date.now()}`,stationId,text:text.trim(),agentId:assigned?.id||null,taskId:task.id,at:new Date().toISOString()});
    this.addEvent('AGENT_MESSAGE',`Ny ändringslapp på ${st.name}${assigned?' till '+assigned.name:''}: ${text.trim()}`,assigned?.id||null,task.id);return task;
  }
  assignStationAgent(agentId,stationId){return this.moveAgent(agentId,stationId);}
  getStationAgents(stationId){return this.project.agents.filter(a=>a.station===stationId);}
  getStationNotes(stationId){return this.notes.filter(n=>n.stationId===stationId);}

  tickEconomy(hours=1/3600){const burn=this.project.agents.filter(a=>a.status==='working').reduce((sum,a)=>sum+(a.provider==='claude'?110:a.provider==='codex'?60:75),0);this.economy.credits=Math.max(0,this.economy.credits-burn*hours);return burn;}
  getProgress(){const t=this.project.tasks;return {done:t.filter(x=>x.status==='done').length,review:t.filter(x=>x.status==='review').length,working:t.filter(x=>x.status==='working').length,total:t.length};}

  autoDelegate() {
    const task = this.project.tasks.find(t => !t.assignee || t.status === 'todo');
    if (!task) return { ok:false, reason:'Alla uppdrag är redan tilldelade.' };
    const candidates = this.project.agents.filter(a => a.id !== this.project.leadId);
    candidates.sort((a,b) => (b.skills[task.requiredSkill] || 0) - (a.skills[task.requiredSkill] || 0));
    const chosen = candidates[0];
    if (!chosen) return { ok:false, reason:'Ingen agent tillgänglig.' };
    this.assignTask(task.id, chosen.id);
    const target=({music:'music',voice:'voice',art:'art',coding:'code',testing:'qa',research:'research',documentation:'docs',planning:'lead'})[task.requiredSkill];
    if(target)this.moveAgent(chosen.id,target);
    return { ok:true, task, agent:chosen };
  }
}
