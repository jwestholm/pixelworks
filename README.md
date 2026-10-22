# Pixel Works v0.12.0.2 – Levande agentsprites

Detta är ett **komplett ersättningspaket** för v0.12.0.1. Det ändrar bara kontorets visuella animationer och versionstext, inte Codex-, Git- eller projektlogik. Ingen AI-tjänst anropas av animationerna.

## Så här märker du skillnaden

- **Ledig:** långsam andning och blinkningar.
- **Går:** fyra tydligt skilda steg; den befintliga vägplaneringen för flytt är kvar.
- **Arbetar:** händerna rör sig över ett litet tangentbord när agentens status är `working`.
- **Fikar:** dricker ur en animerad kaffekopp vid fikabordet.
- **Tillgänglighet:** inga spriteanimationer om webbläsaren/OS har `prefers-reduced-motion: reduce`.

Bildarkens fyra rutor är **48 × 68 pixlar**, hela ark **192 × 68**. Alla åtta karaktärsvarianter har fyra animationstyper (`idle`, `walk`, `working`, `cafe`). Sprites visas med `image-rendering: pixelated` och utan externa grafikberoenden.

**Viktigt:** Vanliga vilorörelser är diskreta. Om ingen Codex-session körs ska agenten **inte** göra programmeringsanimationen. Kontorets grafiska detaljnivå ligger fortfarande under de högupplösta isometriska konceptbilderna.

## Uppdatera lokalt

Stoppa tidigare lokalserver helt. Lägg in hela programmets nya filer i din Git-arbetsmapp **utan att radera `.git`**. Starta `python3 backend/server.py` från programkatalogen. Uppdatera Firefox med **Ctrl + Shift + R**. Dina spelprojekt i `~/.pixelworks/projects/` ska vara orörda.

---

# Pixel Works v0.12.0.1 – Visual loading fix

**Komplett paket.** Ersätter v0.12.0. Du behöver inte installera någon annan ZIP först.

**Åtgärd:** `visual-v2.css`, `visual-v2.js` och alla separata kontorsbilder serveras nu korrekt från Python-servern. I v0.12.0 blockerades de av MIME-säkerhetskontrollen och därför syntes det gamla kontoret.

**Uppdatering:** Stoppa tidigare Pixel Works-server; ersätt programfilerna i din lokala Git-arbetsmapp (låt `.git` vara kvar); starta `python3 backend/server.py` i den nya programkatalogen och öppna `http://127.0.0.1:8765/`. Kör **Ctrl+Shift+R** i Firefox om gammal CSS visas. Rör inte `~/.pixelworks/projects/`.

**Snabbkontroll:** Adresserna `http://127.0.0.1:8765/visual-v2.css` och `http://127.0.0.1:8765/visual-v2.js` ska nu visa CSS respektive JavaScript, inte JSON-fel. På kontoret ska även de separata möbel-/agentspritesen synas.

Se `TEST_REPORT.md` och `CURRENT_STATE.md`. Detta är en visuell laddningshotfix, inte en ny arbetsmotor.

---

> **Version 0.11.8.4:** Klicka på en agent som säger *Jag behöver hjälp* för en enkel dialog. Spelaren behöver aldrig utföra Git-/terminalåtgärder. Läs `CURRENT_STATE.md` om begränsningarna.

# Pixel Works v0.11.8.4 – hela paketet

Detta ZIP är en **fullständig version** ovanpå v0.11.8.2. Läs `CURRENT_STATE.md` och `TEST_REPORT.md` för aktuellt läge, korrigerade fel och begränsningar. Historiska versionsanteckningar längre ned är inte instruktioner för nuvarande beteende.

Uppdatera Pixel Works-källkoden i din lokala Git-arbetsmapp **utan att radera `.git`**. Stoppa den äldre serverprocessen först. Rör inte spelprojekten i `~/.pixelworks/projects/`.

---

# Pixel Works v0.10.9 – Agentidentitet & aktivitetslogg

Uppdatering ovanpå v0.10.8.1. Lägg installationen i **egen katalog**; användarens projekt under `~/.pixelworks/projects` ska inte flyttas, raderas eller kopieras över.

Starta i denna mapp: `python3 backend/server.py` och öppna `http://127.0.0.1:8765`.
Stoppa en server som startats från föregående installationsmapp med `python3 backend/server.py stop` **från den ursprungliga mappen** innan ny version startas. Verktyget stoppar bara sin egen verifierade process.

**Nytt:** Visar korrekt agent-ID i agentdialoger, avsändarnamn i aktivitetsloggen, agentkopplade rapporter och ❗📄 på bord med väntande arbetsorder.

**Inte nytt:** Ingen MCP-server, arbetsledare, autonom scheduler eller samtidiga skrivsessioner i samma projekt. Den verkliga Codex-processen arbetar fortfarande en i taget per projekt.

Se `CURRENT_STATE.md`, `ROADMAP.md`, `TEST_REPORT.md`.

## Nytt i v0.11.0
Under **+ Rekrytera → ⚙ Profil** kan en anställd ändra namn, yrkestyp, titel, personlighet, hemmabord, arbetsbeteende, stationsbehörighet och egna arbetsinstruktioner. **★ Skills** öppnas från profilen.

Separata Codex-processer som skriver samtidigt i samma projekt är **inte** aktiverade. Ytterligare arbetsytor/worktrees och granskat integrationsflöde måste byggas först för att undvika överskrivningar.

## v0.11.2 – Studio Dispatch

Öppna ett arbetsbord och välj **🤖 Autoarbete**. Backend visar en tillåten nästa arbetsorder. För att faktiskt köra behövs ett uttryckligt startbeslut, ett aktivt projektmandat och en agent vars arbetsbeteende i personalprofilen är **Specialist** eller **Självständig**. Automatiska fortsättningar sker endast medan denna webbläsarflik är öppen. **Pausa nya starter** via samma knapp. Vid fel pausas fortsatt körning. Systemet kör fortfarande högst en skrivande Codex-session per projekt och skapar aldrig nya arbetsorder på egen hand. Detta är ett första opt-in-dispatchflöde, inte en permanent serverscheduler eller MCP-arbetsledare.

## v0.11.3 – Arbetsledaren och tydligare autoarbete

Öppna **🤖 Autoarbete → 👔 Arbetsledaren** eller välj en agent med yrke **Arbetsledare** och **Planera arbete**. En explicit bekräftelse låter Codex CLI föreslå högst åtta arbetsorder, med projektets Game Bible som kontext. Codex körs i `read-only` och får inte ändra spelkoden under planeringen. Varje förslag godkänns eller avvisas separat; först efter godkännande läggs det till i den vanliga kön. **Google Gemini/Gemma är ännu inte inkopplade** och inga molnkvoter påstås vara verifierade.

**Autoarbete är fortfarande webbläsarstyrt.** Efter att du tryckt på Starta godkänd arbetskö visas status i kontorets informationsrad: söker agent, arbetar med namngiven verklig Codex-session, väntar på arbetsyta eller pausad med förklaring. Om inget händer, kontrollera först att det finns väntande arbetsorder, aktivt projektmandat och en anställd med beteende Självständig eller Specialist vid tillåtet hemmabord. En redan färdig eller manuellt markerad order startas inte igen.

## v0.11.4: Samtidiga Codex-arbetare / AI-motorer

Arbetsledaren prioriterar behöriga anställda och kan rycka in själv om ingen tillgänglig arbetare är lämpad för arbetsordern. `🤖 Autoarbete` tar upp till fyra förslag per omgång och kan starta flera verkliga Codex-processer **bara när Git-arbetsytan är säker**. Varje process använder en *egen worktree* under `management/worktrees/job-<jobb-id>`. Detta tillhör samma projekt men inte samma fysiska arbetskatalog.

**Förbered första gången:** kontrollera att `~/.pixelworks/projects/<projekt-id>/work` har sitt eget Git-repo, minst en commit och inga ocommittade ändringar. Exempel från den mappen: `git add . && git -c user.name='Studio' -c user.email='studio@localhost' commit -m 'Baseline för parallellt arbete'`. Kontrollera gärna innehållet innan `git add .`; projektet ska inte innehålla hemligheter eller oväntade filer. Pixel Works gör inte denna commit åt dig. Om preflight inte är godkänd körs högst ett jobb åt gången.

**Efter jobb:** `review` betyder att jobbet kördes färdigt i agentens worktree, **inte** att ändringarna har förts in i spelet. Inspektera ändringar manuellt via `git -C <worktree> status` / `git -C <worktree> diff` och integrera först efter granskning. Ingen automatiserad merge finns i denna version. Radera inte worktrees som ännu innehåller arbete.

**Gemini:** `Autoarbete → ⚙️ AI-motorer` låter dig lagra API-nyckeln lokalt i `~/.pixelworks/secrets/gemini.key`, inte i spelprojektets Git. I agentprofilen kan du välja motor Google Gemini, men adaptern är medvetet avstängd tills separat integration och tydligt godkännande finns. Lägg aldrig in API-nycklar i Game Bible eller uppdrag.

### v0.11.4.1 – automatisk lokal Git-baseline
Vid **Starta delegering** skapar Pixel Works automatiskt en Git-commit i projektets `work/` om det behövs för parallella worktrees. Ingen GitHub-push görs. Misstänkta hemliga filer och pågående direktjobb ger ett tydligt fel i stället för en osäker snapshot.


## v0.11.8.0: Projektborttagning och stabiliseringsspår
Två bekräftelser för projektborttagning, lokal papperskorg, skydd mot samtidiga jobb. Kommande prioritet: enda källa för jobb/rapporter/notiser samt end-to-end-verify av preview. Se `CURRENT_STATE.md` och `TEST_REPORT.md`.


## v0.12.0 – Visuell grund

Detta paket innehåller **hela tidigare Pixel Works** plus en första modulär visuell uppdatering. Kör som tidigare via lokalservern. Ersätt programfilerna i ditt Git-repo utan att ta bort `.git`; dina egna spel ligger separat under `~/.pixelworks/projects/`. De tillhör inte ZIP-paketet.

Grafiken ligger i `assets/office-v2/`, och hela utseendeskiktet kan stängas av genom att ta bort referenserna till `visual-v2.css` och `visual-v2.js` samt `#gameDock` i `index.html` (de tidigare menyerna kan då visas genom att återställa `.game-actions`).

Ändringar av riktiga spelprojekt sker bara genom de befintliga uttryckliga uppdragsflödena. Den nya HUD:en genererar ingen backendaktivitet på egen hand.


### Version 0.12.0.9 – popupstil och rapportpärm
Rapportpärmen ligger på **Ditt skrivbord** och kan filtreras/arkiveras via spelmenyn. Alla rapporter och projektfiler behålls vid arkivering; inga externa AI-anrop sker i detta gränssnitt. Se `TEST_REPORT.md` för gränser för verifiering.
