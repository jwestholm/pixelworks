# Pixel Works v0.12.11.15 – tydlig spelstart och parallella arbeten

## Installera

Applicera denna **delta-ZIP direkt ovanpå v0.12.11.14**. Det här är endast ändrade och nya filer, inga speldata, projektmappar, hemligheter eller installationsskript. Inga GitHub-åtgärder görs. Starta som tidigare:

```sh
python3 backend/server.py
```

Uppdatera sidan med Ctrl+Shift+R. Kontrollera att rubriken visar v0.12.11.15.

## Ändringar

- **Nytt spel:** Nytt projekt öppnar nu ett uttalat val **🎲 Bygg med spelguiden** eller **✍️ Skriv min egen spelidé**. Guiden använder de befintliga valen i `src/studio.js` för bland annat genre, värld, karaktär, spelmekanik, målgrupp och grafik. Manuell väg använder snabbstarten med namn och idé. Att öppna valet gör inga externa AI-anrop.
- **Parallell delegering:** Det slutliga personalbaserade planeringslagret tilldelar oberoende uppdrag utan att låta ett rådgivande AI-jobb låsa all kodplanering. En anställd kan ha ett aktivt jobb åt gången; andra kan jobba i separata arbetsuppgifter.
- **Textarbete versus filarbete:** Rådgivande Gemini-jobb (som *inte skriver i work/*) markeras `advisory_only` och separat från skrivjobb i de säkerhetskontroller som annars misstar rådgivningen för en direkt Git-skrivare.
- **Två kodarbetare:** Kodsamtidighet tillåts bara med Git-worktrees som basmotorn kan förbereda/verifiera. Ingen ändring av Codex sandbox, skrivmandat, konfliktkontroll eller Git-push-regler.

## Teststatus

- `backend/test_pw_v0121115.py`: **7 tester godkända**. Verifierar urval (specialist före motor), parallell Gemini + Codex, två Codex-arbetare, skydd vid osäker Git och avsaknad av arbetsledare.
- `test_creator_browser.py` (inte distribuerad i delta): **Chromium-kontroll godkänd** för både Wizard- och manuell väg samt returknappen.
- JavaScript `node --check` och Python `py_compile`: **godkända**.
- Äldre tester har kända inkompatibiliteter från tidigare versioner, bland annat för en **redan avskaffad** lokal Gemini-kvot. Den tidigare samlade testsviten är inte grön. Ingen riktig Codex-/Gemini-session eller Firefox-installation har provkörts i denna testmiljö.

## Viktiga gränser

- Det går fortfarande inte att skicka *flera Gemini-anrop samtidigt* via en och samma adapter. Den skyddar den delade anslutningen genom att tillåta ett aktivt textanrop åt gången. Däremot kan en **Codex-arbetare och en Gemini-arbetare** jobba samtidigt.
- Om två programmerare ändrar överlappande filer kan ett säkert Git-försök fastna i **granskning**. Inga ändringar får tvingas ihop.
- Att en projektmapp saknar godkänd studioåtkomst, en fungerande AI-anslutning eller ett redo Git-läge ska fortfarande blockera motsvarande körning.

## Ändrade filer

- `src/pw-v01211.js` – tydlig start: Wizard / egen idé.
- `backend/pw_v01210.py` – klassificera rådgivande jobb som icke-filskrivande; installera ny personalplanerare.
- `backend/pw_v0121115.py` – parallell, rollbaserad uppdragsplanering.
- `backend/test_pw_v0121115.py` – riktade offline-regressionstester.
