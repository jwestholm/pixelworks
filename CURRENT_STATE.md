# Pixel Works v0.11.8.4 — Aktuellt läge

## NOW – genomfört
- Agentens ❗-markering är nu en klickbar ingång till ett eget hjälpärende, inte en länk till rå Codex-logg. Klicka på agenten; vanlig dragning av agenter lämnas oförändrad.
- Dialogen visar på vanlig svenska vad som gick fel och vilket uppdrag agenten hade. Tekniklogg/utskriven Codex-rapport finns under frivilliga **Mer information**.
- **Låt studion försöka igen** lägger ett nytt avgränsat arbetsuppdrag i kön. **Skicka önskemål** lägger samma slags uppdrag med spelarens förtydligande. **Senare** gör inget.
- Ett arbete som redan blivit byggt i en annan isolerad arbetsyta testas först för säker lokal integration. Vid verklig konflikt skapas en ny arbetsorder utifrån den senaste spelbara versionen utan att gamla filer skrivs över.
- Ett nytt försök får samma prioritet och bilagor där originalordern finns. Äldre ärende arkiveras och den gamla ordern markeras **superseded**, inte falskt **done**. Hjälpmarkeringen försvinner när ärendet hanterats, om inget annat olöst ärende finns.
- En olycklig avbruten rapportuppdatering leder inte till dubbla försök om uppföljningsordern redan finns.
- Inget AI-anrop görs genom att bara öppna hjälpdialogen. Ett aktivt projektmandat och vanlig köhantering gäller fortfarande. Projektdata ligger alltid separat under ~/.pixelworks/projects/.

## Testat
- 156 backendtester passerar, inklusive 12 nya i hjälptestmodulen.
- 12 Node-kontraktstester passerar; syntaxkontroll för Python och JavaScript passerar.
- Testerna kördes med tillfälliga projektmappar och simulerad agentstart. Inga externa AI-anrop, inga verkliga projekt och inga GitHub-åtgärder.
- Headless Chromium kunde inte ansluta till localhost i denna miljö (ERR_BLOCKED_BY_ADMINISTRATOR): faktisk visuell verifiering och Ubuntu/Firefox måste göras på användarens dator.

## NEXT – säkerhet och användbarhet
- En central arbetsmotor med beständig status för arbete, rapport och notis även efter serverkrasch och en samordnad kö-/rapporttransaktion.
- Bekräftat körbar spelpreview efter integration; CSP-förbättring utan att släppa säkerhetsisolering.
- Fler små dialoger för fel som kräver spelägarens beslut; enbart speldesignbeslut, inte Git eller kommandon.
- Förfina arbetsledarens autonomi och återför arbeten utan att fastna i självreparerande köloopar.

## LATER – spelkänsla
- Game Bible med rikare bokuppslag och AI-redaktion, Creative Director, inspiration vid fikabordet, XP och levels, källbelagda modellprofiler för rekrytering.
