# Pixel Works 0.13.0 – observerat nuläge

**Installeringsbas:** 0.12.11.18 med original-Git-klon i `dev` och de efterföljande versionsdeltana. Start: `python3 backend/server.py`.

**Verkligt byggt:** global, projektöverskridande personalvy med stabilt härlett `studio_id` samt säker, explicit personflytt mellan projekt. Personer från andra spel kan klickas i samma kontor. Verkliga arbetsorder går fortsatt via befintliga projektbundna API:er. Efter explicit aktivering skapas inget ytterligare startteam för nya projekt.

**Inte klart:** enda gemensamma schemaläggare/kanoniska HR-tabell, Story Mode, Arcade, permanenta automatiska grupparbetsplaner. Äldre projektbaserade schemaläggare är kvar. Fullständig regressionstestning är ännu inte grön (kända äldre fel).

**Verifierat med mocks:** 15 Python-tester, Chromium studioflöde och stationuppdragsflöde. **Inte verifierat live:** användarens Firefox, Codex/Gemini-jobb, verkliga tokens och isolerade parallella Git-worktrees.

**Dataskydd:** Ingen skrivning vid installation/import/GET. `studio-v013/STUDIO.json` skrivs först när spelaren väljer gemensam studio. En flytt skriver personalfiler och eventuella skillöverstyrningar; inga spelfiler eller Game Bible-redigeringar. Transaktionsjournal är explicit återställbar efter avbrott.
