# Pixel Works – Beslutslappens förhandsvisning v1.7 (CSP-fix)

**Bas:** `jwestholm/pixelworks` branch `dev`, `fb70d1c9a927e07e802537c83705db5b8f9876cd` (2026-10-29 #1), **plus alla tidigare installerade lokala deltafiler, senast Förhandslyssning v1.6**. Ingen GitHub-push eller ändring av spelprojekt har utförts.

## Problemet (återskapat)

Originalservern sätter denna säkerhetspolicy på sina HTTP-svar:

```text
default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'
```

Beslutslappen v1.5–v1.6 hämtar mediebytes genom ett godkänt API-anrop och skapar sedan en tillfällig lokal `blob:`-adress för `<audio>`/`<img>`. Serverns CSP saknar `media-src blob:` och `img-src blob:`. Browsern blockerar därför uppspelningen även när servern faktiskt avkodat en riktig WAV. Den tidigare feltexten *"Firefox kunde inte avkoda"* var missvisande: det kan vara CSP som blockerar, inte ett trasigt ljud.

## Fix

Ändringen är i **en enda befintlig programfil**: `backend/pw_media_review.py`.

När mediegranskningstillägget installeras utvidgas **endast** den redan skickade CSP-headern med följande, genom en smal omskrivning av `send_header('Content-Security-Policy', ...)`:

```text
img-src 'self' data: blob:
media-src 'self' blob:
```

Andra direktiv (särskilt `script-src`, `connect-src`, `object-src`, `frame-ancestors`) lämnas oförändrade. En andra CSP-header skickas **inte** (två policyer kombineras restriktivt av webbläsaren och hade inte löst problemet).

Inga tredjepartsdomäner tillåts för media. Freesound-resultat hämtas fortfarande via den autentiserade lokala backendens API. Ingen extern tjänst, hemlighet eller AI får nya privilegier.

## Installera

1. Gör en lokal säkerhetskopia eller commit av dina egna ändringar.
2. Packa upp ZIP:en direkt i Pixel Works **projektrot** (där `index.html` ligger); skriv över `backend/pw_media_review.py`.
3. **Starta om backendprocessen helt** – enbart Ctrl+F5 räcker inte eftersom CSP kommer från Python-servern. Ladda sedan om Firefox med **Ctrl+F5**.
4. Öppna 💌 Beslutslappen. Tryck **▶ Provlyssna**, sedan **▶ Spela ljud** och välj Ja/Nej/Kanske. Testa även en bild.
5. Om det fortfarande misslyckas, kontrollera i Firefox Utvecklarverktyg → Nätverk → svarshuvuden för `http://127.0.0.1:8765/`: `Content-Security-Policy` ska innehålla **`media-src 'self' blob:`** och **`img-src 'self' data: blob:`**. Om dessa saknas körs den gamla serverprocessen eller fel Python-fil.

Din sparade Freesound-nyckel, tidigare ljudförslag, uppdragskö och beslut påverkas inte av installationen. `ffmpeg` är fortfarande användbart för konvertering men är **inte grundorsaken till det här CSP-felet**.

## Tester utförda i leveransmiljön

- **28 Python-tester godkända** – nya CSP-regressioner samt tidigare media- och beslutstester.
- **Chromium-regressionstest med den riktiga CSP-regeln**: gammal policy återskapar både blockerat WAV och blockerat PNG; fixad policy spelar WAV, visar PNG och aktiverar godkännandeknappen.
- Testet använder en inbyggd, verklig PCM-WAV (440 Hz) och en PNG, inga mockade filheaders.
- Ingen riktig Freesound-/AI-trafik och ingen GitHub-push. **Firefox på din Ubuntu är ännu inte verifierat** från den här miljön.

Repetera lokala enhetstester (ingen extern trafik):

```bash
cd backend
python3 -m unittest -v test_pw_media_csp_v17
```

Valfritt webbläsarregressionstest om Python Playwright och Chromium finns installerade:

```bash
python3 tests/browser_media_csp.py
```

Detta test återger serverns CSP via en inbäddad policy i en **offline-testvy**. Tester av den faktiska `send_header`-omskrivningen görs separat i Python-enhetstesterna.

## NOW / NEXT / LATER

**NOW:** Tillåt tillfälliga blob-ljud/-bilder i den avgränsade CSP-policyn. Provlyssning fungerar i regressionstestet. Inga nya beslut eller bakgrundsjobb startar automatiskt.

**NEXT:** Testa det verkliga v1.7-svaret och ljudförslagen i användarens Firefox på Ubuntu. Om ett *enskilt* prov fortfarande misslyckas efter att CSP-headern är verifierad, felsök dess faktiska MIME/kodning i stället för att ändra regler generellt.

**LATER:** Robustare medieservering med autentiserad same-origin stream-URL och caching, om stora provfiler eller fler medier kräver det. Gemensamma verktygs-/modellregister hanteras i separat roadmap.
