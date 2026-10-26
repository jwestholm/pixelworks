# Pixel Works v0.12.10.1 – Gemini som arbetsledarstyrd anställd

**Delta ovanpå den redan installerade korrigerade v0.12.10.** Basrepository: `jwestholm/pixelworks` → `dev`, commit `b6fdca9f748c1accee725ff88a246063fffe158d`, plus det tidigare v0.12.10-tillägget.

Det här arkivet innehåller endast de ersättningsfiler som ändrats och dokumentation. **Ingen installerare, ingen API-nyckel, inga spelprojekt, ingen GitHub-push.** Packa upp i befintliga Pixel Works-programkatalogen med bibehållen `backend/`- och `src/`-struktur. Ändra inte något under `~/.pixelworks/projects/`.

## Funktion

Gemini är nu ett **valfritt automatiskt rådgivande AI-yrke** som får väntande arbetsorder av den befintliga Codex-arbetsledaren i samma kö. Chef vid `lead`-bordet och aktivt projektmandat krävs. När användaren särskilt ger projektet Gemini-mandat får servern köra Gemini vidare efter avslutade jobb, även med stängd webbläsarflik. Automatik är AV som standard.

**Tillåtna uppgifter:** dokumentation (`docs`), forskning (`research`) och möten (`meeting`). Ingen direkt kodskrivning och inga automatiska Game Bible-ändringar. Codex behåller första prioritet på arbetsorder som den befintliga motorn redan kan ta. En anställd kan flyttas automatiskt från fika till ett tillåtet bord. Svaret lagras i den ordinarie rapportpärmen som `review`, `integrated=false`, `verified=false`; det räknas inte som implementerat arbete. Fel markeras `failed`, och inga arbetsorder skickas om igen utan ny åtgärd.

## Slå på säkert

1. I **Inställningar → AI API → Gemini API**: spara API-nyckeln. Statusfältet uppdateras automatiskt efter sparandet. Nyckeln visas aldrig igen.
2. **Kontrollera i Google AI Studio att just nyckelns projekt har Free Tier och INGEN kopplad fakturering**. API-nyckeln ensam kan inte bevisa detta.
3. Kryssa i bekräftelsen, aktivera Gemini och spara ditt lokala tak: **1–12 anrop per Google-kvotdygn** (noll om Gemini är avstängt). Det är ett lokalt säkerhetstak – Googles riktiga återstående kvot står som **okänd**.
4. Med valt projekt, kryssa i **”Tillåt arbetsledaren dela ut Gemini-uppdrag automatiskt”**, tryck spara och bekräfta. Bekräftelsen gäller ett projekt i taget och kan stängas av i samma meny.
5. Ha en Codex-arbetsledare vid chefsbordet och en Gemini-anställd som har rätt till `docs`, `research` eller `meeting`. Lägg en väntande arbetsorder i ordinarie arbetsorderkö. Gemini tar ett lämpligt uppdrag när den är ledig och lokal kvot finns kvar.

Vid API-/kvotfel (även `429`) stoppas automatiska anrop fram till nästa kvotdygn; **ingen automatisk retry, ingen modelluppgradering och ingen dold betalkoppling**. Automatiken skickar enbart uppdragets text, inte Game Bible, uppladdade bilder eller privata filer. Lägg därför inga hemligheter i uppdragstexten. Googles gratisnivå kan använda skickat innehåll för modellförbättring enligt deras villkor.

## Startkommando och känd begränsning

**Arkitekturskuld från v0.12.10:** detta delta ersätter tilläggsmodulerna, inte den ursprungliga `backend/server.py`. Om du för närvarande startar v0.12.10 med `python3 backend/server_v01210.py` använder denna uppdatering samma startpunkt. `python3 backend/server.py` laddar fortfarande endast ursprungsservern och är därför **inte** korrigerat av detta delta. Vi påstår inte motsatsen. För att återgå till det enda önskade startkommandot krävs en separat, korrekt integration i originalets serverfil; här ska inget skript patcha din server automatiskt.

Om den aktiva servern redan kör måste den gamla processen startas om för att läsa de utbytta Python-filerna. Stoppa den process du faktiskt startat på ett kontrollerat sätt; ta inte bort `.runtime` eller användarprojekt.

## Tester

- 16 automatiska Python-tester PASS: inklusive opt-in, chefsplacering, rätt station, normal slutförd granskningsrapport och 429-paus. Ingen nättrafik i testerna.
- JS-syntax PASS; Chromium med falska API-svar PASS för Gemini-mandatskontroll, Inställningar, Codex 2/4 och arbetsbilagor.
- **Ej verifierat:** verkliga Google-anrop, Googles plan eller faktureringsstatus, Ubuntu/Firefox med riktig server, dagligt reset i en verklig anslutning, verklig projektkö och samtidiga Codex-processer.

## Nästa tekniska prioritet

Integrera de befintliga v0.12.10-tilläggen i den vanliga `backend/server.py` så att samma kommando fungerar i alla versioner. Därefter testa på riktigt i Firefox, rapportflödet och gratis-API:t i en isolerad testproduktion. Inga GitHub-ändringar utförs av detta paket.
