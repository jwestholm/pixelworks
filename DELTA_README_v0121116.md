# Pixel Works v0.12.11.16 – Försök igen på chefens ärenden

**Basversion:** v0.12.11.15. Detta är en **delta-ZIP**, inte en fullständig installation.
Packa upp i Pixel Works-katalogen, starta som vanligt med `python3 backend/server.py` och uppdatera Firefox med Ctrl+Shift+R.

## Ändrat

- Chefens blockerade rapport får en **🔄 Försök igen**-knapp direkt i rapportdialogen.
- Ett klick granskar samma **redan existerande väntande arbetsorder** som chefens rapport refererar till. Inga nya order skapas.
- Om fler order hör till rapporten väljer spelaren uttryckligen vilken som ska startas.
- När projektmappen eller den tilldelade arbetaren fortfarande är upptagen visas skälet i rapporten. Knappen kan användas igen efter att hindret upphört.
- När arbetet kan starta används befintlig personalbaserad delegering och respektive adapters säkerhetskontroller, samtycke och kvoter.
- Programmerare flyttas till rätt arbetsbord innan jobbet startar. Om jobbet inte startar återställs placeringen om personen inte är upptagen.
- Efter framgång visas **Startat** och knappen avaktiveras tills rapporten öppnas på nytt. Ytterligare klick utan en väntande order kan inte skapa dubbletter.

## Begränsningar

- Knappen **överskrider aldrig** låsta Git-arbetsytor och tvingar inte fram parallell skrivning i samma projektmapp.
- Den äldre kömotorn kontrollerar fortfarande kvarvarande arbetsorder automatiskt; denna knapp ger en manuell omkontroll utan väntan på dess interna omförsöksintervall.
- Historiska chefsrapporter utan en länkad väntande order svarar att ärendet redan är klart. De ändras eller raderas inte.
- Ett nytt försök kan fortfarande stoppas av studiotillstånd, stationsbehörighet, arbetsverktyg eller verklig API-kvot.

## Validering

- 11 riktade nya backendtester: godkända.
- 19 befintliga regressionstester för paralell schemaläggning och granskningsstatus: godkända.
- Ett Chromium-test: blockerad -> försök igen -> startad, utan dubblett: godkänt.
- `python -m py_compile` och `node --check`: godkända.
- Ingen verklig Codex-/Gemini-körning eller skrivning till användarens projekt har utförts under testen.

## Filer

- `backend/pw_v01210.py` – laddar den nya korrigeringsmodulen.
- `backend/pw_v0121112.py` – kan välja en exakt redan väntande arbetsorder vid omförsök.
- `backend/pw_v0121116.py` – säkert retry-API.
- `backend/test_pw_v0121116.py` – backendregressionstester.
- `src/pw-v012116.js` – knapp och status i chefens rapport.
- `DELTA_README_v0121116.md`, `NOW_NEXT_LATER_v0121116.md`, `DELTA_MANIFEST_v0121116.json` – dokumentation.

**Oförändrat:** `backend/server.py`, projektdata, AI-nycklar och GitHub.
