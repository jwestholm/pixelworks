# Pixel Works — NOW / NEXT / LATER (v0.12.11.3)

## NOW — fixat i kod, lokalverifierat
- Riktigt Gemini-`generateContent`-test i stället för metadata-GET.
- Ny Free Tier-modell `gemini-3.5-flash-lite`, ingen automatisk uppgradering.
- Befintlig gemensam token, max 12 lokalt räknade Google-anrop/dygn.
- Gemini-spärr tills token+modell verkligen testats; tydliga orsaker i chefsstatus.
- `python3 backend/server.py` fortsatt enda startfil.

## NEXT — behöver verifieras på användarens maskin
- Uppdraget i rapportpärmen som misslyckades med HTTP404 måste läggas i kön igen efter godkänt modelltest.
- Verifiera faktisk Google-inloggning/Free Tier hos användaren utan att dela nyckeln.
- Visa korrekt provideretikett även i den äldre högerspaltens Codex-logg för Gemini-jobb.
- Skilj mellan »Gemini har lämnat designtext« och »Codex har ändrat spelkod« i hjälpdialogerna.
- Flytta teknisk Codex-parallellhantering och arbetsbilagor från Inställningar till riktiga arbetsorderkort.

## LATER
- Spelbaserad rekrytering av fler AI-roller och återkoppling på verifierad leverans.
- Avancerad provider-katalog efter beslut om kostnadsfria externa tjänster.
