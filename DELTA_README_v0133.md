# Pixel Works 0.13.3 – Chefen skapar och fördelar produktionsuppdrag

**Basversion:** v0.13.2. Detta är en **delta-ZIP** med enbart ändrade eller nya filer. Inga användarprojekt, sparfiler, API-nycklar eller install-/startskript ingår. Inga GitHub-ändringar har gjorts.

## Felet som åtgärdas

Filmen 2026-10-26 09:07:48 visar att Chefen gör en utvecklingsplan, men svaret sparas som fri text. Ingen kod, grafik eller annat arbetsresultat skapas, eftersom v0.13.2 saknar kopplingen **plan → strukturerade arbetsordrar → tilldelning → säkert schemalagd exekvering**.

## Så fungerar 0.13.3

1. Ett nytt **planeringsuppdrag vid Arbetsledning** använder befintlig Codex CLI i `read-only` och ber om ett **strukturerat JSON-resultat** med 1–8 konkreta uppdrag. Resultatet måste innehålla station, instruktion, prioritet och eventuella beroenden. Ingen spelkod ändras av Chefen.
2. Servern kontrollerar arbetsstationer, textlängder, prioritet och att beroenden bara pekar bakåt (ingen cykel). Ogiltiga svar ger en **misslyckad chefsrapport utan nya arbetsordrar**. Vi gissar aldrig arbetsordrar från fri text.
3. En godkänd strukturerad plan leder till **en atomär skrivning i det aktuella projektets befintliga arbetsorderfil**. Varje order får projektkoppling via mappen, `source_lead_job`, rubrik, ansvarig medarbetare och `depends_on_order_ids`.
4. Servern väljer **anställda efter yrke, kompetens och stationsbehörighet**. Teknikleverantören visas inte i den vanliga gränsytan. Om ingen behörig anställd finns väntar uppdraget på bemanning.
5. Befintlig Codex/Gemini-schemaläggning fortsätter att starta *redo* arbetsorder i bakgrunden. Oberoende uppdrag får köras parallellt inom befintliga kvot- och Git-skydd. Uppdrag som väntar på beroenden blockeras också server-side, inklusive om någon försöker starta ett jobb direkt via `/api/jobs`.
6. Kod-, grafik- och ljudberoenden räknas som uppfyllda först när **rapporten visar verklig integration** (`state=done` och `integrated=true`). Att en AI-session bara avslutats räcker inte.
7. Ett andra likadant brett planeringsuppdrag eller en upprepad slutförandehändelse ska **inte dubbelskapa** arbetsorder. Befintliga vanliga arbetsorder bevaras.
8. Studions högerspalt får **Produktionsplan** med namn, station, arbetare, status och begriplig orsak när något väntar.
9. **Befintliga chefsrapporter**: när projektet ännu saknar genererade produktionsorder visar produktionspanelen en väljare och **Skapa uppdrag från vald chefsrapport**. Efter tvåstegsklick skapas *ett* vanligt, prioriterat planeringsuppdrag för Chefen; den befintliga rapportens text behandlas som DATA. Chefen bearbetar det till strukturerade order i nästa verkliga arbetspass. Du behöver inte skriva om spelidén.

## Installation

1. Säkerställ att **0.13.2** är installerad.
2. Packa upp `Pixel_Works_v0.13.3_DELTA_Chefen_Producerar.zip` **över** den befintliga Pixel Works-mappen. Ersätt samma filnamn. Projektmappen `~/.pixelworks` ingår inte.
3. Starta som tidigare: `python3 backend/server.py`.
4. Firefox: **Ctrl+Shift+R**.
5. Öppna samma spel som Chefen senast planerade, t.ex. *Minesweeper marathon*. I högerspalten under **Arbetsledarens produktion** ska ett äldre färdigt chefsresultat kunna väljas och skickas för omvandling till arbetsordrar. Om inget finns: skapa ett nytt planeringsuppdrag vid Arbetsledning.
6. När Chefen återkommer syns skapade arbetsorder med faktisk tilldelning och väntande beroenden. Lägg märke till att flera steg kan kräva granskning innan nästa steg startar.

## Viktiga begränsningar

- **Verklig Codex-körning är inte gjord i testmiljön**. Strukturerade svar, planvalidering, personalval och UI har testats med simulerat/mokat Codex-resultat. Om en verklig modell inte svarar med giltig JSON visas ett verkligt fel och inga arbetsorder skapas. Man kan försöka igen.
- Inget löfte om att AI faktiskt skapar användbara bilder, ljud eller spelkod: arbete måste granskas som tidigare. En godkänd plan garanterar inte att samtliga roller eller verktyg finns.
- Redan gamla chefsrapporter konverteras **inte automatiskt** vid installation. Endast ett uttryckligt klick på rapportomvandling skapar ett nytt planeringsuppdrag.
- Engångsgodkännandet för studioarbete gäller fortfarande. Inga externa publiceringar, GitHub-pushar eller betalda modellbyten införs.
- Första fasen av delad studio (0.13) använder fortfarande projektspecifika anställningsposter bakom en gemensam översikt. Fullständig konsolidering av schemaläggarna återstår.
- De äldre 8 misslyckade testerna och 19 testfelen i den historiska stora regressionstestsviten är inte åtgärdade av denna patch.

## Verifiering i denna leverans

- 16 nya offline-automatiserade backendfall passerade: JSON-format och schema, cykel/beroendekontroll, personval, saknad personal, senare anställning, idempotens, säkerhet mot direktstart före beroende, faktiskt kodintegrationskrav och korrekt skapad arbetskö.
- 7 äldre testfall för chefsbordet (v0.13.2) passerade.
- 11 äldre testfall för 0.13 och 13 testfall för personalplanering/parallellkö (6 + 7) passerade, körda separat.
- Chromium-test: arbetsordrar/beroenden/ansvariga visas i högerspalten; äldre chefsrapport väljs, tvåstegsgodkänns och skickas till rätt autentiserad endpoint. Simulerade serverdata.
- `python -m py_compile`, `node --check` och ZIP-integritet verifierade.

## Återgång

Lägg tillbaka `backend/pw_v013.py` och `src/pw-v013.js` från 0.13.2. Lämna bort `backend/pw_v0133.py` (som inte laddas av 0.13.2). Redan skapade order måste hanteras i vanliga arbetskön om du väljer att återgå; gamla versionen tolkar inte beroenden.
