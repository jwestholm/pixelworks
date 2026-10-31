# Pixel Works – Studioidentitet och hjälp över projektgränser (v2.3)

**Installeras ovanpå v2.2.** Git-bas: `jwestholm/pixelworks`, `dev` = `fb70d1c9a927e07e802537c83705db5b8f9876cd` (kontrollerad 2026-10-30). Endast en befintlig JavaScript-fil byts ut. Ingen backendfil, personalfil, spelkod, Game Bible, API-nyckel eller rapport ändras vid installation.

## Varför förra fixen inte räckte

Inspelningen 2026-10-30 09:01:58 visar **5 spel och 15 personalposter** och flera separata Gunnar/Greta/Chefen. Den gemensamma studion (`src/pw-v013.js`, `backend/pw_v013.py`) sammanför **personalvyn**, inte alla personer till en global individ. Vid `transfer()` kan en anställd behålla sitt `studio_id` men få nytt projektlokalt `id`. Arbetsrapporter och historiska hjälpbehov stannar i det gamla projektet. Därför räcker det inte att slå upp ett namn i aktivt projekt; även två olika anställningar kan heta Gunnar.

**Detta paket sammanför INTE automatiskt personer med samma namn.** Det skulle kunna koppla fel uppdrag och historik till en annan anställd. En fullständig, användarstyrd personalkonsolidering och eventuell migrering av historiska ID kräver en separat backendändring med backup och förhandsgranskning.

## Fix NOW: Hitta rätt ursprungsärende

- **Min studio → 💌 Alla hjälpärenden i studion.** Samlar verkligt öppna hjälpärenden från alla projekt, med tydliga **projekt + rapport-ID + ursprungligt agent-ID**. Ingen AI-anrop, inga POST vid öppning.
- Vid tryck på en anställd används i första hand **exakt projekt-ID + exakt agent-ID**. Finns ett sådant hjälpärende öppnas den redan befintliga hjälpdialogen.
- Om det finns äldre ärenden med samma namn, men inte samma ID, öppnas **en urvalslista**. Inga dolda namnmatchningar.
- Välj rätt **Gunnar · Hackertoolkit** eller **Gunnar · Pussel** och öppna exakt rätt projekts hjälpvy. Beslutet skickas fortfarande till det ursprungliga projektet.
- Om hjälpärendet saknas öppnas normal samtalsvy för den verkliga anställda, förutsatt att dess ID fortfarande finns i aktuell personalfil. Annars ett tydligt fel med förklaring, inte ”Okänd anställd”.
- Om ett projekt inte kunde läsas får du en varning om att listan är **ofullständig**.
- Om flera öppna ärenden har samma agent-ID i samma projekt skickas du till projektets gemensamma beslutsinkorg, eftersom den äldre hjälpdialogen väljer första ärendet per agent. Ingen falsk säkerhet om exakt rapport.

## Installera

1. Se till att v2.2 är installerad, så att `src/main.js` redan innehåller `import './pw-agent-help-bridge.js';`.
2. Packa upp ZIP-filen direkt i **Pixel Works rot där `index.html` ligger** och skriv över `src/pw-agent-help-bridge.js`.
3. Kör `Ctrl+F5` i Firefox och ladda om webbläsaren på mobilen. Python-servern behöver inte startas om.
4. Öppna **Min studio** → **Alla hjälpärenden i studion**. Leta upp projektnamnet och rätt rapport. Testa sedan att klicka på Gunnar i det relevanta projektet.

## Tester

Kört: `node --check src/pw-agent-help-bridge.js` och `python tests/browser_studio_identity_v23.py` med Playwright/Chromium, **7 scenarier godkända**: global vy och två Gunnar, explicit projektval, direkt ID-träff, äldre ID med manuell urvalslista, vanlig samtalsväg, föråldrat ID utan namn-gissning och delvis misslyckad datahämtning. Mobilbredd 390 px kontrollerad.

**Inte verifierat:** riktiga rapport-ID:n och faktisk personalfördelning hos användaren, simultan mobil/dator samt produktionsservern med dess nuvarande nätverksstatus. Den här fixen gör inga verkliga API-/AI-anrop under testerna.

## NOW / NEXT / LATER

**NOW:** Säkert åtkomlig hjälp med ursprungsprojekt och original-ID. Alla 15 anställningsposter behålls; inget döljs, raderas eller sammanförs.

**NEXT:** Inventering i backend av unika studio-ID:n, dubbla **personregisterposter** och överföringshistorik. Spelbar sammanläggningsvy där ägaren uttryckligen anger vilka personer som faktiskt är samma person. Förhandsgranska effekten på skills, ansvar, rapporter och pågående uppdrag. Skapa backups och bevara gamla ID:n som alias med projekt/period. **Ingen automatisk matchning på namn.**

**NEXT:** Gör hjälp/dialog/arbete till en serverägd kontext `{studio_id, project_id, agent_id, report_id}`. Dator och mobil läser samma delade projekt och rapportstatus medan öppna fönster och utkast är klientlokala. Konfliktkontroll med versionsnummer vid samtidiga beslut.

**LATER:** Studioövergripande jobbplanerare med en enda aktiv anställning per verklig individ och gemensam, tydlig AI-providerstatus; riktig realtidssynk för flera klienter. 
