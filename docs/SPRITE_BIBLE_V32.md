# Pixel Works 3.2 – Sprite Bible, första spelbara uppsättningen

**Status:** verkliga transparenta RGBA-sprites och instanskoppling i frontend, men endast DEMO-rörelser. Detta är en första pixelgrafikpassning, inte slutgiltig konst.

**Kanonisk personidentitet:** `backend/pw_v3_personas.json` (`id`, `colors`, `traits`, `voice`). SVG-porträtten ritas fortfarande av `portrait(c)` i `src/pw-v3-recruit.js`.

**Sprites:** `assets/characters/<id>/<id>-{idle,walk,working,cafe}.png`. Varje fil är 192×68 pixlar, fyra rutor à 48×68, med transparent bakgrund. `docs/CHARACTER_SPRITES_V32.json` innehåller SHA-256 per fil.

## Identitetsregler

| ID | Fasta kännetecken i både porträtt och sprite |
|---|---|
| `chef` | Prydliga bruna/gråblonda håret, blågrön chefsdräkt och slips. |
| `joppe` | Stor röd keps med gul detalj, blå kläder och brett leende. |
| `siv` | Gråblå uppsatt frisyr och tydliga glasögon, lila kläder. |
| `nisse` | Grönt kantigt hår, brunt skägg, mörka kläder med gult mittfält. |
| `mira` | Asymmetriskt turkost hår med lång sidotofs, gul hårnål och lila kläder. |
| `vera` | Gula hörlurar, lila hårdetalj, mörkblå kläder. |
| `lova` | Långt korallfärgat hår, gult örhänge, gröna kläder. |

**Viktigt:** Arbetsroll, projekt, tilldelning eller AI-leverantör ska ALDRIG ändra karaktärs-ID. `data-character-id` i figurens DOM styr spritefil. Yrkesroll får styra framtida arbetsredskap och uppdrag, men inte personens utseende.

## Animationer

- `idle`: andning / liten positionsförskjutning.
- `walk`: stegvisa benrörelser; endast visuell rörelse, aldrig ett AI-uppdrag.
- `working`: liten handrörelse och arbetsredskap; ännu ingen verklig arbetskoppling.
- `cafe`: kaffekopp och liten handgest; ännu ingen verklig arbetstid.

Alla tillgångar är **spelgrafik** – inte nya AI-motorer, och de startar inga externa anrop. V3.2 ritar kontorsfigurer enbart ur nya personalkatalogen; gamla projektbundna personalvyer visas inte i v3-läget.

## NEXT / LATER

**NEXT:** utvärdera sprites visuellt i riktig Firefox på Ubuntu; jämför varje kandidatkort med figur på kontorsgolvet. Bygg verklig tilldelning och uppgiftsstatus via global v3-jobbkö.

**LATER:** fulla sidor/bakifrån, verktyg efter roll, blinka/prata/reagera, fler animationer och en riktig rekryteringsportfolio. Behåll denna kanoniska ID-konvention.
