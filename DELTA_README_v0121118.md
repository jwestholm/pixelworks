# Pixel Works v0.12.11.18 – Skrivbordsuppdrag, första UX-omgången

**Basversion:** v0.12.11.17. **Format:** delta – endast nya/ändrade filer. **Start:** `python3 backend/server.py`. **Ingen GitHub-push, inget installationsskript.**

## Spelupplevelse

- **Nytt arbetsfönster för åtta yrkesstationer:** Grafikstudio, Testning, Musikstudio, Programmering, Mötesrum, Dokumentation, Forskning och Röststudio. Befintliga chef- och fikasystem lämnas orörda.
- **Samma igenkännbara flöde:** Eget uppdrag först → huvudkategori → underkategori → beskrivning, bilagor, befintliga referenser, prioritet → spara till stationens *befintliga* arbetskö.
- **Grafikstudion har en egen illustrerad pixelbakgrund**, nedtonad med ett ljust pastellager. Övriga yrkesstationer har egna mjuka toningar i denna omgång; full illustrationsserie återstår.
- **Endast relevant rubrik:** stationens namn + vad som görs. Den gamla globala rubriken 'Lokal studio / Pixel Works-version / Aktivt spel' dupliceras inte i dessa nya popupfönster.
- **Prioritet:** tre tydliga val `Låg / Normal / Hög`, där Normal är förvalt.
- **Bifoga bilder, ljud eller textfiler**, högst 4 MB per fil; tidigare projektreferenser går också att välja.
- **Grafik/Föremål:** nya objekt, vapen, samlarföremål, interaktiva föremål, möbler, förbättra befintligt.
- **Grafik/Karaktärer:** bland annat NPC, hjälpreda, djur/katt, fiende/boss.
- **Testning:** testa hela spelet, testa senaste funktion, rapportera bugg → område, prestanda, användartest.
- **Mötesrum:** diskussion om ny figur/katt eller övergripande arbete. `Visa möjlig arbetsplan` ger fem steg (Grafik/Ljud/Programmering/Testning/Dokumentation) som **lokal förhandsgranskning**, inte AI-verifierad plan.

## Vad som INTE görs automatiskt ännu

Planen för en NPC-katt delas **inte** automatiskt upp i fem körbara arbetsorder. **Endast en explicit vald planeringsarbetsorder** får läggas i kön; det är avsiktligt. För automatiska deluppdrag krävs ett serverlagrat plan-ID, godkännande, blockerande beroenden och säkra överlämningar från färdiga rapporter. Att lägga fem omedelbart körbara order i dagens kö vore fel: QA och programmering kunde börja innan grafiken är beslutad. Detta är NEXT.

Backendens befintliga arbetskö, AI-kapacitet, Game Bible-flöde och kvotregler ändras inte. Inga AI-anrop görs av popupen. Den klickbara chefen behåller äldre meny tills den gemensamma arbetsledarmotorn finns.

## Tekniska filer

- `src/pw-v0121118.js` – ny komponent för stationsuppdrag med taxonomi, valbara underkategorier, eget uppdrag, säker skapa-operation och ljusa stationsteman.
- `assets/office-v2/graphics-studio-pastel.png` – originalillustration för grafikrummets popup.
- `backend/pw_v0121118.py` – lägger till frontendkomponenten efter alla befintliga scripts.
- `backend/pw_v01210.py` – laddar det nya lager som sista tillägg och bevarar alla äldre komponenter.
- `backend/test_pw_v0121118.py`, `test_browser_0121118.py` – offline regressionstester.

## Verifierat

- JavaScript-syntax med Node (`node --check`). Python kompilerat med `py_compile`.
- Fyra riktade backendtester för scriptladdning, ordning, hostskydd och idempotent installation.
- Chromium med simulerade backenddata: Grafik → Föremål → nytt objekt; prioritet Hög, befintlig referens och exakt en order; QA → Rapportera bugg → AI/NPC; Möte → Katt-NPC → arbetsplansförhandsvisning utan automatisk körning; manuell planeringsorder; byte till annat projekt hindrar sparning. Inga JS-konsolfel.
- Bildbakgrunden har granskats visuellt i Chromium.

**Ej verifierat:** hela kedjan i verkliga Firefox med användarens installerade version samt samtidiga Codex-/Gemini-körningar. Legacy regressionstestsviten har sedan tidigare kända brister. Ingen sådan verifiering påstås här.

## Installation

Packa upp innehållet över den befintliga **v0.12.11.17**-installationens rot. Skapa inga nya mappar manuellt. Starta som vanligt:

```bash
python3 backend/server.py
```

Uppdatera webbläsaren med **Ctrl+Shift+R**. Klicka först på **Grafikstudio**, testa `Eget uppdrag`, `Karaktärer` och `Föremål`, och kontrollera att en skapad order finns i Grafikstudions vanliga arbetskö.
