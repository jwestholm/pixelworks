# Pixel Works v2.8 – en enda global personalvy

**Git-bas:** `jwestholm/pixelworks`, `dev`, `fb70d1c9a927e07e802537c83705db5b8f9876cd` (2026-10-29 #1).  
**Förutsättning:** v2.7 installerad ovanpå föregående deltor; `WORKFORCE_V27.json` kan vara ej aktiverad.  
**Typ:** minimal klientdelta – `src/main.js` ersätts, `src/pw-global-people-v28.js` läggs till. Ingen serverändring, AI-körning eller ändring av projektdata.

## Felet från inspelningen 2026-10-30 13:29:51

* **Min studio** hämtade hela personallistan via `pw_v013`, men **Agenter → Lokal studio** landade i `local.js` gamla `hireScreen(slug)` och visade bara det markerade spelets medarbetare.
* En gammal `pw24`-filterinställning kunde fortsätta begränsa personallistan vid återöppning.
* I inspelningen stod **"Granska och aktivera global personal"** i Min studio. Den globala v2.7-arbetsmotorn var alltså ännu inte aktiverad vid inspelningen. V2.5-personregistret och global kontorsvy innebär inte i sig att arbetsmotorn är migrerad.
* Projektvalknapparna inne i personaldialogen blandade ihop projektfokus med arbetsstyrkans identitet.

## Vad v2.8 gör

1. **Agenter**, **Personal** och personalgenvägar öppnar samma globala Min studio-dialog. Du ser alla 15 personer oberoende av valt spel.
2. Gamla personalknappen i **Lokal studio** använder också den globala listan. Den separata projektverktygsdelen finns kvar för verkliga projektfunktioner.
3. Projektbyte sker via spelets projektmeny. Personalfönstret visar **nuvarande arbetsprojekt** för varje person, men byter inte automatiskt vilket spel du tittar på.
4. Den valfria personalfiltreringen nollställs till **Alla projekt** vid ny öppning och kallas tydligare **Arbetsprojekt (valfritt filter)**.
5. Högst upp visas **Global arbetsmotor AKTIV** eller **AKTIVERING ÅTERSTÅR**, hämtad från `/api/pw-v027/workforce`.
6. Innan aktivering är projektbundna **flytta/avskeda**-kontroller i personalvyn låsta: annars kunde den oförändrade v2.5-migrationslistan komma ur synk med gamla `STAFF.json`.
7. Efter aktivering går det fortfarande att **Byt arbetsprojekt** på ett bekräftat sätt och att avskeda individuellt via de existerande verifierade funktionerna. Rekrytering sker från Min studio med val av **första arbetsprojekt** som adapter; personen anställs i företaget och får stabilt `studio_id`.
8. Ingen global identitet bestäms genom namn. Två Gunnar är fortfarande två separata personer.

## Installation

1. Säkerhetskopiera gärna hela `~/.pixelworks` och Pixel Works-katalogen före ändringar.
2. Packa upp delta-ZIP **direkt i projektroten** där `index.html` ligger. Skriv över `src/main.js`, lägg till `src/pw-global-people-v28.js`. Övriga filer är endast tester och den här README:n.
3. Ladda om Firefox med **Ctrl+F5**, uppdatera även mobilens sida. **Ingen serveromstart krävs för just v2.8** om v2.7-backend redan är installerad och servern omstartad efter den installationen.
4. Klicka på **Agenter** eller **Min studio** och kontrollera att **alla 15** finns.
5. Kontrollera informationsrutan. Om det står **AKTIVERING ÅTERSTÅR**: använd **Granska och aktivera global personal**, kontrollera alla studio-ID:n och godkänn. Aktivering kan stoppas av pågående eller felaktigt aktiva jobb enligt v2.7. Låt i så fall arbetsorder kontrolleras innan du ändrar projekt-/personalfiler.
6. Välj sedan person och nytt **arbetsprojekt** i den globala personallistan. Projektfokus i kontoret ska förbli oförändrat tills du själv väljer ett annat spel via Projekt.

## Testat / ännu inte verifierat

**Testat:** Chromium i 1366×768 och 390×844 med 15 fiktiva anställda och flera identiska namn; båda gamla personalingångarna öppnar global lista; aktivt spel bevaras; personfilter återställs; v2.7-aktiveringsflödet kan öppnas; innan aktivering är flytt/avsked låst; därefter kan personal rekryteras endast efter uttryckligt klick. Ingen server-/AI-skrivning under normal navigation. Regression: 14 v2.7-backendtester godkända.

**Ej verifierat på din maskin:** den riktiga Firefox-menyn, faktiska globala `WORKFORCE_V27.json`, Codex/Gemini i aktivt arbete eller klienter på mobil + PC samtidigt. Inga riktiga AI-anrop eller GitHub-pushar gjorda.

## NOW / NEXT / LATER

**NOW:** en samlad global personalvy med enhetliga ingångar. Aktiveringsstatus ska vara sanningsenlig och gamla personaloperationer låsta tills arbetsmotorn är migrerad.

**NEXT:** central schemaläggning där Chefen hämtar kompetens från hela studions personalpool och väljer vilket spel en anställd ska arbeta med **per uppdrag**, utan manuell varaktig projekttilldelning. Lägg till central paus/aktiv-status per spel och eliminera Skjutbanans upprepade valideringsförsök. Stöd konfliktfri flerklientssynk via serverrevisioner.

**LATER:** ta bort alla gamla projektbundna personal- och jobb-ID-format först när arbetsorder, hjälp, rapporter och historik är verifierat migrerade. Bevara original och säker återställningsväg.

**Begränsning:** v2.8 förenar menyingångarna, inte själva resursplaneraren. V2.7 har fortfarande **en aktiv arbetsprojekttilldelning per person**. Det är en tilldelning, inte en separat anställning. Radera inte de gamla `STAFF.json` manuellt: de används som historiska återställningskopior och äldre modulvägar kräver fortfarande kompatibilitet.
