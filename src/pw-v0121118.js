/* Pixel Works v0.12.11.18: station-first UX. No automatic AI calls.
   All new orders use the existing authenticated /api/projects/<slug>/orders endpoint. */
(() => {
  'use strict';
  if (window.__PW18_DESKS__) return;
  window.__PW18_DESKS__ = true;
  const esc = v => String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const short = (name,icon,desc,subs) => ({name,icon,desc,subs:subs.map(x => typeof x==='string'?[x,'']:x)});
  const catalog = {
    art:{name:'Grafikstudio',icon:'🎨',help:'Bilder, figurer, föremål och animationer till spelet.',items:[
      short('Eget uppdrag','✍️','Beskriv precis vad du vill skapa.',[]),
      short('Karaktärer','🧑‍🎨','Spelare, NPC, fiender och hjälpredor.',[['Ny spelbar karaktär','Skapa utseendet till en spelbar figur.'],['Ny NPC eller hjälpreda','Skapa en komplett NPC-design med sprites och uttryck.'],['Djur eller fantasivarelse','Designa ett djur eller en fantasivarelse. Bestäm utseende och visuellt beteende efter spelarens beskrivning.'],['Fiende eller boss','Skapa grafik för en fiende eller boss.'],['Förbättra en befintlig karaktär','Uppdatera sprites och stil för en existerande figur.']]),
      short('Föremål','📦','Objekt, vapen, nycklar och föremål.',[['Lägg till nya objekt i spelet','Skapa grafik för nya objekt i spelet, med storlekar och användning.'],['Vapen och utrustning','Designa vapen eller annan utrustning.'],['Samlarföremål och belöningar','Skapa pickups, mynt och belöningar.'],['Interaktiva föremål','Designa föremål som går att öppna, flytta eller använda.'],['Möbler och inredning','Skapa möbler och dekorationer till spelets värld.'],['Ändra befintliga objekt','Förbättra tidigare grafiska objekt.']]),
      short('Miljö och bakgrund','🏞️','Banor, landskap, byggnader och natur.',[['Ny spelmiljö','Designa en ny spelmiljö med passande grafik.'],['Bakgrund och parallax','Skapa bakgrundslager och parallaxgrafik.'],['Byggnader och rum','Rita byggnader, rum och interiörer.'],['Natur och terräng','Skapa terräng, växter och naturdetaljer.'],['Karta eller nivåöversikt','Designa en karta för spelvärlden.']]),
      short('Animation','🏃','Rörelser, uttryck och visuell feedback.',[['Gång och löpning','Skapa animerade gång- och löpsprites.'],['Hopp och fall','Skapa hopprörelse och landning.'],['Interaktioner','Animera användning av föremål och knappar.'],['Figurens känslor','Skapa ansiktsuttryck och reaktioner.'],['Animerat föremål','Skapa bildrutor för ett rörligt föremål.']]),
      short('Gränssnitt','🖥️','HUD, menyer, knappar och indikatorer.',[['HUD och mätare','Förbättra information och mätare på skärmen.'],['Menyer och dialoger','Designa tydliga menyer och dialogrutor.'],['Inventarie och föremålsikoner','Skapa inventarievyer och ikoner.'],['Knappar och spelrespons','Förbättra interaktiva knappar och feedback.']]),
      short('Ikoner','✨','Små grafiska symboler.',[['Spelikoner','Skapa ikoner till spelet.'],['Kartikoner','Skapa kartmarkörer.'],['Föremålsikoner','Skapa inventarieikoner.']]),
      short('Visuella effekter','💥','Partiklar, väder och magi.',[['Explosion och rök','Skapa visuella effekter för explosioner och rök.'],['Väder och ljus','Skapa väder-, ljus- och partikeleffekter.'],['Magi och specialkrafter','Designa specialeffekter för förmågor.']]),
      short('Grafikproblem','🪲','Saknade bilder eller fel utseende.',[['Grafik saknas','Undersök varför grafik inte visas och åtgärda problemet.'],['Fel format eller storlek','Rätta upplösning, skalning eller transparens.'],['Stil passar inte spelet','Anpassa grafiken till Game Bible.']])
    ]},
    qa:{name:'Testning',icon:'🧪',help:'Speltester, felrapporter och kvalitetskontroll.',items:[
      short('Eget uppdrag','✍️','Beskriv ett eget test.',[]),
      short('Testa hela spelet','🎮','Kontrollera hela spelupplevelsen.',[['Spela från start till slut','Testa huvudflödet och dokumentera fel.'],['Testa alla menyer','Kontrollera att alla menyer och knappar fungerar.'],['Testa på olika skärmstorlekar','Testa gränssnitt och spel i olika storlekar.']]),
      short('Testa senaste funktion','🆕','Undersök nyligen ändrat innehåll.',[['Senaste kodändringarna','Testa funktioner som nyligen har införts.'],['Ny karaktär eller NPC','Testa rörelse, interaktioner och AI för nya figurer.'],['Nytt spelmoment','Kontrollera nya regler och spelmekanik.']]),
      short('Rapportera bugg','🐞','Hitta och dokumentera ett fel.',[['Grafik och visning','Reproducera ett fel i bilder, animation eller rendering.'],['Kontroller och rörelse','Reproducera fel i rörelser och styrning.'],['Ljud','Reproducera ett ljudfel.'],['Spelmekanik','Reproducera fel i spelregler eller logik.'],['Menyer och gränssnitt','Reproducera fel i menyer, formulär eller knappar.'],['Spara och ladda','Undersök problem med sparfiler och laddning.'],['Prestanda','Dokumentera hackningar, fördröjningar eller minnesproblem.'],['AI och NPC','Reproducera problem i NPC-beteende eller navigering.']]),
      short('Prestandatest','⚡','Hastighet, stabilitet och belastning.',[['Mät laddtid','Mät spelets laddning och föreslå förbättringar.'],['Långtidstest','Kontrollera att spelet fortsätter fungera efter längre användning.']]),
      short('Användartest','👥','Tydlighet och spelkänsla.',[['Förstagångsspelare','Undersök om spelet är lätt att förstå för en ny spelare.'],['Tillgänglighet','Kontrollera tangentbord, fokus och kontrast.']])
    ]},
    music:{name:'Musikstudio',icon:'🎵',help:'Skapa musik, bakgrundsljud och ljudeffekter.',items:[
      short('Eget uppdrag','✍️','Skriv ett eget ljuduppdrag.',[]),
      short('Bakgrundsmusik','🎶','Musik som kan loopas.',[['Musik till nivå','Skapa eller integrera bakgrundsmusik för en nivå.'],['Intromusik','Skapa musik till spelets start.'],['Segermusik','Skapa musik för belöning eller seger.'],['Menymusik','Skapa lugn musik till spelets menyer.']]),
      short('Effektljud','🔊','Ljud för handlingar.',[['Hopp och rörelse','Skapa rörelseljud för spelaren eller NPC.'],['Träffar och explosioner','Skapa ljud för effekter och strid.'],['Föremål och pickups','Skapa ljud när spelaren hittar eller använder ett föremål.'],['UI och knappar','Skapa knapp-, meny- och bekräftelseljud.'],['Djur- och varelse-ljud','Skapa eller integrera ljud för den beskrivna varelsen.']]),
      short('Miljöljud','🌿','Ljud som får spelvärlden att leva.',[['Natur','Skapa vind, fåglar eller vattenljud.'],['Stad och maskiner','Skapa mekaniska och urbana miljöljud.'],['Rum och atmosfär','Skapa atmosfärljud till en plats.']]),
      short('Förbättra ljud','🎛️','Justera befintliga ljud.',[['Volym och balans','Balansera ljudnivåer.'],['Loopar och övergångar','Skapa mjukare övergångar.'],['Ljud saknas','Undersök varför ljud inte spelas.']])
    ]},
    code:{name:'Programmering',icon:'💻',help:'Bygg och förändra spelets faktiska funktioner.',items:[
      short('Eget uppdrag','✍️','Beskriv vad programmeraren ska bygga.',[]),
      short('Ny funktion','🛠️','Implementera en funktion i spelet.',[['Ny spelmekanik','Implementera en ny spelmekanik.'],['NPC och hjälpreda','Implementera en NPC:s beteende, logik och rörelse.'],['Inventarie och föremål','Implementera användbara föremål och inventarie.'],['Nytt gränssnitt','Implementera en meny eller annan gränssnittsfunktion.']]),
      short('Fixa fel','🐛','Rätta ett känt problem.',[['Kraschar eller startar inte','Undersök varför spelet inte startar.'],['Fel i spelregler','Rätta fel i spelmekaniken.'],['Fel efter senaste ändring','Undersök en regression.']]),
      short('Förbättra befintligt','🔧','Utveckla kod som redan finns.',[['Spelstyrning','Förbättra rörelse och kontroller.'],['Prestanda','Förbättra prestanda och stabilitet.'],['Spara och ladda','Förbättra sparsystemet.'],['Testbarhet','Lägg till testbar struktur.']])
    ]},
    meeting:{name:'Mötesrum',icon:'🗣️',help:'Diskutera idéer och samordna arbete mellan flera yrken.',items:[
      short('Eget uppdrag','✍️','Skriv en egen mötesfråga.',[]),
      short('Ny spelidé','💡','Ta fram ett konkret spelkoncept.',[['Spelkoncept','Ta fram en konkret spelidé som passar Game Bible.'],['Ny värld','Föreslå en ny spelvärld med egna egenskaper.'],['Ny spelmekanik','Ta fram en tydlig spelmekanik.']]),
      short('Ny karaktär / NPC','🧑','Skapa en figur som kan behöva flera yrken.',[['NPC – hjälpreda','Föreslå en ny NPC som hjälper spelaren.'],['Djur eller varelse','Planera ett nytt djur eller en varelse. Ta med design, grafik, ljud, kod, testning och Game Bible utifrån beskrivningen.'],['Spelbar karaktär','Skapa förslag till en spelbar figur.'],['Fiende eller boss','Planera en fiende som behöver grafik, logik och ljud.']]),
      short('Planera flera arbetsbord','📋','Dela upp en idé i rätt arbetsordning.',[['Ny figur eller NPC','Bryt ned en ny figur i uppdrag för Grafik, Ljud, Programmering, Testning och Dokumentation.'],['Ny spelmekanik','Planera design, implementation, test och dokumentation.'],['Nytt spelområde','Planera grafik, ljud, kod och test för en ny miljö.']]),
      short('Sidouppdrag','🗺️','Designa ett nytt äventyr.',[['Nytt sidouppdrag','Skapa ett konkret sidouppdrag med karaktärer, mål och belöning.'],['Förbättra befintligt uppdrag','Bearbeta ett befintligt uppdrag.']]),
      short('Teamavstämning','🤝','Följ upp olika yrkesgrupper.',[['Status på spelprojektet','Gå igenom vad som är gjort och vad som återstår.'],['Hinder och beroenden','Identifiera hinder mellan arbetarna.']])
    ]},
    docs:{name:'Dokumentation',icon:'📖',help:'Håll Game Bible och projektets texter uppdaterade.',items:[
      short('Eget uppdrag','✍️','Skriv fritt.',[]),short('Game Bible','📚','Beslutade regler och vision.',[['Inför godkänd design','För in redan godkända beslut i rätt kapitel.'],['Uppdatera spelvärld','Utveckla godkänd information om världen.'],['Dokumentera karaktär','Sammanställ en beslutad karaktär med roller och relationer.']]),
      short('Spelinstruktioner','📝','Så spelar man.',[['Skriv instruktioner','Skriv tydliga spelinstruktioner.'],['Förbättra befintliga instruktioner','Förtydliga spelmanualen.']]),
      short('Ändringslogg','📋','Dokumentera riktiga ändringar.',[['Senaste ändringar','Dokumentera genomförda och verifierade ändringar.']])
    ]},
    research:{name:'Forskning',icon:'🔬',help:'Undersök alternativ och ge konkreta rekommendationer.',items:[
      short('Eget uppdrag','✍️','Skriv din forskningsfråga.',[]),short('Spelmekanik','🎮','Undersök regler och balans.',[['Spelbalans','Jämför alternativ för svårighetsgrad och spelbalans.'],['Spelarnas beteende','Analysera hur spelarna förväntas använda funktionen.']]),
      short('Referenser','🔎','Undersök projektunderlag.',[['Visuell inspiration','Analysera bifogade referensbilder utan att kopiera skyddat material.'],['Liknande mekaniker','Jämför mekaniker med befintliga spel.']]),
      short('Tekniska val','⚙️','Utvärdera alternativ.',[['Lösningsförslag','Undersök olika tekniska lösningar.'],['Risker','Kartlägg tekniska risker.']])
    ]},
    voice:{name:'Röststudio',icon:'🎙️',help:'Dialoger, röster och tal.',items:[
      short('Eget uppdrag','✍️','Skriv fritt.',[]),short('Karaktärsröst','🗣️','Ge en figur en röst.',[['NPC-dialog','Skriv eller integrera NPC-dialog.'],['Djur- och varelseröster','Skapa eller planera ljud för den beskrivna varelsen.'],['Spelbar figur','Skapa repliker eller röstplan för spelaren.']]),
      short('Berättarröst','📢','Läs upp speltext.',[['Introduktion','Skapa introberättande.'],['Uppdragsberättelse','Skapa röster och repliker till uppdrag.']]),
      short('Röstproblem','🪲','Felsök fel.',[['Röst saknas','Undersök varför dialog inte hörs.'],['Fel timing','Synkronisera tal och text.']])
    ]},
    lead:{name:'Arbetsledning',icon:'👔',help:'Planering och delegering.',items:[]}
  };
  const dialog=document.createElement('dialog');dialog.id='pw18Desk';dialog.setAttribute('aria-label','Arbetsstation – uppdrag');document.body.append(dialog);
  const styles=document.createElement('style');styles.textContent=`
  #pw18Desk{width:min(800px,calc(100vw - 26px));max-height:min(88dvh,800px);border:8px ridge #a56c4a;outline:3px solid #192c4b;box-shadow:9px 10px 0 #0d1626;padding:0;box-sizing:border-box;background:#faedf0;color:#23374c;font:14px/1.45 system-ui,sans-serif;overflow:auto}
  #pw18Desk::backdrop{background:rgba(6,16,32,.73)}
  #pw18Desk .pw18-paper{position:relative;min-height:430px;padding:18px 20px;box-sizing:border-box;background:linear-gradient(135deg,#fffbf1,#e8ecf8);isolation:isolate}
  #pw18Desk .pw18-paper::before{content:'';position:absolute;inset:0;z-index:-1;opacity:.35;pointer-events:none;background:repeating-linear-gradient(0deg,transparent 0 42px,rgba(142,123,148,.08) 43px 44px)}
  #pw18Desk .pw18-art{background:linear-gradient(rgba(255,249,252,.48),rgba(255,249,252,.72)),url('/assets/office-v2/graphics-studio-pastel.png') center 26%/cover no-repeat}
  #pw18Desk .pw18-art::before{opacity:.14}
  #pw18Desk .pw18-qa{background:linear-gradient(140deg,#f9f5ff,#e7f3f5)}
  #pw18Desk .pw18-music{background:linear-gradient(140deg,#fff6f1,#f5e5f4)}
  #pw18Desk .pw18-code{background:linear-gradient(140deg,#f1f8fc,#e5ebf6)}
  #pw18Desk .pw18-meeting{background:linear-gradient(140deg,#fff9e9,#e9edf8)}
  #pw18Desk .pw18-docs{background:linear-gradient(140deg,#fdf8e5,#ebf3e6)}
  #pw18Desk .pw18-research{background:linear-gradient(140deg,#f3f0fc,#e5f6f2)}
  #pw18Desk .pw18-voice{background:linear-gradient(140deg,#ffeff6,#edeffa)}
  #pw18Desk .pw18-head{display:flex;justify-content:space-between;gap:12px;align-items:start;border-bottom:3px solid #bd8c77;padding-bottom:10px;margin-bottom:12px}
  #pw18Desk h2{font-size:23px;color:#1a3552;margin:0;line-height:1.2}
  #pw18Desk .pw18-help{font-size:13px;margin:5px 0 0;color:#34485d}
  #pw18Desk button{cursor:pointer;font:inherit;min-height:42px;border:2px solid #b7a8a1;border-radius:4px;background:rgba(255,255,255,.84);color:#14314d;padding:8px 10px;font-weight:650}
  #pw18Desk button:focus-visible,#pw18Desk input:focus-visible,#pw18Desk textarea:focus-visible{outline:3px solid #3a73ac;outline-offset:2px}
  #pw18Desk .pw18-x{min-width:44px;background:#405773;color:white;border-color:#293c58}
  #pw18Desk .pw18-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:11px;margin:13px 0}
  #pw18Desk .pw18-tile{background:rgba(255,255,255,.86);display:flex;gap:8px;align-items:center;text-align:left;min-height:78px;box-shadow:0 2px 0 #d0c4b6}
  #pw18Desk .pw18-tile:first-child{background:rgba(255,223,144,.96);border-color:#b78635}
  #pw18Desk .pw18-ico{font-size:27px;min-width:33px;text-align:center}
  #pw18Desk .pw18-tile small{display:block;font-weight:400;font-size:11px;line-height:1.3;color:#465766}
  #pw18Desk .pw18-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;margin:13px 0}
  #pw18Desk .pw18-sub{text-align:left;min-height:58px;background:rgba(255,255,255,.88)}
  #pw18Desk .pw18-sub small{display:block;font-size:11px;color:#516276;font-weight:400}
  #pw18Desk .pw18-crumb{font-size:13px;color:#47617a;font-weight:700;margin:0 0 8px}
  #pw18Desk textarea{display:block;box-sizing:border-box;width:100%;min-height:104px;resize:vertical;padding:11px;background:rgba(255,255,255,.93);border:2px solid #8b99ad;color:#203247;border-radius:3px;font:inherit;font-size:15px}
  #pw18Desk .pw18-field{display:block;font-weight:700;margin:14px 0 5px}
  #pw18Desk .pw18-upload{border:2px dashed #879eae;text-align:center;display:block;background:rgba(255,255,255,.6);min-height:48px;padding:10px;box-sizing:border-box;cursor:pointer}
  #pw18Desk .pw18-ref-list{max-height:115px;overflow:auto;background:rgba(255,255,255,.75);padding:6px 10px;margin:6px 0}
  #pw18Desk .pw18-ref-list label{display:block;padding:5px;font-size:12px;overflow-wrap:anywhere}
  #pw18Desk .pw18-ref-list input{width:18px;height:18px;vertical-align:middle;margin-right:6px}
  #pw18Desk .pw18-priority{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:7px;margin:7px 0}
  #pw18Desk .pw18-priority input{position:absolute;opacity:0;width:1px;height:1px}
  #pw18Desk .pw18-priority label{border:2px solid #a1a9b5;border-radius:3px;background:rgba(255,255,255,.86);padding:8px;text-align:center;cursor:pointer;font-weight:700}
  #pw18Desk .pw18-priority label:has(input:checked){background:#f3d58a;border-color:#956b29}
  #pw18Desk .pw18-priority label:has(input:focus-visible){outline:3px solid #3a73ac}
  #pw18Desk .pw18-actions{border-top:2px solid #d2b89b;padding-top:12px;display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin-top:12px}
  #pw18Desk .pw18-primary{background:#e5b75e;border:2px solid #876239;color:#17273e}
  #pw18Desk .pw18-secondary{background:#526c87;color:white;border-color:#334b67}
  #pw18Desk .pw18-status{font-size:12px;min-height:18px;color:#864333;white-space:pre-wrap}
  #pw18Desk .pw18-muted{color:#42566a;font-size:12px}
  #pw18Desk .pw18-preview{border:2px solid #c2af99;background:rgba(255,255,255,.88);padding:12px;margin:10px 0}
  #pw18Desk .pw18-preview li{margin:8px 0}
  @media(max-width:650px){#pw18Desk .pw18-paper{padding:12px}#pw18Desk .pw18-grid,#pw18Desk .pw18-list{grid-template-columns:repeat(2,minmax(0,1fr))}#pw18Desk h2{font-size:20px}#pw18Desk .pw18-tile{min-height:68px}#pw18Desk .pw18-ico{font-size:21px}}
  @media(max-width:420px){#pw18Desk .pw18-grid,#pw18Desk .pw18-list{grid-template-columns:1fr}#pw18Desk .pw18-tile{min-height:55px}}
  `;document.head.append(styles);
  styles.textContent += `
  /* v0.13.7 — one coherent, pastel illustrated desk system. */
  #pw18Desk{width:min(830px,calc(100vw - 22px));max-height:min(90dvh,880px);border:7px ridge #b07d56;border-radius:5px;outline:3px solid #18354e;box-shadow:8px 10px 0 #0d1b2a;}
  #pw18Desk .pw18-paper{--pw-accent:#b8a4d2;--pw-accent-dark:#59718b;min-height:0;padding:21px 24px 18px;background-color:#f9f7f2;background-size:cover;background-position:center;background-repeat:no-repeat;}
  #pw18Desk .pw18-paper::before{opacity:.07}
  #pw18Desk .pw18-art{--pw-accent:#dc9dc2;--pw-accent-dark:#894b86;background-image:linear-gradient(115deg,rgba(255,250,252,.78),rgba(255,249,252,.73)),url('/assets/office-v2/graphics-studio-pastel.png')}
  #pw18Desk .pw18-qa{--pw-accent:#9bbccf;--pw-accent-dark:#377084;background-image:linear-gradient(110deg,rgba(247,252,255,.79),rgba(238,248,252,.81)),url('/assets/office-v2/testing-studio-pastel.png')}
  #pw18Desk .pw18-music{--pw-accent:#c6a0dc;--pw-accent-dark:#7d4d98;background-image:linear-gradient(115deg,rgba(255,247,253,.75),rgba(252,240,255,.81)),url('/assets/office-v2/music-studio-pastel.png')}
  #pw18Desk .pw18-code{--pw-accent:#9fc5e2;--pw-accent-dark:#34678d;background-image:linear-gradient(115deg,rgba(245,251,255,.79),rgba(240,248,255,.82)),url('/assets/office-v2/programming-studio-pastel.png')}
  #pw18Desk .pw18-meeting{--pw-accent:#e7bf91;--pw-accent-dark:#956637;background-image:linear-gradient(115deg,rgba(255,250,243,.78),rgba(255,247,230,.85)),url('/assets/office-v2/meeting-studio-pastel.png')}
  #pw18Desk .pw18-docs{--pw-accent:#bdd6a0;--pw-accent-dark:#598064;background-image:linear-gradient(115deg,rgba(250,255,246,.78),rgba(245,252,238,.84)),url('/assets/office-v2/documentation-studio-pastel.png')}
  #pw18Desk .pw18-research{--pw-accent:#98d3be;--pw-accent-dark:#337969;background-image:linear-gradient(115deg,rgba(244,255,252,.77),rgba(238,250,250,.84)),url('/assets/office-v2/research-studio-pastel.png')}
  #pw18Desk .pw18-voice{--pw-accent:#d9a7c4;--pw-accent-dark:#8a4c72;background-image:linear-gradient(115deg,rgba(255,249,251,.76),rgba(251,241,251,.84)),url('/assets/office-v2/voice-studio-pastel.png')}
  #pw18Desk .pw18-head{align-items:center;border-bottom:3px solid var(--pw-accent);border-radius:4px 4px 0 0;background:rgba(255,255,255,.73);padding:10px 12px 11px;margin:-8px -10px 14px;gap:18px;}
  #pw18Desk h2{font-size:24px;letter-spacing:-.02em;line-height:1.25}
  #pw18Desk .pw18-stage{display:inline-block;background:color-mix(in srgb,var(--pw-accent),white 55%);color:#234058;border:1px solid var(--pw-accent);font-size:11px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;padding:3px 7px;border-radius:5px;margin-top:5px}
  #pw18Desk .pw18-help{margin:6px 0 0;line-height:1.4;font-size:12px;color:#405166}
  #pw18Desk .pw18-help strong{font-weight:600;opacity:.85}
  #pw18Desk .pw18-x{flex:0 0 43px;min-height:43px}
  #pw18Desk .pw18-grid{gap:10px;margin:11px 0 17px}
  #pw18Desk .pw18-tile,#pw18Desk .pw18-sub{border:2px solid color-mix(in srgb,var(--pw-accent),#adb8c1 55%);background:rgba(255,255,255,.87);box-shadow:2px 3px 0 rgba(43,58,75,.13);transition:transform .12s ease,box-shadow .12s ease,border-color .12s ease}
  #pw18Desk .pw18-tile{min-height:82px;padding:11px 10px}
  #pw18Desk .pw18-tile:first-child{background:rgba(255,231,171,.97);border-color:#b78b3f}
  #pw18Desk .pw18-tile:hover,#pw18Desk .pw18-sub:hover{transform:translateY(-2px);box-shadow:3px 5px 0 rgba(43,58,75,.15);border-color:var(--pw-accent-dark);background:rgba(255,255,255,.96)}
  #pw18Desk .pw18-tile:first-child:hover{background:#ffe7ac}
  #pw18Desk .pw18-ico{font-size:30px;min-width:40px;line-height:1.1}
  #pw18Desk .pw18-tile strong{display:block;font-size:14px;line-height:1.3}
  #pw18Desk .pw18-tile small{margin-top:3px;font-size:11px;line-height:1.35}
  #pw18Desk .pw18-sub{display:flex;align-items:center;gap:9px;min-height:69px;padding:9px 11px}
  #pw18Desk .pw18-sub-icon{font-size:24px;flex:0 0 32px;text-align:center}
  #pw18Desk .pw18-sub-copy{display:block;min-width:0}
  #pw18Desk .pw18-sub strong{display:block;font-size:13px;line-height:1.4}
  #pw18Desk .pw18-sub small{font-size:11px;line-height:1.35}
  #pw18Desk .pw18-crumb{display:flex;align-items:center;gap:8px;padding:8px 10px;margin:5px 0 11px;border-left:4px solid var(--pw-accent-dark);background:rgba(255,255,255,.76);border-radius:4px}
  #pw18Desk .pw18-preview,#pw18Desk .pw18-ref-list{background:rgba(255,255,255,.90)}
  #pw18Desk textarea{background:rgba(255,255,255,.96);min-height:125px;border-color:#91a6b9}
  #pw18Desk .pw18-priority label{min-height:42px;display:flex;align-items:center;justify-content:center;padding:7px 8px}
  #pw18Desk .pw18-priority label:has(input:checked){background:#ffdda0;color:#263247}
  #pw18Desk .pw18-actions{border-color:var(--pw-accent);background:rgba(255,255,255,.58);padding:12px 10px 0;margin:13px -10px -3px}
  #pw18Desk .pw18-muted{background:rgba(255,255,255,.58);display:table;padding:3px 5px;border-radius:3px;line-height:1.4}
  #pw18Desk .pw18-upload{background:rgba(255,255,255,.82)}
  #pw18Desk .pw18-paper button:disabled{opacity:.55;cursor:not-allowed}
  @media(max-width:680px){#pw18Desk .pw18-paper{padding:14px}#pw18Desk .pw18-head{margin:-3px -3px 10px;padding:9px}#pw18Desk .pw18-grid{grid-template-columns:repeat(2,minmax(0,1fr))}#pw18Desk .pw18-tile{min-height:72px}#pw18Desk h2{font-size:21px}}
  @media(max-width:410px){#pw18Desk .pw18-grid,#pw18Desk .pw18-list{grid-template-columns:1fr}#pw18Desk .pw18-tile{min-height:59px}#pw18Desk .pw18-priority{grid-template-columns:repeat(3,minmax(0,1fr))}}
  @media(prefers-reduced-motion:reduce){#pw18Desk .pw18-tile,#pw18Desk .pw18-sub{transition:none}#pw18Desk .pw18-tile:hover,#pw18Desk .pw18-sub:hover{transform:none}}

  /* The manager's desk is still the older local-studio builder; theme it without
     replacing its scheduler actions, queues or consent controls. */
  #localStudioDialog:has(.station-task-grid){width:min(825px,calc(100vw - 22px));height:min(580px,calc(100dvh - 20px));background:linear-gradient(105deg,rgba(253,248,237,.88),rgba(247,250,254,.90)),url('/assets/office-v2/leadership-studio-pastel.png') center/cover no-repeat;color:#1f3649;border:7px ridge #b17e56;outline:3px solid #16344e;box-shadow:8px 10px 0 #14283a;padding:16px 20px}
  #localStudioDialog:has(.station-task-grid) .local-shell-header{border-bottom:3px solid #e4bb83;padding:3px 2px 9px}
  #localStudioDialog:has(.station-task-grid) .local-shell-header h2{color:#243b51;font-size:0}
  #localStudioDialog:has(.station-task-grid) .local-shell-header h2::after{content:'👔 Arbetsledning';font-size:22px;font-weight:850;line-height:1.2}
  #localStudioDialog:has(.station-task-grid) .local-shell-info{display:none}
  #localStudioDialog:has(.station-task-grid) .pw17-context{background:rgba(255,255,255,.72);color:#32495b;border-color:#9dc0bf;font-size:11px}
  #localStudioDialog:has(.station-task-grid) .local-shell-header button{background:#4c6886;color:white;border:2px solid #294967;min-height:40px}
  #localStudioDialog:has(.station-task-grid) .station-builder-top h3{color:#31556a;font-size:17px}
  #localStudioDialog:has(.station-task-grid) .local-shell-body{color:#243b50}
  #localStudioDialog:has(.station-task-grid) .station-task-grid{grid-template-columns:repeat(3,minmax(0,1fr));grid-auto-rows:minmax(66px,auto)}
  #localStudioDialog:has(.station-task-grid) .station-task-tile{background:rgba(255,255,255,.89);color:#203c54;border:2px solid #b2c0c7;border-radius:4px;box-shadow:2px 3px 0 rgba(42,60,70,.16);font-size:12px;min-height:65px}
  #localStudioDialog:has(.station-task-grid) .station-task-tile:hover{background:#fff0ce!important;border-color:#bd904b!important}
  #localStudioDialog:has(.station-task-grid) .local-actions{border-color:#dbb78e;background:rgba(255,255,255,.64);padding:8px}
  #localStudioDialog:has(.station-task-grid) .local-actions button{background:#fff3db;color:#294359;border:2px solid #ac916d}
  #localStudioDialog:has(.station-task-grid) .local-actions button.alt{background:#506d88;color:#fff;border-color:#2d4c67}
  #pw13Dialog .pw13-shell{background:linear-gradient(112deg,rgba(255,250,238,.93),rgba(234,245,246,.94)),url('/assets/office-v2/leadership-studio-pastel.png') center/cover no-repeat}
  @media(max-width:620px){#localStudioDialog:has(.station-task-grid){padding:10px;height:min(610px,calc(100dvh - 14px))}#localStudioDialog:has(.station-task-grid) .station-task-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}

`;
  let state=null,renderBusy=false;
  const active=()=>window.__PIXEL_WORKS_DEMO__?.model?.activeProjectId||document.querySelector('#projectSelect')?.value;
  function assertProject(){if(!state||state.slug!==active())throw Error('Du har bytt spel. Inga arbetsordrar skapades. Öppna skrivbordet på nytt.');}
  function api(path,data){if(typeof window.pixelWorksApi!=='function')throw Error('Studioanslutningen saknas.');return window.pixelWorksApi(path,data);}
  function header(stage){const d=catalog[state.station];return `<div class="pw18-head"><div><h2>${d.icon} ${esc(d.name)}</h2><span class="pw18-stage">${esc(stage)}</span><p class="pw18-help">${esc(d.help)} <strong> · ${esc(state.slug)}</strong></p></div><button type="button" class="pw18-x" data-go="close" aria-label="Stäng">✕</button></div>`}
  function shell(stage,content){if(!state||renderBusy)return;const d=catalog[state.station];dialog.innerHTML=`<div class="pw18-paper pw18-${esc(state.station)}">${header(stage)}${content}</div>`;if(!dialog.open)dialog.showModal();}
  function actions(backText='◀ Tillbaka',back='back'){return `<div class="pw18-actions"><button type="button" data-go="${back}" class="pw18-secondary">${backText}</button><button type="button" data-go="queue">📚 Arbetskö</button><span class="pw18-status" role="status" id="pw18Status"></span></div>`}
  function goCategories(){state.page='main';state.category=null;state.sub=null;const d=catalog[state.station];shell('Välj uppdrag',`<p class="pw18-muted">Välj en enkel kategori. <strong>Eget uppdrag</strong> är alltid först.</p><div class="pw18-grid">${d.items.map((it,i)=>`<button type="button" class="pw18-tile" data-cat="${i}"><span class="pw18-ico">${it.icon}</span><span><strong>${esc(it.name)}</strong><small>${esc(it.desc)}</small></span></button>`).join('')}</div>${actions('Stäng','close')}`)}
  function goSub(){state.page='sub';const d=catalog[state.station],cat=d.items[state.category];shell('Välj underkategori',`<p class="pw18-crumb">${cat.icon} ${esc(cat.name)}</p><p class="pw18-muted">${esc(cat.desc)} · välj vad du vill göra.</p><div class="pw18-list">${cat.subs.map((sub,i)=>`<button type="button" class="pw18-sub" data-sub="${i}"><span class="pw18-sub-icon" aria-hidden="true">${cat.icon}</span><span class="pw18-sub-copy"><strong>${esc(sub[0])}</strong><small>${esc(sub[1])}</small></span></button>`).join('')}<button class="pw18-sub" data-sub="other"><span class="pw18-sub-icon" aria-hidden="true">✍️</span><span class="pw18-sub-copy"><strong>Annat inom ${esc(cat.name)}</strong><small>Skriv själv vad som ska göras.</small></span></button></div>${actions()}`)}
  function planPreview(){const desc=state.description.trim();const topic=desc||'den valda idén';state.page='plan';const tasks=[['Grafikstudio',`Ta fram sprites, uttryck och animationsskisser för ${topic}.`],['Musikstudio',`Planera ljud till ${topic}, inklusive rörelse och interaktion.`],['Programmering',`Implementera spelmekanik, rörelse och beteende för ${topic} efter att relevant design är godkänd.`],['Testning',`Testa att ${topic} fungerar efter implementationen.`],['Dokumentation',`För in godkända beslut om ${topic} i Game Bible.`]];state.preview=tasks;shell('Arbetsplan (förhandsgranskning)',`<p>👔 En möjlig arbetsordning. <b>Detta är ett lokalt förslag, inte en AI-genererad plan.</b></p><ol class="pw18-preview">${tasks.map(([name,task])=>`<li><b>${esc(name)}</b> · ${esc(task)}</li>`).join('')}</ol><p class="pw18-muted">Uppdragen skapas inte automatiskt här: de senare stegen behöver riktiga beroenden och granskningar, annars skulle Chefen kunna börja med programmering innan grafiken är beslutad. Välj ”Lägg i arbetskö” för ett gemensamt planeringsuppdrag på mötesbordet.</p><div class="pw18-actions"><button data-go="details" class="pw18-secondary">◀ Redigera idén</button><button data-go="submit" class="pw18-primary">📄 Lägg planeringsuppdrag i arbetskö</button><span class="pw18-status" id="pw18Status" role="status"></span></div>`)}
  function goDetails(){state.page='details';const c=catalog[state.station].items[state.category],sub=state.sub||c.name;let defaults='';if(c.subs.length){const match=c.subs.find(s=>s[0]===sub);defaults=match?.[1]||'';}const desc=state.description||defaults;const refs=state.assets||[];shell('Beskriv uppdrag',`<p class="pw18-crumb">${c.icon} ${esc(c.name)} › ${esc(sub)}</p><label for="pw18Description" class="pw18-field">Vad vill du att medarbetaren ska göra?</label><textarea id="pw18Description" maxlength="4000" placeholder="Beskriv vad du vill skapa, ändra eller testa…">${esc(desc)}</textarea><label class="pw18-field">📎 Referenser (valfritt)</label><label class="pw18-upload" tabindex="0">Släpp bilder eller filer här, eller klicka för att välja <input id="pw18Upload" type="file" multiple accept="image/*,audio/*,.pdf,.txt,.md,.json,.webm,.mp4" style="position:absolute;width:1px;height:1px;opacity:0"></label><div class="pw18-muted" id="pw18Pending">${state.files.length?esc(state.files.map(x=>x.name).join(', ')):'Inga nya filer valda.'}</div><details><summary>Befintliga projektbilder och referenser (${refs.length})</summary><div class="pw18-ref-list">${refs.map(a=>`<label><input type="checkbox" data-ref="${esc(a.id)}" ${state.refs.has(a.id)?'checked':''}>${esc(a.name||'Referens')}</label>`).join('')||'Inga sparade referenser.'}</div></details><label class="pw18-field">Prioritet</label><div class="pw18-priority" role="group" aria-label="Välj prioritet">${[[3,'🟢 Låg'],[2,'🟡 Normal'],[1,'🔴 Hög']].map(([v,t])=>`<label><input type="radio" name="pw18Priority" value="${v}" ${state.priority===v?'checked':''}>${t}</label>`).join('')}</div><p class="pw18-muted">Arbetet hamnar i projektets arbetskö och hanteras av Chefen. Inga AI-anrop sker när du öppnar detta fönster.</p><div class="pw18-actions"><button type="button" data-go="back" class="pw18-secondary">◀ Tillbaka</button>${state.station==='meeting'?'<button type="button" data-go="plan">👔 Visa möjlig arbetsplan</button>':''}<button type="button" data-go="submit" class="pw18-primary">📄 Lägg i arbetskö</button><span class="pw18-status" role="status" id="pw18Status"></span></div>`);const ta=dialog.querySelector('#pw18Description');ta.addEventListener('input',()=>{state.description=ta.value;});dialog.querySelectorAll('[name=pw18Priority]').forEach(x=>x.addEventListener('change',()=>{state.priority=Number(x.value)}));dialog.querySelectorAll('[data-ref]').forEach(x=>x.addEventListener('change',()=>{if(x.checked)state.refs.add(x.dataset.ref);else state.refs.delete(x.dataset.ref)}));const picker=dialog.querySelector('#pw18Upload');picker.addEventListener('change',()=>addFiles(picker.files));const zone=dialog.querySelector('.pw18-upload');zone.addEventListener('dragover',e=>{e.preventDefault()});zone.addEventListener('drop',e=>{e.preventDefault();addFiles(e.dataTransfer.files)});}
  function pasteFiles(e){if(state?.page!=='details')return;const files=[...e.clipboardData?.files||[]].filter(f=>f.type.startsWith('image/'));if(files.length){e.preventDefault();addFiles(files)}}
  function addFiles(files){if(!state)return;for(const file of files){if(file.size>4*1024*1024){message('Högst 4 MB per fil: '+file.name);continue;}if(state.files.length>=10){message('Högst 10 bilagor i ett uppdrag.');break;}state.files.push(file)}const label=dialog.querySelector('#pw18Pending');if(label)label.textContent=state.files.map(f=>f.name).join(', ')||'Inga nya filer valda.';}
  function message(text){const el=dialog.querySelector('#pw18Status');if(el)el.textContent=text;}
  async function uploadFile(slug,station,file,comment){const data=await new Promise((resolve,reject)=>{const fr=new FileReader();fr.onload=()=>resolve(String(fr.result).split(',')[1]);fr.onerror=()=>reject(Error('Kunde inte läsa fil'));fr.readAsDataURL(file)});const res=await api('/api/projects/'+encodeURIComponent(slug)+'/assets',{kind:'file',name:file.name,station,comment,data});return res.asset.id;}
  async function submit(){if(!state||renderBusy)return;try{assertProject();let instruction=state.description.trim();if(instruction.length<10)throw Error('Beskriv uppdraget med minst 10 tecken.');if(state.page==='plan')instruction='Ta fram en prioriterad arbetsplan för följande idé. Dela upp arbetet mellan Grafikstudio, Musikstudio, Programmering, Testning och Dokumentation. Ange ordning, beroenden, granskningspunkter och konkret leverans per uppdrag. Skapa inga automatiska arbetsorder utan spelägarens granskning.\n\nIdé: '+instruction;const buttons=[...dialog.querySelectorAll('button')];renderBusy=true;buttons.forEach(b=>b.disabled=true);message('Sparar arbetsordern…');const ids=[...state.refs];for(const f of state.files){assertProject();ids.push(await uploadFile(state.slug,state.station,f,instruction.slice(0,600)))}assertProject();await api('/api/projects/'+encodeURIComponent(state.slug)+'/orders',{action:'create',station:state.station,instruction,priority:state.priority,attachment_ids:ids});window.pixelWorksRefreshOrders?.(state.slug);renderBusy=false;state.files=[];state.refs.clear();shell('Sparat',`<div class="pw18-preview"><h3>✅ Arbetsordern är sparad</h3><p>Chefen kan nu fördela uppdraget i <b>${esc(state.slug)}</b>. En arbetsplan från mötet måste granskas innan arbetsorder för andra stationer skapas.</p></div><div class="pw18-actions"><button data-go="main" class="pw18-primary">➕ Nytt uppdrag</button><button data-go="queue">📚 Visa arbetskö</button><button data-go="close" class="pw18-secondary">Stäng</button></div>`);}catch(e){renderBusy=false;dialog.querySelectorAll('button').forEach(b=>b.disabled=false);message('⚠ '+e.message);}}
  async function open(slug,station){if(!catalog[station]||station==='lead')return;const current=active();if(slug!==current)return;state={slug,station,page:'main',category:null,sub:null,description:'',assets:[],files:[],refs:new Set(),priority:2,preview:[]};goCategories();try{const r=await api('/api/projects/'+encodeURIComponent(slug)+'/assets');if(state?.slug===slug&&state.station===station)state.assets=(r.assets||[]).filter(a=>a.station===station||a.station==='all'||a.status==='approved');}catch(_){/* Upload still works; existing references are optional. */}}
  function close(){dialog.close();state=null;}
  async function queue(){if(!state)return;const {slug,station}=state;dialog.close();state=null;const previous=window.__PW18_OLD_QUEUE__;if(typeof previous==='function')await previous(slug,station,false,true);}
  dialog.addEventListener('click',e=>{const btn=e.target.closest('button[data-go],button[data-cat],button[data-sub]');if(!btn)return;e.preventDefault();if(renderBusy)return;if(btn.dataset.cat!==undefined){state.category=Number(btn.dataset.cat);state.sub=null;state.description='';if(state.category===0){state.sub='Eget uppdrag';goDetails();}else goSub();return;}if(btn.dataset.sub!==undefined){const c=catalog[state.station].items[state.category];state.sub=btn.dataset.sub==='other'?'Eget val':c.subs[Number(btn.dataset.sub)][0];state.description=btn.dataset.sub==='other'?'':c.subs[Number(btn.dataset.sub)][1];goDetails();return;}const action=btn.dataset.go;if(action==='close')close();else if(action==='main')goCategories();else if(action==='back'){if(state.page==='details'){if(state.category===0)goCategories();else goSub();}else goCategories();}else if(action==='details')goDetails();else if(action==='plan')planPreview();else if(action==='submit')submit();else if(action==='queue')queue();});
  dialog.addEventListener('paste',pasteFiles);
  dialog.addEventListener('cancel',()=>{state=null});
  window.__PW18_OLD_QUEUE__=window.pixelWorksStationOrders;
  if(typeof window.__PW18_OLD_QUEUE__==='function')window.pixelWorksStationOrders=(slug,station,placed=false,openQueue=false)=>{if(placed||openQueue||!catalog[station]||station==='lead')return window.__PW18_OLD_QUEUE__(slug,station,placed,openQueue);return open(slug,station);};
  // The original office click handlers close over an older function and cannot
  // see the new exported renderer. Intercept *only* real station-clicks.
  document.addEventListener('click',event=>{if(!document.body.classList.contains('live-project')||event.defaultPrevented)return;const node=event.target.closest?.('#stationLayer .station');if(!node)return;const station=node.dataset.id;if(!catalog[station]||station==='lead'||event.target.closest('.station-order-badge,.pw17-tooltip'))return;const slug=active();if(!slug)return;event.preventDefault();event.stopImmediatePropagation();open(slug,station);},true);
  document.addEventListener('keydown',event=>{if(!document.body.classList.contains('live-project')||!['Enter',' '].includes(event.key))return;const stationEl=event.target.closest?.('#stationLayer .station');if(!stationEl||!catalog[stationEl.dataset.id]||stationEl.dataset.id==='lead')return;event.preventDefault();event.stopImmediatePropagation();open(active(),stationEl.dataset.id);},true);
  window.addEventListener('pixelworks:project-changed',()=>{if(state&&state.slug!==active())close()});
})();

/* v0.13.8: REAL cafe discussion. Every visible employee reply is persisted from
   their own AI request, never prewritten or simulated. Clicking a topic is the
   one user action; subsequent messages are read-only session polling. */
(()=>{
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const choices=[
    {id:'talk',icon:'💬',name:'Prata om spelet',hint:'Vad kan bli roligare eller tydligare?'},
    {id:'ideas',icon:'✨',name:'Kom på idéer',hint:'Bolla små förbättringar tillsammans.'},
    {id:'test',icon:'🧪',name:'Har vi testat ordentligt?',hint:'Diskutera luckor och ge testaren ett uppdrag.'},
    {id:'research',icon:'🔎',name:'Undersök en fråga',hint:'Fakta och inspiration – bara med verkliga källor.'},
    {id:'other',icon:'✏️',name:'Eget samtalsämne',hint:'Skriv själv vad kollegorna ska prata om.'}
  ];
  const box=document.createElement('dialog');box.id='pw138Cafe';document.body.append(box);
  const style=document.createElement('style');style.textContent=`
  #pw138Cafe{box-sizing:border-box;width:min(800px,calc(100vw - 18px));max-height:90dvh;overflow:auto;color:#233b48;font:14px/1.4 system-ui,sans-serif;border:7px ridge #b78d67;border-radius:6px;outline:3px solid #183b50;padding:0;box-shadow:8px 10px 0 #0f2c40}
  #pw138Cafe::backdrop{background:rgba(5,21,35,.72)}
  #pw138Cafe .pw138-sheet{padding:20px;background:linear-gradient(110deg,rgba(255,249,238,.94),rgba(245,250,246,.94)),url('/assets/office-v2/meeting-studio-pastel.png') center/cover no-repeat;min-height:320px}
  #pw138Cafe .pw138-head{display:flex;justify-content:space-between;align-items:start;gap:10px;border-bottom:3px solid #d1b18c;padding-bottom:12px}
  #pw138Cafe h2{font-size:26px;color:#2e5960;margin:0 0 4px}
  #pw138Cafe h3{margin:14px 0 7px;font-size:16px;color:#294b55}
  #pw138Cafe .pw138-muted{color:#486472;font-size:12px;line-height:1.4}
  #pw138Cafe button{border:2px solid #97aea9;background:rgba(255,255,255,.94);color:#23465e;border-radius:4px;padding:10px 12px;cursor:pointer;min-height:44px;font:700 13px system-ui,sans-serif}
  #pw138Cafe button:hover{background:#fff0c7;border-color:#b78a5c}
  #pw138Cafe button:focus-visible,#pw138Cafe textarea:focus-visible{outline:3px solid #147cad;outline-offset:2px}
  #pw138Cafe button:disabled{opacity:.57;cursor:progress}
  #pw138Cafe .pw138-exit{color:white;background:#526f89;border-color:#27455d;font-size:18px}
  #pw138Cafe .pw138-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;margin:16px 0}
  #pw138Cafe .pw138-choice{text-align:left;display:flex;align-items:center;gap:12px;min-height:81px;box-shadow:2px 3px 0 rgba(25,63,70,.16)}
  #pw138Cafe .pw138-choice strong{display:block;font-size:14px}
  #pw138Cafe .pw138-choice small{font-size:11px;font-weight:400;display:block;color:#46616e;margin-top:3px}
  #pw138Cafe .pw138-choice .pw138-icon{font-size:28px;flex:0 0 35px;text-align:center}
  #pw138Cafe textarea{box-sizing:border-box;width:100%;border:2px solid #97afa8;border-radius:4px;padding:10px;resize:vertical;min-height:78px;max-height:180px;font:14px system-ui,sans-serif;color:#273f4b;background:rgba(255,255,255,.96)}
  #pw138Cafe .pw138-controls{display:flex;flex-wrap:wrap;align-items:center;gap:9px;margin-top:16px;padding-top:12px;border-top:2px solid #d4b99a}
  #pw138Cafe .pw138-state{padding:10px 12px;border:2px solid #d7ba8b;background:rgba(255,252,238,.94);font-size:13px;margin:12px 0}
  #pw138Cafe .pw138-speech{position:relative;border:2px solid #a8b9af;border-radius:8px;background:rgba(255,255,255,.94);padding:12px 14px;margin:10px 0;box-shadow:2px 3px 0 rgba(32,62,78,.1)}
  #pw138Cafe .pw138-speech:nth-child(even){margin-left:25px;background:#edfbf7}
  #pw138Cafe .pw138-speech.pw139-owner{background:#fff0d4;border-color:#e4b05e;margin-left:35px}
  #pw138Cafe .pw139-owner strong{color:#78502a}
  #pw138Cafe .pw139-toolbar{display:flex;align-items:center;gap:6px;flex-wrap:wrap;padding-top:8px;border-top:1px solid #dbe7e4}
  #pw138Cafe .pw139-toolbar button{min-height:31px;padding:4px 9px;font-size:12px}
  #pw138Cafe .pw139-toolbar button[aria-pressed=true]{background:#d7edd8;border-color:#378a70}
  #pw138Cafe .pw139-implement{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:10px;background:#fff7e7;border:1px solid #bda076;margin-top:9px}
  #pw138Cafe .pw139-implement select{border:2px solid #9aac9c;border-radius:4px;padding:9px;background:#fff;max-width:245px;color:#233b48}
  #pw138Cafe .pw139-compose{margin-top:16px;padding:13px;background:rgba(229,245,240,.95);border:2px solid #9abeb0;border-radius:8px}
  #pw138Cafe .pw139-compose textarea{min-height:75px}
  #pw138Cafe .pw139-compose-actions{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-top:8px}
  #pw138Cafe .pw139-primary{background:#236d81;color:#fff;border-color:#184c5c}
  #pw138Cafe .pw139-feedback{color:#2b6550;font-size:12px;margin-top:8px}
  #pw138Cafe .pw138-speech strong{color:#1e6677}
  #pw138Cafe .pw138-speech p{white-space:pre-wrap;overflow-wrap:anywhere;margin:6px 0;font-size:14px}
  #pw138Cafe .pw138-evidence{font-size:11px;color:#406d58;font-weight:700}
  #pw138Cafe .pw138-error{color:#923c3c;background:#ffece5;border:1px solid #dd9990;padding:10px;white-space:pre-wrap;overflow-wrap:anywhere}
  #pw138Cafe .pw138-tag{display:inline-block;border:1px solid #b7c0ac;border-radius:5px;padding:3px 9px;margin:4px 4px 0 0;background:#fffef7;color:#46626b;font-size:12px}
  #pw138Cafe .pw138-orders{border:1px solid #a8bcaa;padding:9px;background:#edf8ee}
  #pw138Cafe .pw138-history{margin-top:12px;font-size:12px}
  #pw138Cafe .pw138-history button{font-size:12px;min-height:32px;margin:3px}
  #pw138Cafe .pw138-live{display:flex;gap:8px;align-items:center}
  #pw138Cafe .pw138-dot{width:11px;height:11px;border-radius:50%;background:#34a37c;animation:pw138Pulse 1.5s infinite}
  @keyframes pw138Pulse{50%{opacity:.35}}
  @media(max-width:620px){#pw138Cafe .pw138-sheet{padding:13px}#pw138Cafe .pw138-grid{grid-template-columns:1fr}#pw138Cafe h2{font-size:21px}#pw138Cafe .pw138-speech:nth-child(even){margin-left:8px}}
  `;document.head.append(style);
  let session=null,slug=null,history=[],note='',pending=false,timer=null,request=null,loadId=0;
  let ownerDraft='',ideaIndex=null,ideaStation='code',actionError='',actionMessage='';
  // The actual AI discussion is also visible IN THE OFFICE, anchored to the
  // real cafe station. This badge is not another employee sprite; it represents
  // only a persisted session with >=2 named real participants.
  let minimized=null;
  const cafeMarker=document.createElement('button');
  cafeMarker.id='pw138CafeMarker';cafeMarker.type='button';
  cafeMarker.title='Öppna pågående riktigt fikasamtal';
  cafeMarker.style.cssText='position:absolute;z-index:33;min-width:112px;max-width:230px;pointer-events:auto;border:2px solid #ebd08d;border-radius:6px;background:#153e50ef;color:#fff6d5;font:700 11px/1.3 system-ui,sans-serif;padding:7px 9px;box-shadow:2px 3px 0 #102939;transform:translate(-50%,-110%);display:none;cursor:pointer;white-space:normal;text-align:center';
  function showCafeMarker(rec){
    const stage=document.querySelector('#officeStage'),station=document.querySelector('#stationLayer .station[data-id="cafe"]');
    if(!rec||!stage||!station||active()!==rec.project){cafeMarker.style.display='none';return;}
    if(cafeMarker.parentElement!==stage)stage.append(cafeMarker);
    const outer=stage.getBoundingClientRect(),inner=station.getBoundingClientRect();
    cafeMarker.style.left=(inner.left+inner.width/2-outer.left)+'px';
    cafeMarker.style.top=(inner.top-outer.top-8)+'px';
    cafeMarker.style.display='block';
    const names=(rec.participants||[]).map(p=>p.name).join(' · ');
    const last=(rec.turns||[]).at(-1);
    cafeMarker.textContent='☕ '+names+(last?'\n💬 '+last.name+': '+last.text.slice(0,58)+(last.text.length>58?'…':''):'\n💬 Samtalet börjar…');
    if(rec.state!=='running'){
      cafeMarker.textContent='☕ '+names+'\n✅ Samtalet är klart – läs replikerna';
    }
  }
  cafeMarker.addEventListener('click',()=>{if(minimized?.project===active())open(active());});

  const api=(url,payload)=>window.pixelWorksApi(url,payload);
  const active=()=>window.__PIXEL_WORKS_DEMO__?.model?.activeProjectId||document.querySelector('#projectSelect')?.value;
  const sheet=inner=>{box.innerHTML=`<div class="pw138-sheet">${inner}</div>`;if(!box.open)box.showModal()};
  const header=(title='☕ Fikarummet')=>`<div class="pw138-head"><div><h2>${esc(title)}</h2><div class="pw138-muted">${esc(slug||'')} · Du och teamet · riktiga AI-svar</div></div><button class="pw138-exit" data-cafe="close" aria-label="Stäng">✕</button></div>`;
  const badge=txt=>`<span class="pw138-tag">${esc(txt)}</span>`;
  function stopPolling(){if(timer){clearInterval(timer);timer=null;}}
  function close(){ownerDraft='';ideaIndex=null;actionError='';actionMessage='';if(session&&slug){minimized={id:session.id,project:slug};showCafeMarker(session);}stopPolling();loadId++;pending=false;session=null;slug=null;request=null;note='';if(box.open)box.close();}
  function menu(error=''){
    if(!slug)return;
    sheet(`${header()}<p class="pw138-muted">Välj vad ni ska prata om. Du kan sedan själv hoppa in med fler inlägg. Två eller tre tillgängliga anställda svarar med sina riktiga AI-verktyg och reagerar på varandras repliker.</p><label for="pw138Note"><h3>Vad vill ni prata om?</h3></label><textarea id="pw138Note" maxlength="1400" placeholder="Valfritt: berätta vad som är viktigt i just det här spelet…">${esc(note)}</textarea><div class="pw138-grid">${choices.map(c=>`<button class="pw138-choice" data-topic="${c.id}"><span class="pw138-icon" aria-hidden="true">${c.icon}</span><span><strong>${esc(c.name)}</strong><small>${esc(c.hint)}</small></span></button>`).join('')}</div>${error?`<p class="pw138-error" role="alert">${esc(error)}</p>`:''}<p class="pw138-muted">Inga färdigskrivna repliker. Samtalet använder riktiga AI-anrop och kan därför ta tid och använda tillgänglig kvot. Grundsamtalet använder fyra till sex AI-anrop. Om du fortsätter efteråt används två nya AI-anrop per följdfråga, högst två gånger. Chefen kan skapa konkreta uppföljningsuppdrag.</p>${history.length?`<details class="pw138-history"><summary>Tidigare samtal (${history.length})</summary>${history.map(h=>`<button data-history="${esc(h.id)}">${esc(h.title)} · ${esc(h.state)}</button>`).join('')}</details>`:''}<div class="pw138-controls"><button data-cafe="close">Till kontoret</button><button data-cafe="studio">👥 Min studio</button></div>`);
    box.querySelector('#pw138Note').addEventListener('input',e=>{note=e.target.value});
  }
  const stations=[['code','💻 Programmering'],['art','🎨 Grafikstudio'],['qa','🧪 Testning'],['docs','📚 Dokumentation'],['music','🎵 Musikstudio'],['voice','🎙️ Röststudio'],['research','🔎 Forskning'],['meeting','💬 Mötesrum']];
  function suggestedStation(text){const t=String(text||'').toLowerCase();return /test|bugg|kvalitet|kontrollera|verifiera/.test(t)?'qa':/grafik|bild|sprite|animation|färg/.test(t)?'art':/musik|ljud|effekt/.test(t)?'music':/design|berättelse|karaktär|game bible/.test(t)?'docs':/forsk|undersök|studera|källa/.test(t)?'research':'code';}
  function thread(){
    if(!session||!slug)return;
    const scroll=box.scrollTop,focused=document.activeElement?.id;
    const state=session.state||'running';
    const bubbles=(session.turns||[]).map((t,i)=>{
      const owner=t.source==='owner_message';const vote=session.reactions?.[i]||'';
      const toolbar=owner?'':`<div class="pw139-toolbar"><button type="button" data-vote="up" data-turn="${i}" aria-pressed="${vote==='up'}" title="Gillar idén">👍</button><button type="button" data-vote="down" data-turn="${i}" aria-pressed="${vote==='down'}" title="Vill inte gå vidare med idén">👎</button><button type="button" data-idea="${i}" title="Skapa riktig arbetsorder från den här idén">🛠️ Gör till uppdrag</button></div>`;
      const plan=!owner&&ideaIndex===i?`<div class="pw139-implement"><label>Vem ska göra jobbet? <select id="pw139Station">${stations.map(([value,name])=>`<option value="${value}" ${value===ideaStation?'selected':''}>${name}</option>`).join('')}</select></label><button type="button" data-order="${i}">✅ Lägg i arbetskön</button><button type="button" data-idea="close">Avbryt</button></div>`:'';
      return `<div class="pw138-speech ${owner?'pw139-owner':''}"><strong>${owner?'🧑 Du · Spelägaren':'👤 '+esc(t.name)}</strong> ${owner?badge('Ditt inlägg'):badge('Runda '+(t.round||1))}<p>${esc(t.text)}</p><span class="pw138-evidence">${owner?'✍️ Skrivet av dig · inte AI':'✓ Riktigt AI-svar · ej oberoende verifierat'}</span>${toolbar}${plan}</div>`;
    }).join('');
    const names=(session.participants||[]).map(p=>badge(p.name+' · '+p.role)).join('');
    const count=(session.turns||[]).filter(t=>t.source==='real_ai_response').length;
    const status=state==='running'?'<span class="pw138-live"><span class="pw138-dot" aria-hidden="true"></span> Kollegorna pratar – du kan hoppa in när som helst…</span>':state==='done'?'✅ Kollegorna har pratat färdigt – skriv om du vill fortsätta.':state==='interrupted'?'⚠️ Samtalet avbröts när servern startades om.':'⚠️ Samtalet kunde inte slutföras.';
    const orders=(session.work_orders||[]);
    const continueAllowed=state==='running'||(state==='done'&&(session.followup_count||0)<2);
    const composer=continueAllowed?`<section class="pw139-compose"><label for="pw139Owner"><strong>☕ Vad vill du säga till kollegorna?</strong></label><textarea id="pw139Owner" maxlength="1000" placeholder="Exempel: Bra idé! Men kan vi börja med en mindre version?">${esc(ownerDraft)}</textarea><div class="pw139-compose-actions"><small class="pw138-muted">Ditt namn visas som Du, inte som Greta. ${state==='done'?'Två medarbetare svarar med riktiga AI-anrop (högst två följdfrågor).':'Ditt inlägg läses före kommande AI-svar.'}</small><button type="button" data-cafe="speak" class="pw139-primary">💬 Säg det till teamet</button></div></section>`:'';
    showCafeMarker(session);
    sheet(`${header('☕ '+session.title)}<p>${names}</p><div class="pw138-state" role="status">${status}<br><small>${count} verkliga AI-repliker · dina egna inlägg märks separat</small></div>${bubbles||'<p class="pw138-muted">Ännu inga AI-svar. Det första anropet pågår…</p>'}${composer}${actionError?`<p class="pw138-error" role="alert">${esc(actionError)}</p>`:''}${actionMessage?`<p class="pw139-feedback" role="status">${esc(actionMessage)}</p>`:''}${session.error?`<p class="pw138-error">${esc(session.error)}</p>`:''}${session.followup_error?`<p class="pw138-error">${esc(session.followup_error)}</p>`:''}${state==='done'?`<div class="pw138-orders"><strong>👔 Uppföljning</strong><p>${orders.length?`${orders.length} riktiga arbetsordrar har skapats i arbetskön.`:'Chefen skapade ingen automatisk arbetsorder. Du kan välja 🛠️ Gör till uppdrag på vilken idé du vill.'}</p></div>`:''}<div class="pw138-controls"><button data-cafe="close">Till kontoret</button><button data-cafe="new">☕ Nytt ämne</button></div>`);
    box.scrollTop=scroll;
    const field=box.querySelector('#pw139Owner');if(field){field.addEventListener('input',e=>{ownerDraft=e.target.value;});if(focused==='pw139Owner')field.focus({preventScroll:true});}
    box.querySelector('#pw139Station')?.addEventListener('change',e=>{ideaStation=e.target.value;});
    if(state==='running'){if(!timer)timer=setInterval(()=>refresh(),2200);}else stopPolling();
  }
  async function refresh(){
    if(!session||!slug||session.state!=='running')return;
    const snap=slug,id=session.id,seq=loadId;
    try{const r=await api('/api/pw-v0138/cafe?project='+encodeURIComponent(snap)+'&session='+encodeURIComponent(id));
      if(seq!==loadId||snap!==active()||slug!==snap||session?.id!==id)return;
      const next=r.session;
      if(JSON.stringify(session)!==JSON.stringify(next)){ownerDraft=box.querySelector('#pw139Owner')?.value??ownerDraft;session=next;thread();}
    }catch(err){if(seq===loadId&&session?.id===id){stopPolling();session.error='Kunde inte hämta status: '+err.message;session.state='interrupted';thread();}}
  }
  async function open(nextSlug){if(!nextSlug||nextSlug!==active())return;close();slug=nextSlug;history=[];const seq=loadId;menu();try{const r=await api('/api/pw-v0138/cafe?project='+encodeURIComponent(slug));if(seq!==loadId||slug!==nextSlug)return;history=r.history||[];if(r.active){const running=await api('/api/pw-v0138/cafe?project='+encodeURIComponent(slug)+'&session='+encodeURIComponent(r.active));session=running.session;thread();}else menu();}catch(err){if(seq===loadId)menu('Kunde inte läsa fikarum: '+err.message);}}
  async function begin(topic){if(pending||!slug||slug!==active())return;const key=JSON.stringify([slug,topic,note.trim()]);if(!request||request.key!==key)request={key,id:(globalThis.crypto?.randomUUID?.()||('cafe'+Date.now().toString(36)+Math.random().toString(36).slice(2)))};
    pending=true;box.querySelectorAll('button').forEach(b=>b.disabled=true);
    try{const started=slug;const r=await api('/api/pw-v0138/cafe',{project:started,topic,note:note.trim(),request_id:request.id});pending=false;request=null;if(slug!==started||active()!==started)return;session=r.session;thread();}
    catch(err){pending=false;menu(err.message+' · Inga låtsasrepliker har skapats.');}
  }
  box.addEventListener('click',async e=>{const btn=e.target.closest?.('button');if(!btn||pending)return;
    if(btn.dataset.topic){begin(btn.dataset.topic);return;}
    if(btn.dataset.history){const s=slug,seq=loadId;try{const r=await api('/api/pw-v0138/cafe?project='+encodeURIComponent(s)+'&session='+encodeURIComponent(btn.dataset.history));if(seq!==loadId||s!==slug)return;session=r.session;thread();}catch(err){menu(err.message);}return;}
    if(btn.dataset.idea!==undefined){if(btn.dataset.idea==='close')ideaIndex=null;else {ideaIndex=Number(btn.dataset.idea);ideaStation=suggestedStation(session?.turns?.[ideaIndex]?.text);}actionError='';actionMessage='';thread();return;}
    if(btn.dataset.vote){const i=Number(btn.dataset.turn),old=session?.reactions?.[i],vote=old===btn.dataset.vote?'clear':btn.dataset.vote;
      try{const r=await api('/api/pw-v0138/cafe',{action:'reaction',project:slug,session:session.id,turn_index:i,vote});session=r.session;actionError='';thread();}catch(err){actionError=err.message;thread();}return;}
    if(btn.dataset.order!==undefined){const i=Number(btn.dataset.order);if(pending)return;
      pending=true;try{const r=await api('/api/pw-v0138/cafe',{action:'implement',project:slug,session:session.id,turn_index:i,station:ideaStation});session=r.session;ideaIndex=null;actionError='';actionMessage=r.created?'✅ Arbetsordern skapades – teamet kan börja.':'✅ Idén finns redan i arbetskön.';}catch(err){actionError=err.message;}pending=false;thread();return;}
    const action=btn.dataset.cafe;
    if(action==='speak'){const message=(box.querySelector('#pw139Owner')?.value||ownerDraft).trim();if(pending)return;
      pending=true;try{const r=await api('/api/pw-v0138/cafe',{action:'message',project:slug,session:session.id,message});session=r.session;ownerDraft='';actionError='';actionMessage='';}catch(err){actionError=err.message;}pending=false;thread();return;}

    if(action==='close')close();
    if(action==='new'){session=null;stopPolling();note='';menu();}
    if(action==='studio'){close();document.querySelector('#pw13StudioNav')?.click();}
  });
  box.addEventListener('cancel',e=>{if(pending){e.preventDefault();return;}close()});
  document.addEventListener('click',e=>{
    if(!document.body.classList.contains('live-project')||e.defaultPrevented)return;
    const station=e.target.closest?.('#stationLayer .station[data-id="cafe"]');
    if(!station||e.target.closest('.station-order-badge,.pw17-tooltip'))return;
    e.preventDefault();e.stopImmediatePropagation();open(active());
  },true);
  document.addEventListener('keydown',e=>{
    if(!document.body.classList.contains('live-project')||!['Enter',' '].includes(e.key))return;
    if(!e.target.closest?.('#stationLayer .station[data-id="cafe"]'))return;
    e.preventDefault();e.stopImmediatePropagation();open(active());
  },true);
  // If player closes the popup, the real discussion continues server-side.
  // Check it at a modest rate, without running any extra AI calls on GET.
  setInterval(async()=>{
    if(!minimized||slug||minimized.project!==active()){
      if(minimized&&minimized.project!==active()){minimized=null;cafeMarker.style.display='none';}
      return;
    }
    const target=minimized;
    try{const r=await api('/api/pw-v0138/cafe?project='+encodeURIComponent(target.project)+'&session='+encodeURIComponent(target.id));
      if(minimized!==target||slug)return;
      showCafeMarker(r.session);
      if(r.session.state!=='running')minimized=null;
    }catch(error){cafeMarker.style.display='none';minimized=null;}
  },5000);
  window.pixelWorksCafeOpen=()=>open(active());
  window.addEventListener('pixelworks:project-changed',()=>{if(slug&&slug!==active())close();});
})();
