# Pixel Works v2.7 – Global arbetsstyrka i den riktiga arbetsmotorn

**Bas:** `jwestholm/pixelworks` `dev`, `fb70d1c9a927e07e802537c83705db5b8f9876cd`. **Installera ovanpå v2.6.1**, inklusive redan installerad v2.5 med 15 registrerade personer. Ingen GitHub-push, inga AI-anrop under test. Denna ZIP innehåller endast de ändrade filerna.

## Varför

Tidigare gav v2.5 en stabil central identitet och v2.6 en global kontorsvy, men Codex-/Gemini-motorn läste fortfarande `management/STAFF.json` för varje spel. Det innebar att samma person visuellt kunde finnas i en studio men vid jobbstart fortfarande var anställd i ett enda gammalt projektregister.

V2.7 inför en **frivillig cutover**: filen `~/.pixelworks/studio-v013/WORKFORCE_V27.json` blir auktoritativ för **nya uppdragskopplingar och personaländringar** först efter att du klickar på en bekräftelse i *Min studio*. Adapterfunktionerna `staff_read`, `staff_write`, `get_skill_settings`, `save_skill_setting`, `dismiss_staff` och den äldre personalflytten läser/uppdaterar då detta globala register. Utåt får varje projekt en tillfällig personallista med projektlokala *alias* för kompatibilitet med jobb- och rapportrutiner. `studio_id` är identiteten; namn är det inte.

**En person har högst en aktiv projekttilldelning åt gången i denna version.** Du kan omfördela personen till ett annat spel utan avsked/nyanställning. Att bara byta *visat spel* i Firefox ändrar inte personalens arbetstilldelning. Samtidigt arbete med samma person i flera projekt ingår inte.

## Installation

1. Säkerhetskopiera `~/.pixelworks` och `~/pixelworks/pixelworks-git` före steget. Denna ZIP **ändrar inte** något på din dator förrän du installerar den.
2. Packa upp ZIP direkt i roten med `index.html`, och skriv över `backend/server.py` samt `src/main.js`. Nya filer: `backend/pw_global_workforce_v27.py`, `src/pw-global-workforce-v27.js`, tester och denna README.
3. Stoppa och starta servern helt. Till exempel: `python3 backend/server.py stop` följt av `bash start-lan.sh` om du använder hemnätverket, alternativt ditt vanliga startkommando.
4. Uppdatera Firefox (`Ctrl+F5`) och mobilen. Öppna **Min studio**. Kontrollera personerna och välj **Granska och aktivera global personal**. Läs namn, ursprungsprojekt och unika studio-ID:n och välj därefter **Använd global personal för uppdrag**.
5. Aktivering **nekas** om det finns pågående/köade AI-jobb eller arbetsordrar som är markerade som aktiva. Vänta på dem, eller kontrollera varför gamla order inte avslutats innan du försöker igen.
6. Efter aktivering: använd befintligt **Min studio → Tilldela** för att ge en ledig person ett annat spel. Personen får samma studio-ID och en säker projektalias för nya arbeten. En flytt stoppas om personen har ett pågående AI-jobb eller en aktiv arbetsorder.
7. Du kan sedan **manuellt avskeda extra personer** via den befintliga knappen Avskeda i *Min studio*. Välj med omsorg: personer med lika namn är separata, och historiska rapporter bevaras. Ingen avskedas vid uppdatering eller aktivering.

## Säkerhet, bakåtkompatibilitet och begränsningar

- Global arbetsstyrka är avstängd fram till godkänd aktivering. Inget GET/startup skapar eller skriver register.
- Global cutover använder fullständiga personalprofiler från projektens *aktuella* register, men kräver att alla 15 identiteter överensstämmer med v2.5-snapshot. Om en person har tillkommit, försvunnit eller bytt projekt sedan v2.5 blockeras cutover med ett tydligt fel: **vi migrerar inte tyst med gissningar**.
- Personens skills och egna skillinstruktioner följer med mellan projekttilldelningar via samma centrala register; de gamla projektspecifika skillfilerna behålls som historiskt underlag.
- `WORKFORCE_V27.json` skrivs via en atomisk ersättning med `0600`-behörighet; `PEOPLE_V25.json` och dess säkerhetskopior bevaras, liksom **alla** gamla `STAFF.json`, skillfiler, arbetsordrar, rapporter, Git-arbetsytor, spelprojekt och API-nycklar.
- När cutover är aktiv använder standardmotorns personal-API en projektspecifik **vy över det centrala registret**. Äldre filer är endast återställningsunderlag; radera dem inte ännu. Individens historiska rapporter ligger kvar i ursprungsprojektet under tidigare projekt-agent-ID. V2.3:s hjälpöversikt kan visa äldre projektärenden.
- Anställda vid ett annat spel kan inte automatiskt arbeta på det spel du just öppnar – använd *Tilldela*. **Den gamla schedulerfunktionen kan fortfarande försöka starta arbeten i andra projekt** om de har tilldelad chef och arbete. En central *produktionspaus* planeras separat. Det kända felet ”Instruktionen matchar inte arbetsordern” i Skjutbanan löses inte av denna delta.
- Inget automatiskt omdöpande, sammanslagning efter namn, avslut av anställningar eller byte av AI-motor sker.
- V2.7 byter primär personaldatakälla men inte alla historiska hjälp- och rapportformat; dessa använder fortfarande äldre per-projektalias. Fullständigt avskaffande av de gamla formaten kräver ytterligare migration.
- **Nedgradera inte till en äldre ZIP efter att du börjat flytta/avskeda/anställa i v2.7**, eftersom de äldre filerna då inte återspeglar det nya centrala registret. Bevara säkerhetskopian och kontakta oss för kontrollerad återställning vid fel.
- Inget WAN/extern server anropas av migrationen. Den använder redan konfigurerade lokala API-autentiseringsskydd; LAN-läget och port 8765/8766 ändras inte.

## Test och verifikation

- `python -m unittest -v test_pw_global_staff_v25 test_pw_global_workforce_v27` – **22 tester** (8 tidigare identitetstester + 14 nya cutover/assign/dismiss/skills/skrivtester) med fiktiva lokala projekt.
- `node --check src/pw-global-workforce-v27.js`, `node --check src/main.js` och `python -m py_compile` på backend – godkända.
- Playwright Chromium desktop 1260×840 och mobil 390×780: tydlig manuell aktivering, 15 separata personer, ingen oväntad POST vid öppnande av personalvyn, samma nuvarande personalkort efter aktivering, scrollning och fem projekt – godkänt.
- **Ej verifierat i din Ubuntu-installation:** arbetsmotorn efter cutover med riktiga Codex-/Gemini-arbeten, flerwebbläsarsynk, verkliga femton profiler eller migrering under skarpa aktiva arbeten. Testerna är lokala med fiktiv data.

## NOW / NEXT / LATER

**NOW (v2.7):** frivillig global personaldatakälla för kärnans arbetsmotor via säker adapter; beständiga ID:n och projekthistoriska alias; manuell projekttilldelning, skills, anställning och avsked som uppdaterar det globala registret; bevarad gammal data.

**NEXT:** central projektstyrning av aktiv/pausad AI-produktion (inklusive Skjutbanans upprepade valideringsfel); stabiliserade arbetsledarroller per uppdrag och kontroll av samtliga äldre modulers direkta filåtkomst; synkronisering mellan mobil och dator med revisioner.

**LATER:** ombyggda globala uppdrags-/hjälp-/rapport-ID:n utan kompatibilitetsadapter, därefter pensionering av gamla projektbundna personalflöden och säker migrerings-/återställningsguide. Färre dubbletter först när du själv väljer.
