# Pixel Works v0.11.7.0 — Aktuellt läge

## NOW — Levererat i denna version
- 📖 Game Bible som väggobjekt i kontoret och bokvy med bläddringsbara kapitel.
- Åtta redigerbara kapitel: Vision, Spelvärlden och platser, Karaktärer, Berättelsen, Spelmekanik, Grafik och referenser, Musik och ljud, Idébanken.
- Befintliga `studio-bible/GAME_BIBLE.md` visas skrivskyddad som originalsida. Befintligt material finns kvar i referensbiblioteket; bokvyn listar bildreferenser med namn/kommentar.
- Kapitel sparas per projekt i `studio-bible/book/<kapitel>.json` med atomisk filersättning och kontroller mot symlänkar och ogiltiga ID.
- Misslyckad Codex-session får tydligare "Jag behöver hjälp" i rapportens sammanfattning och felorsak om känd.
- Agent med olöst misslyckad eller blockerad rapport får en tydlig, ihållande hjälpmarkering ovanför figuren vid nästa synkronisering (kräver aktiv projektvy).
- Versionsmarkering i gränssnitt och server uppdaterad.

## NEXT — Högsta prioritet
- End-to-end-test med riktig Codex och Firefox på användarens dator: kontrollera att felrapport, olästmarkering, arbetarpopup och arbetsorderns status alltid stämmer överens.
- Förfina hjälpmarkeringen med en riktig animerad pratbubbla och ett åtgärdsflöde som kan lösa blockeringen utan att manuellt arkivera rapporten.
- Redigering och visning av bilder, tabeller, matriser och relationskartor direkt på boksidorna. Vårt materialbibliotek är separat i nuläget.
- Säker tvåvägssynkning mellan nya bokkapitel och Codex-kontexten (ännu inte implementerad).

## LATER
- Designmöten med AI-förslag, godkänd uppdatering av Game Bible och versionshistorik för hela boken.
- Arbetsledargranskning, Gemini/Creative Director, XP/level för projekt, rekrytering med källbelagda modellbetyg.

## Verifiering
- 122 backendtester passerar i isolerad tillfällig projektrot.
- JavaScript syntax och samtliga befintliga `.mjs`-kontroller passerar.
- Inga autentiserade Codex-anrop, ingen riktig Firefox-rendering och inga ändringar i `~/.pixelworks/projects/` i denna utvecklingsmiljö.
