# Pixel Works v3.5.1 – Gemensam dialognavigation (DELTA)

**Bas:** den fungerande installationen med Pixel Works v3.5.0. GitHub-bas `fb70d1c9a927e07e802537c83705db5b8f9876cd`; inget har pushats.

## Installera

1. Packa upp ZIP-filen direkt i `~/pixelworks/pixelworks-git/` (projektrot med `index.html`).
2. Skriv över `src/main.js` och lägg till `src/pw-v351-dialogs.js`, `src/pw-v351-dialogs.css`.
3. Uppdatera Firefox med **Ctrl+F5**, och uppdatera mobilen. Ingen Python-serveromstart krävs för dessa JS/CSS-filer.
4. Öppna Personal, Uppdrag och Chefen. Överst finns nu **Personal / Uppdrag / Chefen / Beslut** plus **Tillbaka / Kontor**. Beslut når gamla mediagranskningen, med dess befintliga ljud och godkännanden.

## Det här förändras INTE

- Rekrytering, personregister, AI-jobb, Codex-Git-worktrees och Gemini-tokenhantering.
- Bild- och ljudförhandsvisning, Ja/Nej/Kanske, och projektfiler.
- Ingen automatisk AI-start, ingen skrivning till GitHub och inga avskedningar.

## Verifiering och kända begränsningar

Isolerade Chromiumtester med stubbade API: 10/10. Sammanlagt 33 UI-regressioner och 30 backendtester har passerat mot aktuella källor. Ingen riktig Firefox-/Ubuntu-/mobiltest hos användaren har gjorts.

Det är en **navigationskomponent**, inte en komplett totalrenovering av alla legacy-dialoger. AI-jobblistans beslut och mediainkorgens beslut är fortfarande separata backendflöden. Se `docs/PIXELWORKS_V351_DIALOGSYSTEM.md` för NOW/NEXT/LATER.

## Återställning

Återställ `src/main.js` från v3.5.0-ZIP-filen. De två nya `pw-v351-dialogs.*`-filerna kan då ligga kvar oanvända eller tas bort. Backend och projektdata behöver inte ändras.
