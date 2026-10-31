# Pixel Works v3.1 – Karaktärer och intervjuer

**Bas:** v3.0 Rekryteringsbyrån installerad över den tidigare dev-baserade Pixel Works-installationen (`fb70d1c`).  
**Typ:** liten överläggs-ZIP i projektroten. **Ingen GitHub-push**, ingen filändring i dina spelprojekt vid installation.  
**Status:** isolerade Python- och Chromiumtester. Verkliga Firefox/Ubuntu-miljön ej kontrollerad.

## Varför ändringen?

Spelarens inspelning från 2026-10-30 visar en bra grund, men karaktärskorten är för lika: samma ansiktsgeometri, två redovisningar av kompetens och tre identiska företagsförbud på varje kort. De viktiga besluten och intervjun hamnar för långt ner. Rekrytering ska vara en del av spelet, inte ett administratörsformulär.

## Ingår

- Sex *egna* transparenta pixelporträtt ritade med inline-SVG: Joppes keps, Sivs glasögon och håruppsättning, Nisses skägg, Miras långa frisyr, Veras hörlurar och Lovas fläta/örhänge. Chefens porträtt är också eget. Ingen extern asset eller bild-API.
- Fiktiv **ålder, kön, pronomen, tidigare yrke, erfarenhetsår, skruvad bakgrund och favoritsak** för alla karaktärer. Dessa är permanenta delar av karaktärsmallen; de används inte som faktor i kompetensbedömning.
- Rollmatchning som lättlästa stjärnor; två grupper med styrkor och svagheter; detaljer om alla åtta skills bakom ett expanderbart fält. Spelvärde är **inte verifierad AI-kvalitet**.
- Personlighet med röst och egenheter bakom en utfällbar karaktärssektion. På personalsidan ligger företagets gemensamma förbud samlade bakom **Studions gemensamma regler**, inte på varje kandidatkort.
- Två valbara fiktiva intervjuprov per yrkesroll (14 totalt); fråga och kandidatfärgat, förskrivet svar sparas i v3-registret. Ett särskilt grafikprov visar en statisk gorilla-SVG; ett särskilt ljudprov spelar lokal Web Audio. Inget API-anrop eller faktiskt arbetsprov görs.
- Permanent knapp för **Anställ** i botten på rekryteringsfönstret. Endast du godkänner anställning. Samma kandidat kan väljas till valfri yrkesroll.
- Teamkort och medarbetarprofil visar nu bakgrundsdata. Persona-kontraktet får med bakgrunden och pronomen för *framtida* motorintegration; det används **inte** för riktiga AI-jobb i v3.1.

## Installation

1. Gör gärna en privat säkerhetskopia av `~/.pixelworks`, särskilt `studio-v3/CREW.json`. Säkerhetskopian kan innehålla känslig projektinformation.
2. Packa upp `PixelWorks_V31_KARAKTARER_INTERVJU_DEV_fb70d1c_DELTA.zip` **direkt i Pixel Works-projektroten**, alltså katalogen med `index.html`.
3. Tillåt överskrivning av `backend/pw_recruitment_v3.py`, `backend/pw_v3_personas.json` och `src/pw-v3-recruit.js`.
4. **Starta om servern** eftersom Python-modulen och katalogen ändrats. Exempel:

   ```bash
   cd ~/pixelworks/pixelworks-git
   python3 backend/server.py stop
   bash start-lan.sh
   ```

5. Ladda om Firefox med `Ctrl+F5`, och ladda om sidan på mobilen.
6. Välj **Personal & rekrytering → Rekrytera**, bläddra, prova olika roller och gör två provintervjuer.

**Om du redan har aktiverat v3.0 behöver du inte aktivera igen.** Befintlig `CREW.json` behålls utan migrering; det är fortfarande samma sex kandidat-ID:n och samma fasta personligheter. Gamla intervjusvar visas där de passar, nya intervjuer får vald frågetyp.

## Filöversikt

| Fil | Funktion |
| --- | --- |
| `backend/pw_v3_personas.json` | Fasta fiktiva biografier, ålder, kön, pronomen, erfarenhet och porträttidentifierare. |
| `backend/pw_recruitment_v3.py` | 14 deterministiska DEMO-prov, frågevalidering och persona-kontrakt. Samma befintliga API-sökvägar. |
| `src/pw-v3-recruit.js` | Nytt karaktärskort, distinkta SVG-ansikten, kompakt rollmatchning, intervjuscener, mobillayout. |
| `backend/test_pw_recruitment_v31.py` | Nya regressionstester som inte använder externa tjänster. |
| `tests/test_recruitment_v31_ui.py` | Isolerade Chromiumtest med server-mock; inget verkligt Pixel Works-API. |

## Tester

- **12 Python-enhetstester** godkända (7 befintliga v3 + 5 nya). Validerar bland annat skillnad mellan två intervjuer, ålder/erfarenhet, låsta egenskaper, bevarade arbetar-ID:n och oförändrade gamla projektfiler.
- **Chromium 1400 × 940 och 390 × 844:** kandidatbläddring, olika ansikten, ålder/erfarenhet, rollmatchning, grafisk DEMO-gorilla, PHP-fråga, anställning, befintlig personprofil och dialogscroll. **Dessa tester använder fiktiv API-data.**
- JavaScript (`node --check`) och Python-kompilering godkända. **Ingen riktig bildgenerering, AI-anrop eller LAN-/Firefoxverifiering utförd.**

## NOW / NEXT / LATER

**NOW:** Rekrytering som ett spelbart beslut med sex unika kandidater, bakgrunder, roller och lokala DEMO-intervjuer.

**NEXT:** Utveckla arbetsintervjun till ett mer avancerat gameplaymoment (kandidatens egen kommentar, spelarens Ja/Nej/Kanske och portfolio), skapa fler kandidater och dynamiska lediga tjänster. Behåll tydlig skillnad mellan spelvärden och observerad AI-kvalitet.

**LATER:** Koppla en gemensam uppdragsmotor till worker-objekten och riktiga, utbytbara AI-modeller (under uttryckligt godkännande). Chefen får rekommendera rekryteringar men aldrig anställa själv.

## Begränsningar och skydd

- **Den gamla AI-schemaläggaren förblir pausad** om v3 är aktiverat. Den här uppdateringen startar inga gamla personjobb och förändrar inga Git-arbetsytor.
- Ålder, kön och yrkesbakgrund är **fiktiva karaktärsdrag**. Kön och ålder påverkar aldrig rollpoängen.
- Skillnivåer och intervjusvar är fiktiva. En intervju är inte en kvalitetssäkrad bedömning av en verklig AI-modell.
- Gamla v2-personalregister finns kvar som arkiv. Inga anställda avskedas automatiskt.
- Företagets befintliga spärrar mot publicering, GitHub-push och otillåten betald AI fortsätter vara en policy-/exekveringsfråga, inte karaktärsdrag.
