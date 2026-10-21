# Testprotokoll – v0.11.4

**91 backendtester passerar** (`python -m unittest discover -s backend -p 'test_*.py' -q`).

JavaScript syntax (`node --check local.js`) och frontendtesterna `test-model.mjs`, `test-navigation.mjs`, `test-recruit-routing.mjs`, `test-station-creator.mjs` passerar.

Nya tester verifierar att: projekt utan Git-commit begränsas till ett jobb; två agenter får två olika Git-worktrees efter en ren baseline-commit; arbetsledaren bara utför när arbetare inte kan ta uppdraget; Gemini-nyckeln lagras som 0600 utanför projektet och inte exponerats i status; sparad nyckel inte startar molnanrop.

**Ej verifierat**: riktiga samtidiga Codex-processer på användarens Ubuntu, faktisk integration av deras ändringar, fungerande popup i Firefox, live-status efter servers omstart. Systemet kräver fortfarande aktiv flik för automatisk distribution av nya jobb. Arbetsytorna behålls för manuell granskning och måste hanteras av projektägaren. Git-avvikelse/konflikthantering samt automatiserad review/merge återstår.
