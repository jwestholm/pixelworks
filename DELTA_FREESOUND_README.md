# Pixel Works – Ljudstudion 1.0 (Freesound, agentstyrd)

**Bas:** `jwestholm/pixelworks` **dev** commit `fb70d1c9a927e07e802537c83705db5b8f9876cd` – `2026-10-29 #1`.

**Installation:** packa upp denna ZIP **direkt i projektroten**, alltså samma mapp som `index.html`, med bevarad `src/`- och `backend/`-struktur. Välj att skriva över `src/main.js` och `backend/server.py`. Den här ZIP-filen innehåller **inte** en extra överordnad projektmapp. Var säker på att din egen lokala checkout fortfarande bygger på angiven commit och att du inte skrivit om dessa två filer sedan dess. Ta annars en diff först.

Starta om servern och hårduppdatera webbläsaren (`Ctrl+F5`). Behåll din lokala `.git`, eftersom befintliga Pixel Works-servern kräver den. Ingen GitHub-push, merge, riktig Freesound-sökning eller riktig AI-körning har gjorts vid framställningen av ZIP-filen.

## Spelarflöde (game first)

1. Klicka på **Musikstudion** eller **Röststudion**, och välj **🎧 Ljudagent · Freesound**. Den gamla uppdragsmenyn och arbetskön är kvar.
2. Välj **🔐 Freesound-inställningar**, klistra in *API-nyckeln* från Freesound och välj Spara anslutning. Nyckeln lagras lokalt i Pixel Works privata `secrets/freesound-api.key` med rättigheter `0600`, inte i Git. *Sparad* betyder inte att nyckeln har verifierats mot Freesound.
3. Placera en verklig anställd med aktiverad **Codex** eller **Gemini** vid musik-/röstbordet. Beskriv vilken ljudeffekt eller musik spelet behöver.
4. Klicka **🎼 Ge ljudagenten uppdrag**. **Först då** gör systemet verkliga AI- och Freesound-anrop. Ett AI-anrop formulerar en sökfråga på engelska; API:et lämnar verkliga ljudresultat; ett andra AI-anrop väljer upp till tre kandidater utifrån metadata.
5. Lyssna på kandidaterna via förhandsproven och öppna källan vid behov. AI:n har **inte lyssnat på ljudet** – motiveringarna baseras på namn, taggar och beskrivningar.
6. Klicka **✅ Godkänn och hämta ljudprov** om du vill spara den valda, licensmässigt tillåtna MP3-förhandsversionen i projektets egna privata ljudbibliotek (`management/freesound-library`). Metadata sparas tillsammans med ljudet: upphovsperson, licens, källa och filhash. Det lägger **inte** automatiskt in ljudet i spelets kod eller Game Bible.

## Säkerhet, licens och gränser

- API-nyckeln stannar på servern och returneras aldrig till webbläsaren. Koppla från tar bort nyckelfilen.
- Endast faktiska Freesound-resultat visas. Okända, NonCommercial- och övriga icke godkända licenser filtreras bort. Endast **CC0** och **CC BY** accepteras. CC BY kräver erkännande av upphovspersonen.
- Nedladdning sker först efter spelarens godkännande och endast från HTTPS-adresser under `freesound.org`. Max 8 MB per ljudprov, filen kontrolleras som MP3.
- **Freesound API är gratis för icke-kommersiell användning. Kommersiell API-användning kräver separat avtal med Freesound.** Att ljudet har CC0/CC BY betyder inte i sig att en kommersiell Freesound-API-integration är tillåten.
- Freesounds **originalfiler kräver OAuth2**, vilket inte ingår. Det här verktyget importerar endast MP3-förhandsprov efter godkännande. Granska slutlig licens och ljudkvalitet innan publicering av spelet.
- Freesound API-kvot visas som **ej verifierad**; ingen gissad restkvot. Anrop görs inte vid sidladdning, vid öppen modal eller vid polling.
- Ljudarbetets status och förslag sparas per projekt; projekten kan inte läsa varandras ljudjobb. Jobb som avbrutits av serveromstart visas som avbrutna.
- Ingen automatisk git-push, AI-modellinstallation, aktivering av betalplaner eller ändring av användarens spelkod.

## Verifiering av denna delta

- Bash/Python-syntax: `python3 -m py_compile backend/server.py backend/pw_freesound.py`, `node --check src/pw-freesound.js`.
- **6 offline Python-tester:** projektisolering, hemligheter, validering av licens och CDN, AI-resultat via mockad provider/sökning, avslag utan godkännande, lokal import av testljud och autentisering.
- **Mockad Chromium-UI:** knapp i befintlig Musikstudio, sparad nyckel, start med vald verklig agent, förslag, spelbar ljudkontroll, godkännande och mobil layout.
- Befintliga `src/main.js` och `backend/server.py` verifierades mot exakta Git-blobhashar för bas-commit, innan våra tillägg lades till.
- **Ej verifierat:** verklig Freesound-autentisering, riktiga ljudfiler, riktiga Codex/Gemini-anrop eller hela spelets integrationstest under din lokala server. Dessa kräver din konfiguration och aktiva val.

## NOW / NEXT / LATER

**NOW:** Agentstyrd sökning, upp till tre verkliga metadata-baserade förslag, lyssning, val, projektbunden import av MP3-förhandsprov och hemlig API-nyckel.

**NEXT:** Granskad integration av godkända ljud i spelprojekt, krediteringslista, OAuth2-originalhämtning och tydligare feedback/omtag mellan spelare och ljuddesigner.

**LATER:** Fler verktygsadaptrar (ElevenLabs, Suno där officiellt API/tillstånd tillåter), lokal ljudkonvertering med FFmpeg, budgetgränser och en generell verktygsbehörighetsmodell för anställda.

## Källor

- https://freesound.org/docs/api/
- https://freesound.org/docs/api/resources_apiv2.html
- https://freesound.org/docs/api/authentication.html
- https://freesound.org/docs/api/terms_of_use.html
