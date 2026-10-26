# Pixel Works v0.12.11.17 – Projektflöden & UX-stabilitet

**Installationsbas:** v0.12.11.16. **Format:** endast ändrade/nya filer. Packa upp i spelets befintliga mapp, **utan att radera andra filer**. Starta som vanligt med `python3 backend/server.py` och gör Ctrl+Shift+R i Firefox. Ingen GitHub-push, ingen installation, ingen migrering av användarens sparade projekt eller API-nycklar.

## Kritisk korrigering: felaktigt projektbyte

- Den tidigare `restoreSelection()` återställde lokalt sparat projekt **vid varje personaluppdatering** och kunde flytta spelaren till ett äldre projekt efter att ett nytt just skapats.
- Sparat projektval läses nu **bara vid första laddningen**. Därefter är spelets aktiva `model.activeProjectId` den auktoritativa sanningen; alla medvetna `model.switchProject()` sparas omedelbart.
- GUI:t visar **AKTIVT PROJEKT** överst i kontorets högerspalt och projektnamn i rapport-/arbetsdialoger.
- Nya extension-baserade POST-anrop nekas i webbläsaren om deras projekt-ID inte överensstämmer med det aktiva projektet; serverns egna behörighetskontroller gäller fortfarande. Vid avsiktligt projektbyte stängs dialoger som öppnats för ett annat projekt.
- Gamla projekt och rapporter ändras inte av patchen.

## Projektstart och personal

- Den befintliga stora spelguiden och alternativet **Skriv min egen spelidé** från v0.12.11.15 är bevarade.
- När guiden skapat ett spel ges en tydlig bekräftelse med **Gå till kontoret / Ge chefen första uppdraget / Visa personal** i stället för att spelaren kastas direkt in i anställningsformuläret.
- Skapandeknappen är i sig ett uttryckligt beslut att skapa en ny projektmapp; gamla webbläsarfrågan om att skapa själva mappen behövs därför inte för varje nytt projekt. **Detta ger inte AI:erna nya arbetsrättigheter.**
- Nya projekt får startpersonerna **Chefen, Gunnar och (om Gemini är konfigurerad) Greta**. Befintliga personer byter inte namn.
- Anställningsformuläret visar *Ny medarbetare* och föreslår inte automatiskt ett AI-produktnamn som personnamn. Den tekniska AI-motorn är kvar i personalprofilen.

## Studioåtkomst och rätt väg till beslut

- **Studioåtkomst är fortsatt ett uttryckligt, serverlagrat engångsbeslut** med möjlighet att stänga av det under Inställningar. Inga nya behörigheter ges automatiskt. Den nya synliga knappen **Aktivera studioarbete** återanvänder den befintliga engångsdialogen i v0.12.11.16. Äldre duplicerad varning döljs när den nya visar verkligt tillstånd.
- Kontoret har **Arbete och beslut** med antal aktuella granskningar och väntande uppdrag, direkta länkar till Gretas konkreta rapporter, varningar om granskningsordrar utan hittad rapport och en knapp till bordets arbetskö.
- En ny **Försök starta uppdrag**-knapp använder den befintliga skyddade arbetsdispatchern för en aktuell arbetsorder. Inga dubblettordrar skapas av gränssnittet. Om arbetsrättigheter, kapacitet eller säker Git-arbetsyta saknas ska serverns egentliga hinder visas.

## Bord och hover

- Bordsnamn utan kodförkortningar, bland annat **Programmering, Forskning, Testning, Dokumentation, Röststudio**.
- Tooltip, `title` och `aria-label` beskriver vad bordet används till, vilka medarbetare som är där och kända väntande/granskningsärenden.
- Bord öppnas fortfarande med samma ordinarie klick som tidigare; inga stationer tas bort.

## Verifiering

- 3 nya backend-kontraktstester gröna: HTML-injektion/version, åtkomstskydd och mänskliga startnamn.
- Sammanlagt **33 riktade backendtester gröna**: nya tester och befintliga tester för retry, parallell planering och granskningsregler.
- **Chromium-test med simulerade API-svar** grönt: startprojekt återställs endast en gång, projektbyte bevaras över personaluppdatering, wizard-skapande utan onödig extra bekräftelse, onboarding, byte under öppen dialog, korrekt rapportlänk, engångsstudiotillstånd, bordsnamn/hover och skydd mot fel projekt.
- Den **fullständiga äldre testsamlingen är inte grön**: v0.12.11.16 hade 131 tester och **8 misslyckade / 19 testfel**; v0.12.11.17 har 134 tester och **samma 8 misslyckade / 19 testfel**. Detta är äldre testkontrakt och återstående regressionsarbete, inte en ny felfri totalversion.
- Riktiga Codex-/Gemini-anrop eller installation i användarens Firefox har **inte utförts** här.

## Kända återstående begränsningar

- Arbetsledaren har fortfarande flera underliggande planerings-/delegeringssystem och separata äldre formulär. Detta kräver en gemensam transaktionell arbetsmotor i en separat version, med säkerhets- och live-verktygstester.
- Några gamla tekniska dialoger och historiska chefstexter kan fortfarande nämna leverantörsnamn; de är ännu inte systematiskt omarbetade.
- ❗-märken på bord öppnar fortfarande den äldre arbetskön. Den nya högerspalten kan öppna en verklig Gemini-rapport direkt, men varje äldre rapporttyp har ännu inte en egen direktkoppling.
- Vi kan inte garantera Googles externa kvoter eller verklig parallell AI-körning med användarens konto utifrån simulerade tester.

## Ändrade/nya filer

- `backend/pw_v01210.py` – mänskliga namn på *nya* startarbetare och modul-installation för v17.
- `backend/pw_v0121117.py` – enda versionerade UI-laddaren/versionsmärkningen; ingen ny AI-endpoint.
- `src/pw-v01211.js` – **korrigerad ovanpå v0.12.11.15**: projektval stabilt, guider kvar, spelstart-händelse.
- `src/pw-v0121117.js` – projektkontext, studioåtkomstknapp, beslutspanel, stationer, onboarding och skydd mot fel projekt.
- `backend/test_pw_v0121117.py`, `test_browser_0121117.py` – offline-tester.
- `DELTA_README_v0121117.md`, `NOW_NEXT_LATER_v0121117.md`, `CURRENT_STATE_v0121117.md`, `DELTA_MANIFEST_v0121117.json` – dokumentation.
