# Pixel Works v0.13.4 – Produktionsplaner och första spelbara grund

**Basversion:** v0.13.3. Packa upp DELTA-filerna ovanpå din lokala Pixel Works-installation. Kör sedan `python3 backend/server.py` och ladda om Firefox med Ctrl+Shift+R. Inga installationsskript eller GitHub-ändringar ingår.

## Vad som ingår

### 1. En samlad granskning av Chefens produktionsplan

- Chefen använder fortfarande **lokal Codex CLI i `read-only`** för att föreslå 1–8 konkreta arbetsordrar med station, instruktion, prioritet och beroenden.
- När planen innehåller **fler än en arbetsorder** skapas uppgifterna som **utkast**. De startar inte ens om arbetaren dras manuellt till bordet eller om någon försöker starta ordern direkt via jobb-API:t.
- Högerpanelen **Arbetsledarens produktion → Granska produktionsplan** öppnar en redigerare för ansvarig person, rubrik, instruktion, prioritet, ordning och beroenden. Välj **Godkänn och starta produktionen** en gång för hela planen; inget ytterligare per-arbetar-godkännande tillkommer.
- Servern validerar samtliga steg, stationernas personalbehörigheter, beroendeordning och versionsnummer **före en enda atomisk arbetsköskrivning**. Ett ogiltigt utkast ska inte sparas halvvägs.
- Befintliga **v0.13.3-order** fortsätter enligt sina tidigare regler. Endast nya flerstegsplaner omfattas av utkastgranskningen.
- När ett nytt spel saknar programmerare (vanligt om **gemensam studio** har aktiverats) visas *Ingen behörig medarbetare* och en genväg till **Min studio** för att tilldela personal till just det projektet. Tilldelningen startar inte jobb av sig själv.

### 2. Nytt projekt får spelbar startprototyp **automatiskt**

- Ett nytt projekt får fortfarande sin Game Bible med spelarens egna val och målgruppsregler via den befintliga projektmotorn.
- Utöver Game Bible skapas i **nya projekt** fasta, säkra filer `work/index.html`, `work/style.css`, `work/game.js` och ett avsnitt i Game Bible som anger att koden är en **startprototyp**.
- Namn/genre/idé med *Minesweeper* eller *minröjare* väljer en enkel **8×8 minröjare** med tio minor, flaggning, förstaklicksskydd, vinst och omstart. Övriga idéer får en **generisk stjärnjakt**. Den är **inte** en automatiskt AI-designad version av användarens spelidé.
- De nya filerna och de två ursprungliga projektdokumenten sparas som **en lokal Git-commit** i det nya spelets `work/`. Detta ger Codex-schemaläggaren den första `HEAD` som krävs för isolerade arbeten.
- **Inget Codex/Gemini-anrop** sker när spelprototypen skapas. Koden är en deterministic HTML5-mall och inte ett färdigt AI-resultat. Klicka på **🎮 Spela** för att testa den.
- **Befintliga projekt ändras inte vid uppstart eller uppdatering.** Om ett äldre projekt har tom spelmapp (bara de ursprungliga `AGENTS.md` och `README.md`) visas en uttrycklig **Skapa spelbar grund**-knapp i högerspalten. Om det redan finns annat spelarbete skriver funktionen inget.
- Om första Git-commiten inte lyckas visas en felstatus i projektstartens serversvar; ingen falsk färdigmarkering sätts. Befintliga arbetsresultat skrivs aldrig över.

## Kända begränsningar

- En **godkänd plan** börjar automatiskt enbart om det finns behöriga anställda, tillräckliga verktyg, en aktiv projektmandatinställning, godkänd Git-arbetsyta och uppfyllda beroenden. Detta är inte en garanti för att Codex kan köra i just din lokala installation.
- Ett nytt projekt i **delad studio** är inte automatiskt bemannat. Flytta en befintlig anställd via **Min studio**, eller anställ en ny. Programmets uppgift blir inte körbar förrän detta är gjort.
- Inga personliga API-nycklar, sparade spelprojekt, privata data eller GitHub-ändringar ingår i ZIP-filen.
- Ingen verklig AI-körning har gjorts här. JSON-planens schema och slutresultat valideras lokalt; spelets hela regressionssvit innehåller äldre kända fel utanför den riktade testningen.
- Det finns ännu två schemaläggningslager under delar av arbetsledarfunktionen. En gemensam transaktionell produktionsmotor är fortfarande NEXT.

## Testning av denna leverans

- **28 offline-backendtester** godkända, inklusive nya tester för automatiskt HTML5-projekt, säker återanvändning av äldre projekt, Git-initiering, planutkast, godkännande, felaktiga beroenden, behörighet och samtidig planredigering.
- **Chromium-prototyptest:** den genererade minröjaren går att klicka och återställa; den generiska prototypen går att spela. JS kördes som genererat innehåll i isolerad testmiljö.
- **Chromium-gränssnittstest:** planredigeraren öppnas, visar två arbetsuppgifter, sparar rätt instruktion till rätt projektendpoint utan JS-fel – **med simulerade API-svar**.
- Python- och JavaScript-syntax samt deltaarkivets filintegritet kontrollerade.

## Prova med Minesweeper marathon

1. Installera ovanpå v0.13.3, starta backend, Ctrl+Shift+R.
2. Öppna **Minesweeper marathon**. Om `work/` är nästan tom syns **Skapa spelbar grund**. Om spelet redan har egen kod lämnas den ifred.
3. Öppna **Min studio** och se till att Gunnar/annan programmerare faktiskt är tilldelad detta spel.
4. Skapa en ny plan vid **Arbetsledning**. När Chefen har svarat, öppna **Granska produktionsplan** i högerspalten.
5. Kontrollera bemanning och beroenden; godkänn hela planen en gång. Spelutveckling, verkliga programmeringsresultat och tester följer den säkra arbetskön.
