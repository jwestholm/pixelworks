import { GameModel } from './model.js';
import { GameUI } from './ui.js';
import { DemoSimulation } from './simulation.js';
import { StudioMenus } from './studio.js';
import './pw-cafe-images.js';
import './pw-freesound.js';
import './pw-media-review.js';
import './pw-dialog-hub.js';
import './pw-provider-presence.js';
import './pw-agent-help-bridge.js';
// Pixel Works v3 recruitment replaces legacy project-staff UI, not worker objects.
import './pw-v3-recruit.js';
import './pw-v3-jobs.js';
import './pw-v3-chief.js';
// v3.5 A+B pixel office: visual-only ambient cycle and shared dialog theme.
import './pw-v35-world.js';
// V3.5.1: one navigation controller for personnel, jobs, chief and review.
import './pw-v351-dialogs.js';
// v3.5.2: readable pixel-game personnel cards; CSS is served by the allowlisted backend.
import './pw-v352-personnel.js';
// V3.5.3: window-aligned ambient art and readable office placement controls.
import './pw-v353-office.js';

const model = new GameModel();
const ui = new GameUI(model);
const studio = new StudioMenus(model,ui);
let paused = false;

const simulation = new DemoSimulation(model, {
  onMessage: (agent, message) => ui.showSpeech(agent, message),
  onState: () => { ui.renderAgents(); ui.renderTasks(); ui.renderEvents(); if (ui.selectedAgentId) ui.renderDrawer(model.getAgent(ui.selectedAgentId)); }
});

ui.bind({
  onProjectChange(projectId) {
    ui.resetWalks();
    model.switchProject(projectId);
    ui.selectedAgentId = null;
    ui.closeDrawer();
    ui.renderAll();
    window.dispatchEvent(new Event('pixelworks:v3-office-refresh'));
    window.pixelWorksRefreshOrders?.(projectId);
    ui.toast(`Projektvärld: ${model.project.title}`);
  },
  onMoveAgent(agentId, stationId) {
    if(model.project.live && window.pixelWorksMoveLive) {window.pixelWorksMoveLive(model.activeProjectId,agentId,stationId).then(()=>{ui.walkTo(agentId,stationId);ui.toast("Arbetsplats vald · Codex går till stationen");}).catch(e=>ui.toast("Flytt misslyckades: "+e.message));return;}
    ui.walkTo(agentId,stationId);
    const result = model.moveAgent(agentId, stationId);
    if (!result) return;
    ui.renderAgents(); ui.renderEvents(); ui.renderTasks();
    if (ui.selectedAgentId === agentId) ui.renderDrawer(result.agent);
    ui.showSpeech(result.agent, `Byter till ${result.station.short}.`);
    ui.toast(`${result.agent.name} → ${result.station.name}`);
  },
  onFocus(agentId, focus) {
    model.setAgentFocus(agentId, focus);
    ui.renderEvents(); ui.renderDrawer(model.getAgent(agentId));
    ui.toast('Fokus uppdaterat · DEMO');
  },
  onCreateTask(formData) {
    const task = model.createTask(formData);
    ui.renderTasks(); ui.renderAgents(); ui.renderEvents();
    ui.toast(`Uppdrag skapat: ${task.title}`);
  },
  onTaskStatus(taskId, status) {
    model.updateTaskStatus(taskId, status);
    ui.renderTasks(); ui.renderAgents(); ui.renderEvents();
    if (ui.selectedAgentId) ui.renderDrawer(model.getAgent(ui.selectedAgentId));
  },
  onAutoDelegate() {
    if(model.project.live){ui.toast("Skarpt läge: välj Codex-arbetsstation och godkänn verkligt uppdrag via Lokal studio.");return;}
    const result = model.autoDelegate();
    if (!result.ok) { ui.toast(result.reason); return; }
    ui.renderTasks(); ui.renderAgents(); ui.renderEvents();
    ui.showSpeech(model.getLead(), `${result.agent.name} tar ${result.task.requiredSkill}.`);
    ui.toast(`${result.task.title} → ${result.agent.name}`);
  },
  onTalk(id){
    if(model.project.live && window.pixelWorksTalkOrHelpLive){
      window.pixelWorksTalkOrHelpLive(model.activeProjectId,id,model.getAgent(id));return;
    }
    studio.talk(id);
  },
  onStationClick(id){studio.station(id);},
  onSkills(id){studio.skills(id);},
  onClearEvents() { model.clearEvents(); ui.renderEvents(); },
  onToggleSimulation() {
    paused = !paused; simulation.setRunning(!paused); ui.setSimulationPaused(paused); ui.toast(paused?'Demo-simulering pausad':'Demo-simulering igång');
  }
});

model.sendIdleToCafe();
ui.renderAll();
studio.bind();
simulation.start();
window.pixelWorksApplyLive = (projects,staffById,available)=>{const active=model.activeProjectId;ui.resetWalks();model.loadLiveProjects(projects);for(const p of projects)model.setLiveStaff(p.id,staffById[p.id]||[],available);if(projects.some(p=>p.id===active))model.activeProjectId=active;ui.closeDrawer();ui.renderAll();simulation.setRunning(false);window.dispatchEvent(new Event('pixelworks:v3-office-refresh'));};
window.pixelWorksAgentTravel=(agentId,station,state)=>{if(!model.project.live)return;const agent=model.project.agents.find(a=>a.id===agentId);if(!agent)return;agent.status=state==='running'?'working':'idle';agent.activity=state==='running'?'code':'cafe';if(ui.walkTo(agent.id,station,()=>ui.renderAgents()))ui.renderAgents();};
// Pratbubblor för faktiska Codex-sessioner. Texten är UI-tolkningar av logghändelser,
// aldrig fria påståenden om att en bugg har verifierats som löst.
window.pixelWorksLiveSpeech=(message,kind='info',agentId=null)=>{
  if(!model.project.live)return false;
  const agent=model.project.agents.find(a=>a.id===agentId)||(!agentId?model.project.agents.find(a=>a.provider==='codex'):null);
  if(!agent)return false;
  return ui.showAgentSpeech(agent,message,kind);
};
setInterval(()=>{if(!paused)model.tickEconomy(2/3600);studio.updateHUD();},2000);

window.__PIXEL_WORKS_DEMO__ = { model, ui, simulation };
