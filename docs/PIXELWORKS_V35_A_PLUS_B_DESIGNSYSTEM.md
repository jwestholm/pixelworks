# Pixel Works v3.5 — A+B, ett sammanhängande pixelspel

**Visuell riktning:** varm levande studio från koncept A + tydliga, lättlästa, enhetliga verktygsrutor från koncept B. Bildkoncepten är inspirationsmaterial, inte skärmbilder på faktisk funktion.

## Designregler

1. **En värld.** Alla projekt använder samma rum; projektval är bara arbetsfokus. Ljus och väder är dekoration, inte AI-kapacitet.
2. **Karaktären är identiteten.** Unika ansikten, hår, kläder och spriteark väljs av `character_id`. Yrkesroll, motor, skills och arbetsbeskrivning får ändras oberoende.
3. **En gemensam dialogkomponent.** Designkontrakt: titel + kort sammanhang + en huvudhandling + tydligt Bakåt/Stäng + *en huvudsaklig scroll*. Maximalt en modal i taget. V3.5.0 inför endast gemensamma visuella tokens; komponenten behöver refaktoreras.
4. **Fem huvudvägar:** Kontor, Uppdrag, Personal, Beslut, Projekt. Andra verktyg/teknik under Mer. Kontoret ska vara den största ytan på både dator och mobil.
5. **Spelvänlig men ärlig:** Gröna godkännanden, gula väntan, röda fel, blå info; text och symbol tillsammans. Ingen uppfinningsrik kvot eller verifieringsstatus.
6. **Tillgänglighet:** minst 44×44 px mobilt, hög kontrast, tangentbord/fokus, reducerad rörelse, inga kritiska åtgärder gömda bakom hover.
7. **Fikabordet lever:** avatarer kan dricka kaffe, prata och reagera – fiktiv animation separerad från faktisk AI-kommunikation.

## NOW – v3.5.0 första kodleverans

- Simulerat dag/natt-flöde i befintliga kontoret: sol, måne, stjärnor, ljus, lampor och moln.
- Tydliga knappar för att förhandsvisa ljus och styra dekorativ rörelse/småprat.
- Nya talk/celebrate-spriteark per karaktär. Tidigare fyra states kvar.
- Visuellt enhetligt tema för tre nya v3-dialoger.
- Ingen ändring av verklig AI-pipeline, personalregister eller projektdata.

## NEXT – v3.5.1 designkomponenter och navigation

- Inför **en** riktig `GameDialog` som hanterar bakåt, stäng, återställning av oskickad text, focus-trap och en scroll.
- Flytta Personal, Chefen, Uppdrag och Beslut till samma kodkomponent och samma design-tokens (inte bara likadan CSS).
- Ta bort äldre dubbla ingångar som fortfarande leder till "Okänd anställd" utan att ta bort arkiverade arbetsrapporter.
- Konsolidera menyn till Kontor/Uppdrag/Personal/Beslut/Projekt + Mer, mobilens stora touchvänliga nedre navigering.

## NEXT – v3.5.2 konst och kontorskamera

- Uppdatera **själva kontorsbakgrunden** till en ny pixelillustration med stora fönster, dynamisk utsikt, 10 tydliga skrivbord och kaffe-/mötesyta.
- Förfina de sju sprite-identiteterna: ansikte från Sprite Bible, tydliga silhuetter, transparenta ark, arbetsplatsinteraktioner, sitt/gå/lyssna/peka/kaffe, ytterligare blink-/väntanimationer.
- Panorera/zooma med pekskärm och mus; klick/touch-karta som inte felaktigt drar personer.
- Atmosfärsinställningar: simulerad spelklocka eller riktigt lokalt dygn; eventuellt årstider men inga gissade väderdata.

## NEXT – v3.5.3 gameplay: skapa, granska, godkänn

- Visa personporträtt/sprite intill varje verkligt uppdrag och resultat, samma identitet i varje vy.
- En gemensam beslutsruta: provlyssna ljud, förhandsvisa bild och kodändring, **Ja/Nej/Kanske**, kommentarsfält och återgång till samtalet.
- Chefen ger prioriterade förslag men du beslutar rekrytering, verktygsanvändning och kodintegration.

## LATER – kvalitet & multi-klient

- Designregression i Firefox/Chromium och mobil 360–430 px, 1366×768 och 1920×1080.
- Två klienter samtidigt: verkliga projektstatusar delas, öppet fönster och visuellt klockval är lokalt per klient.
- 10 automatiska uppdateringar och projektbyte utan försvunna figurer; tydliga nät-/API-fel; stabil FPS även 15 personer.
- Kontrollera verklig/rapporterad/verifierad status separat.

## Klart när...

- Ett och samma spelkänsla i Kontor, Personal, Uppdrag, Beslut och Chefen.
- Alla 7 karaktärerna har olika och igenkännbara kroppssprites, med konsekventa porträtt.
- Dag/natt och scenrörelser fungerar med möjlighet att avaktivera rörelse.
- Inga försvinnande anställda efter F5 eller statuspolling.
- Alla primärknappar nås med en tumme på mobil och fönstren använder en rullning.
- Ingen animerad figur utger sig för att utföra ett AI-jobb som inte har startat.
