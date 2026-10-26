# Pixel Works 0.13.8 – Verkliga AI-samtal i fikarummet

**Basversion:** 0.13.7. **Leverans:** ZIP-delta med endast nya/ändrade filer.

## Spelflöde

1. Klicka på **Fikarummet**. Detta är en egen dialog, inte en genväg till Arbetsledning.
2. Välj ett av fem ämnen: *Prata om spelet*, *Kom på idéer*, *Har vi testat ordentligt?*, *Undersök en fråga* eller *Eget samtalsämne*. Fritext är frivilligt utom för **Eget**.
3. Pixel Works söker **två eller tre lediga, projekttilldelade medarbetare** med fungerande Codex-/Gemini-anslutning. En chef deltar om möjligt och får sista repliken. Om färre än två är tillgängliga startar inget låtsassamtal.
4. Varje medarbetare får ett **eget riktigt AI-anrop** och nästa deltagare får läsa de tidigare faktiska replikerna. Två korta rundor, sammanlagt **4–6 anrop per samtal**. Inga textmeddelanden förgenereras av spelet.
5. Samtalet sparas privat i `<projekt>/management/cafe-sessions/`. Klicka på fikabordets pratbubbla för att se replikerna, även efter att popupen har stängts. Kontorets övriga stationstilldelningar ändras inte.
6. Om Chefen faktiskt deltar och avslutar samtalet kan han föreslå **högst två konkreta arbetsordrar** (exempelvis test av spelmekanik). Dessa valideras och skapas i projektets vanliga arbetskö; vanlig behörighets-, personal- och AI-schemaläggning tar över därifrån. Inget påstås vara implementerat eller verifierat av fikadialogen.

## Verkliga AI-anrop

- **Codex:** Den anställdes befintliga lokala CLI, `codex exec --sandbox read-only --json` i projektets `work`-mapp. Skriver inte kod, gör inga Git-pushar.
- **Gemini:** Den redan testade/modellverifierade Google-adaptern. Anropen räknas i den befintliga statistiken. Googles egna kvotfel stoppar rundan utan automatisk återförsöksstorm.
- **Faktabaserad status:** Varje replik kommer från ett verkligt providersvar och är märkt som sådant, **inte oberoende faktaverifierad**. Ett fel ger ett ärligt felmeddelande och eventuell tidigare godkänd del av transkriptet kvarstår.
- **Webbsök:** Fikarummet lovar inte nätåtkomst. Medarbetaren får bara ange verifierbara källor om respektive arbetsverktyg faktiskt har kunnat öppna dem. Ingen påhittad faktakontroll.
- **Kostnad:** 4–6 verkliga modellförfrågningar kan belasta användarens leverantörskvot eller fakturering. Inga betalda fallback-modeller aktiveras automatiskt.

## Säkerhet och kompatibilitet

- Fika kräver befintligt studiotillstånd och projektets arbetsmandat, men lägger **inte** till ett nytt godkännandefönster för varje replik eller intern uppföljningsorder.
- GET är endast status/pollning, aldrig en AI-anropsstart. Bara ett uttryckligt topic-klick gör en POST som startar en session.
- Projektidentiteten är strikt validerad. Tidigare arbetande anställda väljs inte till fika; fikadeltagare reserveras medan deras samtal pågår.
- Samma `request_id` kan inte skapa dubbla sessioner eller dubblettordrar. En session per projekt åt gången.
- Om servern startas om under en session markeras den som **avbruten** vid nästa visning; inget AI-svar hittas på och ingen automatisk omkörning sker.
- Ingen ändring av befintlig `backend/server.py`, egna projektfiler, Game Bible, API-nycklar eller GitHub.

## Installera

Packa upp ZIP ovanpå **Pixel Works 0.13.7**, utan att ta bort befintliga filer. Starta därefter:

```sh
python3 backend/server.py
```

Uppdatera webbläsaren med Ctrl + Shift + R. Klicka på **Fikarummet** och välj ett ämne.

Om du ser meddelandet att två medarbetare saknas, öppna **Min studio**, tilldela minst två medarbetare till det aktuella spelet och verifiera respektive AI-anslutning under Inställningar. De kan använda samma Codex-installation som separata anställda; olika leverantörer är inte ett krav.

## Verifierat i leveransen

- 60 riktade backendtester passerar i samma körning (12 nya fikarumstester).
- Chromium-test: fika öppnas från fikabordet; topic skapar exakt en session; olika medarbetarbidrag återges korrekt; tidigare vanliga stationer kan fortfarande öppnas.
- Python-kompilering, Node-JavaScript-syntax, ZIP-innehåll och SHA-256-manifest kontrollerade.
- **Inte liveverifierat:** riktiga Codex/Gemini-samtal, modellåtkomst, kostnad, faktisk webbsökfunktion och användarens Firefox-miljö.

## Ändrade/nya filer

- `backend/pw_v013.py` – installerar ny modul efter befintlig 0.13-serie.
- `backend/pw_v0138.py` – ny sessionmotor, adapteranrop, transkript, säkerhets-/kvotkontroll, uppföljningsorder och två nya API-vägar via GET/POST samma path.
- `src/pw-v0121118.js` – ny fikarumsdialog och markering i kontoret; övriga skrivbordsmenyer oförändrade.
- `src/pw-v013.js` – uppdaterat versionsmärke.
- `backend/test_pw_v0138.py`, `test_browser_0138.py` – riktade regressionstester.
