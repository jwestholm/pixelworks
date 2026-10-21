const chatter = {
  coding: ['Jag har en liten patch redo för QA.', 'UI-state är separerad från renderingen.', 'Jag minskar beroenden innan nästa steg.'],
  research: ['Jag har ett fynd, men det är inte verifierat.', 'Två hypoteser återstår att jämföra.', 'Jag markerar osäkerheten i rapporten.'],
  testing: ['Jag kan reproducera beteendet i demon.', 'En edge case återstår.', 'Jag testar stationbyte en gång till.'],
  planning: ['Nästa deluppgift är tydlig.', 'Jag delegerar först när kriteriet är konkret.', 'Vi håller oss till NOW.'],
  documentation: ['Jag uppdaterar beslut och begränsningar.', 'Jag märker det här som DEMO.', 'Jag skiljer rapporterat från verifierat.'],
  music: ['Jag komponerar ett nytt tema.', 'Melodin börjar ta form.', 'Jag provar ett nytt gitarr-riff.'],
  voice: ['Jag spelar in dialog i mikrofonen.', 'Jag provar en annan rösttolkning.', 'Replikerna behöver bättre timing.'],
  art: ['Jag skissar nya sprites.', 'Jag justerar paletten.', 'Animationens nyckelrutor tar form.'],
  cafe: ['Kaffet är perfekt idag!', 'Har du sett den nya pixelkatten?', 'Vi borde skaffa en kaffemaskin till.', 'Ska vi ta en fika innan nästa sprint?'],
  review: ['Jag vill se evidensen före godkännande.', 'Det här behöver ett motexempel.', 'Bra — nu finns ett verifierbart kriterium.'],
};

export class DemoSimulation {
  constructor(model, callbacks) {
    this.model = model;
    this.callbacks = callbacks;
    this.running = true;
    this.timers = [];
  }

  start() {
    this.stopTimers();
    this.timers.push(setInterval(() => this.tickMessage(), 5200));
    this.timers.push(setInterval(() => this.tickStatus(), 9200));
    this.timers.push(setInterval(() => {if(this.running){this.model.sendIdleToCafe();this.callbacks.onState?.();}}, 4400));
  }

  stopTimers() { this.timers.forEach(clearInterval); this.timers = []; }
  setRunning(value) { this.running = value; }

  tickMessage() {
    if (!this.running) return;
    const agents = this.model.project.agents;
    if (!agents.length) return;
    const agent = agents[Math.floor(Math.random() * agents.length)];
    const primarySkill = agent.station==='cafe' && !agent.currentTask ? 'cafe' : Object.entries(agent.skills).sort((a,b)=>b[1]-a[1])[0]?.[0] || 'review';
    const options = chatter[primarySkill] || chatter.review;
    const message = options[Math.floor(Math.random() * options.length)];
    const others=primarySkill==='cafe'?agents.filter(a=>a.id!==agent.id&&a.station==='cafe'):[];
    const audience=others.length?` till ${others[Math.floor(Math.random()*others.length)].name}`:'';
    this.model.addEvent('AGENT_MESSAGE', `${agent.name}${audience}: “${message}” (DEMO)`, agent.id, agent.currentTask);
    this.callbacks.onMessage?.(agent, message);
    this.callbacks.onState?.();
  }

  tickStatus() {
    if (!this.running) return;
    const workers = this.model.project.agents.filter(a => a.currentTask && a.status !== 'blocked');
    if (!workers.length) return;
    const agent = workers[Math.floor(Math.random() * workers.length)];
    if (agent.status === 'working' && Math.random() > .55) {
      const task = this.model.getTask(agent.currentTask);
      if (task && task.status !== 'done') {
        task.status = 'review';
        this.model.addEvent('FINDING_REPORTED', `${agent.name} rapporterade ett demo-resultat för “${task.title}”.`, agent.id, task.id);
      }
    }
    this.callbacks.onState?.();
  }
}
