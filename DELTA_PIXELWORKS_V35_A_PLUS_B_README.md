# Pixel Works 3.5.0 — A+B: levande kontor & enhetlig UI-grund

**Bas:** GitHub `jwestholm/pixelworks`, `dev` = `fb70d1c9a927e07e802537c83705db5b8f9876cd` + kumulativa deltor genom **v3.4**.

## Installera

1. Packa helst upp en kopia/backup av nuvarande `src/main.js` och spara dina lokala Pixel Works-data separat.
2. Packa upp **ZIP:en i Pixel Works-rotkatalogen**, på samma nivå som `index.html`. Skriv över `src/main.js`.
3. Öppna/uppdatera sidan med `Ctrl+F5` i Firefox; ladda om mobilen. **Ingen backendomstart behövs** för denna frontend-/spriteändring. Vid gammal cache kan en serveromstart hjälpa.
4. Gå till kontoret. Ett nytt speldygnsfält visas nere till vänster. Välj **Auto / Dag / Solnedgång / Natt** och slå på/av **Prat** och **Rörelse**.

Inga arbetsorder, projekt, medarbetare, API-nycklar eller backendfiler ändras av denna delta. Ingen AI-körning startar av animationerna.

## Implementerat nu

- **Samma varma kontor hela tiden:** dekorativ simulering av 12-minuters speldygn, morgon, dag, kväll och natt med sol/måne, stjärnor, moln, ljusstråk, lampglöd och färgskiftande kvälls-/månljus.
- **Tydlig visualisering:** `SPELTID · DEMO`. Simulerad klocka är inte operativsystemets klocka, verkligt väder eller AI-aktivitet. Spelklockan baseras på klientens tidskälla och är ungefär synkad mellan dator och mobil, men är inte serverauktoritativ.
- **Ljusläge kan förhandsvisas:** Auto → Dag → Solnedgång → Natt → Auto; val per webbläsare (`localStorage`).
- **Sju unika personer:** Chefen, Joppe, Siv, Nisse, Mira, Vera, Lova får två extra transparenta spriteark var: `talk` och `celebrate` (fyra bildrutor, 48×68 per ruta). Tidigare sprites för `idle`, `walk`, `working`, `cafe` är kvar.
- **Personlighet i kontoret:** korta lokalt fördefinierade *DEMO*-pratbubblor och liten glädjeanimation när en ny person tillkommer; visar **inte** ett faktiskt AI-svar eller utfört jobb.
- **Enhetligare Pixel UI:** v3-rutorna för Personal/Rekrytering, AI-uppdrag och Chefsbordet använder en gemensam palett, pixelramar, knappar, text- och fokusfärger, plus en fullskärmsvy på mobil. De behåller sina existerande riktiga funktioner.
- **Tillgänglighet:** användaren kan pausa **dekorativ rörelse** och småprat oberoende; `prefers-reduced-motion` respekteras. Ingen automatisk ljuduppspelning.
- **Robust visuell lagerkoppling:** nytt ljuslager återskapas efter att scenens DOM ritats om; det ersätter inte det befintliga personalobjektet.

## Tekniskt upplägg

- `src/pw-v35-world.js` hanterar scen, spelklocka och dekorativa sprite-state; **inga API-anrop**.
- `src/pw-v35-world.css` definierar sky, belysning, rörelse och delade v3-designtokens.
- `src/main.js` importerar den visuella modulen **efter** v3 Chefen.
- `assets/characters/<id>/<id>-talk.png` och `...-celebrate.png` skapas från de fasta v3.2-identiteterna utan att byta hårfärg, porträtt eller person-ID.

## Testat

- 31 Python-backendtester gröna (fiktiva data, ingen verklig provider).
- 23 äldre Chromium-UI-tester gröna (v3.3/v3.4).
- 8 nya Chromium-tester gröna (dygnslägen, omritning, ID-koppling, mobilfönster, reducerad rörelse, dialogtema, ingen extra providertrafik, sprite-format).
- Inga riktiga AI-anrop eller internetförfrågningar gjordes. **Inte verifierat i användarens Firefox/Ubuntu med hela spelkontoret och riktiga kontorsassets.**

## Begränsningar

1. Visuella sol- och månpositioner följer ett simulerat 12-minutersdygn, **inte geografisk soluppgång eller riktigt väder**.
2. Figurerna har nu **sex animtillstånd** (idle, walk, working, cafe, talk, celebrate) på teknisk nivå, men `talk` och `celebrate` är **enkla första pixelposer**. Kompletta art-direktionerade animationer, blinka, sitta/resa, interaktiva samtal och variation per karaktär är inte färdiga.
3. Detta ger de tre centrala **v3-dialogerna** en visuell grund, men bygger ännu inte om alla äldre dialoger till *en gemensam modal-komponent*. Vissa tekniska/äldre rutor har fortfarande annat utseende. Gör den större refaktorn efter nytt visuellt godkännande.
4. Personers verkliga arbetsstatus styrs endast av backends jobbinformation, **aldrig av dekorativa bubbelslingor**.
5. Frontendklockan ändrar inte deadlines, chefens delegering, Git eller AI-API-åtkomst.

## Om du vill återställa

Ta bort importen av `./pw-v35-world.js` i `src/main.js` eller återställ `src/main.js` från din v3.4-backup och uppdatera sidan. Övriga v3-filer har inte ändrats. De extra PNG-filerna är ofarliga att låta ligga kvar.

## Fortsatt riktning

Se `docs/PIXELWORKS_V35_A_PLUS_B_DESIGNSYSTEM.md` (NOW/NEXT/LATER).
