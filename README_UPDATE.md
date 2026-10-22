# Uppdatering till v0.11.7.1

Stoppa äldre Pixel Works-server. Packa upp programfiler utan att ta bort `.git` i din lokala källkodskatalog. Projektens data under `~/.pixelworks/projects/` bevaras.

### Game Bible styr AI-arbetet
- Öppna 📖 GAME BIBLE i kontoret och skriv dina övergripande designval i bokens kapitel.
- Codex-arbetare och Codex-planeraren får både den gamla originalsidan och de nya boksidorna som referens.
- Efter en **lyckad lokal integration** kan Codex lämna en strukturerad bokuppdatering (till exempel en ny plats, en karaktär eller en spelmekanik). Uppdateringen läggs till i rätt kapitel utan att tidigare text försvinner.
- Visionen förblir under din kontroll; AI kan inte uppdatera Vision-kapitlet via denna funktion.
- Om arbetet inte integrerats läggs inte heller nya spelpåståenden in som färdiga fakta.

Test: skapa en arbetsorder om en ny plats och låt en Codex-arbetare slutföra den. Öppna Game Bible → Spelvärlden och platser när ändringen införts. Om agenten inte genererar den strukturerade bokfilen finns ingen ny automatiskt införd notering; funktionen gissar aldrig vad som gjorts.
