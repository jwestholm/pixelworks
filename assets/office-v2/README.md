# Pixel Works – Office v2 sprite-kit

Detta är de första **lokalt framtagna originalspritarna**. De är separata från Pixel Works backendsystem och kan ersättas utan att uppdragslogiken ändras.

## Innehåll
- `office-backdrop.svg`: kontorets väggar, fönster och golv. Inga osynliga interaktionsytor.
- `desk-*.png`: 10 fristående skrivbords-/stationsbilder med transparens (276×213 px). Varje verklig station är fortsatt ett eget DOM-objekt.
- `agent-N-idle.png`, `agent-N-walk.png`, `agent-N-working.png`, `agent-N-cafe.png`: åtta karaktärsvarianter, fyra verkligt olika 48×68-bildrutor per animation. Arkets dimensioner är 192×68 px.
- `plant.png`: separat transparent miljödekoration.
- `CONCEPT_ATLAS_REFERENCE.png`: AI-genererad **visuell referens**, ej uppdelade produktionstillgångar; den används inte för klickbara objekt.

## Att byta till mer detaljrika sprites
Behåll filnamn eller uppdatera `visual-v2.css`. Behåll transparent bakgrund, bildrutornas enhetliga storlek och samma perspektiv inom varje assetfamilj. Karaktärernas status kommer från det befintliga agenttillståndet, inte från en animation. Ingen AI-tjänst anropas av bilderna.

## OBS
Det här är ett första tekniskt sprite-kit; det motsvarar ännu inte fullt ut konceptbildens detaljnivå eller en äkta isometrisk tile-motor.

**v0.12.0.2:** Nya bildrutor är olika på riktigt (ögon, huvud, armar, steg, tangentbord och kaffekopp). Endast agenter med serververifierad `working`-status använder arbetssprites. Animationerna respekterar `prefers-reduced-motion`.
