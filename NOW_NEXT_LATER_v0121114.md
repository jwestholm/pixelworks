# NOW / NEXT / LATER — Pixel Works v0.12.11.14

**NOW (verifierat offline):** Kort aktivitetslogg, synlig personal/statistik, exakta gransknings-ID:n, beslut som överlever rapportavstämning, korrekt nolländringsstatus, skrivmandats-spärr för manuellt Gemini-jobb, ingen återlämning av sparade API-nycklar till GUI. Start sker fortfarande från `backend/server.py`.

**NEXT:** Konsolidera all personaldelegering genom en atomisk arbetarkö (anställd → exekveringsadapter). Gör `auto_projects`/`work_mode` meningsfulla eller ta bort dem ur gränssnittet. Direkta granskningslänkar från ❗ till rätt rapport. Förbättra idempotenta jobbavslut och gör den samlade testsviten grön.

**LATER:** Strukturera Game Bible-beslut för versionssäker AI-redigering, komplettera verklig användningsstatistik, förbättra beständig spelork och implementera fler verktygsadaptrar när anslutningarna faktiskt finns.

**SIMULERAT ≠ VERIFIERAT:** Ingen extern AI, lokal användarprojektdata eller live-Firefox har ändrats/testats. De riktade automatiserade testerna använder attrapper. Alla AI-kvoter hos tjänsterna är fortfarande tjänsternas ansvar.
