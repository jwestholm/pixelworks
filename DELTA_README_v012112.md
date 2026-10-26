# Pixel Works v0.12.11.2 — återställd inställningsmeny & Gemini-test

**Utgångspunkt:** v0.12.11.1. Packa upp filerna i samma Pixel Works-katalog och bevara undermapparna. Endast angivna filer ersätts eller tillkommer. Inga installationsskript ingår.

## Vad som rättas

1. **Inställningarnas startsida återställd.** Klicka `Inställningar` -> befintliga `Inställningar & diagnostik` öppnas. Där finns åter de befintliga raderna för AI-motor och lagring **samt** en rad `Google Gemini` med sparad/verifierad status och knappen `API-token / Testa anslutning`.
2. **Gemini går att testa direkt.** `Testa/verifiera anslutning` är aldrig avstängd bara för att nyckeln ännu inte sparats. Om token i fältet är ny sparas den lokalt innan ett uttryckligen användarstartat test mot Google utförs.
3. **Valideringen accepterar nya nyckeltyper.** Formatkontrollen gissar inte på ett `AIza`-prefix eller en viss bokstavsuppsättning; den stoppar bara uppenbara inklistringsfel, radbrytningar, kontrolltecken och orimliga längder. Google avgör faktisk giltighet.
4. **Ärlig status och fel.** Testet gör endast ett läsande modellisteanrop och visar Googles HTTP-felstatus eller om den valda modellen inte stöds. Ingen textgenerering görs i testet. Gratisnivå, fakturering och faktisk återstående kvot förblir okända från ett lyckat nyckeltest.

## Installations-/startkontroll

1. Stoppa nuvarande Pixel Works-server på vanligt sätt.
2. Lägg filerna från ZIP:en över den befintliga v0.12.11.1-katalogen. Inga sparade projekt, Game Bible eller hemliga nycklar ingår i paketet.
3. Starta **endast** med: `python3 backend/server.py`
4. Firefox: `Ctrl+Shift+R`. Klicka **Inställningar**, därefter på Gemini-raden, klistra in nyckeln och klicka **Testa/verifiera anslutning**.

Nyckeln förblir under studions lokala hemlighetsmapp (`ROOT/secrets/gemini.key`, filbehörighet `0600`) och skrivs inte till Git. Testknappen gör ett Google-API-anrop först när du klickar på den. Den här leveransen innehåller inga verkliga Google-anrop utförda av utvecklaren.

## Testat lokalt

- 35 Pythonregressionstester, simulerade Google-svar: **PASS**.
- JavaScript syntaxkontroll (`node --check`): **PASS**.
- Headless Chromium med falskt API: **PASS** — startsidan kvar, Gemini-rad synlig, testknapp aktiverad utan lagrad token, spara + testa med ett klick, status grön på simulerat positivt svar.
- Din verkliga Gemini-nyckel, riktiga Google-konto och Firefox-installation: **ej verifierat**.

## Ändrade filer

- `backend/pw_v01210.py` — format, läsande verifiering, felstatus, versionsnummer.
- `src/pw-v01210.js` — Inställningar öppnar rätt startsida; Gemini ingår i den; testknapp fungerar utan förhandssparande.
- `backend/test_pw_v01210.py` — uppdaterad versionsassertion.
- `backend/test_pw_v01211.py` — uppdaterad testfixtur för Googles modellista.
- `backend/test_pw_v012112.py` — nya regressioner, utan nätverksanrop.

**Ingen `backend/server.py` ändras.** Fasta startfilen är fortfarande `backend/server.py`. Äldre `server_v01210.py` används inte.
