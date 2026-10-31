# Pixel Works v2.4 – Gemensam personalvy och fungerande scroll

**Installera ovanpå v2.3.** Git-bas: `jwestholm/pixelworks`, `dev` = `fb70d1c9a927e07e802537c83705db5b8f9876cd` (kontrollerad 2026-10-30). Minimal frontend-delta: `src/main.js` ändras för att importera `src/pw-studio-roster-v24.js`. Inga backend-, API-nyckel-, Game Bible-, personal- eller rapportfiler ersätts.

## Varför och vad som rättas

Inspelningen 2026-10-30 09:25:36 visar en äldre gemensam studio med 5 projekt och 15 personalposter. Rutnätet för de anställda finns i samma långa dialog som projektknappar och allmänna instruktioner, vilket gör det svårt att navigera, särskilt på mobil.

### NU – fungerande *Min studio*

- **Ett kontor, en fullständig personalvy.** Befintlig serverkälla `/api/pw-v013/studio` används för att lista alla projektens anställda i samma ruta. Varje post representerar en *separat individ* med eget `studio_id`. Två personer som heter Gunnar hålls isär och visar respektive ursprungsprojekt.
- **Sök på namn, roll eller projekt** och **filtrera på projekt** utan att förlora vilka andra personer som finns i studion.
- **Personallistan scrollar själv** med mus, styrplatta eller mobilens touch, medan projektval, sökning och hjälpingång ligger kvar överst. Listan är tvåspaltig på desktop och enspaltig på mobil. Ingen horisontell sidskroll behövs i 390 px bredd.
- **Avskeda direkt i Min studio** genom `🚪 Avskeda…` → skriv personens namn → `Bekräfta avsked`. Dialogen visar projektet, servern omkontrollerar *exakt* `studio_id + project_id + agent_id`, och slutlig POST använder redan befintliga `/api/projects/<projekt>/staff/dismiss` som vägrar avskeda en agent med aktivt jobb. **Inget händer när sidan öppnas eller när du bara klickar `Avskeda…`.** Rapporter och spelkod behålls.
- **Inga automatiska namnsammanslagningar, personalflyttar, avsked eller AI-anrop**.

## Installation

1. Kontrollera att v2.3 är installerad, inklusive dess `src/pw-agent-help-bridge.js` och den tidigare importen i `src/main.js`.
2. Packa upp ZIP-filen i Pixel Works projektrot (där `index.html` finns), skriv över `src/main.js` och lägg till `src/pw-studio-roster-v24.js`.
3. Tryck `Ctrl+F5` på datorn; uppdatera webbläsarsidan på mobilen. **Ingen Python-serveromstart krävs.**
4. Öppna **Min studio**, prova sök/filter och scrolla ned till sista personen. Avskeda ingen förrän du själv valt vem som ska bort.

## Test och begränsningar

Test: `python3 tests/browser_roster_v24.py` (kräver Chromium + Playwright). Genomfört i utvecklingsmiljön med fiktiva data: 15 separata ID, desktop- och mobillistans scrollbar, sökfilter, projektfilter, tomt sökresultat, spärr för upptagen anställd dubbelt bekräftat avsked och att en gammal dialog kan byggas om utan att sökfältet försvinner. Ingen POST utan explicit användarbeslut. `node --check` passerat. **Detta verifierar inte dina verkliga personallistor på Ubuntu.** Testet använder endast mockade API-svar och gör ingen uppkoppling till Codex, Gemini eller andra externa AI-tjänster.

Inbyggda serverns avskedningsfunktion bevarar rapporthistoriken men tar bort den aktiva anställningsposten och dess stationsansvar. Flera *olika* personer med samma namn förblir olika personer. Den nya vyn visar dessa befintliga identiteter, men skapar **ännu inte ett självständigt globalt personalregister på disk**.

## NOW / NEXT / LATER – säkert skifte från gamla projektkontor

**NOW (v2.4):** Personal som redan finns synlig som separata anställda i en gemensam lista; scroll, filter, identitetsmärkning och trygg avskedning. Inga migrationsskrivningar vid start.

**NEXT (större v2.5+):** Skapa ett **beständigt serverägt globalt personregister** där `studio_id` är nyckel. Migrera historiska projektlokala `agent_id` till explicita alias `{project_id, agent_id, period}` med säkerhetskopia, förhandsgranskning och återställningspunkt. Jobb, arbetsorder, personalprofil, hjälp, speltester och fikarumsdeltagare ska alla referera till samma identitet. Projekt tilldelas anställda, äger dem inte. Ingen automatisk hopslagning på namn; skapa en egen urvalsprocess om ägaren senare vill slå ihop två *verkligen identiska* personer.

**NEXT:** Samordna flera klienter (mobil och dator) genom serverstyrd versionskontroll för uppdrag/beslut; per-klientfönster och oskickade utkast förblir lokala.

**LATER:** Ta bort eller adaptera det äldre projektlokala personal-UI:t **efter** att nya ID-systemet och alla arbetsflöden testats mot migrerade data. Ta inte bort `management/STAFF.json`, historiska rapporter eller äldre API:er medan jobb kan bero på dem.

**Ingen GitHub-push, ingen ändring av användarens lokala installation eller nätverk har utförts.**
