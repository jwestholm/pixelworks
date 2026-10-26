# Pixel Works v0.12.11.4 – Studioåtkomst en gång

**Delta mot v0.12.11.3.** ZIP-filen innehåller enbart filer som ska ersätta eller läggas till. Inga installationsskript, ingen projektdata och ingen serverstartfil.

## Ändringar
- En enda välkomstruta: **Ja, fråga mig inte igen** / **Inte nu – bara titta**.
- Beslutet sparas i lokal serverkonfiguration (`~/.pixelworks/secrets/studio-consent-v012114.json` under standard arbetsrot), så det gäller även efter omstart och för alla projekt i samma Pixel Works-installation.
- Inställningar → Studioåtkomst visar tillåtet/avstängt och låter dig stänga av eller aktivera igen.
- Befintlig arbetsledare kontrollerar ett gemensamt mandat i stället för att begära godkännande projekt för projekt.
- Automatiska Gemini-jobb kräver godkänd studioåtkomst. Inget AI-anrop görs enbart genom att trycka Ja. När åtkomst stängs av startas inga nya automatiska Gemini-jobb; ett redan pågående jobb kan avslutas.
- Nyproduktion ger inte längre ett tyst projektmandat bara för att klienten skickar `startup_consent`. Den avancerade projektguiden slipper också sitt extra godkännande efter att studioåtkomst aktiverats.
- Inga GitHub-pushar, betaluppgraderingar eller mappar utanför Pixel Works arbetsrot godkänns.

## Användning
1. Utgå från Pixel Works **v0.12.11.3**. Om du fortfarande kör v0.12.11.2, lägg först in delta v0.12.11.3.
2. Packa upp den här ZIP-filen i Pixel Works-katalogen med undermapparna kvar. Fem filer är uppdaterade/nya.
3. Starta om med samma kommando som alltid: `python3 backend/server.py`.
4. Uppdatera Firefox med Ctrl+Shift+R. Välj **Ja, fråga mig inte igen** en gång.
5. Kontrollera att Inställningar innehåller både den gamla startsidan, Google Gemini och Studioåtkomst.

## Teststatus
- 50 Python-tester: passerade lokalt (ingen kontakt med Google eller Codex).
- Chromium: förstagångsdialog, sparat ja/nej, omstartsliknande återöppning, status i Inställningar, avstängning: passerat med falska HTTP-svar.
- Verklig Codex-process, riktig Gemini-anropsserie samt din Firefox-installation: **inte verifierade**.

## Varför tillstånd alls?
En gång för att godkänna **verkliga ändringar på disken och återkommande API-anrop** inom Pixel Works egna projekt. Därefter ska appen inte fråga igen för rutinjobb. Detta är inte ett allmänt operativsystemsmandat; appar eller externa tillåtelsekontroller utanför Pixel Works kan fortfarande kräva egna beslut.

Ingenting är ändrat på GitHub och inga projektfiler behöver ersättas.
