# Pixel Works v0.12.11.9 – Granskningsmarkeringar på arbetsbord

Bas: v0.12.11.8. Packa upp endast den ändrade `src/pw-v012118.js` i befintlig spelmapp. Ingen backend, lagringsdata, spelkod eller API-nyckel ändras.

- ❗ visas på varje station med aktuell arbetsorder i `review` eller en olöst granskningsrapport.
- Flera ärenden vid samma station visas som ❗2, ❗3 osv.
- Markeringen använder samma visuella princip som skrivbordets badge och öppnar stationens befintliga arbetskö.
- Godkända/arkiverade/ersatta rapporter ger inte nya indikatorer. En arbetsorder som säger `review` men saknar rapport får en markering eftersom den behöver hanteras.
- Uppdateras automatiskt var 3,2 sekund och vid granskningsbeslut.

OBS: Detta gör väntande granskning synlig på bordet. Själva separata felet från skärminspelningen — arbetskö med `Väntar på granskning` utan en fungerande beslutsknapp — åtgärdas **inte** av denna visuella patch.

Start: `python3 backend/server.py`, uppdatera Firefox med Ctrl+Shift+R. Inga verkliga AI-anrop gjorda.
