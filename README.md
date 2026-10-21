# Pixel Works v0.10.9 – Agentidentitet & aktivitetslogg

Uppdatering ovanpå v0.10.8.1. Lägg installationen i **egen katalog**; användarens projekt under `~/.pixelworks/projects` ska inte flyttas, raderas eller kopieras över.

Starta i denna mapp: `python3 backend/server.py` och öppna `http://127.0.0.1:8765`.
Stoppa en server som startats från föregående installationsmapp med `python3 backend/server.py stop` **från den ursprungliga mappen** innan ny version startas. Verktyget stoppar bara sin egen verifierade process.

**Nytt:** Visar korrekt agent-ID i agentdialoger, avsändarnamn i aktivitetsloggen, agentkopplade rapporter och ❗📄 på bord med väntande arbetsorder.

**Inte nytt:** Ingen MCP-server, arbetsledare, autonom scheduler eller samtidiga skrivsessioner i samma projekt. Den verkliga Codex-processen arbetar fortfarande en i taget per projekt.

Se `CURRENT_STATE.md`, `ROADMAP.md`, `TEST_REPORT.md`.

## Nytt i v0.11.0
Under **+ Rekrytera → ⚙ Profil** kan en anställd ändra namn, yrkestyp, titel, personlighet, hemmabord, arbetsbeteende, stationsbehörighet och egna arbetsinstruktioner. **★ Skills** öppnas från profilen.

Separata Codex-processer som skriver samtidigt i samma projekt är **inte** aktiverade. Ytterligare arbetsytor/worktrees och granskat integrationsflöde måste byggas först för att undvika överskrivningar.
