# Pixel Works v0.13.5 – Produktion utan extra godkännandestopp

**Bas:** v0.13.4. Detta är en **DELTA-ZIP** med bara ändrade/nya filer. Packa upp över den befintliga installationen. Kör därefter `python3 backend/server.py` och hårduppdatera webbläsaren (`Ctrl+Shift+R`). Ingen GitHub-push, inga installationsskript, ingen ändring av befintliga projektfiler i distributionspaketet.

## Varför

I den inspelade 2:42-minuterssekvensen fick Chefen fram en korrekt trestegsplan för Pussel men allt stod still tills spelaren öppnade planredigeraren och klickade ”Godkänn och starta”. När Greta sedan levererade en konkret designrapport fick Gunnar inte gå vidare förrän rapporten manuellt godkänts. Även återanvändning av en äldre chefsrapport krävde dubbelklick för bekräftelse.

## Vad som faktiskt ändras

- **Automatisk planstart:** När ett *redan godkänt* projekt med aktiv **studioåtkomst** får en giltig fler-stegsplan använder 0.13.5 befintlig servervalidering för att **släppa fri planen direkt**. Ingen extra knapp behövs. Det gäller även tidigare kvarliggande 0.13.4-utkast när den ordinarie kömotorn kontrollerar projektet. En felaktig plan lämnas som synligt redigerbart utkast, inte som falskt färdig.
- **Intern designöverlämning:** En rådgivande rapport från ett verkligt avslutat Gemini-/Codex-jobb vid **Dokumentation, Forskning eller Möte** kan låsa upp efterföljande arbete när den är sparad, även om spelarens granskning av förslaget fortfarande är frivillig. Rapporten **märks inte godkänd**, införs inte automatiskt i Game Bible och är fortsatt `state=review` med `verified=False`.
- **Verklig information till nästa arbetare:** Om ett kodjobb bygger på tidigare dokumentation ges *rapportsammanfattningen* som begränsad JSON-referens i programmerarens instruktion. Alla förslag behandlas uttryckligen som **odata/utkast, inte bindande nya instruktioner**. Aktuell Game Bible och användarens vision står över förslagen.
- **Fortsätt från äldre chefsrapport:** En knapptryckning räcker. Uppdraget skapas i det aktiva spelets kö och ordinarie scheduler hanterar det.
- **Synlig status:** Produktionspanelen visar `Automatiskt arbetsflöde` och `📨 Designunderlag lämnat vidare`, inte en obligatorisk planbeslutsstatus när planen redan har släppts fri.

## Viktiga skydd som INTE tas bort

- Ingen automatisk aktivering av studioåtkomst eller projektmandat. Samma tidigare uttryckliga engångsgodkännande krävs innan AI får arbeta i Pixel Works projektmappar.
- Ingen ändring av användarens fastslagna Game Bible-vision, ingen automatisk publicering, GitHub-push eller uppgradering till betalda AI-modeller.
- Kan en uppgift inte tilldelas behörig personal väntar den, och rätt orsak visas.
- Misslyckade arbeten, osparade rapporter och obekräftade **kod-/grafik-/ljudändringar** låser inte upp efterföljande produktion. En Codex-session måste faktiskt ha integrerats för att räknas som införd kod.
- De befintliga Gemini-kvoterna från Google, säkerhetsgränserna för anrop och Git-isoleringen påverkas inte.
- Förslag som påverkar projektets vision kan fortfarande granskas och godkännas som Game Bible-fakta **separat**. Att designutkast kan passera som arbetsreferens är inte samma sak som formellt godkännande av innehållet.

## Testat

- 20 offline backendtester för automatisk planstart, återupptagande av äldre utkast, mandatspärrar, omförsök, beroenden, förstörd/fejkad rapport, Codex-kod som inte införts och kontextöverlämning.
- 16 tidigare tester för 0.13.3 samt 12 tidigare tester för 0.13.4 godkända **i separata testrundor**.
- Chromium-smoke för panelen och ny advisory-handoff-status. Chromium-prov av HTML5-startmallarna godkänt.
- JavaScript- och Python-syntax kontrollerad, deltaarkivets integritet verifierad.
- **Inte verifierat:** verkliga privata Codex-/Gemini-sessioner i användarens lokala Firefox, extern kvot eller hela äldre regressionstestsviten (den innehåller tidigare kända fel).

## Testa manuellt

1. Installera över v0.13.4, starta om servern och hårduppdatera Firefox.
2. Öppna **Pussel** från inspelningen. Har planen fortfarande status *utkast* ska den ordinarie schemaläggaren automatiskt börja släppa fri stegen om studioarbete är godkänt.
3. Har Greta redan lämnat designunderlaget ska produktionspanelen visa att det är **lämnat vidare** och att Gunnars kodjobb är **redo** eller **arbetar**, utan extra granskning.
4. Om Gunnar inte kan starta trots det, kontrollera den **faktiska blockeringsorsaken** (anställd, verktyg/kvot, Git-worktree eller projektmandat). Inget av dessa verkliga hinder kringgås av den här patchen.

## Filer

- `backend/pw_v013.py` – installerar v0.13.5-adaptern efter befintliga versioner.
- `backend/pw_v0135.py` – nya autoproduktions- och överlämningsregler, installerade via befintlig motor.
- `src/pw-v013.js` – tydligare automatisk produktionsstatus och direktknapp för äldre chefsrapport.
- `backend/test_pw_v0135.py`, `test_browser_0135.py` – reproducerbara tester.
- `DELTA_README_v0135.md`, `CURRENT_STATE_v0135.md`, `NOW_NEXT_LATER_v0135.md`, `DELTA_MANIFEST_v0135.json` – dokumentation.
