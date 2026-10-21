export const STATIONS = [
  { id: 'lead', type: 'lead', name: 'Projektledning', short: 'LEAD', color: '#ff78b7', x: 18, y: 43, skill: 'planning' },
  { id: 'code', type: 'code', name: 'Programmering', short: 'CODE', color: '#65e8d8', x: 42, y: 45, skill: 'coding' },
  { id: 'research', type: 'research', name: 'Forskning', short: 'R&D', color: '#ae83ff', x: 66, y: 43, skill: 'research' },
  { id: 'qa', type: 'qa', name: 'QA-labb', short: 'QA', color: '#ffd45e', x: 84, y: 60, skill: 'testing' },
  { id:'cafe', type:'cafe', name:'Stora fikabordet', short:'FIKA', color:'#d49d62', x:54, y:86, skill:null },
  { id: 'meeting', type: 'meeting', name: 'Mötesbord', short: 'SYNC', color: '#ff9f59', x: 60, y: 60, skill: 'review' },
  { id: 'docs', type: 'docs', name: 'Dokumentation', short: 'DOCS', color: '#70a8ff', x: 26, y: 73, skill: 'documentation' },
  { id:'music', type:'music', name:'Musikstudio', short:'MUSIC', color:'#ffa9c9', x:83, y:82, skill:'music' },
  { id:'voice', type:'voice', name:'Röststudio', short:'VOICE', color:'#f9b86a', x:39, y:68, skill:'voice' },
  { id:'art', type:'art', name:'Pixelverkstad', short:'ART', color:'#b8f16a', x:10, y:64, skill:'art' },
];

const commonProviders = {
  codex: { label: 'Codex', engineState: 'DEMO', quota: 'okänt' },
  claude: { label: 'Claude', engineState: 'DEMO', quota: 'okänt' },
  google: { label: 'Google', engineState: 'DEMO', quota: 'okänt' },
  microsoft: { label: 'Microsoft', engineState: 'DEMO', quota: 'okänt' },
};

export const PROJECTS = [
  {
    id: 'pixel-forge',
    title: 'Pixel Forge',
    goal: 'Bygg en spelbar AI-kontorsprototyp med tydlig feedback och charm.',
    leadId: 'nova',
    providers: commonProviders,
    agents: [
      { id:'nova', name:'Nova', initials:'NV', role:'Arbetsledare', provider:'codex', skills:{planning:5,review:4,documentation:3}, status:'working', station:'lead', x:18, y:49, focus:'Bryt ned huvudmålet, matcha uppdrag mot skills och stoppa vid oklar evidens.', color:'#ff78b7', hair:'#4b305b', currentTask:'pf-1' },
      { id:'byte', name:'Byte', initials:'BY', role:'Programmerare', provider:'codex', skills:{coding:5,testing:2,documentation:2}, status:'working', station:'code', x:42, y:51, focus:'Implementera den minsta spelbara vertikala skivan utan externa beroenden.', color:'#65e8d8', hair:'#26364f', currentTask:'pf-2' },
      { id:'iris', name:'Iris', initials:'IR', role:'Researcher', provider:'claude', skills:{research:5,review:3,planning:2}, status:'idle', station:'research', x:66, y:49, focus:'Kartlägg användarflöden och rapportera tydliga designfynd.', color:'#ae83ff', hair:'#50344f', currentTask:null },
      { id:'patch', name:'Patch', initials:'PT', role:'QA Engineer', provider:'google', skills:{testing:5,review:4,coding:2}, status:'working', station:'qa', x:84, y:66, focus:'Försök bryta interaktioner och markera reproducerbara fel.', color:'#ffd45e', hair:'#3e4054', currentTask:'pf-3' },
      { id:'quill', name:'Quill', initials:'QU', role:'Dokumentatör', provider:'microsoft', skills:{documentation:5,review:3,research:2}, status:'idle', station:'docs', x:26, y:79, focus:'Håll NOW/NEXT/LATER begripligt och skilj demo från verifierat.', color:'#70a8ff', hair:'#5b3d35', currentTask:null },
    ],
    tasks: [
      { id:'pf-1', title:'Polera management-loopen', details:'Säkerställ att uppdrag, stationer och feedback hänger ihop i en enda scen.', priority:'high', assignee:'nova', status:'working', requiredSkill:'planning' },
      { id:'pf-2', title:'Interaktiv agentflytt', details:'Dra agent till station och visa synlig beteendeförändring + event.', priority:'high', assignee:'byte', status:'working', requiredSkill:'coding' },
      { id:'pf-3', title:'Testa drag & drop', details:'Verifiera klick, drag, stationbyte och att state stannar inom projektet.', priority:'normal', assignee:'patch', status:'review', requiredSkill:'testing' },
      { id:'pf-4', title:'Designa findings-kort', details:'Gör evidensstatus begriplig utan att scenen blir en dashboard.', priority:'low', assignee:null, status:'todo', requiredSkill:'review' },
    ],
    seedEvents: [
      ['TASK_STARTED','Byte öppnade uppdraget “Interaktiv agentflytt”.','byte'],
      ['AGENT_MESSAGE','Nova → Patch: “Testa stationbyte först, kosmetik sen.”','nova'],
      ['FINDING_REPORTED','Iris: “Kontoret behöver vara visuellt viktigare än panelerna.”','iris'],
      ['TASK_ASSIGNED','Nova tilldelade Patch QA av drag & drop.','nova'],
    ]
  },
  {
    id: 'aurora-relay',
    title: 'Aurora Relay',
    goal: 'Simulera ett forskningsprojekt där fynd granskas innan de blir “verifierade”.',
    leadId: 'saga',
    providers: commonProviders,
    agents: [
      { id:'saga', name:'Saga', initials:'SG', role:'Arbetsledare', provider:'claude', skills:{planning:5,review:5,research:3}, status:'working', station:'lead', x:18, y:49, focus:'Prioritera falsifierbara deluppgifter och håll rapporterat ≠ verifierat.', color:'#ff78b7', hair:'#392f4c', currentTask:'ar-1' },
      { id:'flux', name:'Flux', initials:'FX', role:'Programmerare', provider:'codex', skills:{coding:5,testing:3,review:2}, status:'idle', station:'code', x:42, y:51, focus:'Bygg mock-adaptern och håll providergränsen tunn.', color:'#65e8d8', hair:'#293c50', currentTask:null },
      { id:'moss', name:'Moss', initials:'MS', role:'Researcher', provider:'google', skills:{research:5,documentation:3,review:3}, status:'working', station:'research', x:66, y:49, focus:'Samla tre konkurrerande hypoteser och markera osäkerhet.', color:'#ae83ff', hair:'#31483b', currentTask:'ar-2' },
      { id:'echo', name:'Echo', initials:'EC', role:'QA Engineer', provider:'microsoft', skills:{testing:5,review:5,documentation:2}, status:'blocked', station:'qa', x:84, y:66, focus:'Vänta på reproducerbart underlag innan verifiering.', color:'#ffd45e', hair:'#4b3b33', currentTask:'ar-3' },
      { id:'note', name:'Note', initials:'NT', role:'Dokumentatör', provider:'claude', skills:{documentation:5,research:3,planning:2}, status:'idle', station:'docs', x:26, y:79, focus:'Sammanfatta beslut med proveniens och status.', color:'#70a8ff', hair:'#553743', currentTask:null },
    ],
    tasks: [
      { id:'ar-1', title:'Definiera evidensgrind', details:'Beskriv vad som krävs för att ett fynd får status verifierat.', priority:'high', assignee:'saga', status:'working', requiredSkill:'review' },
      { id:'ar-2', title:'Kartlägg tre hypoteser', details:'Rapportera fynd med osäkerhet, källa och alternativ förklaring.', priority:'normal', assignee:'moss', status:'working', requiredSkill:'research' },
      { id:'ar-3', title:'Oberoende QA', details:'Blockerad tills reproducerbart underlag finns. Självpåstående räcker inte.', priority:'high', assignee:'echo', status:'todo', requiredSkill:'testing' },
    ],
    seedEvents: [
      ['TASK_STARTED','Moss började kartlägga hypoteser.','moss'],
      ['AGENT_MESSAGE','Echo → Saga: “Jag verifierar inte på enbart rapport.”','echo'],
      ['FINDING_REPORTED','Moss rapporterade ett preliminärt fynd (ej verifierat).','moss'],
      ['AGENT_IDLE','Flux väntar på ett nytt uppdrag.','flux'],
    ]
  }
];
