# Pixel Works – Verktygsregister, Freesound-spårning och QA-överlämning v1.2

## Bas och installation

**GitHub `jwestholm/pixelworks`, `dev`, commit `fb70d1c9a927e07e802537c83705db5b8f9876cd` (2026-10-29 #1)**.

**VIKTIGT: Detta är en delta ovanpå Freesound v1.1.** Du ska redan ha installerat:
1. `PixelWorks_Freesound_Ljudstudion_v1_DEV_fb70d1c_DELTA.zip`
2. `PixelWorks_Freesound_integrerad_ljudstudio_v1_1_fb70d1c_DELTA.zip`

På grund av att dessa tillägg ännu inte finns incheckade på `dev` kan GitHub-versionen inte ensam köras med den här deltan. Nycklar, befintliga projekt och arbetsytor påverkas inte av ZIP-filerna.

1. Stoppa Pixel Works normalt. Se över `git status` och säkerhetskopiera ändrade filer om du har egna lokala ändringar.
2. Packa upp **direkt i projektroten** (mappen med `index.html`) och behåll undermapparna `src/` och `backend/`. Skriv över de tre befintliga filerna i ZIP-filen. Inga Git-kommandon, installationer eller migrationer körs vid uppackning.
3. Starta om din befintliga server och ladda om webbläsaren med `Ctrl+F5`.
4. Testa från **Inställningar & diagnostik**: kategorierna **AI-motorer & tokens** respektive **Verktyg & API-nycklar** visas. Freesound har en liten rad som öppnar eget inställningsfönster. Även huvudinställningarna har vertikal scroll.
5. Skapa vanlig arbetsorder på Musikstudion eller Röststudion och starta den via befintlig behörig scheduler. Öppna ljudbordets **Visa ljudförslag från teamet** och **Visa verkliga verktygshändelser** för konkreta API-sökevidens.
6. När en Codex-session faktiskt har *integrerats* för `code`, `art`, `music` eller `voice` kan **en väntande QA-order** automatiskt läggas i samma projekts existerande arbetskö. Läs QA-statusen i arbetsrapporten och den senare QA-rapporten; att ordern är klar innebär inte att testerna är godkända.

## Förändrade filer

- `backend/server.py` – registrerar serverägt verktygsregister och QA-överlämning efter existerande tillägg.
- `backend/pw_freesound.py` – använder verktygsregistret vid verkliga agentval, spårar begäran/svar/urval/import, binder resultat till den ordinarie arbetsorderns jobb-id.
- `src/pw-freesound.js` – enklare inställningsöversikt, separat Freesound-fönster, scroll, verktygsspårning och QA-indikator på vanliga rapporter.
- `backend/pw_tool_registry.py` – ny generisk serverägd registrerings-/behörighetsfunktion. Har en **verklig adapter** nu: Freesound `audio.search`; framtida verktyg är inte markerade anslutna.
- `backend/pw_qa_handoff.py` – ny automatisk, passiv QA-köpost vid riktig kodintegration; skapar inga provider-anrop själv.
- `backend/test_pw_toolbridge_v3.py` – isolerade Python-kontraktstester utan nätverk.

## Viktiga beteenden / säkerhet

- `Freesound` är ett *verktyg*, inte en AI-anställd. Servern äger API-nyckeln; agenten ser bara tillgängliga verktyg och returnerar ett strukturerat verktygsval. Servern kontrollerar projekt, anställd, arbetsstation och verifierad anslutning innan Freesound anropas.
- **Väntande order eller enbart besök på ljudbordet gör aldrig AI-/Freesound-anrop.** Ett verktygsanrop sker först efter att normal scheduler startat ordern och AI-agenten valt verktyget. Det kan skapa extra verkliga Codex/Gemini- och Freesound-anrop som använder tillgängliga kvoter.
- **Begränsning:** ljudverktygets AI-planering och metadataurval körs ännu i en separat serverägd följdprocess, knuten till *samma order*, parallellt med huvudagentens kodkörning. Det är **inte samma interaktiva Codex-session** och resultaten matas **inte automatiskt tillbaka i kodkörningen**. Inga automatiska kodändringar, nedladdningar eller API-krediter uppstår genom enbart en ljudkandidat.
- Endast CC0/CC BY-ljud med säker HTTPS-MP3-preview föreslås. Bara explicit godkänd import av ett preview-ljud sparar en fil i privat projektbibliotek med licens/källa. Stora original-WAV-filer hämtas inte.
- **QA-överlämning:** servern köar max en ny `qa`-order per integrerad Codex-session i en relevant station, och endast om originalordern fortfarande hör till samma jobb. Den väntande ordern kan sedan tas av befintlig AI-scheduler om den redan är aktiv och behörig. **Ingen QA-order får värdet verifierat=true automatiskt.** QA-rapporten kräver verkliga testresultat och användarens granskning.
- Avstängd Freesound-nyckel, icke testad nyckel eller avstängd anställd innebär ingen Freesound-sökning. Spara nyckel och **Testa anslutning** i separat inställningsdialog.
- Freesounds kommersiella API-användning kräver separat avtal. Leverantörens återstående kvot är **okänd** tills den faktiskt går att verifiera.
- Ingen automatisk Git-push, merge, extern publicering, ny anställd, Freesound-nyckel eller betald leverantör har skapats.

## Testning

**Offline, verifierat här:** 16 Python-enhetstester (v1, v1.1 och v1.2 kontrakt), `python3 -m py_compile` för modulerna, `node --check` för frontend och ett Chromium-gränssnittstest med *simulerade API-svar*. Allt ovan använder testdata, inte riktig API-nyckel. Projekt- och rapportisolation, väntande kontra körande order, verktygsbehörighet, testad nyckel, deduplicering, importgodkännande och QA utan falsk verifiering ingår.

Kör de medföljande v1.2-backendtesten manuellt från projektroten:

```bash
cd backend
python3 -m unittest test_pw_toolbridge_v3 -v
```

**Inte verifierat här:** din lokala Pixel Works-server med historisk Git-motor, den riktiga Freesound-nyckeln, verkliga Codex-/Gemini-körningar, ljuduppspelning med riktiga previews eller Firefox. Provkör särskilt en verklig ljudorder och kontrollera att QA inte skapar oönskade extra arbetsorder när befintliga Codex-jobb integreras.

## NOW / NEXT / LATER

**NOW:** Tool Registry (en adapter), verifierings-/behörighetskontroll före sökning, spårbara verktygshändelser, normal ljudorder, QA-överlämning och separat Freesound-inställningsfönster.

**NEXT:** Gör en gemensam per-jobb tool-call-brygga där den **ordinarie** Codex/Gemini-sessionen kan be om verktygsanrop och läsa resultatet i samma jobbkontekst. Låt QA-systemet lagra verifierbara testbevis innan något märks verifierat. Visa QA-status även i uppdragskorten.

**LATER:** ElevenLabs/Suno-adaptrar efter godkända API-/betalvillkor; OAuth2 för originalfiler, ljudcredits, ljudkonvertering via lokal FFmpeg, valfria verktygsbudgetar per projekt.
