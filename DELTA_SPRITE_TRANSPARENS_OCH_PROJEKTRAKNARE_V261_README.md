# Pixel Works – Transparenta pixelfigurer + tydlig spelräknare (v2.6.1)

Minimal delta ovanpå **v2.6** (som i sin tur kräver v2.5 med aktiverat globalt personregister). Utgångspunkt för GitHub dev: `fb70d1c9a927e07e802537c83705db5b8f9876cd`.

## Installation

1. Packa upp ZIP-filen i projektroten (`index.html` och `src/` finns där) och skriv över **`src/pw-global-office-v26.js`**.
2. Tryck **Ctrl+F5** i Firefox; ladda om mobilen.
3. Backend behöver normalt **inte** startas om – endast en JavaScript-fil ändras.
4. Gå till Kontor. Figurerna ska inte längre ha vit knappbakgrund; nedre räknaren ska exempelvis visa **🏢 15 anställda · 5 spel · 1 studio** om API:et rapporterar 15 personer och fem spel.

## Varför buggen fanns

Varje global figur är en `<button>` för att kunna klickas och dras. Den saknade explicit transparent bakgrund. Standardutseendet hos webbläsarknappar kan därför måla en ogenomskinlig rektangel bakom pixelgrafikens genomskinliga pixlar. Ändringen **sätter enbart `background-color:transparent`** och bevarar sprite-bildens `background-image` (vi använder inte CSS `background`-shorthand, som hade raderat själva bilden).

Texten ”1 studio” är **inte** ”1 projekt”: studion är gemensam och flera spel finns kvar. Nu visas både **antal spel från `/api/pw-v013/studio`** och antalet anställda som verkligen ritats, utan hårdkodad siffra. Om projektlistan inte kan läsas visas ”spelantal okänt”, inte 0 eller 1 på gissning.

## Test

- `node --check src/pw-global-office-v26.js` – godkänd.
- Playwright Chromium med fiktiv backend: 15 individuella figurer, exakt transparent knappbakgrund, 5 spel i räknaren, projektbyte utan försvunnen personal, knappklick, projekt-ID-styrd dragning, scroll på desktop och mobil – godkänt.
- Inga riktiga AI-anrop, projektändringar, avskedningar eller GitHub-pushar.
- **Inte verifierat i din Firefox på Ubuntu.** Om någon vit rektangel blir kvar efter Ctrl+F5, behöver vi granska faktisk sprite-PNG/ytterligare CSS-lager.

## NOW / NEXT / LATER

- **NOW:** transparent bakgrund bakom sprites och pedagogisk räknare.
- **NEXT:** migrera jobbsystemet och avsked till ett enda serverbaserat globalt personalregister, så personal inte behöver vara knuten till gamla `STAFF.json` per projekt.
- **LATER:** avveckla äldre projektlokala personalvägar efter verifierad datamigrering; synkronisering mellan telefon och dator, och förbättrad mobilkamera.

**Avskeda inte gamla poster enbart för att göra kontoret mindre** innan jobbmotorn och historikkopplingarna är globalt migrerade. Inget i v2.6.1 ändrar det underliggande personalregistret.
