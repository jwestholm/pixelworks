# Pixel Works v3.1 – Sprite Bible / visuell identitet

**Status:** designkontrakt för framtida sprites, inte färdiga sprites.  
**Kanonisk referens:** `src/pw-v3-recruit.js` → `portrait(c)` samt `backend/pw_v3_personas.json`.  
**Referensbild:** `assets/character-reference/v31-six-faces-reference.png` (UI-montage; **inte** spelresurs eller spritesheet).  
**Manifest:** `docs/SPRITE_IDENTITY_V31.json` innehåller ID, färger och SHA-256 för källversionen.

## Huvudregel

**En person behåller sitt ansikte, hår, hudton, kännetecken och grundpalett oavsett yrke, projekt, AI-motor eller arbetsstation.** Byt arbetsredskap och eventuella kläder per roll, inte grundidentitet. Använd aldrig namn som nyckel; använd fasta `id` i personas-filen och senare unikt anställnings-ID för instanser.

## Fasta utseenden

| Karaktärs-ID | Person | Kännetecken som måste kännas igen i alla sprites | Grundfärger hud / tröja / hår |
|---|---|---|---|
| `chef` | Chefen | Kort prydlig frisyr, välordnad uppsyn, markerad kontorsskjorta med slipsliknande detalj. | `#efc09f` / `#385e6c` / `#b19a76` |
| `joppe` | Joppe Nyström | Röd keps med gul detalj, mörka sidolockar, blå jacka/tröja och ett brett, kaxigt leende. | `#f1c191` / `#50618a` / `#fa895e` |
| `siv` | Siv Paragraf | Gråblå uppsatt frisyr med högre hårtopp på ena sidan, fyrkantiga glasögon, lila överdel. | `#eac9a7` / `#665477` / `#8eafc5` |
| `nisse` | Nisse Genväg | Kort kantig grön frisyr, markerat brunt skägg och mörk tröja med gul mittdetalj. | `#dba37b` / `#4c4953` / `#9bbd82` |
| `mira` | Mira Byte | Lång asymmetrisk turkos frisyr, gul hårnål, liten rosig detalj på kinden, lila överdel. | `#f5c6ac` / `#5c5075` / `#91c5c6` |
| `vera` | Vera Volt | Lila/rosa mössa/hårdetalj, stora gula hörlurar och mörkblå överdel. | `#efb67b` / `#375972` / `#b6a4d5` |
| `lova` | Lova Sagofrö | Lång varmkorallfärgad frisyr/fläta, gult örhänge och grön överdel. | `#eac6a9` / `#536955` / `#d98a7c` |

**Viktigt:** Chefens portrait finns i koden men **inte** i montaget med de sex kandidaterna. Hans källritning är `portrait(c)` med ID `chef`. Det är den korrekta sjunde referensen.

## Sprites som ska skapas – förslag till produktionskontrakt

Varje person ska ha samma dimensioner och animationsgränssnitt som kontorets figurer använder. Det befintliga pixelkontoret har idag 48×68 pixlar per animationsruta och fyra rutor i rad (192×68); använd detta som **kompatibilitetsmål**, inte som påstående att nya v3-sprites redan finns.

| Animation | Minsta krav | Extra detaljer |
|---|---|---|
| `idle` | 4 frames | Andning, blinkning, personlig liten gest |
| `walk` | 4 frames | Synkroniserad gång, bevara ansiktssilhuett |
| `working` | 4 frames | Arbeta vid skrivbord; arbetsredskap är rollberoende |
| `cafe` | 4 frames | Koppla av, dricka kaffe, samtala |
| `talk` / `reaction` | Senare | Prat, tvekan, glädje, irritation, förvåning |

- **Transparent bakgrund (RGBA)**. Inga vita/solida rektanglar bakom figurerna; inga UI-ramar i själva spritebilden.
- **Nearest-neighbor / pixelated** vid skalning; inga utjämnade kanter som ändrar pixelstilen.
- Samma ungefärliga kroppshöjd, tyngdpunkt och fotförankring för samtliga, så de kan dela navigering och kollisionsytor.
- Kända detaljer syns i **minst framifrån** och så långt möjligt i sid-/bakvyer: Joppes keps, Sivs glasögon, Nisses skägg, Miras hårnål, Veras hörlurar och Lovas fläta/örhänge.
- Eventuella arbetskläder eller verktyg kan variera, men behåll en bas-sprite per karaktär och separata overlays för yrkesrollen.
- Frys inte figuren i en särskild AI-motor. Motor är en utbytbar arbetsresurs.

### Förslag på filnamn

`assets/characters/<character-id>/<character-id>-idle.png` och motsvarande `walk`, `working`, `cafe`. Övriga vyer kan föras in som `front`, `side`, `back` när vi har valt riktning/atlasstandard.

## Innan någon ritar sprites

1. Läs `portrait(c)` och respektive `colors` från de två kanoniska källfilerna.
2. Kontrollera referensmontaget visuellt; det är **ett foto av v3.1-kort**, inte ett redigerbart masteroriginal.
3. Gör först **en komplett figur** (t.ex. Mira: idle + walk + working + cafe). Godkänn detaljnivå och hur stor hon ser ut i kontoret.
4. Bygg övriga sex från samma mall, med bevarad individuellt igenkännbar silhuett.
5. Testa tre saker innan import: genomskinlighet, animation i fullskärm + mobil samt igenkänning mellan porträtt ↔ figur.

## Skillnad mot aktuellt läge

- **Verifierat i v3.1-källkod:** fasta färger, unika SVG-porträtt, persona-ID:n och bakgrundsdata.
- **Inte gjort ännu:** exporterade kontorssprites för de sju v3-karaktärerna, färdiga animationsatlaser, färdig integrering med kontorets spriteklasser.

Detta dokument får versioneras när den visuella designen ändras medvetet. Ändra inte källporträtt i smyg utan att samtidigt uppdatera manifest och framtida spritefiler.
