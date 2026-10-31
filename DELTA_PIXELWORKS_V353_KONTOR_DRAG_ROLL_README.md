# Pixel Works 3.5.3 – kontorsplacering, fönster och rekryteringsroller

**Installera efter v3.5.2.** Byggd mot GitHub `dev` vid `fb70d1c9a927e07e802537c83705db5b8f9876cd` och de senare lokalt installerade delta-versionerna v3.0–v3.5.2. Ingen GitHub-push och inga verkliga AI-anrop i bygget.

## Installation

1. Säkerhetskopiera gärna `~/.pixelworks/studio-v3/CREW.json` innan du provar förflyttningar, eftersom nya positioner sparas i det globala personregistret.
2. Packa upp zip-filen **i projektroten**, samma katalog som `index.html`, och skriv över filerna.
3. **Starta om backend**, då en ny API-rutt och en ny statisk CSS-filsväg har lagts till:

   ```bash
   python3 backend/server.py stop
   bash start-lan.sh
   ```

4. Ladda om Firefox med **Ctrl+Shift+R** (ingen Fn/F5 behövs). Gör motsvarande omladdning på mobilen.
5. Testa att dra Mira till ett skrivbord och sedan ladda om sidan. Hon ska stå kvar. Tryck en gång på henne för att öppna profilen.
6. Bläddra i rekryteringen: kandidatens bästa roll ska vara vald, men går att ändra.

## NOW – åtgärdat

- Global v3-personal går att dra med mus och finger. Ett tryck öppnar fortfarande profilen.
- Placering sparas som **kontorsposition** i v3-registret (`office_position`: x/y och eventuell station), inte i äldre projektanställningar. Flytt skapar **inte AI-jobb** eller ändrar arbetsroll.
- Två klienter använder registrets revisionsnummer. En gammal revision ger ett synligt fel och nyhämtning; inga tysta överskrivningar.
- En person som placerats manuellt får inte sin position överskriven av den dekorativa gånganimationen.
- Vid rekrytering är **bäst lämpad yrkesroll förvald när kandidaten byts**. Egna manuella rollval per kandidat sparas tills sidan laddas om.
- Den tidigare rektangulära sol-/månljusbilden är begränsad till mittfönstret; sidofönstren får matchande dags-/kvälls-/nattfärger. Sol- och månanimationen finns kvar.
- Kontoret får diskreta golvmattor, ångeffekt vid fikabordet, något större figurer och tydligare infokontrast. Dekoren är oklickbar och ska inte täcka stationerna.
- UI-version 3.5.3 märks separat från det äldre serverversionsnumret.

## Vad som är verkligt och inte

- **Verkligt:** servern lagrar en placeringskoordinat för en global person, kontorsvyn återhämtar den; rekryteringsrollen påverkar en framtida verklig anställning om du själv godkänner den.
- **Endast visuellt:** dag/natt, dekorativa gångrörelser, mattor, prat, rök från kaffe.
- **Oförändrat:** Codex/Gemini-jobb, AI-behörighet, kontroll av uppdrag, Git-arbetsytor, rapporter och beslutsflöden.
- Att flytta en figur till ett skrivbord betyder **inte** att den blir schemalagd att arbeta där. Det verkliga uppdraget ges separat via AI-uppdrag/Chefen.

## Tester

- 50 backend-regressionstester för rekrytering, AI-arbetsflöde, Chefen och kontorsplacering.
- 6 nya Chromium-tester: klick, musdragning, sparad position efter omritning, skrivbordssläpp, fingerdragning och rollförval.
- 6 äldre personal-UI-regressioner och 6 HTTP-tester för statiska CSS/sprite-resurser.
- **Inte verifierat i användarens Firefox/Ubuntu:** verklig LAN-anslutning och grafik på den maskinen.

## NEXT – större grafikomtag

- Ny **sammanhållen kontorsillustration** med mer möbler, ljus, skuggor och arbetsstationer som faktiskt passar spriteplaceringar. Den aktuella uppdateringen är en riktad grafisk förbättring, inte en fullständig omritning av kontoret.
- Arbeta vidare på riktiga karaktärssprites: rörelser från flera riktningar, sit- och jobbanimationer, tydligare skuggor, utseenden identiska med porträtten.
- En gemensam layoutkomponent för äldre rapporter/beslut med samma ramar, navigering och single-scroll som personalvyn.

## LATER

- Delad kontorskamera/zoom och mobilpanorering.
- Studioövergripande stationstilldelning som faktiskt kan ge arbetsledaren signal om bemanning **efter** spelarens uttryckliga godkännande.
- Företagsminne och versionsriktig konfiguration för AI-motorer, kopplad till varje karaktär utan att blanda ihop personlighet och behörigheter.
