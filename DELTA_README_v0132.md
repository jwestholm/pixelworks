# Pixel Works v0.13.2 – Chefsbordet startar planeringsarbete

**Installera ovanpå v0.13.1.** ZIP:en innehåller endast ändrade/nya filer; den rör inte spelprojekt, rapporter, API-nycklar eller GitHub. Starta med `python3 backend/server.py`, ladda om Firefox med **Ctrl+Shift+R**.

## Rotorsaken – verifierad mot inspelningen från 2026-10-26

Tre order på station `lead` står som väntande: **Gör en prioriterad utvecklingsplan**, **Föreslå arbetsorder och ansvariga**, **Granska befintliga rapporter**. Chefen är korrekt placerad vid `lead` och studioarbete är tillåtet.

I v0.12.11.11 infördes `_eligible` som uttryckligen nekar `role_type=lead` för **alla** arbetsorder. Den nya parallellplaneraren i v0.12.11.15 bygger sedan helt på den behörighetskontrollen. Ingen kan väljas för de tre `lead`-orderna. Dessutom anropade högerspaltens "Försök starta uppdrag" en äldre endpoint som bara returnerade `ready` för Codex-personal utan att starta Codex-jobbet. Varken omstart eller personalflytt åtgärdar något av felen.

## Korrigering

1. Chefen är valbar **endast för egna planerings- och granskningsorder** på station `lead`, och endast när personen faktiskt står där och har behörighet. Chefen blir inte generisk kodskrivare.
2. Planeraren reserverar **högst ett chefsuppdrag i taget**. Nästa order ligger kvar och kan tas när det första är avslutat. En pågående chefssession blockerar dubbelstart.
3. Endpoint `/api/pw-v0132/start-lead` nås via det befintliga användartokenet och samma-origin-kontrollen. Den återanvänder nuvarande väntande order, studioåtkomst, Codex-tillgång och skyddad `/api/jobs`-start. Inga nya eller dubbla arbetsorder skapas.
4. Chefens arbetsorder kör Codex CLI med `--sandbox read-only`, inte `workspace-write`. Den ger en **planeringsrapport**, ändrar inte spelkod, gör ingen merge och skapar inga riktiga underuppdrag automatiskt.
5. All annan programmering, Gemini, Game Bible och personal-/projektlagring använder oförändrat tidigare beteende.

## Tänk på

- Den första chefsordern skapar en rekommendation. Den **genomför inte** alla underuppdrag automatiskt. Plan till riktiga beroendestyrda uppdrag är en separat produktfunktion.
- Om Codex CLI saknas, autentisering misslyckas eller uppstarten av en säker isolerad arbetsyta misslyckas ska ett konkret fel visas, inte en falsk lyckad start.
- Testerna använder mockade CLI/API-svar. Faktisk Codex-session och din Firefox är **inte** verifierade här.

## Testning

- 7 riktade testsituationer: korrekt val av Chefen, inget jobb på fel station, högst en chefssession, inget dubbelarbete, start med exakt befintlig order och skrivskyddad CLI-körning.
- 24 äldre relevanta backendtester för personalplanerare, parallelljobb och studiopersonal kördes i separata processer och passerade.
- Python-kompilering, JavaScript-syntax och ZIP-integritet kontrollerades.
- Äldre osynkroniserade tester för avskaffad lokal Gemini-dygnskvot förblir kända. Ingen fullständig grön regressionstestsvit utlovas.

## Ändrade filer

- `backend/pw_v0121111.py` – valbar chef för `lead`.
- `backend/pw_v0121112.py` – manuell start för Chefens station.
- `backend/pw_v0121115.py` – chefens jobb planeras ett i taget.
- `backend/pw_v013.py` – laddar senaste fixen och höjer version.
- `backend/pw_v0132.py` **ny** – skrivskyddat chefsarbete + autentiserad startendpoint.
- `src/pw-v0121117.js` – startknappen använder nya endpointen för chefsbordet.
- `src/pw-v013.js` – versionsetikett.
- `backend/test_pw_v0132.py` – riktade säkerhets-/funktionstester.

## Rollback

Återställ filerna ovan från v0.13.1-paketet (och ta bort `backend/pw_v0132.py`). Inga bestående migreringar har utförts.
