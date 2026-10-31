# Pixel Works – Freesound / Codex nätverksfix och uppdragskontrast v1.3

**Git-referens:** `jwestholm/pixelworks` → `dev` → `fb70d1c9a927e07e802537c83705db5b8f9876cd` (`2026-10-29 #1`).

**Installationsbas:** projektet ska redan ha delta v1, v1.1 och v1.2 (Verktygssystem & QA) installerade. Detta är en **delta ovanpå v1.2**. GitHub-`dev` innehåller inte dessa lokala deltafiler.

## Installation

1. Stäng av Pixel Works-servern normalt och spara eventuellt arbete.
2. Packa upp ZIP **i projektroten**, där `index.html` ligger, och skriv över filerna. Endast `src/pw-freesound.js` och `backend/pw_freesound.py` ersätts; testfilen är ny.
3. Starta om servern från rätt checkout och gör `Ctrl+F5` i webbläsaren.
4. Du behöver **inte lägga in API-nyckeln igen** – den finns fortsatt i studions privata `secrets`-mapp. Gå till Inställningar → Freesound om du vill kontrollera anslutningsstatus.
5. Starta **ett nytt** godkänt ljuduppdrag från Musikstudion/Röststudion och låt den vanliga arbetskön köra det. Redan påbörjade jobb får inte sin prompt ändrad i efterhand.
6. Välj Musikstudion → `🎧 Visa ljudförslag från teamet` för att se verklig sökning, verktygshändelser, metadata och lyssningsbara förhandsprov.

## Varför uppstod felet?

Skärminspelningen visar att Chefen körde ett eget Freesound-anrop från **Codex-sandboxen**, som inte kunde slå upp `freesound.org` (`Could not resolve host`). Det är en **annan nätverksmiljö** än Pixel Works-servern där det lyckade API-anslutningstestet gjordes. Den gamla v1.2-funktionen startade verktygssökning och ordinarie Codex-körning **parallellt**, så de delade inte sökresultat.

Nu sker följande vid *en redan godkänd, pågående vanlig ljudarbetsorder*:

- Anställdas befintliga AI-motor får välja om Freesound passar. Originalkomposition kan välja bort Freesound.
- **Pixel Works-servern** gör Freesound API-sökningen med den privat lagrade nyckeln, via befintligt behörighetskontrollerat verktygsregister.
- AI-medarbeteren kan välja upp till tre kandidater **utifrån metadata** (aldrig påstådd provlyssning).
- Sökresultaten, källor, licenser och eventuellt verktygsfel **lämnas in som läsbart, begränsat underlag till samma ordinarie Codex-jobb innan kodarbetet påbörjas**.
- Den ordinarie jobb- och QA-schedulern ansvarar fortsatt för uppdrag, status, kodintegrering och passiv QA-uppföljning. Inget ljud importeras utan spelarens godkännande.

**API-verifiering:** `GET https://freesound.org/apiv2/search/`, `Authorization: Token <nyckel>` och `fields=...previews...` stämmer med aktuell Freesound-dokumentation. API-nyckel krävs för sökning, **OAuth2 behövs först för att hämta originalfiler** (inte vanliga sökningar). API:ets faktiska anrop, kvot och tillgänglighet har **inte live-testats i den här testmiljön**.

## Extra förbättringar

- Uppdragstext i agentkort: mörk text på ljusgul bakgrund, bättre radbrytning. Testat i Chromium.
- Särskiljer nyckel-/rättighetsfel (401/403), DNS från **servern**, TLS-fel och timeout. Kod återgår säkert till vanligt uppdrag om det extra verktygssteget misslyckas; misslyckad sökning får inte påstås vara verifierad.
- API-hemligheter exponeras aldrig i Freesound-jobbens publika JSON eller i Codex-instruktionerna.
- Freesound-förslag knyts fortfarande till rätt projekt, anställd och originalarbetsorder utan dubbelkörning.
- QA-uppföljningen i v1.2 är oförändrad. `git diff --check` är inte ett spel-/ljudtest; QA-markeringen är fortsatt `Inte oberoende verifierat` tills riktig evidens finns.

## Begränsningar och risker

- Detta är **serverförberedda tool results före Codex-körning**, inte ett interaktivt MCP-tool-calling-protokoll inne i en redan pågående Codex-session. Ett fullständigt dynamiskt verktygsgränssnitt är framtida arbete.
- Verktygsvägen är kopplad till **ordinarie Codex-arbetsorder vid `music`/`voice`**. Gemini vid dessa stationer är ännu inte integrerat i ordinarie schemaläggning. Direkt manuellt startade jobb utan arbetsorder använder inte förberedelsen.
- Freesound-verktyget använder samma AI-agent för planering och rangordning som tidigare, vilket kan medföra **ytterligare två AI-anrop** vid ett verktygsval. Dessa är inte gratis eller kvotverifierade av Pixel Works.
- API-sökningar och preview-förslag innebär inte att ljudet har lyssnats på, importerats, lagts i spelkoden eller testats. Förhandsprov är inte originalfiler. Licens och Freesounds kommersiella API-villkor måste kontrolleras inför distribution.
- Den gula markeringen **"Studioåtkomst behövs"** syntes i videon medan agenter arbetade. Jag har inte ändrat den i den här deltan eftersom skärminspelningen ensam inte säkert visar om det är gammal status, global studioåtkomst eller ett aktuellt projektmandat. Detta är en möjlig separat UX/status-bugg att kontrollera efter ominstallationen.

## Testning

- 13 nya offline-regressionstester (API-endpoint, Token-header, hantering av DNS/401, verklig backend-sökning före Codex, ingen sökning på väntande order, idempotens, källkonsistens, nyckelisolering och säkra fel).
- 5 bibehållna register- och QA-tester.
- Chromium-smoketest med mockade API-/AI-svar: anslutningsdialog, ljudkort, QA-indikator, mobilvyn och verifierad mörk text i det gula uppdragskortet.
- JavaScript-syntax med Node; Python-syntax med `py_compile`.
- Inga verkliga Freesound-, Codex- eller Gemini-anrop har gjorts under testningen, och inga Git-ändringar har skickats till GitHub.

## NOW / NEXT / LATER

**NOW:** Testa nytt ljuduppdrag och visa verktygshistorik samt Chefsrapport i Ubuntu; vid misslyckande klistra in relevant fel utan API-nyckel.

**NEXT:** Koppla in ett riktigt MCP-/tool-call-flöde för att kunna göra flera Freesound-sökningar under *samma aktiva* AI-session, och en mer enhetlig verktygsstatus/indikator.

**LATER:** Fler ljudleverantörer, hantering av originalnedladdning via OAuth2, godkänd medieintegration och automatiserad ljud- och webbläsar-QA.
