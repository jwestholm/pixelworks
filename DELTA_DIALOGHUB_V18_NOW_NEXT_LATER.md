# Pixel Works – projektminne efter dialogerna v1.8

Bas: GitHub `dev` `fb70d1c` + Freesound-/media-/decision-deltor v1.1–v1.7.

## NOW (implementerat i delta v1.8)

- Beslut och mediegranskning kommer från **en** kanonisk serverdriven inkorg.
- `src/pw-dialog-hub.js` är den generiska registreringspunkten för kontextbaserade dialogingångar: `root + target + section`.
- `window.pixelWorksOpenDecisionContext({kind,station,employee,label})` är det återanvändbara klientgränssnittet. `window.pixelWorksOpenMediaReview()` finns kvar för bakåtkompatibilitet.
- Beslutsvyn stödjer flikar, kontextfilter, sök och sparade feedbackutkast.
- QA-, Fikarums-, personal- och ljudflöden använder samma beslutslapp. Inga extra tillstånd, simulerade ljud eller nya AI-aktiviteter.
- Viktig säkerhet: media-CSP från v1.7, privat Freesound-nyckel, serverägda tillgångar, krav på spelarens godkännande och projektisolering kvarstår.

## NEXT

- Gemensamma dialogkomponenter för *nytt uppdrag*, *rapport*, *personalprofil* och *integrationsinställningar*. Enkla konsekventa rubriker, samma hjälptext och tydlig återväg.
- Bärbara `media_ref` i chattrepliker/QA-rapporter så ett erbjudet ljud kan visas **inne i själva meddelandet** utan att skapa nya beslutsdatabaser.
- Undersök process för att länka QA-bevis till samma beslutskort utan att förväxla "infört" med "verifierat".

## LATER

- Gemensamt leverantörs-/undermodellsregister (Codex, Gemini-submodeller, Pollinations efter verifiering).
- Fler beslutstyper, med mandat och återkallbara rättigheter, utan ogenomtänkta auto-godkännanden.
