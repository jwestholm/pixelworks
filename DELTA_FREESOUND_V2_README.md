# Pixel Works – Verktyg i vanliga ljuduppdrag (Freesound v1.1)

**Baskod:** GitHub `jwestholm/pixelworks` `dev` vid `fb70d1c9a927e07e802537c83705db5b8f9876cd` (`2026-10-29 #1`).

**Uppgradering från:** `PixelWorks_Freesound_Ljudstudion_v1_DEV_fb70d1c_DELTA.zip` som redan installerats ovanpå den här baskoden. Den nya delta-ZIP-filen innehåller bara två ersättningsfiler (`src/pw-freesound.js`, `backend/pw_freesound.py`), ett kompletterande backendtest och detta dokument/manifest. Den skriver **inte** över `local.js`, `src/main.js`, `backend/server.py` eller spelprojekt.

## Installation

1. Ta gärna en säkerhetskopia eller kör `git status`/`git diff` innan du skriver över filer. **Kontrollera att v1-Freesound-deltan finns installerad** – alltså att `src/main.js` redan importerar `./pw-freesound.js` och `backend/server.py` redan installerar `pw_freesound`.
2. Packa upp ZIP-filen **direkt i projektroten**, bredvid `index.html`, och behåll undermapparna `src/` och `backend/`.
3. Skriv över de två befintliga Freesound-filerna. Starta om den lokala Pixel Works-servern och gör `Ctrl+F5` i webbläsaren.
4. Öppna **⚙ Inställningar → Inställningar & diagnostik**. Under **☕ Google Gemini** finns nu **🧰 Verktyg · Freesound**. Här kan du spara/ersätta nyckeln, **testa den på riktigt** eller koppla från den. API-testet utför ett sökanrop först när du klickar **Testa anslutning**. Nyckeln visas aldrig i svaret.
5. Klicka på **🎵 Musikstudion** eller **🎙️ Röststudion** och skapa en **vanlig arbetsorder**. Ingen ny Freesound-uppdragsdialog visas. **En kölagd order gör inga Freesound- eller extra AI-anrop.** När det befintliga dispatchsystemet markerar ljudordern som `running`, får den ansvariga, verkliga AI-anställda bedöma om Freesound behövs. Om svaret är ja används Freesound och en kort lista med verkliga förslag skapas. Ett ej testat Freesound-konto används inte automatiskt.
6. Öppna ljudstationen igen och klicka **🎧 Visa ljudförslag från teamet** för att lyssna. Om du godkänner ett förslag laddas bara dess MP3-förhandsprov ned till projektets privata ljudbibliotek, tillsammans med licens och källa. Originalfiler och spelkod ändras inte automatiskt.

## Viktiga gränser

- **Freesound är ett verktyg, inte en anställd.** Ingen separat Freesound-agent eller manuell Freesound-sökruta. En riktig anställd med en befintlig motor (Codex/Gemini) använder verktyget.
- **Befintlig arbetsledare/scheduler äger fortfarande själva uppdraget.** Freesound genererar ett separat *förslagsresultat kopplat till samma order-ID*. Det här v1.1-tillägget kan ge extra AI-anrop samtidigt som den vanliga ljudordern körs. Det är **ännu inte ett komplett generellt verktygsanropsgränssnitt där samma AI-körning kan konsumera Freesound-filer direkt i arbetsytan**. Det kräver en separat scheduler-/provider-integration.
- **Ingen automatisk Freesound-sökning** utan sparad, uttryckligen testad nyckel och en redan påbörjad ljudorder. Vid nyckelbyte måste anslutningen testas på nytt. Riktiga externa Freesound-anrop kan använda kvot.
- Bara **CC0** och **CC BY** blir kandidater; CC BY kräver kreditering. Licens och resultat kontrolleras vid import; granskning innan publicering krävs fortfarande. Kommersiell Freesound-API-användning kräver separat överenskommelse.
- API-nycklar och teststatus lagras lokalt i serverns privata `secrets/` med begränsade filrättigheter. Inga nycklar sparas i frontend eller ZIP.
- **ElevenLabs och Suno** är endast framtida verktygsplatser, inte aktiverade integrationer.
- Ingen GitHub-push, merge, betaluppgradering eller verkligt AI-/Freesound-anrop utfördes vid framställningen.

## Kontroll / teststatus

**Verifierat offline:** 11 Python-backendtester inklusive normaliserade licenser, säker import, auth, projektisolering, sparad/testad/utbytt nyckel, väntande kontra pågående order, deduplicering, verktygsavstående och att kärnans riktiga jobb inte tas över; Python/JavaScript-syntax och ett Chromium-test med simulerat API som verifierar samma inställningssida som Gemini, nyckelflöde, befintlig ljudstation, förhandslyssning, godkännande, mobil bredd och inga runtime-fel.

**Inte verifierat:** Freesound-sökning med användarens riktiga API-nyckel, en verklig Codex/Gemini-jobbkörning, Firefox, samt komplett integration med användarens lokala historiska Git-motor. Observera att serverstarten fortfarande kräver lokal Git-historik med äldre engine-blob enligt `backend/server.py`.

## NOW / NEXT / LATER

**NOW:** Rätt inställningsvy, verkligt anslutningstest efter klick, befintligt ljudbordsuppdrag, ordningskopplade agentförslag och explicit importgodkännande.

**NEXT:** Ett generellt serverägt Tool Registry med ett per-jobb verktygsanropsprotokoll så agenten använder Freesound direkt **inne i samma pågående arbetsorder** och kan föra godkända materialreferenser vidare i produktionskedjan. Visa ljudresultat även i vanliga uppdrags-/rapportvyn. Automatiska krediteringslistor.

**LATER:** ElevenLabs, Suno (enbart när avtals-/API-villkor är godkända), FFmpeg-adaptrar, budgetsatta verktygsbehörigheter och OAuth2 för Freesound-original.
