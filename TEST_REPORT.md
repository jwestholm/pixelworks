# TEST_REPORT – Pixel Works v0.12.0.9

Datum: 2026-10-22. **Endast lokal källkod och tillfälliga testdata har ändrats.** Inga externa AI-anrop, GitHub-åtgärder eller riktiga användarspel.

## Genomfört

- **177 backendtester passerar**: `python3 -m unittest discover -s backend -p 'test*.py' -q`. En av befintliga testerna skriver det förväntade felmeddelandet `KRITISKT RAPPORTFEL: disk full` för att testa felvägen; hela testsviten avslutas med `OK`.
- **20 JavaScript-tester passerar**: `node test-*.mjs` (körda individuellt). Nytt `test-report-binder-v01209.mjs` testar kombinerade filter på typ, arbetsstatus och läst/oläst, att arkiverade poster är dolda, korrekt skillnad mellan integrerat och ej integrerat resultat, samt att nya dialog- och whiteboard-klasser finns.
- `node --check local.js` och `node --check visual-v2.js` godkända; `python3 -m py_compile backend/server.py` godkänd.
- Lokal HTTP-kontroll på port **18865** med **separat temporär `PIXEL_WORKS_HOME`**: `/visual-v2.css` gav HTTP 200 med `text/css` och `/local.js` gav HTTP 200 med `text/javascript`.
- En **statisk visuell designkontroll** av rapportpärmen renderad i headless Chromium med `page.set_content` (förhandsbild ingår separat). Detta är INTE en bekräftelse på att Pixel Works fullständiga Firefox-vy eller interaktionen fungerar på användarens Ubuntu.

## Vad som ändrats

- Gemensam egenritad pixelträinramning med stiliserad ådring och sprickor för popupfamiljerna; ingen extern stockbild och ingen extra extern resurs.
- Rapportpärmen visar rapporttyp, arbetsstatus, läst/ny, agent, datum och om självständig verifiering saknas.
- Tre kombinerbara filter (läst, typ, status), enskild arkiveringsikon och grupparkivering av exakt det aktuella filtrets rapport-ID:n.
- Grupparkivering kräver egen Pixel Works-bekräftelse. Arkiveringskommandon använder befintligt server-API och ändrar enbart rapportflaggor (`archived`). Spelkod, arbetsorder och Git-historik ändras inte.
- Topplistan för uppdrag får en whiteboard-stil och personalfönstret en kortbaserad variant av samma ram.

## Inte verifierat / kända begränsningar

- Chromium kan inte navigera till `127.0.0.1` i denna testmiljö (`ERR_BLOCKED_BY_ADMINISTRATOR`). Ingen fullständig browser end-to-end-kontroll; användarens Firefox återstår.
- Grupparkivering skickar **ett lokalt API-anrop per rapport**. Om ett anrop misslyckas kan tidigare poster redan vara arkiverade; UI visar antalet genomförda och lämnar återstående poster kvar. Backend gör ingen atomär grupptransaktion.
- UI förändrar inte äldre Codex-processer, rapportinnehåll eller integrationsmotor; felen i återhämtning efter serveromstart och previewvalidering är fortfarande separata utvecklingspunkter.
