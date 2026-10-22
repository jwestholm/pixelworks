# CURRENT_STATE – Pixel Works v0.12.0.2

## NOW / levererat
- Riktiga fyrbildsrörelser för alla 8 agentutseenden: ledig, går, arbetar och fikar.
- Lediga agenter har lågmäld blinkning/andning, fika har kaffeanimationsark, arbetande agenter växlar synligt mellan tangentbordsposer.
- Befintligt agenttillstånd styr animationstyp; arbete markeras inte automatiskt när agenten står vid ett skrivbord.
- `prefers-reduced-motion` respekteras; frontendfilerna och tillgångarna serveras via befintlig MIME/allowlist.

## Verifierat
- 165 backendtester passerar inklusive 3 nya regressionstester för innehållsligt olika spritebildrutor.
- Alla 13 JavaScript-skript tester passerar, plus JS/Python-syntaxkontroller.
- Samtliga 32 nya PNG-animationer innehåller fyra skilda bildrutor. CSS-vägar kontrollerade.

## EJ verifierat
- Firefox på användarens Ubuntu, verkligt Codex-jobb och att rörelserna upplevs rätt i storlek i alla fönsterstorlekar.

## NEXT
- Visuell QA i Firefox; förbättrad scenkomposition och perspektiv/tio bord, bättre högupplösta isometriska sprites, test med verkliga statusar.
- Stabilitet i arbetsorder, rapporter och automatisk integration innan större nya system.

## LATER
- Fler rumsanimationer, sprites efter yrke/utrustning, rekrytering, nivåer, Game Bible-redaktion och Gemini-integration.

## v0.12.0.3
- **NOW:** Yrkesstyrda animerade sprites med 4 visuella varianter/yrke, alternativa feminina/maskulina siluetter i spriteunderlag. Utseendet är kosmetiskt och väljs stabilt per agent.
- **NOW:** Spelnavigering i sidhuvudet, Projekt-menyn innehåller byte/nytt/borttagning. Tekniska statusvärden under Inställningar i stället för permanent toppstatus.
- **NEXT:** Riktig karaktärseditor (könsuttryck, hår, kläder, porträtt) och fler detaljerade sprites.
- **LATER:** Isometrisk grafikmotor och ytterligare stationer.

## v0.12.0.5 – Uppdragslista och HTTP (2026-10-22)
**NOW / implementerat:** Uppdragslistan visar bara aktiva riktiga arbetsorder; historiska och ersatta poster räknas inte. Knapparna för varje uppdrag öppnar direkt samma stations serverbaserade arbetskö som bordet. HTTP-serverns JSON-svar hanterar avbruten anslutning utan att försöka skicka ett andra svar.

**Verifierat:** 167 backendtester samt alla JS-kontraktstester och ett nytt simulerat interaktionstest passerar. Inga verkliga Codex-processer startade.

**NEXT:** Visuell kontroll av uppdragslistan i Firefox; vidare utveckling av en gemensam modell för uppdrag/status/pappershögar och beständiga jobbsessioner; säkrare överföring vid omstart.

**LATER:** Avancerat managementgränssnitt, Game Bible-redaktion, nivåer och lägesanpassade AI-motorer.

## v0.12.0.5 – Stale arbetsorder och navigation (NOW)
- Servern tillåter uttryckligt arkiverande av väntande och gamla blockerade arbetsorder. Kända aktiva Codex-sessioner blockerar arkivering. Endast orderstatus ändras; kod, rapporter och Git-historik berörs inte.
- Skrivbordets arbetskö erbjuder Arkivera med bekräftelse inuti Pixel Works, även för gamla review/failed/claimed/running-poster. Historiken visar arkiverade poster.
- Toppnavigationen återgår till Kontor när ett menyfönster stängs med Stäng/X/Escape.
- Begränsning: efter serveromstart kan en extern Codex-process fortsätta utan att JOBS känner till den. Arkivering är då endast en visuell/kömässig åtgärd, inte en processavbrytning.

## v0.12.0.6 – Lugnt kontor, osynkroniserade animationer (NOW)
- Avlägsnade den fasta `chiefDispatchHealth`-rutan över kontorets tips. Chefens verkliga status finns kvar i högerspaltens aktivitetslogg.
- Om projektmandat saknas kan det godkännas där med en egen Pixel Works-dialog; godkännande är alltid uttryckligt. Ingen automatisk AI-körning tillkommer.
- Animationernas fas beräknas stabilt från projekt-ID och agent-ID, med negativ `animation-delay`; gubbar rör sig inte längre i takt. Fasen ligger kvar vid omritning och vid byte av aktivitetsläge.
- `prefers-reduced-motion` och verklig arbetsstatus fortsätter att styra animationsvalet.
- Versionsetiketter frontend/backend synkroniserade till 0.12.0.6.

### NEXT
- Visuellt verifiera avstånd mellan figurer vid fikabordet och väggobjektens överlapp i Firefox.
- Fler olika rörelsemönster (inte bara startförskjutning), mer detaljerade stationer och isometrisk kontorslayout.
- Fortsätt med persistent jobbtillstånd och kontrollerad Codex-integration utan att skriva över spelprojekt.

### LATER
- Utbytbara animationsbanker, fler karaktärsuttryck, rekrytering med dokumenterade AI-modellutvärderingar, Game Bible-fördjupning och XP-system.

## v0.12.0.7 – Isometriska yrkesbord (NOW, 2026-10-22)
- Tio nya isometriska pixelmöbler, med gemensam ljusriktning, fotavtryck och transparent bakgrund. Yrkesutrustning för chef, programmering, QA, research, grafik, dokumentation, röst, musik, möte och fika.
- Stationstypen visas alltid tydligt; en eventuell anställds namn visas **endast när arbetsstatusen säger `working`**. Inget visuellt arbete fabriceras.
- Alla stationer är fortsatt separata klickbara och flyttbara mål i samma fungerande logik; Enter/mellanslag öppnar stationer.
- Kontrollerat med nya sprite- och UI-tester, plus regressionssviten. Chromium-skärmbildsförsök gick inte att slutföra i testmiljön; visuell förhandsgranskning visar spritebilderna, inte en körande Firefox-vy.

### NEXT
- Finjustera storlek, skyltar och djupsortering i verklig Firefox. Sittande arbetsposer och bättre stationsplacering i den isometriska kontorsscenen.
- Fortsätt stabilitetsarbete för beständiga Codex-jobb, pålitliga rapporter och spelpreview.

### LATER
- Utbyggbar kontorslayout med cirka tio separata **personliga** skrivbord, valbar inredning, fler animationer och rekryteringspersonas.

## v0.12.0.9 – Spela-knapp & riktiga färdiglappar (NOW, 2026-10-22)
- `🎮 Spela` ligger direkt efter **Kontor** i toppmenyn. Knappen använder oförändrat det verifierings- och previewflöde som redan fanns i den äldre, nu dolda, huvudnavigationen. Ingen alternativ preview-server eller ny simulering.
- **Färdiga, integrerade Codex-arbeten skapar en oläst, oarkiverad rapport på Ditt skrivbord.** Tidigare gömdes dessa av backend direkt vid skapandet.
- Även äldre ej arkiverade `review`-arbeten som senare integreras skapar en ny synlig slutrapport när integrationen lyckas. Dubbel slutbehandling ger inte dubbletter.
- Röda sifferbadge på Ditt skrivbord uppdateras från verkligt rapportantal; inga tidigare manuellt arkiverade rapporter återställs eller ändras.
- Rapportlistan uttrycker tydligt *infört i spelet* kontra *speltest ej verifierat*.
- TEST: 177 backendtester, 19 JavaScript-tester, Python/JS syntaxkontroller. Inga riktiga Codex-processer eller användarprojekt har rörts. Firefox visuellt ej verifierat.

### NEXT
- Kontrollera i verklig Firefox att färdiglappen syns efter en ny Codex-session och att `Spela` öppnar projektets preview.
- Enhetlig händelselagring, bättre avstämning av gamla arbetsorder och rapporter, test av gameplay efter integration. Undvik att blanda in Git-detaljer i vanliga rapporter.

### LATER
- Personliga skrivbordsplatser och sittande figurer, levande Game Bible, mötesbord och nivåsättning utifrån verifierat arbete.

## v0.12.0.9 – Rapportpärm och träinramade popupfönster (NOW)
- Rapporter på **Ditt skrivbord** har nu en pärmlayout med tydliga rapporttyper, status, läst/ny, datum och agent.
- Tre kombinerbara filter: läst/ny, rapporttyp och arbetsstatus. Arkivera en rapport via ikon eller arkivera exakt det filtrerade urvalet efter Pixel Works egen bekräftelse. Rapporter arkiveras lokalt; spelkod och historik behålls.
- Gemensam pixlig träpanelram med ådring och små sprickor för modaler. Uppdrag visas på en ljus whiteboard, personal på kort i samma visuella familj. Originalgrafik i CSS, inga betalda stockassets.
- **Testat:** 177 backendtest, 20 JavaScript-tester, syntax och lokal CSS/JS-HTTP. Statisk Chromium-rendering; fullständig Firefox-interaktion ej verifierad.

### NEXT
- Verifiera filtrering, arkivering och mobil/Firefox-layout i verklig installation. Förbättra ikoner och täckning för övriga popupfamiljer efter skärmbilder från användaren.
- Ersätt återstående native `alert`/`confirm`/`prompt` i viktiga flöden; beständig jobbscheduler och korrekt preview-test.

### LATER
- Riktig animerad bok/pärm med sidbläddring, finkornig rapportklassificering och tydligare resultatförhandsvisning.
