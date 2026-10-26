# Pixel Works v0.12.11.6 – Personal, skapande och Game Bible

Utgår från **installerad v0.12.11.5**. ZIP innehåller ENDAST de filer som ska ersättas eller läggas till. Inga installationsskript. Rör inte spelprojektens data.

## Lägg in
Packa upp med bibehållen mappstruktur i Pixel Works-projektmappen. Ersätt de namngivna tilläggsfilerna. Avsluta körande server och starta med det enda stödda kommandot: `python3 backend/server.py`. Uppdatera Firefox med Ctrl+Shift+R.

## Ändrat
- Skapande uppdrag till Gemini styrs mot färdig design, inte mallar. Arbetsinstruktionen inkluderar begränsad Game Bible-kontext; privat projektdata delas inte generellt.
- Godkänt förslag sparas som **beslutad design, ej implementerad eller verifierad**, i redigerbart Game Bible-kapitel. Ursprunglig skrivskyddad Game Bible skrivs inte över. Samma rapport får inte dubbla kapitelblock. Tomma mallfält blockeras vid godkännande.
- Vid godkännande/vidareskickning/avslag flyttas arbetaren till fikarummet när inget jobb körs. Om ny förbättring beställs stannar personen kvar.
- Personbaserad aktivitetslogg: namn + uppdrag, inte AI-leverantör. Visar aktuella jobb samt oprövade hjälp-/granskningsärenden. Granskade förslag försvinner från den aktiva listan. Klick på arbetaren med olöst ärende ska öppna det direkt.
- Åtgärdsknappar säger medarbetarens namn i stället för AI-motorns namn där det är relevant.

## Avgränsning
- Ingen ny ork-/hälsobar eller tokensaldo i denna version; se NEXT.
- Äldre tekniska dialoger, historiska rapporttitlar och diagnostik kan fortfarande nämna en leverantör. Den nya grundytan och aktiva listan visar personalnamn.
- Godkännandet innebär **inte** att koden i spelet ändrats eller kontrollerats.
- API-nycklar ingår inte i ZIP-filen. Ingen GitHub-push, inga AI-anrop vid uppackning.

## Tester
60 Python-regressionstester godkända. JavaScript syntaxkontroller genomförda. Chromium-rendertest med simulerade API-svar godkänt. Inga verkliga Gemini-/Codex-anrop eller full integration med användarens lokala Firefox genomförda.
