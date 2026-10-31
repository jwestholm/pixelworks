# Pixel Works v3.5.2 – UI och testkontrakt

## Ett system, inte fler fönster

- **Personalkort:** karaktärsporträtt, namn, aktuell roll, *rekommenderad* roll, två starka skills och en personlig replik. Två primära val: öppna profilen / ge uppdrag.
- **Profil:** samma karaktär och porträtt, ändringsbar roll och arbetsbeskrivning. Persona, bakgrund och AI-instruktion i utfällbara detaljer.
- **Intervju:** den tidigare rekryteringsscenen finns kvar och är fortfarande DEMO när det står DEMO.
- **Navigation:** back/office i samma toppmeny, utan dubbla Kontor-knappar när man saknar historik.
- **Grafik:** Mira/Joppe m.fl. använder samma karaktärs-ID över porträtt och sprites. Endast redan befintliga PNG-filer tillåts från servern.

## Statiska filer – varför en fix behövdes

Originalservern tillåter `/src/*.js` men inte `/src/*.css`. Den tillåter `/assets/office-v2/*` men inte `/assets/characters/<id>/*`. Det gjorde att CSS och sprites kunde ligga på disk men nekas över HTTP. V3.5.2 lägger till en snäv vitlista för de filer som faktiskt behövs. Core's `Cache-Control: no-store`, CSP och `nosniff` behålls.

## Testkontrakt

Backend: inga nya AI-anrop vid menyöppning. Stats/skills är spelvärden, inga verifierade modellbetyg. Profilen ändrar inte fasta karaktärsdrag. Befintliga arbetsobjekt och besluts-API lämnas orörda.

Frontend: 1 scrollbar i personalfönstret; mobilen en kortkolumn. Namn/roll/char-ID separeras. Inga dubbla kontorsknappar. Resursen måste svara 200 och `text/css` respektive `image/png` innan den anses grafiskt laddad.

## Nästa iteration

V3.5.3: samma kortlayout för AI-uppdrag, Chefen, beslut och granskning; separera *skriv ett uppdrag* från *se tekniska loggar*. Visualisera en fysisk arbetsstation utan att anta att AI-jobb körs. Ingen omskrivning av personaldata.
