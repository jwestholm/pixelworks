# Pixel Works CURRENT STATE – v0.13.4

- **Launcher:** `python3 backend/server.py`. Kräver den ursprungliga lokala Git-motorn. Ingen nytt installationsskript.
- **Studion:** gemensam kontorsvy; tilldelad personal i projektspecifika register med stabil `studio_id`, ingen destruktiv automatisk migrering.
- **AI:** Codex CLI kan ta fram strikt JSON-plan med rätt arbetsstationer, beroenden och instruktioner i skrivskyddad arbetsyta. Gemini- och Codex-exekvering ligger i befintliga adaptrar, ej omarbetade i denna patch.
- **Produktionsplaner:** v0.13.4 håller nya flerstegsplaner låsta i arbetskön tills en människa granskat och godkänt hela planen. Åtgärderna valideras i backend.
- **Projektstart:** Game Bible får ett registrerat prototypavsnitt, `work/` får en användbar HTML5-miniproto och Git får första lokala commit. För gamla projekt krävs valfri knapp och helt ren work-mapp.
- **Verifierat:** 28 lokala backendtester, två simuleringar i Chromium (genererat HTML5-spel + UI med mock-API), Python/JS-syntax. **Ej verifierat med riktig AI-session eller i användarens Firefox.**
- **Begränsning:** full historisk regressionstestsvit är inte grön; gemensam transaktionell kö återstår.
