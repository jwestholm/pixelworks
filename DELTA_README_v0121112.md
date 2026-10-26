# Pixel Works v0.12.11.12 – Lokal kapacitet och manuell delegering

**Installeras ovanpå v0.12.11.11.** ZIP innehåller endast tillagda/ändrade filer; **ingen GitHub-push, ingen start-/installationsskript och inga spelprojekt**. Kör fortsatt `python3 backend/server.py` från din befintliga Git-klon. Ladda om webbläsaren med Ctrl+Shift+R.

## Rotorsak till stillastående dokumentationsjobb

- För Gemini `gemini-3.5-flash-lite` hade appen ett **lokalt tak 12 anrop per Google-kvotdygn (America/Los_Angeles)**. Detta är **inte** bevis för att Google-kontots faktiska Free Tier är slut. Anropsräknaren finns kvar efter serveromstart.
- Den kompetensbaserade planeringen valde Greta för ett kreativt dokumentationsjobb. Om den lokala anropsgränsen var nådd kunde hon inte starta. Schemaläggaren avstod från att ge Gunnar jobbet automatiskt, med avsikt att respektera specialistens prioritet.
- Manuell placering skickade **inte anställd-ID** till tilldelningsfunktionen. Följaktligen valdes Greta om när Gunnar drogs till arbetsbordet.
- Chefens gamla blockeringsrapport kombinerade "min kapacitet slut" med en inaktuell Codex-specifik text. Därmed lät det som om chefen själv hade slut på resurser.

## Ändringar

1. **Tydlig status per person:** ny lokal kapacitetsdiagnostik, utan förväxling med faktisk Google-/Codex-kvot. När 12/12 lokala anrop använts framgår det uttryckligen.
2. **Manuell tilldelning:** drag till ett arbetsbord skickar den anställdas ID. Det är ett uttryckligt spelarbefäl: personen du flyttar får försöka starta den väntande ordern, även om en annan specialist har högre automatisk ranking. Roll/station/tillstånd/körkapacitet kontrolleras fortfarande. För Codex nyttjas befintlig localhost-API för isolerade Git-worktrees, inte en ny genväg runt sandlådan.
3. **Valbar lokal gräns:** Inställningar → Gemini → "Lokal arbetskapacitet" visar räknaren och låter spelägaren uttryckligen välja 12, 25, 50 eller 100 anrop/dygn. **Standard förblir 12.** Detta gör inga API-anrop, nollställer inte redan använda anrop och innebär INTE att Google lovat någon kvot eller gratis användning. Om Google har blockerat modellen eller verklig kvot är slut kan ingen lokal inställning kringgå det.
4. **Arbetsledarstatus:** blockerade personer redovisas med faktisk lokal orsak i stället för gamla Codex-blockeringar. Inga nya missvisande "chefen saknar kapacitet"-rapporter vid personväntan. Historiska rapporter ändras inte automatiskt; de kan arkiveras via Rapportpärmen.
5. **Personalstatusen i högerspalten:** flyttad från en gammal dold widget till synlig panel.

## Teststatus och begränsningar

- **32 riktade backendtester gröna** (11 nya + 21 från närliggande moduler).
- Chromium-test med mockad status och inställningssparning godkänt. JavaScript- och Python-syntax kontrollerade.
- Det äldre `test_pw_v012115` kräver fortfarande uppdatering för senare Game Bible-arbetsflöde. Den fullständiga generationsövergripande regressionstesten har tidigare fel och är **inte** grön.
- Inga verkliga Codex-/Gemini-anrop gjordes och ingen verklig Firefox-installation kunde testas här.
- Ändrar inte i övrigt äldre arkitekturproblem från kodrevisionen (t.ex. stale review-reconciliation, status "infört" utan Git-diff, parallella schedulerlager).

## Säkerhet

- Avstängd studioåtkomst får fortsatt alltid företräde.
- Endast valbara, begränsade lokala tak. Inga hemligheter i status-API. Ingen betaltjänst eller automatisk modelluppgradering.
- Klick/drag vid väntande order är användarens explicita starthandling. API-tillstånd och projektsäkerhet kontrolleras server-side.
