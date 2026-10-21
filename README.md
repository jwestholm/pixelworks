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
