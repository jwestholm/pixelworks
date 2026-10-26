# Pixel Works v0.12.11.14 – Stabilitet: kort aktivitetslogg och säkrare status

**BAS:** v0.12.11.13. ZIP-filen innehåller bara ändrade/nya filer. Packa upp över din befintliga installation efter att ha tagit en säkerhetskopia. Starta som vanligt med `python3 backend/server.py`, ladda om Firefox med Ctrl+Shift+R. Inga GitHub-ändringar och inga externa AI-testanrop har utförts.

## Åtgärder

1. **Kort kontorslogg:** Aktiva arbetspass och granskningsärenden visar nu en neutral, stationsbaserad fras (exempelvis "Arbetar med koden"). Inga råa arbetsinstruktioner eller kompletta Game Bible-utdrag i högerspalten. Detaljer finns fortfarande i rapporterna och de tekniska jobbloggarna.
2. **Granskning:** En gammal återställningsfunktion kunde sätta en godkänd Gemini-order tillbaka till `review` eftersom rapporten kvarstod som `state=review`. Det nya avstämningssteget respekterar det sparade beslutet (`approve`, `forward`, `revise`, `reject`) och ändrar endast den ursprungliga ordern när `job_id` och `order_id` fortfarande matchar. Äldre arkiverade/ersatta order återupplivas inte.
3. **Ärlig Codex-status:** Ett lyckat jobb med identisk/ redan införd Git-kod får `completion_kind=no_code_changes`, `integrated=False`, status `done` (avslutat), inte "infört i spelet". Det kan inte heller införa ett nytt automatiskt Game Bible-sidecar som om ny kod hade integrerats.
4. **Säker åtkomst:** Att inaktivera Studioåtkomst stoppar också det manuella Gemini-jobb-API:t även om klienten skickar ett gammalt `approval`-fält.
5. **Hemligheter:** Geminis sparade nyckel returneras inte längre från GET `/api/pw-v01210/gemini/token`, utan enbart `configured`/maskerad indikator. Befintlig lagrad nyckel kan fortfarande testas från Inställningar utan ny inklistring; tomt fält behåller nyckeln.
6. **Synliga paneler:** Statistik och personalstatus ligger i den faktiska högerspalten och raderas inte när aktivitetslistan renderas om. Studioåtkomstknappen läser aktuellt serverbeslut i stället för ett föråldrat webbläsarvärde.
7. **Rätt rapport:** Game Bible-godkännande binds till modalens exakta rapport-ID. En annan rapport från samma anställda med samma inledning väljs inte av misstag.
8. **Anställdas namn:** Nya förslagsrapporter namnges efter medarbetaren, inte efter den tekniska leverantören. Historiska rapportnamn ändras inte.

## Verifiering

- **21 riktade backendtester passerade** (12 nya v0.12.11.14-tester + 9 v0.12.11.13-tester).
- **2 Chromium-kontroller med simulerad backend passerade**: stor arbetsinstruktion exponeras inte i den synliga aktivitetsloggen, personal/statistik visas; sparad hemlig nyckel återlämnas inte till input-fältet och kan testas utan ny inmatning.
- `node --check` för ändrade JS-filer, `compileall` för backend: godkända.
- Samlad **113-testers regression:** 86 godkända, **8 failures + 19 errors**. Detta är samma antal kända fel som i basversionen (101 tester: 8 failures + 19 errors). Felen består huvudsakligen av gamla testattrapper/ändrade historiska API-kontrakt. **Sviten är fortfarande inte grön**. Inga verkliga Codex-/Google-anrop gjordes; beteendet i användarens Firefox är inte verifierat.

## Avgränsningar

- **Ingen full konsolidering av delegeringsmotorer** i detta delta. Basens Codex-schemaläggare och senare Gemini-personmotor kvarstår; en separat, transaktionstestad ombyggnad behövs.
- **Ingen ändring av nuvarande Google-kvoter eller modellval.** Google styr som i 0.12.11.13.
- **Ingen automatisk migrering av gamla rapporttexter**. Korrigeringen gäller framtida jobb och orderavstämning framåt. Att ett historiskt kodjobb felmärkts kan kräva manuell kontroll i Git.
- De lokala `auto_projects`-inställningarna och flera äldre QA-/UX-punkter kräver ytterligare samordning.

## Filer

Se `DELTA_MANIFEST_v0121114.json` för exakta filer och SHA256.
