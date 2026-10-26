# Pixel Works 0.13.7 – Skrivbordsdesign och konsekventa menyer

**Basversion:** 0.13.6. **Format:** endast ändrade/nya filer. Start som vanligt med `python3 backend/server.py` och hård uppdatering i webbläsaren (`Ctrl+Shift+R`). Ingen automatisk installation, datamigrering, GitHub-ändring eller AI-anrop.

## Underlag

Film: `Skärminspelning från 2026-10-26 12:14:49.webm`, längd ~69 sekunder.

Observerade skillnader:
- 0–5 sek: Arbetsledning använder äldre, mörk skribordsruta med versionsrubrik. Möjliga uppdrag fungerar men stilen avviker.
- 5–17 sek: Programmering, Forskning och Testning visar ljusa standardkort utan tydlig scenbild.
- ca 18–24 sek: Grafikstudion visar den avsedda ljusa, illustrerade bakgrunden.
- ca 24–35 sek: Rapportpärm och Musikstudio. Musik har genomtänkta kategorier men bara gradient, inte egen arbetsplatsillustration.
- ca 35–60 sek: Personal, övriga administrationsmenyer och rapporter visas fortfarande i en mer teknisk/dunkel stil. Dessa är inte vanliga uppdragsbord och behöver en särskild UX-fas, inte en bred osäker CSS-override.

## Ändringar

- Alla **åtta stationer** i den moderna uppdragsbyggaren får egen mjuk färgpalett, dekorerande arbetsplatsillustration, enhetligt rubrikfält, jämna kort, hover/fokus, bättre underkategoriikoner och kompaktare höjd.
- Grafikstudions tidigare bild behålls; Programmering, Forskning, Testning, Dokumentation, Möte, Musik och Röst får nya illustrationer.
- Det äldre **Chefsbordets** uppdragsval får en matchande, diskret illustrerad bakgrund och ljusare kort, men använder exakt samma befintliga funktioner och händelsehanterare.
- Gemensamma **Min studio**-dialogen får en mjukare illustration, utan att funktionerna ändras.
- Appens synliga versionsetikett uppdateras till 0.13.7.

## Oförändrat

- Alla uppdragskategorier och underkategorier, beskrivningstext, bilagor, prioritet, projektgräns, arbetskö och delegation.
- API:er, sparade projekt, personal, Game Bible och AI-motorer.
- Rapportpärmar och avancerade adminpaneler är fortsatt separata arbetsflöden med befintliga färger och layouter. De ska harmoniseras senare med design-system-komponenter efter full UX-regression, inte via generella riskabla selectors.

## Viktig verifiering

Backendens statiska filrouter tillåter just nu **PNG/SVG**, inte WebP. Samtliga nya bakgrunder levereras därför i **PNG** och är sökbara under `assets/office-v2/` utan backendändring.

### Tester (simulerat)

- `python test_browser_0121118.py` – pass: referenser, kategori, underkategori, prioritet, QA, Möte, projektgräns och sparat uppdrag.
- `python test_visual_0137.py` – pass: åtta olika uppdragsfönster, illustrerade CSS-bakgrunder, undermenyer och beskrivningsfält.
- `python test_legacy_desk_0137.py` – pass: Chefens äldre uppdragsdialog visar eget tema och knapparna förblir tillgängliga.
- `python tests/test_rail_simple.py` – pass: förenklad högerspalt oförändrad.
- `node --check src/pw-v0121118.js` och `node --check src/pw-v013.js` – pass.

Verklig Firefox, andra projekt och riktiga AI-jobb är **inte verifierade**.

## Installera

1. Packa upp ZIP-filen över din fungerande 0.13.6-installation.
2. Starta/omstarta med `python3 backend/server.py`.
3. `Ctrl+Shift+R` i Firefox.
4. Klicka på Programmering, Testning, Musik, Dokumentation, Forskning, Röst, Möte, Grafik samt Chefsbordet. Samma arbetsflöden ska fungera som tidigare.

## Återställning

Återställ `src/pw-v0121118.js`, `src/pw-v013.js` och `tests/test_rail_simple.py` från 0.13.6/0.13.0. De åtta nya PNG-bilderna är dekorativa och kan ligga kvar eller raderas. Inga sparfiler konverterades.
