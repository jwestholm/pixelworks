# Pixel Works 0.13.0 – Gemensam studio (delta)

**Installationsbas:** v0.12.11.18, med alla tidigare deltan installerade. **Startkommando:** `python3 backend/server.py`. Projektets lokala `dev`-Git-historik med originalmotorn måste finnas kvar, precis som tidigare. Inga `pip install`, installationsskript, GitHub-ändringar eller externa API-anrop ingår.

## Vad som är nytt

- **Ett kontor, flera spel:** Menyn **🏢 Min studio** visar en gemensam personalöversikt och de anställda som hör till andra projekt syns som klickbara kollegor i samma kontor. Kontorets miljö ändrar inte karaktär när fokusprojektet byts. Rubriken anger i stället vilket spel du just nu tittar på.
- **Stabil identitet:** Äldre personalposter har en deterministisk studioidentitet baserad på ursprungligt projekt och anställnings-ID. Samma äldre kort-ID i två projekt betyder inte samma person. Identiteten bevaras om den anställda senare byter spelprojekt.
- **Kontrollerad tilldelning:** Aktivera först **Gemensam studio** genom ett uttryckligt knappval i studioöversikten. Därefter kan lediga medarbetare tilldelas ett annat projekt med två spelknappar. Koden flyttar personalposten och kopierar relevanta kompetensinställningar. Kod, Game Bible, rapporter, assets och Git-historik stannar i sina egna projekt.
- **Ingen dubbelstart:** Flytt nekas om personen har aktiv session; krockande lokala person-ID byts ut i målprojektet utan att den stabila studioidentiteten ändras.
- **Nya projekt återanvänder teamet:** Efter att delad studio aktiverats skapas inga nya startkopior av Chefen/Gunnar/Greta för varje nytt spel. Det nya spelet har till en början ingen tilldelad anställd; använd Min studio och flytta önskad personal dit. Tidigare sparade projekt och anställningar rörs inte av själva aktiveringen.
- **Säkrare personalflytt:** En transaktionsjournal i den lokala studiokatalogen möjliggör explicit återställning efter en avbruten flytt. Fel mitt under en flytt rullas tillbaka i samma process. Ingen automatisk tyst återställning skriver över personalfiler.
- **Generiska menyer:** Den tidigare hårdkodade katten är borttagen. I grafik, möte, musik och röst finns nu generella **Djur eller varelse**-val med valfri beskrivning.

## Prova efter uppdateringen

1. Packa upp ZIP-filen ovanpå din befintliga **0.12.11.18**-installation. Starta som vanligt. Uppdatera Firefox med `Ctrl+Shift+R`.
2. Klicka **🏢 Min studio**. Kontrollera att du ser medarbetare från alla dina befintliga spel utan att något har flyttats.
3. Läs aktiveringstexten och klicka **Aktivera gemensam studio** om du vill sluta skapa separata startteam. Detta ändrar en inställning, men skriver inte om befintliga projekts spelkod eller personalregister.
4. Välj en **ledig** person, välj målspel och tryck **Tilldela** och sedan **Bekräfta**. Personens arbetsstation återgår till fikarummet; det är inte ett AI-jobb i sig.
5. Välj projektet du flyttade till och ge arbetaren ett nytt uppdrag på vanligt sätt. Samtidigt kan anställda i de andra projekten fortsätta med sina egna uppdrag.
6. Starta ett nytt spel och kontrollera att det skapas **utan** ett nytt automatiskt startteam. Flytta dit en befintlig anställd via Min studio.

**Observera:** När du växlar fokusprojekt i den gamla projektväljaren visas fortfarande det fokuserade projektets befintliga ursprungsfigurer genom den gamla spelmodellen; övriga medarbetare läggs som klickbara studiofigurer ovanpå samma kontor. 0.13 är en **säker övergångsarkitektur**, inte ännu en total omskrivning av arbetsledarens schemaläggare.

## Kompatibilitet och avgränsningar

- Befintliga `management/STAFF.json` och projektbundna jobbrapporter förblir läsbara. Anställda är ännu lagrade i sina **aktuellt tilldelade projekts personalfil**, med en gemensam studioidentitet som binder ihop flyttningar. **Ett fullt kanoniskt företagsregister** och en enda transaktionell schemaläggare är fortfarande nästa fas.
- Gamla projekt kan ha flera olika anställda med namnet *Gunnar* eller *Chefen*, eftersom de tidigare fick startteam per projekt. Dessa **slås inte ihop automatiskt**; det vore osäkert för historik och gamla jobb-ID. Du ser vilka spel de hör till i studioöversikten.
- 0.13 innehåller ännu inte Story Mode, ekonomi, rekryteringsprogression, DAG-uppdrag, automatisk flytt av hela ett arbetspass eller publicering. Det är planerat senare.
- En medarbetare kan vara tilldelad **ett** spelprojekt åt gången, men flera olika medarbetare kan arbeta i olika projekt samtidigt om deras motorer och Git-arbetsytor tillåter det.
- Leverantörernas riktiga anrop/kvoter ändras inte. Publicering på internet sker inte.
- Ingen av programmets nätverksrutter för studioöversikt ger ut API-nycklar. De skyddas av samma lokala token/origin-kontroller som övriga administrativa anrop.

## Testning

- **15 riktade Python-tester gröna** (v013 och v0121118) med simulerad backend; krockande äldre ID, rollbacks, avbruten flytt, studioaktivering, rätt projekt, parallella jobb, säkerhet och HTML-injektion.
- **Chromium-studiotest grönt:** gemensamma avatarer och personalregister, uttrycklig aktivering och flytt, aktivt spel oförändrat, upptagen medarbetare skyddad, inga inbyggda browser-confirm-rutor.
- **Chromium-skrivbordstest grönt:** Grafik, QA, mötesplan, referenser och projektgräns.
- **Hela äldre testsviten är fortfarande inte grön**: 8 misslyckanden och 19 fel i 146 tester före ytterligare v013-testfall. Flera tester speglar gamla API-gränser eller ersatta kvotregler.
- Verkliga användarkonton, Firefox, Google, Codex och produktionsdata testades **inte** av dessa automatiska tester.

## Avinstallera / backa

Inga befintliga spelprojekt skrivs över av uppdateringens installation. För att backa **koden**: återställ filerna i delta-paketet från din säkerhetskopia och ta bort de nya `backend/pw_v013.py` och `src/pw-v013.js` efter att servern stoppats. Om du har **flyttat personal**, använd Min studios återställningsflöde om en flytt avbrutits; utförda, lyckade flyttningar backas inte automatiskt vid en kodnedgradering. Gör först en kopia av hela `.pixelworks`-datakatalogen.

**Ändrade filer i delta:** `backend/pw_v01210.py`, `backend/pw_v0121118.py`, `src/pw-v0121118.js`.

**Nya filer:** `backend/pw_v013.py`, `src/pw-v013.js`, testfiler samt versionerad dokumentation.
