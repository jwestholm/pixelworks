# NOW / NEXT / LATER – v0.12.11.18

## NOW – implementerat och offline-testat

- Ljus station-specifik uppdragsdialog med egen Grafikstudio-illustration.
- `Eget uppdrag` som första val på alla åtta arbetsstationer; relevanta kategorier och underkategorier.
- Tre prioritetsknappar, Normal förvalt; textfält; uppladdning; tidigare referenser.
- Verklig serverlagrad arbetsorder via befintligt API efter uttryckligt knapptryck.
- Mötesrummets NPC-katt med **lokal** femstegsplan som förhandsgranskning.
- Ingen projektväxling eller externa AI-anrop från fönstrens visning.

## NEXT – kärnan i arbetsledarens samarbete

1. Gör en gemensam, serverlagrad arbetsplansmotor (`plan_id`, `phase`, `depends_on`, `role/skills`, `approval_state`) med transaktionell idempotent skapning.
2. Låt arbetsledaren, med spelägarens godkännande, använda valbar faktisk AI-motor för att **föreslå** en plan utifrån Game Bible, tillgängliga yrken och projektets mål. Modellens text behandlas som förslag, inte som en order att kringgå behörigheter.
3. Visa en granskbar plan med redigerbar ordning/ansvar, och kör endast deluppdrag vars beroenden är uppfyllda. Tydlig överlämning efter godkänd grafik till kod, efter implementation till QA, efter godkännande till Game Bible.
4. Skapa unika illustrationsbakgrunder för övriga sju skrivbord samt gör QA:s buggformulär mer specifikt med reproduktionssteg/förväntat/utfall.
5. Testa hela arbetsflödet mot originalmotorn, olika projektnamn och verkliga Codex/Gemini-kopplingar utan att riskera källfiler.

## LATER

- Visuella beroendelinjer mellan arbetsstationer i kontorsvyn.
- Flera deltagare i möten, arbetsledarens kvalitetssäkring och automatiskt genererade QA-testfall.
- Studie-/ljudreferenser och egna framtida AI-adaptrar i samma spelmekanik.
