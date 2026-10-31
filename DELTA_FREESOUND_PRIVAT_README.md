# Pixel Works – Freesound sökfix v1.4 (privatläge)

**Källa:** `jwestholm/pixelworks`, gren `dev`, commit `fb70d1c9a927e07e802537c83705db5b8f9876cd` (2026-10-29 #1). **Installationsbas:** lokalt installerad Freesound v1.3 samt dess förutsättningar (v1, v1.1, verktygssystem/QA v1.2). GitHubs `dev` innehåller inte dessa Freesound-deltafiler; det här paketet är därför en **överlagring ovanpå v1.3**, inte en fristående version av hela spelet.

## Installation

1. Stäng Pixel Works-servern och spara arbete.
2. Packa upp **ZIP-filen i projektroten** där `index.html` ligger. Skriv över `backend/pw_freesound.py` och `src/pw-freesound.js`. Alla mappar finns på rätt nivå i arkivet.
3. Starta servern och uppdatera webbläsaren med Ctrl+F5.
4. Gör ett **nytt** ljuduppdrag via vanliga Musikstudion. Tidigare misslyckade Freesound-jobb startas inte om automatiskt. Inga sökningar sker bara för att du öppnar menyn.
5. Kontrollera Musikstudion → **Visa ljudförslag från teamet** → **Visa verkliga verktygshändelser**. Mätvärden visar antal API-träffar och bortfall på grund av saknade/säkerhetsogiltiga MP3-prover. Ingen licensfiltrering sker.

## Ändringar

- **Freesound privat testläge:** alla licenstyper får visas som ljudförslag (CC0, CC BY, CC BY-NC och andra/okända). Ingen blockering vid sökning eller import baserat på licens. Vi sparar dock Freesounds licensmetadata, upphovsperson och källadress så de finns kvar vid eventuell publicering.
- **Verifierad sökfix från v1.4:** Freesounds textbaserade licensfält hanteras korrekt som metadata; hög- och lågkvalitativa säkra MP3-förhandsprov kan användas. Om en sökning utan API-fel inte ger användbara träffar prövas högst två bredare sökningar, utan extra AI-anrop.
- **Säkerhetsgränserna kvar:** API-nycklar lämnar inte servern, sökningar kräver en redan godkänd och pågående ljudarbetsorder, endast HTTPS MP3-prover från Freesounds domäner accepteras, och spelaren godkänner varje import. Importerat ljud märks **förhandsprov, ej original**; det förs inte automatiskt in i spelkoden.
- **Spårbarhet:** sökresultat och orsaken till att vissa förhandsprov inte kunde användas visas tydligt, utan att dölja ett lyckat API-svar som ett anslutningsfel. Arbetsrapporter och QA-verifiering behåller sina separata statusar.

**Viktigt:** Detta är för din privata prototyp. Licensinformation sparas endast, men för användning utanför privat testning (exempelvis publicering eller kommersiell distribution) måste respektive ljuds villkor och Freesounds API-villkor fortfarande följas. Freesounds API-kvot rapporteras inte som något påhittat värde.

## Tester (offline)

- 9 nya v1.4-privatlägestester: licensmetadata utan filtrering (inklusive CC BY-NC), API-kontrakt, säkra ljudprover, fallback, import, agentens arbetsflöde, projektskydd och kvotfel.
- 13 äldre v1.3-regressionstester: bl.a. DNS, API-autentisering, nyckelskydd, agentens ordinarie jobb och dubbletter.
- 5 verktygsregister- och QA-tester (v1.2).
- Chromium: Inställningar, licensmeddelande utan blockering, förslagslista, spårbarhet, QA-indikator, kontrast och mobilbredd.
- Python- och JavaScript-syntax.

Inga riktiga Freesound- eller AI-anrop gjordes i testerna och ingen GitHub-push. Ljudkvalitet och verklig körning i Ubuntu är inte verifierad här.

## NOW / NEXT / LATER

**NOW:** skapa nytt ljuduppdrag och se antal riktiga API-träffar/förslag i verktygshistoriken.
**NEXT:** verifiera med ditt riktiga konto i Ubuntu att MP3-provet går att lyssna på och importera, och att QA-ordern testar resultatet.
**LATER:** interaktiva agentanrop till verktyg mitt under pågående Codex-session, ElevenLabs/Suno och publiceringskontroll vid export.
