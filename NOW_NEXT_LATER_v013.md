# NOW / NEXT / LATER – Pixel Works v0.13.0

## NOW – levererat och verifierat lokalt
- En gemensam visuell studio och studioroster, utan att den aktuella Game Bible/kodmappen byts ut.
- Explcit opt-in till gemensam personal för framtida projekt.
- Säkrare manuell tilldelning av ledig personal mellan projekt med projektisolering och felåterställning.
- Ingen automatisk nyanställning per nytt spel efter aktivering.
- Generiska uppdragskategorier i stället för hårdkodad katt.
- 15 riktade backendtester och två simulerade Chromium-tester passerar.

## NEXT – viktigaste återstående tekniska arbete
1. Bygg ett **kanoniskt gemensamt personalregister** som alla exekveringsvägar och historiska rapporter kan läsa, utan att de gamla projektbundna schemaläggarna konkurrerar.
2. Inför transaktionell global arbetskö med `studio_employee_id`, oföränderligt `project_id` och idempotent claim; skydda alla flyttningar mot samtidiga profiledits.
3. Rensa gamla testkontrakt och gör hela regressionssviten grön; lägg till verklig Firefox-kontroll.
4. Finputsa kontorets gemensamma sprites, positionering och antal anställda vid kaffebordet.
5. Skapa fritt rekryteringsflöde för **Open Studio** med personal i studion utan tilldelat projekt, och definiera separat Story-profil för senare användning.

## LATER
- Arbetsledare + Game Designer som skilda roller; planer med beroenden och verifierade resultat.
- Story Mode: starta med en allroundare, utbilda och anställ, simulera ekonomin utan AI-kvoter.
- Reproducerbara build/release-artefakter; därefter privat delning och eventuell Pixel Works Arcade.

**Aldrig:** slå ihop två äldre personer enbart för att de har samma namn; flytta jobb mellan projekt utan explicit tilldelning; påstå att ett AI-svar innebär verifierad kod.
