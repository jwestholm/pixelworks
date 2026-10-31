# Pixel Works v3.2 – Rekryteringsnavigation, rekommenderade roller, personaprompt och unika sprites

**Bas:** `jwestholm/pixelworks` `dev` vid `fb70d1c9a927e07e802537c83705db5b8f9876cd`, installerad Pixel Works v3.1 + tidigare deltor.

## Installation

1. Behåll en säkerhetskopia av `~/.pixelworks` och dina lokala ändringar innan du uppdaterar.
2. Packa upp ZIP-filen i projektroten (`~/pixelworks/pixelworks-git`, samma mapp som `index.html`) med bevarad undermappsstruktur. Skriv över de tre tidigare filerna `src/pw-v3-recruit.js`, `backend/pw_recruitment_v3.py` och `backend/pw_v3_personas.json`.
3. Starta om backend: `python3 backend/server.py stop` följt av `bash start-lan.sh` om du använder LAN-läget (annars din vanliga startmetod).
4. Uppdatera Firefox med `Ctrl+F5` och ladda om mobilwebbläsaren.
5. Öppna Rekrytering, titta på **Bäst lämpad för**, bläddra bland historierna, anställ om du vill och prova Stäng-krysset från ett agentkort. Kolla att en anställd Mira har eget turkost hår i kontoret även om du ändrar rollen.

## Ändringar

- **Navigation:** Stäng/ESC återvänder till kontoret och stänger en eventuell äldre personaldialog. Personalkortets bakåtknapp leder till Mitt team, medan X lämnar rekryteringen.
- **Rekommenderad roll:** Varje kandidat har tydlig `Bäst lämpad för`/`Bör jobba som`, en fast rekommendation sammanvägd utifrån karaktärens fiktiva kompetenser, erfarenhet och yrkesprofil. Vald yrkesroll visas separat och kan vara en annan. Siffrorna är spelvärden – inte verifierad AI-prestanda.
- **Berättelser:** Nytt personligt minne, ett kontorsrykte, en vana och ett talexempel för samtliga sju fasta personer (inklusive Chefen). Dessa attribut ligger i katalogen och ändras inte via företagsprofilen.
- **Persona som AI-konfiguration:** Backend tar fram `persona_config` och en visningsbar `prompt_preview` med fasta traits, preferenser, språkstil, företagets roll och redigerbara arbetsinstruktioner. Exekvering är alltjämt **INTE ANSLUTEN**; inga verkliga AI-anrop startas.
- **Karaktärssprites:** 28 nya transparenta PNG-atlaser för sju identiteter; fyra typer × fyra rutor. Figurens utseende styrs av `character_id`, inte av yrkesrollen. README i `docs/SPRITE_BIBLE_V32.md`.

## Lagring och säkerhet

- Installerandet skriver inte till `~/.pixelworks`, skapar inga jobb och raderar inga gamla personalfiler. Befintliga v3-anställningar finns kvar.
- Backend skickar inte persona till Codex/Gemini/Pollinations ännu. Fasta personliga egenheter kan inte kringgå företagets säkerhetsregler, instruktioner eller manuell godkännandeplikt.
- Den gamla arbetsmotorn ska fortfarande vara pausad medan v3-personalläget är aktivt.

## Verifiering

- Backend: regressionstester för v3.0, v3.1, v3.2, 15 tester gröna med mockade servrar.
- UI: isolerat Chromium desktop 1350×900 + mobil 390×844, krysset, äldre dialoglager, rekommenderad roll, personahistorier och att Mirasprajtens källa inte byts med rollen.
- PNG-filer validerade 192×68, RGBA och 7 olika identiteter; binärerna avkodade i Chromium via testdata.
- **Inte verifierat i användarens Firefox/Ubuntu eller med verkliga AI-anrop.** Webbläsartesterna kördes på isolerad mock (testmiljön blockerar direkta lokala fil-URL:er).

## NOW / NEXT / LATER

**NOW:** Spelbar rekryteringsinteraktion, unika figurer och korrekt stängning. **NEXT:** en v3-arbetsmotor som tilldelar den globala personalstyrkan riktiga arbetsorder och laddar `persona_config` som promptinstruktion med godkänd motor. **LATER:** fördjupade intervjuer mot verifierade motorer, större animationsuppsättning och en mer levande fikarumskultur.
