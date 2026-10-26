# NOW / NEXT / LATER — efter v0.12.11.2

## NOW (rättat i kandidat)
- Återställ huvudsidan **Inställningar & diagnostik**, med en Gemini-rad.
- Avblockera testknapp och låt den spara osparad Gemini-token innan verkligt test.
- Anpassa lokal nyckelformatkontroll för nya Google API-nyckeltyper.
- Visa tydligt ansluten/ej testad/nekad/modell saknas/kvotstopp.

## NEXT
- Testa mot användarens riktiga Gemini-projekt *endast när användaren själv trycker Testa*.
- Förenkla spelets menynavigering; flytta arbetsbilagor till uppdragskort och parallell Codex-start till arbetsledarens arbetsflöde.
- Verifiera arbetsledarens Gemini-delegering i riktig Firefox/med testkonto utan fakturering, inklusive behöriga stationer.
- Felsök om projektlista och stationstillstånd fortfarande skiljer sig mellan sparade projekt.

## LATER
- Flera AI-motorer genom utbytbara adaptrar; personlighet och yrke oberoende av motor.
- GUI-regressionstest i CI för startsida/inställningar och byte mellan projekt.

**Regel:** `python3 backend/server.py` är enda serverstartkommando. Endast deltafiler i ZIP, inga installationsskript.
