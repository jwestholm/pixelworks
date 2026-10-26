# Pixel Works v0.13.6 — Enkel högerspalt

**Basversion:** v0.13.5. **Ändringstyp:** bara GUI, inga backend-/datamigrationer.

## Ändrat
- Högerspaltens stora `Pixel Works – gemensam studio`-ruta tas bort. Funktionerna och samtliga personalposter finns kvar under **Min studio** i toppmenyn.
- Dubbelvisningen av fokusprojekt tas bort från högerspalten. Projektet visas redan i huvudrubriken.
- Godkänd studioåtkomst visas inte längre som en separat stor statusruta. Om åtkomst saknas är aktiveringsrutan fortfarande synlig. Äldre dubbelvarning `Studioåtkomst behövs` döljs bara när faktisk `Studioarbete tillåtet` syns.
- Personalöversikten och statistikdetaljerna tas bort från högerspalten. Personal finns under **Min studio** och statistik under **Statistik**. Personalork i kontoret påverkas inte.
- Produktionspanelen visas bara när det finns verkliga produktionssteg, en plan att redigera eller en chefsrapport att fortsätta från. En rad visar kort status. Detaljerna går att fälla ut och innehåller samma knappar som tidigare.
- Beslutsrutan döljs när inget behöver göras. När flera åtgärder finns visas första åtgärden direkt och övriga under **Fler åtgärder**, med ursprungliga klickhändelser intakta.
- Planredigerarens valfria körknapp heter nu **Starta produktionen** snarare än **Godkänn och starta produktionen**. Serverns behörighetskontroll ändras inte.

## Oförändrat
- All serverfunktionalitet, AI-anrop och kvothantering.
- Automatiska produktionsplaner, arbetsordrar, Game Bible och projektkopplingar.
- Tillstånd för studions faktiska åtkomst, inklusive möjlighet att återkalla.
- Detaljvy för arbetsordrar, rapporter, planredigerare och personaladministration.

## Installation
Packa upp **endast delta-ZIP** ovanpå befintlig v0.13.5 och starta:

```sh
python3 backend/server.py
```

Gör sedan en hård omladdning i Firefox (**Ctrl+Shift+R**). Versionsmärket i webbläsaren ska visa `v0.13.6`. Backendloggens versionsrad kan fortfarande vara `0.13.5` eftersom ingen serverkod ändrats.

## Tester
- `node --check src/pw-v013.js` — godkänd.
- `python3 tests/test_rail_simple.py` — godkänd i headless Chromium med simulerade, lokala API-svar: tomt läge, arbetande medarbetare, utfällning, bevittnade åtgärdsklick, dold redundans, revokerat studiotillstånd, JS-konsolfel.
- 20 av 20 befintliga v0.13.5 backendtester — godkända med kompletta befintliga testmoduler på PYTHONPATH. Ingen verklig AI-anslutning använd.
- Fullständig gammal regressionstestsvit är inte grön sedan tidigare; inget anspråk på genomtestad totalversion.

## Säkerhet
Ändringen tillför inga nya API-anrop, ändrade behörigheter, Git-åtgärder, exekvering eller externa tjänster. Enbart visning och navigation. Ingen ändring i GitHub eller sparade spel.
