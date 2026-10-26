# Pixel Works v0.12.11.5 – Gemini granskas i spelet

**Delta från v0.12.11.3 eller v0.12.11.4.** Endast ersättningsfiler och nya moduler. Ingen `server_v01210.py`, inga installationsskript, ingen GitHub-push. De tidigare tilläggen från v0.12.11.3 (inklusive `src/pw-v01210.js` och `backend/server.py`) måste redan finnas.

## Vad är nytt?

- **Högerspalten:** visar både Codex och Gemini med sin riktiga AI-leverantör. Gemini-uppdrag listas som *köad / arbetar / förslag klart för granskning / misslyckades*. Uppgiftsbeskrivningen visas när den är tillgänglig.
- **Direktgranskning:** knappen `📝 Granska / godkänn` för Gemini visas i aktivitetsloggen och på befintliga Gemini-rapporter i rapportpärmen.
- **Godkänn förslaget:** sparar ett uttryckligt beslut om förslaget. **Ändrar inte** spelfiler eller Game Bible, **kallas inte verifierat**.
- **Skicka till programmeraren:** skapar exakt **en** väntande arbetsorder på KOD-bordet, med Gemini-förslaget märkt som referensdata. En behörig Codex-programmerare måste senare utföra jobbet. Inga omedelbara API-anrop.
- **Be Gemini förbättra:** återför förslaget tillsammans med din feedback som en ny väntande dokumentations-/researchorder. Gemini arbetar igen om modell/kvot/studiotillstånd tillåter.
- **Avvisa:** sparar avslag utan att röra spelkod.
- Gemini-förslag ska inte längre visas som *blockerad Git-integration*: de har ingen kod-worktree att integrera. Tekniska modellfel redovisas i rapport/logg.
- **Studioåtkomst från v0.12.11.4 ingår**: godkänn lokalt arbete en gång, slå av via vanliga Inställningar.

## Installation

1. Stoppa Pixel Works på normalt sätt.
2. Packa upp filerna i ZIP-filen i din redan befintliga Pixel Works-mapp, med befintlig mappstruktur. Bara listade ersättningsfiler ändras.
3. Starta **alltid** med `python3 backend/server.py`.
4. Uppdatera Firefox med `Ctrl+Shift+R`.
5. Under **Ditt skrivbord → Rapportpärmen → Läs** finns `📝 Granska / godkänn Gemini-förslag`. Samma knapp finns vid färdiga Gemini-jobb till höger.

### Om du kör v0.12.11.2 eller äldre

Detta paket ersätter **inte** basuppdateringarna v0.12.11.3. Lägg in den versionen först, eller återställ spelkatalogen enligt din tidigare backup.

## Teststatus

- `PYTHONPATH=backend python3 -m unittest discover -s backend -p 'test_pw_v*.py'`: **57 tester godkända** i isolerad testmiljö.
- `python3 test_browser_012115.py`: **godkänt i Chromium** med simulerade API-svar och utan Google-anrop.
- Syntaxkontroller genomförda på Python och JavaScript.
- **Ej verifierat mot din riktiga Firefox, Gemini-kvot eller Codex CLI.** Resultaten av verkliga uppdrag måste skiljas från simulering.

## Tekniskt

Ändringar i `backend/pw_v01210.py` och `src/pw-v01211.js` utgår från 0.12.11.4. De laddar i sin tur de nya modulerna `backend/pw_v012115.py` och `src/pw-v012115.js`. Inga andra startskript tillkommer. Reviewbeslut lagras i befintlig projektlokal rapportfil; nya arbetsordrar i projektets vanliga WORK_ORDERS-lagring. Automatisk GitHub-push, användarens filer utanför Pixel Works och betalda modelluppgraderingar ingår inte.
