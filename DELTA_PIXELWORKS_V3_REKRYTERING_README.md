# Pixel Works v3.0 – Rekryteringsbyrån (spelbar första version)

**Byggbas:** `jwestholm/pixelworks` · `dev` · `fb70d1c9a927e07e802537c83705db5b8f9876cd` (2026-10-29).  
**Förutsätter:** dina tidigare installerade deltor t.o.m. **v2.8** inklusive fungerande server från v2.7.  
**Typ:** minimal ZIP att lägga över Pixel Works-projektroten. Inga GitHub-ändringar.

## Vad du får

- Ett helt nytt **Personal & rekrytering** i samma spel, utan koppling till ett särskilt spelprojekt.
- **En Chef från start**, och sex unika rekryteringskandidater: **Joppe, Siv, Nisse, Mira, Vera, Lova**.
- Välj först **yrkesroll** (programmerare, pixelgrafiker, ljudproducent, QA, berättare, research eller allroundare), och bläddra fritt bland kandidaterna. Samma kandidat kan anställas i *vilken roll som helst*, även där personen har låg lämplighet.
- Varje person har **fast karaktär, egenhet, talstil och grundskills** (låsta), medan **roll och företagets arbetsbeskrivning** kan ändras efter anställning.
- Visa **Bäst lämpad för / OK på / Bör ej / Får ej / Kan inte just nu**. `Får ej` är en behörighetsgräns, inte ett spelvärde; i demot är externa kostnader och publicering spärrade.
- **Arbetsintervju (DEMO)** med fiktivt, rollanpassat textsvar, statisk gorillaskiss för grafikrollen och lokalt Web Audio-ljudexempel för ljudrollen. Allt märks DEMO och använder **inga riktiga AI-anrop**.
- **Anställ**, redigera arbetsroll/arbetsbeskrivning, **avskeda** efter bekräftelse eller återanställ samma person. **Endast spelaren** kan godkänna anställning/avskedning.
- Nya anställda syns som individuella, klickbara figurer på **samma kontorsgolv**, oavsett vilket spelprojekt som är markerat. Vi återanvänder kontorets sprite-animationer.
- Nya personalobjekt har `person_id`, `role`, `skills`, `worker`, och ett **låst `persona_contract`** redo att ges till en framtida verklig AI-motor. **Ingen** modell kopplas in i denna version.
- Samma serverlagrade personallista och revision används av mobil/dator. Konflikter vid samtidiga personaländringar ger ett tydligt fel; inga ändringar skrivs över tyst.

## Mycket viktigt: hur bytet fungerar

**Installationen ändrar inte gamla personaldata.** Den nya personalvärlden aktiveras först när du själv väljer **"Starta nya personalstudion"**.

När du godkänner starten:
1. En helt ny fil `~/.pixelworks/studio-v3/CREW.json` skapas med endast **Chefen**. Detta är v3:s personalstyrka.
2. Alla gamla 15 personposter, projektens `STAFF.json`, historiska rapporter och Git-arbetsytor **lämnas orörda** och visas inte längre som v3-personal. Detta är en *logisk nystart*, inte radering.
3. **Den gamla bakgrundsschemaläggningen pausas.** Nya Codex-jobb via gamla `/api/jobs` och äldre personaloperationer stoppas. Gamla arbetarobjekt/AI-adaptrar i Python och JavaScript finns kvar för senare anslutning; inga nya AI-jobb startas av v3-personalen.
4. Aktivering vägras om backend känner till ett köat eller pågående AI-arbetspass. Avsluta det först; inga arbetspass avbryts automatiskt.

**OBS:** Den här versionen är ett spelbart *rekryteringssystem*, **inte en färdig ny AI-dispatcher**. Efter aktivering kommer den gamla automatiska produktionen inte längre att starta arbetspass. Vänta med aktivering om du behöver att nuvarande Chefen fortsätter köra verkliga AI-uppdrag direkt. Nästa etapp återansluter v3:s `worker`-objekt till riktig uppgiftsfördelning.

## Installation

1. Säkerhetskopiera gärna `~/.pixelworks` och projektroten. Säkerhetskopior kan innehålla API-nycklar och ska hållas privata.
2. Packa upp `PixelWorks_V3_PERSONALBYRAN_6_PERSONAS_DEV_fb70d1c_DELTA.zip` **i projektroten**, samma katalog som `index.html`. Tillåt överskrivning av `backend/server.py` och `src/main.js`.
3. Starta om Pixel Works-servern. Exempel med ditt LAN-startläge:

   ```bash
   cd ~/pixelworks/pixelworks-git
   python3 backend/server.py stop
   bash start-lan.sh
   ```

4. Uppdatera Firefox med **Ctrl+F5**; ladda om på telefonen.
5. Öppna **Personal & rekrytering** (ny knapp). Bekräfta **Starta nya personalstudion** om du accepterar att gamla schemaläggningen pausas.
6. Gå till **Rekrytera**, välj roll, bläddra kandidater, kör **Arbetsintervju (DEMO)** och **Anställ**.
7. Öppna **Mitt team** för att se Chefen och dina nya anställda, ändra arbetsbeskrivning och kontrollera dem på kontorsgolvet.

Om servern inte startar, kontrollera att hela ZIP:en är upplagd, framför allt `backend/pw_v3_personas.json` och `backend/pw_recruitment_v3.py`.

## Vad som har ändrats i koden

| Fil | Ändring |
|---|---|
| `backend/server.py` | Installerar v3 **före LAN-säkerhetslagret**. Gammal serverkärna lämnas orörd. |
| `backend/pw_recruitment_v3.py` | Eget datalager, låsta personas, transaktionella rekryteringsoperationer, API och spärr mot äldre jobbstart när v3 är aktiv. |
| `backend/pw_v3_personas.json` | Sex deterministiska karaktärer, startskills, rolltabell, egenheter. |
| `src/main.js` | Använder nya personalmodulen i stället för gamla personallager i GUI:t. Tekniska `GameModel`, `GameUI`, `worker`-objekt och övriga verktygsmoduler finns kvar. |
| `src/pw-v3-recruit.js` | Ny rekryteringsbyrå, en scrollbar, mobilvy, porträtt, mockintervjuer, kontorsfigurer. |

## Testresultat (isolering mot verkliga tjänster)

- **21 Python-backendtester godkända**, varav 7 för v3 och 14 regressionstester från v2.7.
- **Chromium 1400×940 och 390×844 godkänt:** start, anställning, rollval, svag matchning, intervju, SVG-förhandsbild, persongolv, profilredigering, scroll.
- **JavaScript- och Python-syntax godkända**.
- Ingen riktig AI, GitHub-push eller modellanvändning har gjorts; inget är verifierat i **din** Firefox/Ubuntu-installation.
- Säkerhet: befintliga `allowed`, `auth`, `same_origin` används för server-API. Varje personaländring kräver serverrevision och aktivt spelarval.

## NOW / NEXT / LATER

**NOW:** Spelbar rekrytering med sex fasta karaktärer, flera roller, korta provintervjuer och eget serverlagrat team. Äldre produktion pausas efter aktivt val.

**NEXT:** Koppla v3-anställdas `worker`/`persona_contract` till en riktig, central uppdragskö som använder samma personal på alla spel utan en permanent projektkoppling. Företagsägaren styr allt kostnads- och anställningsgodkännande. Chefen får bara föreslå ny personal.

**LATER:** Riktiga provjobb med explicit motorgodkännande, modellkatalog (inklusive Gemini-undermodeller och möjliga Pollinations-motorer), mediepreview, uppföljning av faktiskt observerad kvalitet, relationer och progression. Arkivera/avveckla gammal backend permanent först efter verifierad ersättare.

### Begränsningar

- Spelfärdigheter är **fiktiva** och säger inte något säkert om modellernas kvalitet.
- Karaktärerna påverkar **DEMO**-intervjuns ordval; verkliga AI-modeller använder inte personakontraktet förrän nästa integration.
- Intervjuns gorilla är en **statisk exempelillustration**, inte en genererad bild från AI.
- Spelprojekt, gamla anställda och riktiga arbetsrapporter finns kvar på disken, men är *inte* knutna till de nya medarbetarna.
- Ingen automatisk återställningsknapp finns i denna prototyp. Behåll säkerhetskopian om du senare vill återgå till äldre motor.
