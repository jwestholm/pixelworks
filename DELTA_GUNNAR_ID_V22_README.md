# Pixel Works – Gunnar och äldre agent-ID / v2.2

**Bas:** `jwestholm/pixelworks`, `dev` commit `fb70d1c9a927e07e802537c83705db5b8f9876cd`, med lokalt installerade deltor till **v2.1**. Ingen GitHub-push, ingen automatisk migrering, inga AI-anrop.

## Installera

1. Säkerhetskopiera eventuella egna ändringar i `src/main.js`.
2. Packa upp denna ZIP **direkt i Pixel Works-projektrot**, där `index.html` ligger. Skriv över `src/main.js`. Den nya filen `src/pw-agent-help-bridge.js` läggs till.
3. Uppdatera Firefox med `Ctrl+F5` och mobilen genom att ladda om sidan. Serveromstart behövs **inte** för dessa JS-ändringar.
4. Öppna projektet med Gunnar, tryck på honom eller **Prata med Gunnar**. Om en äldre, öppen arbetsrapport säger att han behöver hjälp ska samma hjälpärende öppnas med rätt knapp för åtgärd.

## Vad som rättas

Äldre avdelnings-/anställnings-ID kan finnas kvar i projektets arbetsrapporter trots att personalvyn senare använder ett nytt gemensamt agent-ID. Den gamla koden försökte alltid öppna dialogen på sprite-ID och visade då `Okänd anställd` / `Ingen registrerad session`.

- Hjälp och arbetsrapporter hämtas **endast för aktivt projekt** från redan befintliga `GET /api/projects/<slug>/help`.
- Matcha först rapportens **exakta agent-ID**. Om det misslyckas: koppla endast till en **enda entydig** träff med samma namn inom samma projekt (t.ex. Gunnar). Inga rapport-ID:n, personalfiler eller Git-filer skrivs om.
- Finns flera gamla hjälpärenden under samma namn, visas en förklaring och genväg till **gemensamma beslutsinkorgen**. Ingen gissning om rätt ärende.
- Om inga hjälpärenden finns, matchas den uppdaterade personalens ID. Annars visas ett begripligt meddelande och en väg till beslutsinkorgen, inte en falsk identitet.
- Vanlig klickning på anställd utan hjälpbehov fortsätter att öppna agentkortet. Dra-flytta-funktionen lämnas orörd.
- Bakgrundsöppning av dialogen startar **inga AI-jobb** och godkänner inget automatiskt.

## Testning

Kör `python3 tests/browser_agent_identity_v22.py` i en miljö med Playwright och Chromium (på en vanlig Ubuntu-installation kan binärsökvägen behöva justeras). Testet använder enbart påhittade API-svar och skriver inte till projektfiler.

Sju browser-scenarier: historiskt rapport-ID, entydigt nytt personal-ID, dubbelnamn, direktklick på Gunnar med hjälp, direktklick utan hjälp, projektisolering och tydlig fallback om personen inte längre finns i listan. `node --check` körd på båda JS-filerna.

**Inte live-testat:** Ditt verkliga projekt `Hackertoolkit`, dess historiska rapport-ID:n eller telefon+Firefox samtidigt. Att ett namn ersatts av ett ID är en hypotes som matchar den observerade koden; inga privata projektdata finns i denna ZIP.

## NOW / NEXT / LATER

- **NOW:** Fixa klick- och samtalsvägen till ett befintligt hjälpreport även när äldre agent-ID används. Inga dataförändringar.
- **NEXT:** Skapa ett serverägt, explicit identitetsregister för agenternas migreringar (`previous_ids`), så namnmappning aldrig behövs. Enhetligt dialogflöde för alla personalåtgärder.
- **NEXT:** Separera och märk tydligare *projektets delade serverstatus* från varje telefons/dators egna browser-session. Två samtidiga klienter delar projekt och arbetsorder, men har varsitt valt jobb, öppna rutor och formulär. Detta paket förändrar inte samarbets-/låsbeteendet.
- **LATER:** Realtidsdelning mellan flera klienter med serverhändelser och versionskontroll på samtidiga ändringar, utan att skriva över varandras beslut.
