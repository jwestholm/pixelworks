# Pixel Works v0.12.11 — SNABBSTART & AI-ANSTÄLLDA

**Delta** för `jwestholm/pixelworks` från `dev` på commit `b6fdca9f748c1accee725ff88a246063fffe158d` (`v0.12.0.9`) **med v0.12.10.1 redan installerad**. Endast nya eller ändrade filer. **Inga installationsskript och inga projekt- eller API-nyckelfiler** ingår. Ingen GitHub-push eller merge har gjorts.

## Viktigt före uppackning

**Stäng den gamla v0.12.10.1-servern innan du ersätter filer.** Den gamla `backend/server_v01210.py`-starten ska inte längre användas. Avsluta processen du faktiskt startade (t.ex. med Ctrl+C i terminalen). Låt pågående AI-jobb avslutas först.

**Krav i just denna delta-version:** Pixel Works-programkatalogen måste vara en **lokal Git-klon** som har originalfilens Git-blob `1abf4bdd611ba543d73f79f6b7f79be28f777899` i sin historik. Den nya `backend/server.py` läser v0.12.0.9-motorn **från den lokala Git-historiken** och laddar AI-tilläggen. Den hämtar ingenting från internet och ändrar inte Git-historiken. Detta är en kompatibilitetslösning för små delta-paket, **inte** en fristående utgåva av hela serverkoden. Om originalblobben saknas stoppas starten med tydligt fel **innan** programmet rör projektfiler.

Du kan kontrollera att blobben finns i din Pixel Works-programkatalog:

```bash
git cat-file -t 1abf4bdd611ba543d73f79f6b7f79be28f777899
```

Svaret ska vara `blob`. Om kommandot inte fungerar: **ersätt inte din server.py med detta paket**. Då behövs en fullständig serverfil i en senare leverans.

## Byt filer

1. Gör gärna en säkerhetskopia av programkatalogen (inte hemligheterna).
2. Packa upp ZIP i Pixel Works-programkatalogen och behåll `backend/` och `src/`.
3. Starta **enbart** med `python3 backend/server.py`.
4. Öppna `http://127.0.0.1:8765` och gör hård omladdning (`Ctrl+Shift+R`). Version ska vara **0.12.11**.
5. När allt fungerar får du **manuellt** ta bort den oanvända `backend/server_v01210.py`. Arkivet tar inte bort filer automatiskt (inga installationsskript).

**Rör inte** `~/.pixelworks/projects/`, `~/.pixelworks/secrets/` eller Git-worktrees. Befintliga anställda, rapporter, Game Bible och projekt behålls. Nya standardanställda skapas **endast för nyskapade projekt** utan personal. Inga AI-anrop görs bara av att paketet packas upp; automatisk Gemini får däremot senare utföra väntande uppdrag om token finns, en behörig chef är på plats och uppgiften är ett läsuppdrag.

## Spelfunktioner

- **Ny produktion** öppnar nu snabbstart med spelnamn och spelidé, medan *Fler spelval* öppnar gamla avancerade guiden. Knappen *Skapa spel och starta studion* ger ett tydligt projektspecifikt tillstånd för arbete i det spelets arbetsmapp – inte GitHub-push.
- Varje nytt projekt får **Arbetsledaren vid chefsbordet och Programmeraren vid kodbordet**. Om studion har Gemini-token skapas även en Gemini-anställd för dokumentation/research.
- **Ett enda Codex-arbetsmandat:** nya snabbstartprojekt får mandat vid start. Äldre projekt som saknar mandat får en tydlig knapp i aktivitetspanelen.
- **Projektbyte:** senast valda projekt sparas i webbläsaren; nyast skapade visas först. Projektmenyn har en *Fortsätt senaste spelet*-knapp och varnar om ett sparat projekt saknas från serverns lista. Servern visar mappar med trasig metadata under `needs_attention`, utan att radera eller reparera något automatiskt.
- **Gemini:** bara global token, Visa/Dölj, Spara, Testa/verifiera anslutning samt status. Gemini-specialister kan få vanliga docs/research/meeting-uppdrag av arbetsledaren utan extra projektmandat. Textsvar märks **rapporterat, ej verifierat**; Gemini skriver inte spelkod.
- **Gratisförsiktighet:** Googles kvot/fakturering kan inte bevisas av token. Använd ett Google-projekt utan fakturering. Appen har ett konservativt lokalt tak **12 anrop per Google-kvotdygn**, gör inte automatiska omförsök på fel/429, och gör ingen automatisk betaluppgradering. Knappen *Testa anslutning* begär modellmetadata hos Google utan att generera text.
- Gamla `Projektstatus`-tavlan hålls borttagen; riktiga arbetsorder finns kvar i spelmenyn.

## Tester utförda i leveransmiljön

- **26 Python-regressionstester godkända** (ingen nättrafik i testerna).
- JavaScript-syntax: **PASS**.
- **Chromium offline-test med falska API-svar: PASS** för snabbstart, projektbyte, Gemini Visa/Testa och borttagen tavla.
- **Inte verifierat:** verklig Google-nyckel, faktureringsstatus, faktisk Codex-inloggning, GUI på användarens Ubuntu/Firefox, lokal `dev`-Git-klon och riktiga samtidiga arbetspass.

## Om ett spel saknas

Öppna `http://127.0.0.1:8765/api/projects` och kontrollera `projects`, `needs_attention` och `root`. Uppdatera inte eller radera projektmappar på chans. Förklara vilket spel-ID som saknas och vad API:et rapporterar.
