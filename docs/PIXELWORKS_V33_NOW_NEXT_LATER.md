# Pixel Works v3.3 – aktuell status (2026-10-30)

## NOW – faktiskt implementerat

- V3-teamet är den kanoniska personalstyrkan. Sex rekryteringspersonas + Chefen har fasta karaktärs-ID:n, arbetsstil, sprites och rollstyrkor.
- Person och AI-motor är separata. Roll/arbetsbeskrivning kan redigeras; personlighetskatalogen styrd av spelet förblir oförändrad.
- `pw_v3_jobs` skapar manuellt godkända AI-jobb per anställd och projekt med fasta personspecifika promptavtal.
- Gemini: bekräftad kapacitet från befintliga inställningar; verkligt textanrop endast efter godkännande; svar kräver granskning.
- Codex: kräver verifierad CLI+lokalt skrivmandat+ren Git-rot; isolerad worktree, ingen autointegration, explicit andra godkännande.
- Jobbresultat och beslut sparas i studio-v3/jobbfiler; `source=provider_reported`, `verified=false` om ingen oberoende QA föreligger.
- Två lokala testsviter plus gamla rekryteringstester och Chromium på desktop/mobil gröna. Inga riktiga AI-anrop i testerna.

## NEXT – viktigast före automatisk delegering

1. Testa v3.3 med *ett* kort Codex-uppdrag och *ett* kort Gemini-textuppdrag på användarens Ubuntu, verifiera verklig behörighet, prompt och felhantering. Gör inte externa AI-anrop utan spelarens uttryckliga klick.
2. Låt Chefen föreslå *vem och varför* via spelstats + verkliga behörigheter, med spillerstyrda uppdragsbeslut. Bygg idempotenta jobb och central kö över flera klienter.
3. Öppna verkliga testartefakter och Git-diff i granskning, med verifierbara testresultat, samt återkopplingsorder från avvisade förslag.
4. Integrera uppdrag, granskning och rapporter med den generella beslutslappen utan nya specialdialoger.
5. Modellunderval för Gemini samt Pollinations via verifierad katalog; kvoter och pris måste hämtas från leverantör, aldrig gissas.

## LATER

- Bild- och ljudmotorer, Freesound/verktygsregister i v3-jobb med förhandsvisning; riktig testning på användarens maskin.
- Globalt projektoberoende arbetslag med samarbetsmönster, småprat, personliga drag och mentor/QA-par, utan felaktiga psykiatriska stereotyper.
- Full livscykel, bättre uppföljning, tydliga behörigheter per roll, opt-in automatisering, tydlig enhets-/LAN-synk.

## Kända gränser

- Nuvarande v3.3 är ett avgränsat manuellt uppdragssystem, inte en autonom chefsplanerare.
- Ingen automatisk jobbretry vid serveromstart eller kvotfel, inga automatiska GitHub-pushar.
- När en model säger att den har testat något räknas det inte som verifiering utan separat bevis.
- Jobbarens rollpoäng baseras på **fiktiva spelstats**, inte mätningar av AI-modellens kvalitet.
