# Pixel Works v1.9 – AI-personalens tillgänglighet

**Bas:** `dev` `fb70d1c9a927e07e802537c83705db5b8f9876cd` (**2026-10-29 #1**) med de tidigare installerade delta-paketen **fram till v1.8**.

## Installation

1. Kontrollera att v1.8 (Gemensamma dialoger) redan är installerad.
2. Packa upp ZIP-filen direkt i projektroten där `index.html` ligger. Skriv över `src/main.js`.
3. Gör en hård omladdning av webbsidan (`Ctrl+F5`). Serveromstart behövs **inte** för denna frontendändring.
4. Öppna ett verkligt projekt med en Gemini-anställd och kontrollera sidopanelen **Personalläge**.

## Vad ändras?

- Var 12:e sekund läser klienten **befintligt** `/api/providers` via Pixel Works lokala backend. Ingen Gemini-kvot förbrukas för denna statusläsning.
- Vid **429 / verifierat kvotfel**: Gemini-personalen visas som **hemgången** och tar inga nya uppdrag. Resettid visas inte om Google inte verifierat den.
- Vid **HTTP 503 / tillfälligt API-fel**: Gemini-personalen visas vid fikabordet med systemnotisen **Kan inte arbeta · API-paus**. Det är ingen AI-genererad replik och ändrar inte agentens serverlagrade stationsplacering.
- Vid annan ej verifierad Gemini-status: personen markeras blockerad utan påhittad förklaring.
- När `can_send` och `execution_enabled` åter är `true`: notisen tas bort och personen visas i kontoret igen.
- Agentkortet har samma aktuella förklaring. Länken **Gemini-inställningar** öppnar det existerande anslutningstestet.
- Befintliga aktiva jobb visas fortfarande som pågående tills servern faktiskt rapporterar att de slutat; klientsidan avslutar **aldrig** ett verkligt jobb.
- Ingen ändring av serverns godkännanden, scheduler, API-nycklar, sparade personalprofiler eller projektfiler.
- Simulerade projekt får inte denna verkliga leverantörsstatus.

**OBS:** Detta är en synlig/visuell närvarostatus. Backend hindrar redan nya Gemini-jobb när `can_send=false`. En äldre serverpaus kan kräva ett nytt lyckat Gemini-test innan `can_send` åter blir sant. Paketet ändrar inte gamla paus-/retryregler eller gissar när Googles tjänst återställs.

## Ändrade filer

- `src/main.js` – exakt en ny importrad ovanpå **v1.8**.
- `src/pw-provider-presence.js` – ny återanvändbar statusmodul.
- `tests/test_browser_presence.py` – offline regressionstest (behöver Playwright och Chromium).
- `DELTA_PERSONALSTATUS_V19_README.md` och `DELTA_PERSONALSTATUS_V19_MANIFEST.json` – dokumentation.

## Testat

- `node --check` på båda JavaScript-filerna.
- Chromium med fejkade lokala `/api/providers`-svar: HTTP 503 → fikabord, 429 → hemgång, lyckad återanslutning → tillbaka, agentkort, Gemini-inställningsknapp, Codex-personal oförändrad.
- **Inte testat:** verklig Google-API-tillgång eller din Ubuntu-/Firefox-installation. Ingen nätverksbegäran till Google gjordes i testerna.

## NOW / NEXT / LATER

**NOW:** Faktisk Gemini-status blir synlig i personal och kontor; inga nya AI-anrop från statusmodulen.

**NEXT:** Samma närvarokomponent för övriga leverantörer, eventlogg för plötsliga avbrott samt tillförlitlig 503-paus/återhämtningspolicy i backend.

**LATER:** Spelanimation när en arbetare lämnar kontoret, rollbaserade arbetsersättare, valbar automatisering och mer generiska leverantörers undermodeller.
