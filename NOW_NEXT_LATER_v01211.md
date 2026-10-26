# Pixel Works 0.12.11 — projektstatus

## NOW — implementerat / lokalt testat

- [x] Ny spelstart i två fält, avancerad guide kvar.
- [x] Startteam direkt i nya spel: chef + programmerare; Gemini om global token finns.
- [x] Ett tydligt godkännande vid snabbstart, synlig mandatknapp i äldre projekt.
- [x] Projektbyte med ihågkommet senast valt spel och nyast först.
- [x] Projekt-API visar `needs_attention` för skadad metadata utan dataförlust.
- [x] Gemensam Gemini-token, Visa/Dölj, Spara, Testa anslutning, ärlig status.
- [x] Gemini i chefens ordinarie arbetskö med lokalt säkerhetstak och ej verifierade resultat.
- [x] Endast `backend/server.py` är avsedd startfil (OBS: kräver originalets blob i lokal Git-klon).
- [x] Offline-regressionstester och offline-Chromiumtest passerade.

## NEXT — test på riktig Ubuntu/Firefox

- [ ] Verifiera att användarens Git-klon verkligen innehåller 0.12.0.9-originalblobben.
- [ ] Verifiera att server.py start/stop/status fungerar på samma lokala miljö.
- [ ] Kontrollera varför det tidigare nya projektet saknades; jämför `projects` och `needs_attention`.
- [ ] Kontrollera sparad Gemini-token och explicit modellmetadatakontroll mot Google.
- [ ] End-to-end-test: arbetsledare -> docs-uppdrag -> Gemini -> rapportgranskning.
- [ ] Förbättra startfilen till **helt fristående server.py** utan Git-historikberoende.
- [ ] Förenkla resterande menyer och DEMO-texter efter speltest.

## LATER

- [ ] Fler AI-motorer via utbytbara adaptrar, under gratis-/kvotbegränsningar.
- [ ] Rekryteringsbyrå, färdigheter, karaktärsutveckling och personalens spelanimationer.
- [ ] Mer fördjupad nybörjarguide med visuell introduktion utan tekniska dialogs.
