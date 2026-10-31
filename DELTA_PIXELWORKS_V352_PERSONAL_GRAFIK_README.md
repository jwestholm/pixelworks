# Pixel Works v3.5.2 – Personalkort, grafikåtkomst och Firefox

**Bas:** Delta ovanpå Pixel Works v3.5.1, ursprunglig Git-dev-bas `fb70d1c9a927e07e802537c83705db5b8f9876cd` (2026-10-29 #1). Ingen GitHub-push eller ändring av spelprojektdata. Installation är en lokal filöverskrivning.

## Installeras så här

1. Säkerhetskopiera gärna `~/pixelworks/pixelworks-git` och `~/.pixelworks` om du har gjort egna ändringar.
2. Packa upp ZIP-innehållet **i spelprojektets rot** (där `index.html`, `src/`, `backend/` ligger). Skriv över filer.
3. **Starta om servern** (den här deltan innehåller en ny, strikt statisk filrutt):

   ```bash
   cd ~/pixelworks/pixelworks-git
   python3 backend/server.py stop
   bash start-lan.sh
   ```

   Om du inte kör LAN-läge använder du din vanliga startmetod i stället.
4. I Firefox: **Ctrl + Shift + R**, även på tangentbord där F5 kräver Fn. Alternativt klicka på webbläsarens uppdateringsknapp efter serveromstart. Pixel Works originalserver skickar `Cache-Control: no-store` för resurser.
5. Kontrollera att dessa länkar svarar med **CSS-text och inte JSON-fel**:

   - `http://127.0.0.1:8765/src/pw-v35-world.css`
   - `http://127.0.0.1:8765/src/pw-v351-dialogs.css`
   - `http://127.0.0.1:8765/assets/characters/mira/mira-idle.png` (ska vara en transparent spritebild)

   På mobil inom LAN: byt `127.0.0.1` mot datorns LAN-IP, t.ex. `192.168.0.8` om den fortfarande gäller.

## Vad som faktiskt ändras

- `backend/pw_v352_static.py` – tillåter endast tre namngivna v3.5-stilmallar och de **42 namngivna** spritebilderna för sju befintliga personer och sex animationslägen. Behåller filskydd och ursprungliga säkerhetsheaders. Inga generella filkataloger öppnas.
- `backend/server.py` – registrerar den snäva statiska filrutten, innan LAN-åtkomstkontrollen appliceras ytterst.
- `src/pw-v3-recruit.js` – förenklad personallista och personprofil. **Samma anställda, person-ID:n, arbetsbeskrivningar och uppdragsknappar som tidigare.** Chefen får tydlig identitet som arbetsledare.
- `src/pw-v352-personnel.css` och `.js` – ny spelanpassad kortlayout på desktop och mobil, versionerat CSS-anrop.
- `src/main.js` – importerar den nya visuella komponenten utan att röra AI-motorerna.
- `src/pw-v351-dialogs.js` och `.css` – hindrar dubbel **Kontor**-knapp när ingen tillbakahistorik finns.

## Testad kvalitet / begränsningar

- **46 äldre backendtester** för personal och AI-uppdrag godkända.
- **6 HTTP säkerhets-/statiska tester** godkända, inklusive felaktig värdadress och symlänkar.
- **1 riktig Chromium+HTTP-kontroll** godkänd: webbläsaren läser paketets Mira-sprite (192×68 PNG) och personalkortets CSS genom servern.
- **6 nya personalkortstester + 33 tidigare UI-tester** godkända. De två äldre rekryteringsfilerna för v3/v3.1 gick också igenom på mobil och desktop.
- **Äldre v3.2-UI-fixtur** testar sprite-URL från en isolerad `about:blank`-sida; den utlöser avsiktlig reservfigur och kan därför ge ett felaktigt negativt resultat. Den nya HTTP-kontrollen ovan testar en riktig tillåten URL i stället.
- Ingen riktig AI-klient, faktisk nätverksnyckel eller användarinstallation i Firefox på Ubuntu har testats här. Ingen automatisk kodintegration eller migration av personal utförs.

## NOW / NEXT / LATER

**NOW:** Verifiera de statiska resurserna efter omstart och prova personalkorten med verkliga anställda. Låt en synlig sprite gå till fika/arbete och kontrollera att det fortfarande är samma person.

**NEXT:** Ombyggnad av uppdrags-, gransknings- och ljud/bild-korten med samma pixel-designsystem. Färre tekniska fält, samma beslut i alla sammanhang. Möjlig visuell "Ny version finns – uppdatera" när klient och serverversion skiljer sig åt.

**LATER:** Förbättra kontoret konstnärligt med en sammanhängande bakgrund, större läsbara karaktärer och välbyggda animationssekvenser. Fortsatt projekt-oberoende personalidentitet och robust datasyndning dator/mobil.

## Rollback

Stoppa servern. Återställ filerna i den här deltan från din tidigare v3.5.1-installation/säkerhetskopia och starta om. **Ändringar i verkliga spelprojekt och v3-personaldata görs inte av den här deltan**, så ingen datamigrering behöver återställas.
