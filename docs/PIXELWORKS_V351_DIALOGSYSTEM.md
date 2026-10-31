# Pixel Works 3.5.1 – Gemensam spelmeny för dialoger

## Beslutad riktning

Pixel Works är ett spel: det ska inte krävas kunskap om gamla projekt- eller teknikmenyer för att hitta personal, uppdrag, Chefen eller granskningsinkorgen.

### Genomfört (NOW)

- Ny **delad `pixelWorksGameDialog`-kontroller** i `src/pw-v351-dialogs.js` som låter befintliga v3-dialoger använda samma navigation/back/kontor.
- Personal, Uppdrag, Chefen och Beslut får samma navigeringsrad, definierad och inkopplad på ETT ställe. V3-komponenternas formulär och affärslogik är fortsatt oförändrade.
- En återgångskedja inom de fyra vyerna och samma stängning till kontoret. Befintliga gamla UI-genvägar till dessa vyer kopplas till samma navigering.
- Påbörjad uppdragstext bevaras i minnet när du går från Uppdrag till Chefen och tillbaka. Ingen ny AI-start eller ny databasskrivning.
- Beslutsdialogen får samma navigering utan att ersätta ljud-/bildkomponenter, fält eller godkännandeknappar. Beslutskortens tillstånd styrs fortfarande av den tidigare mediagranskningen.
- Gemensamma CSS-tokens för pixelramar, tydliga knappar och mobil 390 px.
- Den dubbla interna Chefen-genvägen inne i Uppdrag döljs visuellt. Chefens funktion finns i en konsekvent huvudflik.

### Arkitektur

`src/main.js` importerar `src/pw-v351-dialogs.js` efter v3-dialogerna. Kontroller sköter endast dialognavigation och lokala textutkast. Ingen affärslogik eller faktisk AI-körning ligger i den.

`src/pw-v351-dialogs.css` laddas av kontroller via ett lokalt style-link. Ingen CDN eller extern anslutning.

### Begränsningar

Detta är den **första riktiga gemensamma dialogkontrollern**, inte en färdig total ersättning av alla legacy-/teknik-/stationsfönster. `#localStudioDialog`, gamla stationsrutor, äldre agentpanel, inställningar och specialdialoger behöver inventeras och successivt portas utan att förstöra data eller arbetsrapporter.

`Beslut` är mediasystemets inkorg för verkliga beslut och hjälpärenden. Den v3-specifika AI-jobblistan finns dessutom under Uppdrag; dessa två granskningstyper är ännu inte sammanslagna till en enda servermodell.

### Testläge

- 10 riktade Chromiumtester för dialogstyrningen, inkl. desktop/mobil, bakåt, navigering, bevarat utkast, beslutslappens DOM-stabilitet och att navigationen inte startar AI.
- Ytterligare 23 äldre UI-tester och 30 backendtester körda mot oförändrad affärslogik vid första regressionsvarvet (det nyare UI-varvet sammanlagt 33 UI-tester). En fristående äldre sprite-fixtur har ett eget laddningsantagande och räknas **inte** som passerad.
- Lokalt testad med fiktiva/stubbade API-svar. Inte verifierad på användarens Firefox eller vid riktiga Codex/Gemini-anrop.

## NEXT

1. En komponent som renderar *hela* de fyra dialogernas shell, inte bara navigationen; fas ut gamla separata HTML-header-renderare.
2. En gemensam beslutsmodell som kan presentera ljud, bilder, text och kodresultat från olika arbetsytor i ett sammanhållet spelkort. Behåll kvalitetskontroll och användargodkännande.
3. Bättre personalprofil: stor personlig sprite, kompetens/risk/får ej, historia och en enkel meny med roller och motorer.
4. Visuellt förbättrat kontor och touch-kamera med pan/zoom; samma pixelutseende som menyerna.

## LATER

- Kontrollerad avveckling av gamla projektbundna specialfönster och dubbel navigering.
- Samtidiga klienter: gemensamt uppdrags-/beslutstillstånd från servern men lokala dialoger och utkast per klient.
- Designregression på Firefox/Ubuntu/Android med riktiga ljudfiler och 15 anställda.
