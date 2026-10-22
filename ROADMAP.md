# Uppdatering 2026-10-22 – v0.11.8.4

## UI-regel: Inga tekniska åtgärder krävs av spelaren
- [x] Klick på en arbetare med aktiv ❗-bubbla öppnar en hjälpdialog med begriplig förklaring och ursprungligt uppdrag.
- [x] Spelaren kan låta studion försöka lösa felet, skriva egna önskemål eller vänta. Åtgärder köas som vanliga arbetsorder, utan konsol och utan tvångsintegration.
- [x] En säker integrationsomprövning görs innan en konflikt leder till nytt arbetspass. Verkliga konflikter skapar ett separat nytt arbete på aktuell spelversion, aldrig blind överskrivning.
- [x] Tekniska detaljer är frivilliga i en expanderbar sektion.
- [ ] Egna Pixel Works-dialoger i alla gamla flöden som ännu använder alert/confirm/prompt.
- [ ] Serverstyrd automatisk, testad konfliktlösning utan onödiga användarfrågor och med begränsad retry-policy.
- [ ] Browserbaserade funktionstester av dragningsbeteende, bubbla, dialog och felrapportering i Firefox.
- [ ] Permanent arbetsmotor, integrationstest för körbart spel och beständig återhämtning efter omstart.

# Uppdatering 2026-10-22 – v0.11.8.3

**NOW:** Säker återhämtning av gamla rapporter, live-loggens senaste händelser, samtidiga rapportknappar, korrigerade hjälpstatusar och sanningsenliga avslutsmeddelanden – levererat och testat lokalt.

**NEXT:** Beständig arbetsmotor/jobbjournal, transaktioner för ordertilldelning, kontroll av levande processer efter serveromstart, säkra preview-tester och incidenthantering.

**LATER:** Game Bible med rika sidor och AI-redaktion, fikarum/inspiration, XP/levels, modellunderbyggda kandidater.

---

# Roadmap – Pixel Works

## NOW
- v0.11.2: Servervaliderad arbetsfördelningsplan + explicit, webbläsarstyrt opt-in-autoarbete.
- Roll/behörighetsprofiler och exklusiva stationer matchas mot verkliga väntande arbetsorder.

## NEXT
- Serverstyrd beständig scheduler: atomiska reservationer, återskapad status vid omstart, administrativ paus och ansvarsfull körning utan flik.
- Gemensam personal- och köstatus, särskilda yrkessprites, tydlig indikator på pausat automatläge.
- Separata Git-worktrees för verkligt parallella Codex-processer och kontrollerad sammanfogning.

## LATER
- MCP-verktyg för riktig Codex-arbetsledare att delegera och granska; leverantörsadaptrar för andra modeller.

### v0.11.3
NOW: Codex-arbetsledare för läsbaserade planförslag med separat mänskligt godkännande, tydligare autoarbetsstatus.
NEXT: permanent backend-scheduler och separata arbetsytor för parallella Codex-agenter; verifierad agentanimation.
LATER: Gemini-adapter med konfigurerbara kostnads-/takregler och kontoverifierade kvoter; specialiserade stationer.

### Framtida rekrytering och utveckling (TODO, inte implementerat)
- Kandidatbläddring inspirerad av Game Dev Story / Pizza Tycoon: porträtt, namn, yrke, persona, AI-motor och styrkor/svagheter innan anställning.
- Färdiga rekryteringsprofiler, persona-arketyper och tydligt anpassningsbara anställningsvillkor.
- Utvecklingsbara skills med verklighetsbaserade modellbetyg: samla publicerade benchmarks (t.ex. SWE-bench och kod-/resonemangsutvärderingar), dokumentera exakt modellversion, källa, datum, metod och osäkerhet. Ej verifierad förmåga märks ”ej utvärderad”, aldrig fabricerat värde. Agentens individuella specialisering och verifierade egna arbetsresultat visas separat.
- Skillprofil och vald AI-provider ska vara oberoende; modellen begränsar möjligheter, pris och kvoter, medan spelskill styr hur arbetsledaren prioriterar.

### v0.11.5.1 – personalprofil (genomförd)
- Spara-knappar högst upp och längst ned; profil direkt från agentkort; färre redundanta fält.
- Anställd som styr förvalda stationer och kompetenser, manuella justeringar möjliga.
- Framtida kandidatbläddring och modellranking enligt källbelagda tester är TODO.

## Personalordlista (v0.11.5.2)
- **Yrke** = anställd som (Programmerare, Arbetsledare, QA-testare, Creative Director).
- **Station** = fysisk plats (Chefsbord, Kodbord, Musikstudio, QA-bord). Interna stationsnycklar behålls för bakåtkompatibilitet.
- **Kompetenser** = skills; kan justeras individuellt, ska senare påverkas av verifierad AI-modellförmåga.
- **NEXT:** rekryteringskandidater med verifierade AI-utvärderingar och personas; historik om avsked och starkare persistent jobblåsning.

## v0.11.6.1 – Integration utan Git-dialoger

**NOW:** Isolerade Codex-resultat integreras direkt vid ren fast-forward; aktiv arbetsledare får godkänna en konfliktfri divergerande Git-sammanfogning automatiskt. Vid faktisk konflikt eller blockerad integration lämnas en rapport på ägarens skrivbord; lyckade integrationer arkiveras tyst. Äldre färdiga worktrees kontrolleras en gång per serverstart under projektmandat.

**NEXT:** Oberoende speltest före/efter integration och automatiska återställningspunkter med tydlig UI-förhandsvisning; arbetsledaren kan begära korrigerat resultat av arbetaren.

**LATER:** Säkert semantiskt konfliktstöd med testade korrigeringsförslag, förslag från Creative Director och verifierade modellbetyg i rekrytering.

## NEXT/LATER – Fikabord och omvärldsbevakning
- Fikabordet som frivillig inspirationsstation: spelbranschrykten, genrenyheter, roliga klipp, trender och förslag på spelinnehåll.
- Verkliga webbuppgifter ska ha källa och datum. Inga automatiska externa anrop utan användarens godkännande; idéer skapar inte kodjobb utan godkännande.
- Fikabordet ska även fortsätta fungera som manuell paus från arbete och kreativitet.

## v0.11.6.5 – riktad integrationsfix (2026-10-21)
- [x] Automatisk lokal sammanfogning av konfliktfria parallella resultat, utan chefsberoende.
- [x] Känn igen redan införda, identiska filer.
- [x] Rättad hänvisning till Game Bible för nya projekt + instruktion för äldre worktrees.
- [x] Skilj Codex eget påstående från faktiskt integrerad status i samtal.
- [ ] Lösa verkliga konflikter genom kontrollerad arbetsledargranskning och automatiska tester.


## v0.11.7.1 — Game Bible som central designkälla (2026-10-22)
- NOW: Codex-uppdrag och planeraren använder originalsida och redigerbara kapitel. Efter lyckad integration läggs verifierat nyinnehåll till utan att AI kan skriva över visionen.
- NEXT: Förslag på stora designändringar till ägaren, synliga sidnotiser; förbättrad bild-/matrisredigering och agenternas designmöte.
- LATER: Redaktionell versionering, strukturerade relationer, spårbar källa för varje faktapåstående och konflikthantering mellan agentskrivna bokposter.


## v0.11.8.0: Projektborttagning och stabiliseringsspår
Två bekräftelser för projektborttagning, lokal papperskorg, skydd mot samtidiga jobb. Kommande prioritet: enda källa för jobb/rapporter/notiser samt end-to-end-verify av preview. Se `CURRENT_STATE.md` och `TEST_REPORT.md`.

## UI-beslut och fortsatta stabilitetsfixar (2026-10-22)
- [ ] Ersätt webbläsarens `alert`, `confirm` och `prompt` med egna Pixel Works-modaler, i synnerhet för projektborttagning och andra viktiga beslut. Dessa dialoger kan blockeras eller döljas av webbläsaren. Säkerhetskontroller på servern behålls.
- [x] Skapa rapport innan ett färdigt jobb får ändra arbetsorderns synliga status.
- [x] Koppla arbetsorder till rätt sessions-ID och hindra gammalt jobb från att skriva över en nyare tilldelning.
- [ ] Återhämtning av ej kvitterade jobb/rapporter efter serveromstart och persistent schemaläggning.
- [ ] Fullständigt end-to-end-test med verklig Codex CLI och webbläsarpreview.
