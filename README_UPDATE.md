# Uppdatering till v0.11.7.0

Packa upp i en ny programkatalog eller kopiera källfilerna över en existerande Git-arbetskatalog **utan att radera `.git/`**. Stoppa äldre Python-server innan start. Projektdata under `~/.pixelworks/projects/` påverkas inte när ZIP-filen packas upp.

## Prova
1. Välj ett befintligt spelprojekt.
2. Klicka **📖 GAME BIBLE** på väggen bredvid Projektstatus (eller knappen `📖 Game Bible`).
3. Bläddra bland kapitlen. Den ursprungliga Game Bible är skrivskyddad.
4. Välj t.ex. **Spelvärlden och platser**, skriv om kaféet och fotolabbet och klicka **💾 Spara sida**.
5. Öppna kapitlet igen och kontrollera att texten finns kvar.

Bokkapitlen sparas i `studio-bible/book/*.json` och är inte ännu automatiskt AI-synkroniserade. Referensfiler hanteras fortsatt via **📎 Material**. Befintlig `GAME_BIBLE.md` ändras inte.
