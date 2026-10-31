# Pixel Works – Gemensamma dialoger / Kontextuell beslutsinkorg v1.8

**Bas:** `jwestholm/pixelworks`, `dev` commit `fb70d1c9a927e07e802537c83705db5b8f9876cd` (`2026-10-29 #1`), **plus tidigare lokalt installerade Freesound- och beslutsdeltor t.o.m. v1.7**.

## Installera

1. Gör en lokal backup/commit av dina egna källfilsändringar.
2. Packa upp denna ZIP **direkt i Pixel Works-projektroten** (där `index.html` ligger). Behåll katalogstrukturen `src/` och `tests/`; skriv över filerna som finns i ZIP:en.
3. Kör `Ctrl+F5` i Firefox. Den här deltan ändrar bara JavaScript, **ingen serveromstart krävs normalt**. Om din server har en egen JS-cache: starta om som du brukar.
4. Öppna fikarummet och prata om ljud – tryck den nya gemensamma knappen **Öppna inkorgen**. Prova samma knapp i Musikstudion, Grafikstudion, Testning, agentkort och en arbetsrapport.

## NOW – levererat

- **Samma faktiska beslutskälla och förhandsvisning överallt.** Inga separata godkännandelistor skapas. Befintliga autentiserade `/api/pw-tools/review` och `/api/pw-tools/decisions` återanvänds; `Ja / Nej / Kanske` sparas fortsatt via original-API.
- **En enhetlig väg in** till granskningsinkorgen från befintliga dialoger: Fikarummet, stationernas vanliga uppdragsfönster (inklusive QA), agentkort, Lokal studios rapportvy och studiodialogen.
- Kontext styr vad som visas först: ljud i Musikstudio/Röststudio, bilder i Grafikstudio, senaste ljud-/bildämne i fikarummet, den valda anställdas ärenden i agentkortet. Det går alltid att välja **Visa hela studion**.
- **Kategorier + sökning** inne i *samma* beslutslapp: Alla, Ljud, Bilder, Hjälp. Sök på exempelvis titel, agent eller uppdragsbeskrivning.
- **Ingen dubbeletablering:** den tidigare särskilda `💌 Förslag från ljudteamet`-rutan i Musikstudion tas bort. Nya allmänna kontextknappen ersätter den; Freesounds API-inställningar och QA-indikatorn behålls.
- **Förhandsljud och -bilder fungerar via samma tidigare testade spelare** (`blob:` kräver v1.7-CSP); inga direktförfrågningar till Freesound från UI:t. Återkommande 5-sekundersläsning ska inte förstöra ett spelande ljud eller ett oskickat utkast.
- **Inga dolda AI-anrop** när en dialog öppnas eller man byter kategori. Data läses från servern; aktivt beslut görs först vid spelarklick.
- Dialoger ovanpå varandra: den gamla kontextdialogen finns kvar bakom beslutsvyn, så fikatext eller formulär inte kastas vid navigering. När beslutsvyn stängs återkommer man till ursprungskontexten.
- Läsbar på mobil, tangentbord med fokusmarkerade knappar, alla knappar är native HTML.

### Viktig avgränsning

Det här är **v1 av en generell navigations- och granskningskomponent**, inte en full omskrivning av alla specialdialoger. Befintliga formulär för t.ex. rekrytering, inställningar och nyproduktion är ännu inte konsoliderade. Det är medvetet: vi återanvänder deras riktiga funktioner och ändrar inte agenternas arbetsflöden i samma delta.

Ett kontextkort är **en knapp till den gemensamma beslutsvyn**, inte en separat ljudspelare inbäddad i fikabordets chattmeddelanden. Beslutsvyn kan öppnas ovanpå fikarummet utan att fikautkastet försvinner. Mer avancerade inbäddade kort i enskilda AI-repliker kräver ett separat strukturerat mediereferensformat i samtals-API:t; vi gissar inte att ett godtyckligt ord som ”ljud” är ett verkligt förslag.

## Testat (utan nätverk)

- `node --check` för de fyra JavaScript-filerna.
- **18 kompatibla Python-regressionstester** i den tidigare CSP-/besluts-/uppspelningssviten: gröna.
- Offline Chromium med riktiga PCM-WAV-bytes under en CSP som tillåter `media-src blob:`: Fikarum → samma beslutsvy → faktisk uppspelning → sökning/kategori/Kanske → tillbaka utan att tappa text → agent Gunnar → samma beslutsvy i hans kontext.
- Samma dialog testad vid 375 px mobilbredd (ingen horisontell klippning).
- Obs: ett äldre test från media v1.5 byggde en **ogiltig låtsas-MP3** som med rätta avvisas av den striktare valideringen i v1.7. Det äldre testet är inte en giltig regression för verklig avkodning; uppdaterad v1.6-v1.7-testsvit används.
- **Inte testat:** Din faktiska Firefox- och Ubuntu-installation samt fullständiga riktiga agent-/samtalskörningar. Inga faktiska API-nycklar eller nya AI-anrop användes.

Kör webbläsartest lokalt (frivilligt, kräver Playwright/Chromium):

```bash
python3 tests/browser_dialog_hub.py
python3 tests/browser_dialog_mobile.py
```

## NOW / NEXT / LATER

- **NOW:** En gemensam beslutsingång i de fem viktigaste kontexterna + kategorier och sök. Samma data och ja/nej/kanske-regler överallt.
- **NEXT:** Använd samma komponentmodell även för uppdrag, arbetsrapporter, personal och inställningar; minimera specialfönster. Skicka strukturerade mediereferenser som del av fikarumets AI-repliker och QA-rapporter, inte bara fria textsträngar.
- **LATER:** Samma designmönster för budget-, rekryterings-, publicerings- och designbeslut efter att dessa finns som riktiga verifierbara serverärenden.

**Ingen GitHub-push/merge, inget ingrepp i privata spelprojekt, inga nya nätverksanrop i test.**
