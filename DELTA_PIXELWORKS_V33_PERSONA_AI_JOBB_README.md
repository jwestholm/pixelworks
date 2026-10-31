# Pixel Works 3.3 – Riktiga uppdrag med v3-personas (DELTA)

**Bas:** GitHub `jwestholm/pixelworks`, `dev` `fb70d1c9a927e07e802537c83705db5b8f9876cd`. **Kräver installerad v3.2** och dess föregående deltan. Inga ändringar pushade.

## Installera på Ubuntu

1. Säkerhetskopiera `~/.pixelworks` och din Pixel Works-projektkatalog före uppdatering (skydda kopian; den kan innehålla API-nycklar). Kopiera inte nycklar till Git.
2. Packa upp ZIP **i Pixel Works-roten**, där `index.html`, `backend/`, `src/` ligger. Skriv över filerna i de underkataloger som följer ZIP:en; skapa inte en extra `PixelWorks_V33/`-mapp.
3. Stoppa och starta servern med dina befintliga kommandon, exempelvis:
   ```bash
   python3 backend/server.py stop
   bash start-lan.sh
   ```
4. Firefox: `Ctrl+F5`. På mobilen: ladda om sidan. Du behöver inte återaktivera eller migrera personregistret.
5. Öppna **🧠 AI-uppdrag** via spelmenyn, eller **Personal → en person → Ge verkligt AI-uppdrag**.

## Spelbart arbetsflöde

- Välj **anställd** (Chefen eller en annan anställd i nya v3-studion), **spelprojekt**, **motor** och **uppdrag**. Första vyn visar tillgänglighet enligt de befintliga motorernas verkliga status; spelstats redovisas separat och är **inte** mätning av modellens förmåga.
- **Godkänn och starta** ger ett andra uttryckligt användargodkännande. Ingen AI startar när du bara öppnar personalkortet.
- Servern bygger prompt från **fast karaktärs-ID + persona + personlig arbetsstil + din ändringsbara arbetsbeskrivning + arbetsuppgiften + projektets Game Bible som otillförlitlig referensdata**. Rollen ändrar inte personens ansikte eller fastslagna personlighet.
- **Gemini**: använder den befintligt verifierade Gemini-anslutningen och dess för närvarande konfigurerade textmodell; ett API-anrop, inget automatiskt byte eller återförsök. Textförslaget blir **väntar på granskning**. Godkännande markerar förslaget som godkänt, **men skriver inte in det i Game Bible eller projektfilerna**.
- **Codex CLI**: kräver faktisk Codex CLI, Studioåtkomst och **ren/committad egen Git-rot i `project/work/`**. Skapar en isolerad worktree och kör `codex exec --sandbox workspace-write --json`. Ingen automatisk Git-commit i ditt ursprungliga arbetsprojekt vid start. Resultatet stannar för **Ja/Nej/Kanske**. Vid **Ja** används befintlig lokal säker Git-integration (`integrate_worker_result`): avbryt vid konflikt eller smutsig huvudmapp. **Ingen push**. Filnamn från Git visas inför beslut, men är inte kvalitetsverifiering.
- **Nej:** avvisar utan att integrera. **Kanske:** lämnar i granskningskö. Feedback vid Nej lagras i jobbrapporten, men **skapar inte automatiskt ett nytt AI-jobb**.
- Jobb, resultat och beslut sparas i **`~/.pixelworks/studio-v3/jobs/<job-id>.json`**, alltså skilt från gamla personalfiler och projektens spelkod. Jobb kan läsas från andra webbläsare på samma LAN. Inget startas om automatiskt efter omstart; ofullbordade jobb visas som **avbrutna**.

## Vad versionen INTE gör

- **Ingen automatisk delegation från Chefen.** Du väljer vem som kör. Chefen kan jobba själv; senare versioner får ha rekommendationer och godkänd delegering.
- Ingen fri undermodellsväljare för Gemini/Pollinations, ingen verklig bild- eller ljudgenerering och ingen automatisk Freesound-koppling i den nya v3-pipelinen.
- Inget betalt verktyg, ingen extern tjänst och inga riktiga AI-anrop har använts av testsviterna. Med en riktig API-nyckel kan **ditt uttryckliga Start-beslut** däremot förbruka kvot eller pengar beroende på tjänst/abonnemang.
- Den nya uppdragsrutan ersätter inte ännu samtliga äldre rapport- och fönsterkomponenter. Den gamla personalschemaläggaren är fortsatt pausad när v3-personalstudion är aktiv.
- Inga testbevis för verkliga Codex-/Gemini-anrop i användarens Ubuntu-miljö. Testerna använder fake Codex-CLI och stubbat Gemini API.

## Begränsningar och säkerhet

- Personliga karaktärsdrag styr **ton, arbetstempo, rapporteringsform och förslag**, aldrig behörighet eller sanningskrav. En fiktiv slarver får inte medvetet skriva osäker eller felaktig kod.
- Gemini-resultat, Codex-rapporter och eventuella testpåståenden är **leverantörsrapporterade – inte oberoende verifierade**. Godkännande är ett spelarbeslut, inte en automatisk QA-stämpel.
- Codex har en maximal körtid på 10 minuter. Om det körs via CLI som kan exekvera kommandon bör du ge begränsade, tydliga uppdrag i projektets isolerade arbetskopia. Aldrig automatiska GitHub-åtgärder.
- Ett avbrutet Codex-arbete kan lämna en isolerad Git-worktree kvar. Inga arbetsgrenar tas bort automatiskt, eftersom de kan innehålla arbete som bör sparas.
- Om terminalen indikerar att den **gamla schemaläggaren** fortfarande startar jobb efter v3-aktivering: stoppa servern och kontrollera att `backend/server.py` verkligen kommer från den här deltan. Starta inte om gamla uppdrag av misstag.
- På lösenordsfritt hemma-LAN kan andra enheter i det betrodda nätet använda samma manuella AI-uppdragsknappar. Ingen port forwarding mot internet.

## Filöversikt

- `backend/server.py` – installerar v3.3-kopplingen före LAN-säkerhetswrappers.
- `backend/pw_v3_jobs.py` – säkerhet, uthålliga jobbrapporter, providers, prompt/roll/skills, tvåstegsgodkännande, Git-worktrees och resultat.
- `src/main.js` – laddar uppdrags-UI.
- `src/pw-v3-recruit.js` – uppdaterar personalprofil/handlingsknappar; bevarar spriteidentiteter.
- `src/pw-v3-jobs.js` – AI-uppdrag och granskning, desktop/mobil.
- `backend/test_pw_v3_jobs.py`, `backend/test_pw_v33_routes.py`, `tests/test_pw_v33_ui.py` – återkörbara isolerade tester.
- `docs/PIXELWORKS_V33_NOW_NEXT_LATER.md` – aktuell arbetsstatus och nästa steg.

## Tester (miljön där paketet byggdes)

```bash
PYTHONPATH=backend python3 -m unittest -q backend/test_pw_v3_jobs.py backend/test_pw_v33_routes.py \
  backend/test_pw_recruitment_v3.py backend/test_pw_recruitment_v31.py backend/test_pw_recruitment_v32.py
python3 -m unittest -q tests/test_pw_v33_ui.py
node --check src/pw-v3-jobs.js
node --check src/pw-v3-recruit.js
```

37 backendtester och 5 Chromium-webbläsartester var gröna; generering/testning sker med fiktiva providers. Lokal fake Codex-exekvering testar Git-isolering och att integration **inte** sker innan spelaren klickar Ja. Testad på desktop + mobil bredd. Se detaljer i testfilerna.

## Rollback

1. Stoppa Pixel Works.
2. Återställ `backend/server.py`, `src/main.js` och `src/pw-v3-recruit.js` från din v3.2-installation eller backup.
3. Ta bort de två **nya kodfilerna** `backend/pw_v3_jobs.py` och `src/pw-v3-jobs.js` om du vill; de laddas inte i återställd v3.2.
4. **Radera inte** `studio-v3/jobs/`, projektens worktrees eller projektdata automatiskt. De kan innehålla arbete som behöver granskas.
5. Starta servern igen och rensa Firefox-cache med `Ctrl+F5`.
