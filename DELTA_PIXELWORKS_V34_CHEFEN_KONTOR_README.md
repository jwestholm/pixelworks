# Pixel Works v3.4 – Chefsbord + stabilt kontor

Bas: GitHub `jwestholm/pixelworks` dev `fb70d1c9a927e07e802537c83705db5b8f9876cd`, installeras **ovanpå Pixel Works v3.3** (inklusive tidigare v3.2 spriteassets).

## Installation
1. Säkerhetskopiera `~/.pixelworks` och projektkatalogen om du vill kunna återställa.
2. Packa upp DELTA-ZIP i `~/pixelworks/pixelworks-git/` (samma nivå som `index.html`), skriv över filerna.
3. Stoppa tidigare instans: `python3 backend/server.py stop`.
4. Starta med ditt befintliga LAN-startskript: `bash start-lan.sh`.
5. Firefox: `Ctrl+F5`. Telefon: ladda om sidan helt. Ingen GitHub-push gjord.

## Chefen (nytt)
- Knapp `👔 Chefen` i spelmenyn; samma vy nås från `AI-uppdrag → Fråga Chefen` och Chefens personalprofil.
- Välj spel, kategori, motor och textuppdrag. Chefen rangordnar personal med **fiktiva skills, aktuell roll och verkliga tillgänglighetsspärrar**, helt lokalt utan AI-anrop.
- Saknad specialist ger **rekryteringsrekommendation**, aldrig automatisk anställning.
- `✅ Välj för uppdrag` öppnar **v3.3:s befintliga godkännanderuta** med förifyllda uppgifter. Ingen modellstart sker på Chefsbordet.
- Codex kräver fungerande CLI, tillstånd och ren Git-arbetsyta. Gemini kräver verifierad tillgänglighet. Grafik/ljud är ännu bara textidéer eller kodunderlag i v3-pipelinen.

## Kontorsfix (nytt)
- Ritar tillbaka personalfigurer om ett äldre UI-lager uppdateras, eller om scenens DOM byts efter F5/inläsning.
- Förhindrar dubbla figurer och behåller person-id → egen sprite.
- Kontorsscenen får en explicit uppdateringssignal från `src/main.js` vid projektbyte och vid inläsning av live-projekt.
- Kontorslagrets existens kontrolleras lokalt var 1,8 sekund utan nätverkstrafik eller AI-anrop. Samma personaldata används.
- Om en spritebild saknas blockeras inte personen: en färgad reservfigur med initial visas och personen går fortfarande att klicka.

## Testad här
- 9 backendtester för Chefen (ingen AI startas; spärrar, giltig JSON, projekt och roller).
- 30 tidigare v3.3-/v3.2-backendtester.
- 10 Chromium-tester för v3.4, däribland att explicit **ta bort kontorslagret efter att figurerna visats** och verifiera att det byggs upp igen; fallback om spritebild saknas; mobilbredd, navigering och ingen oavsiktlig start.
- 5 äldre v3.3-webbläsartester och v3.2 webbscenarier på mobil/dator.
- JS syntaxkontroll samt ZIP-integritet och SHA256-manifest.
- Inga verkliga Codex-/Gemini-anrop, ingen nätverksanvändning för AI, och ingen installation på användarens Ubuntu har verifierats.

## Begränsningar
- Fixen avvärjer kända DOM- och spritebortfall, men den specifika Firefox-miljön behöver testas på din dator.
- Chefsförslagen är en lokal spelregel, **inte en AI-genererad plan**. Arbetsstart är alltid spelarstyrd i denna version.
- Den äldre pixelspelsarkitekturen kan fortfarande visa andra statusrutor; total UI-översyn görs separat.
- Om sprites försvinner trots fixen: granska webbkonsolens HTTP-fel för `/assets/characters/<id>/<id>-idle.png` och säkerställ att v3.2-assets installerats.

## NOW / NEXT / LATER
**NOW:** Chefen föreslår personal; stabila synliga figurer efter F5, projektbyte och DOM-refresh.
**NEXT:** enhetliga pixelbaserade dialoger för personal, uppdrag, rapporter och beslut, samt test av faktisk Ubuntu/Firefox.
**LATER:** säker automatisk delegering efter opt-in, fler verifierade motorer med undermodeller, användargranskad media direkt i kontext.
