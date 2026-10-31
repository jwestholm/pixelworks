# Pixel Works – Beslutslappen v1.5 / game first

**Byggbas:** GitHub `jwestholm/pixelworks`, `dev` på `fb70d1c9a927e07e802537c83705db5b8f9876cd` (2026-10-29 #1). Denna ZIP är en delta ovanpå tidigare **Freesound v1.4 PRIVAT** och **ToolBridge/QA v1.2**. Det finns inga nya nycklar och inget nytt dataformat i spelfilerna.

## INSTALLERA

1. Säkerhetskopiera eller committa din lokala Pixel Works-installation (särskilt dina egna kodändringar).
2. Packa upp ZIP-filen **i projektroten** där `index.html` ligger – inte i `src/` eller `backend/`. Bekräfta överskrivning.
3. Starta om servern: `cd backend && python3 server.py stop` (om ditt befintliga kommando stödjer det) och sedan `python3 server.py start`. Alternativt stoppa den tidigare serverprocessen med Ctrl+C och kör den ordinarie startsekvensen. Uppdatera webbläsaren med Ctrl+F5.
4. Öppna ditt aktiva spel. Väntande riktiga beslut dyker upp som **💌 Teamet behöver ditt beslut** när ingen annan modal är öppen.
5. Öppna `Inställningar & diagnostik → 💌 Teamets beslut → ⚙ Hantera beslut`. Här kan du avaktivera automatisk Git-omförsök och frivilliga tekniska omförsök.

## NU – DET SOM IMPLEMENTERAS

- **En beslutsinkorg för alla för närvarande identifierbara spelarbeslut:** anställdas faktiska hjälpärenden (`/api/projects/<slug>/help`) och verkliga ljud-/bildförslag från Freesound och Codex. Källorna är samma som kontoret redan använder, inte ny AI-simulering. Inkorgen har en fast knapp när du stängt den.
- Hjälp: **Ja, låt studion åtgärda** använder samma säkra serverfunktion som tidigare hjälpdialog; **Skicka min instruktion** skapar en vanlig uppföljningsorder med spelarens text; **Kanske, senare** påminner om 30 minuter och sparar återstående tid projektvis. Efter påminnelsetiden kan samma olösta ärende visas automatiskt igen.
- Medier: **▶ Provlyssna** eller **🖼 Visa**, därefter **Ja/Nej/Kanske** med feedback. Förhandsprov hämtas genom den befintliga autentiserade Pixel Works-servern, inte som en oskyddad direktlänk från webbläsaren. Väljer du **Nej + 'Gör älgen mer cartoonig'** skickas originalfilen som säker referens i nästa arbetsorder.
- Bilder/ljud som faktiskt exporterats av en Codex-agent kan få granskningskort från dennes arbetsgren. Om en agent endast syntetiserat Web Audio i JavaScript och inte exporterat WAV/MP3/OGG finns inget ärligt ljudprov att spela; det visas tydligt och du kan begära en export.
- **Engångsomförsök vid verklig Git-konflikt (på som standard, enligt spelarens önskemål):** När en normal Codex-jobbintegration rapporterar en faktisk konflikt (`krockar med andra ändringar`) och studio-/projektmandat är aktivt skapas **EN** vanlig väntande order för att återskapa förändringen på aktuell kod. Ingen automatisk force merge, reset, push, eller obegränsad retry. Den nya ordern är markerad som redan omförsökt och kan aldrig skapa en andra automatisk retry.
- **Opt-in direkt på hjälplappen:** `Låt Chefen försöka själv vid liknande tillfälliga teknikfel framöver` sparar policyn direkt när du kryssar i eller ur. Samma val finns under Inställningar → Beslutsregler och går alltid att återkalla. `Låt Chefen hantera enkla tillfälliga fel själv` är **AV** initialt. När du aktiverar det får tydliga timeout-/temporära tekniska fel högst ett automatiskt nytt försök via vanliga arbetskön. Beslut om bilder, ljud, betalningar, radering, publicering och andra kreativa godkännanden automatiseras **inte**.
- Beslutspolicyn sparas säkert lokalt, `~/.pixelworks/secrets/decision-policy-v1.json`, med privat filbehörighet. Kanske/påminn senare lagras i respektive projekts `management/decision-later.json`. Inga API-nycklar kopieras till arbetsordrar.

## TESTER

Utan nätverk och utan riktiga Codex-/Freesound-anrop:

```bash
cd backend
python3 -m unittest -v test_pw_decision_center.py test_pw_media_review.py
```

I leveransmiljön: **19 offline Python-tester godkända**, JavaScript-syntax kontrollerad med Node och Chromium-funktionstest för hjälpkort, sound-preview med spelbar WAV-testfil, bildvisning, påminn senare, anpassad instruktion, serverpersistens av settings och mobil layout.

## KÄNDA BEGRÄNSNINGAR

- Beslutsbrevet kontrollerar nya ärenden ungefär var femte sekund (så länge Pixel Works är öppet). Det öppnas när inga andra modalrutor blockerar. Hjälpmarkeringen ovanför agenten döljs när den gemensamma inkorgen tar över.
- Den nya lappen kan samla **nuvarande** hjälpfall + mediasvar; helt nya beslutstyper (anställning, budget, manusbeslut etc.) behöver kopplas in i den gemensamma inkorgen senare. Ingen implementerad generisk autonom AI-policy kan godkänna vad som helst.
- **Skapad QA-arbetsorder = inte oberoende verifierat.** QA arbetar och lämnar rapport via ordinarie system. Ingen falsk 'verifierat'-badge sätts.
- Denna delta stoppar inte redan pågående Codex-jobb och skriver inte om tidigare rapporter. Den automatiska engångsretries gäller framtida jobbhändelser när backend är aktiv.
- Inga verkliga molnanrop har körts här. Förhandslyssning med just din Freesound-nyckel och agentgenererade filer behöver provas i Ubuntu. Underliggande Freesound-anslutning och kvoter ändras inte i denna delta.
- En fri Pollinations-integration ingår **inte**. Pollinations kan bli ny **AI-leverantör med valbara undermodeller**, men aktuella modellpriser/behörigheter måste först hämtas ur deras levande katalog. Samma modellväljare bör senare läggas till för Gemini.

## NEXT

- Visa även fler framtida beslut (budget, rekryteringsförslag, designalternativ, integreringsgranskning) i samma inkorg via egna datakällor.
- Kodgenererat procedural-ljud: export och uppspelning av faktisk ljudfil i arbetsrapporten innan kvalitetsgodkännande.
- För fler AI-leverantörer: provider → modell → capabilities → verklig token-/kvotinfo; börja med Gemini-undermodeller och Pollinations discovery.

## LATER

- Fördjupad chefspolicy för rutinärenden som kräver explicit uppgiftsgräns, budget och loggad återkallbar behörighet.
- Mer tycoon-liknande feedback, agenternas reaktioner och belöningssystem för spelarens kreativa beslut.

**Ingen GitHub-push eller extern ändring genomförd.**
