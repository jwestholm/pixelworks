# Pixel Works – Förhandslyssning v1.6 (liten felsökningsdelta)

**Bas:** GitHub `jwestholm/pixelworks` branch `dev` på `fb70d1c9a927e07e802537c83705db5b8f9876cd` (2026-10-29 #1), PLUS tidigare installerade Freesound v1.4 PRIVAT, ToolBridge v1.2 och Beslutslappen v1.5. ZIP-filen ersätter bara v1.5-filer för mediaförhandsvisning.

## INSTALLERA

1. Spara en säkerhetskopia av dina lokala ändringar eller gör en egen commit.
2. Packa upp **direkt i projektroten** där `index.html` finns. Skriv över `backend/pw_media_review.py` och `src/pw-media-review.js`. Två testfiler medföljer.
3. **Starta om backendservern**, inte bara Firefox. Kör sedan `Ctrl+F5`.
4. Öppna 💌 beslutslappen och tryck **▶ Provlyssna**. Vänta tills ljudet faktiskt har en verifierad längd; klicka sedan **▶ Spela ljud** (separat knapp finns eftersom Firefox ofta blockerar autoplay efter ett asynkront nätverksanrop). Inbyggd ljudspelare finns kvar för spolning och volym.
5. `✅ Ja, använd i spelet` blir valbar först när webbläsaren faktiskt har laddat förhandsfilens metadata. `❌ Nej` och `🤔 Kanske` finns alltid kvar. Bilder visas som tidigare.

## BEKRÄFTADE BUGGAR I v1.5

- JS gjorde `await audio.play()` efter att hämtningsanropet avslutats och svalde fel från Firefox om tillstånd eller avkodning. Följden blev en missvisande **'✅ förhandsfilen är laddad'** även när webbläsaren visade **0:00/0:00**.
- Backend kontrollerade endast MP3-/WAV-filernas signaturer, inte att de gick att avkoda. En ogiltig ljudfil kunde därför lämnas till spelaren.
- En statusändring i ett annat kort kunde orsaka att det uppspelade `<audio>`-elementet byttes ut vid automatisk uppdatering var femte sekund.

## NOW (fixat)

- Ljud förhandsavkodas **på Pixel Works-servern**. Om `ffmpeg` finns installerat skapas en spelbar, standardiserad mono 24 kHz 16-bitars WAV på **högst 20 sekunder**. Konverteringen körs med strikt tidsgräns, lokala protokoll och begränsad utfil. Förhandsvisningen är ett utdrag, inte en ändring av originalfilen i projektet.
- Saknas `ffmpeg` läses PCM-WAV med Pythons inbyggda `wave`. MP3/OGG kontrolleras med `ffprobe` när det finns; annars är webbläsarens dekoder avgörande. Det visas aldrig en påhittad speltid.
- Webbläsaren får en tydlig **▶ Spela ljud**-knapp som är en faktisk användarklickning (inte ett borttappat Firefox-gesture). Vid avkodningsfel, trasig fil, DNS-fel eller timeout visas feltext och **🔄 Hämta nytt förhandsprov**.
- `✅ Ja` låses tills ljud/bild faktiskt kan förhandsvisas i den aktuella spelarsessionen. `Nej` och `Kanske` påverkas inte.
- Beslutslappen ersätter inte en pågående ljudspelare eller utkast till feedback när dess automatiska polling upptäcker ändringar. Efter egna beslut uppdateras innehållet normalt.
- Inga nya AI-anrop, Freesound-sökningar eller Git-integreringar startar när förhandsvisningen hämtas.

## TESTER

```bash
cd backend
python3 -m unittest -v test_pw_media_review.py test_pw_decision_center.py test_pw_audio_playback_v16.py
```

**I leveransmiljön:** 24 isolerade backendtester godkända; Chromium med riktig PCM-WAV, knappar för att spela, väntande Ja-knapp, felande ljudfil, bevarad spelare under polling och mobilvy godkänt. JS-syntax kontrollerad med Node. Riktiga API-ljud från ditt Freesound-konto och Firefox på din Ubuntu är **ännu inte verifierade**.

**Serverberoende:** `ffmpeg` rekommenderas för robust provlyssning av MP3-/OGG-ljud. På Ubuntu kan du kontrollera med `ffmpeg -version`. Om det saknas kan du själv installera paketet `ffmpeg` via din ordinarie pakethanterare; deltan installerar ingenting utanför projektet.

## NEXT

- Testa i din riktiga Firefox med ett befintligt Freesound-kort och en verklig exporterad WAV från Chefen. Om ljudet fortfarande inte kan avkodas visar kortet nu ett verkligt fel istället för tyst 0:00.
- Eventuellt serverägd korttids-cache för att undvika upprepad Freesound-nedladdning av samma ljud; inga token-/kvotvärden gissas.

## LATER

- Fler mediagenereringsmotorer och revisionsgranskning via samma beslutslapp; leverantör -> modell -> verktyg.

**Ingen GitHub-push, serverinstallation eller extern molntrafik har utförts här.**
