# Aktuellt tillstånd – Pixel Works v0.12.11.18

Det här är en **delta-uppdatering** på v0.12.11.17; ingen fullständig installationsbild.

GUI: samtliga åtta vanliga arbetsstationer får den nya kategoribaserade popupen vid klick. Grafik har första stationsunika pixelillustrationen, övriga mjuka färgteman. Chefsbord/Fika och gamla arbetsköflöden bevaras.

Backend: arbetsorder sparas i befintligt per-projekt-API; inga nya provider-anrop eller filskrivningar vid sidladdning. Körning via `python3 backend/server.py` kräver fortfarande originalmotorn i användarens lokala Git-historik. Kända tidigare regressionstestproblem kvarstår.

Planering: mötet kan visa ett lokalt, deterministiskt planförslag för en NPC, och skicka ett särskilt planeringsuppdrag till arbetskön efter explicit val. **Riktiga beroenden och automatisk flera-arbetsordrar-delegering återstår.**

Verifierat: fyra isolerade backendtester, ett Chromium-flöde med fiktiv API-respons samt JavaScript-/Python-syntax. Inte verifierat: användarens faktiska Firefox, live-anrop, hela äldre systemregressionen.
