# Pixel Works v0.12.11.7 – ork och Game Bible-redaktör

**Utgår från v0.12.11.6.** Endast dessa filer läggs till eller ersätts:

- `backend/pw_v01210.py` – laddar v0.12.11.7-modulen, versionstext.
- `backend/pw_v012115.py` – hindrar den gamla 'klistra in text i kapitel'-funktionen och laddar nytt gränssnitt.
- `backend/pw_v012117.py` – AI-assisterad kapitelsammanfogning med förhandsgranskning och historik.
- `src/pw-v012117.js` – spelork på figurer, studiostatistik och kapitelgranskning.
- `backend/test_pw_v012117.py` – offline-tester.

Ingen installationsfil. Ingen `server_v...py`. Starta som vanligt med `python3 backend/server.py`.

## Så fungerar Game Bible

Välj **Godkänn förslaget** för en rapport från den kreativa medarbetaren. Modellen får **det aktuella kapitlets hela text (upp till 18 000 tecken) + det godkända förslaget (upp till 9 500 tecken)** och skapar ett nytt komplett kapitel. Det räknas som **ett verkligt Gemini-anrop** och förbrukar kvot. Ingen automatisk retry och inget automatiskt modellbyte. Användaren får läsa både den tidigare sidan och det nya utkastet, därefter **Inför kapitlet** eller **Avbryt**. Fram till andra klicket ändras inte boken. Vid införandet sparas föregående version i `management/bible-history/`. Om kapitlet ändrats efter genereringen stoppas införandet; ingenting skrivs över. Ursprunglig skrivskyddad Game Bible ändras inte.

Viktigt: AI:s version måste fortfarande **granskas av användaren**; modellen kan missa eller feltolka befintliga formuleringar. Om Gemini-anropet misslyckas finns inga sidoeffekter på kapitlet. Ett ännu ej införlivat förslag visas fortsatt som väntande.

## Spelork och statistik

Ork visas som en liten färgad bar över personen vid hover och när den blir låg. Den ändras av verkligt observerade aktiva jobb och simulerad återhämtning, men **påverkar ännu inte AI-motorns kvot**. En ledig anställd med mycket låg ork går till fikarummet om förflyttningen tillåts. Värdet hålls i webbläsarsessionen och är inte beständigt över omladdning. Det är medvetet inte märkt som verklig hälsa.

**Studiostatistik** ligger överst i aktivitetsloggen som en expanderbar panel. Den visar aktiva arbetare, spelork per person och rapporterade token från serverns senaste jobb. Alla externa återstående leverantörskvoter visas som **Okänt** eftersom de inte är tillgängliga från denna endpoint. Token-summan gäller inte hela kontot eller tidigare serversessioner.

## Teststatus

- 4 specifika offline-regressionstester: gröna.
- 60 befintliga tester på 0.12.11.6: gröna (körda mot den tidigare versionens oförändrade testsystem).
- Python-syntax och JavaScript-syntax kontrollerade.
- Ej verifierat mot ditt verkliga Google-konto eller lokala Firefox. API-anrop startar **enbart** efter ditt klick för att förbereda kapitelutkastet.

## Kvarstående

- Persistenta orknivåer och en riktig kaffepaus-animation knuten till spelets simulerade dygn.
- Separat leverantörsspecifik kvottelemetri för Gemini och Codex när den är verifierbart tillgänglig.
- Valbar manuell redigering av AI:s hela kapitelförslag före införande.
