# Pixel Works v0.11.4 – Studio Management / Parallel Workers

## NOW – implementerat
- Personalprofilen skiljer **provider** (Codex/Gemini) från yrkesroll, beteende och stationsbehörighet. Gemini står som otillgänglig/”sjukskriven” även om nyckel sparas.
- Studio Dispatch föreslår flera olika behöriga agenter vid väntande arbetsorder (när isolerad drift är redo). Företräde ges till vanliga arbetare; ledaren kan rycka in om ingen sådan är ledig.
- Opt-in autoarbete i aktiv webbläsarflik startar flera Codex-jobb mot separata Git-worktrees när `work/` är ren och har commit. Nytt arbete initieras periodiskt; existerande backend-säkerhetskontroller tillämpas.
- Varje isolerat Codex-jobb får en egen arbetsyta under `management/worktrees/job-<id>` och branch `pixelworks/job-<id>`, med Game Bible som textkontext. Färdiga jobb markeras `review`. **Ingen automatisk merge eller radering.**
- Gemini-nyckel kan sparas via AI-motorer-vyn till `~/.pixelworks/secrets/gemini.key` med filrättighet 0600. Ingen API-körning, gratisstatus eller extern kvot påstås.

## NEXT – viktigt
- Granskningsvy: faktisk diff, tester, konflikter och godkänd integrering i spelprojektets work/.
- Serverägd persistent scheduler, säkert parallellt jobbtak, arbetsledarens granskning av resultat och omdelegering.
- Gemini-provider-adapter som genomför godkända, budgetbegränsade read-only-jobb, med kvot-/rate-limit-policy.

## LATER
- Creative Director med förslag Ja/Nej/Berätta mer/Vänta; självständig QA-/designer-loop; specialiserade stationsgränssnitt.

## Säkerhetsgränser
- Samtidighet är inte samma fysiska mapp: parallella processer skriver i **olika** Git-worktrees i **samma logiska Pixel Works-projekt**. Detta förhindrar direkta filkollisioner men kräver efterföljande integration.
- För att aktivera isolerat läge krävs Git, lokal commit på `work/`, ren arbetskopia, projektmandat och ett uttryckligt klick på Autoarbete. Utan dessa spärras parallell körning.
- En webbläsarflik måste vara öppen för att nya jobb ska schemaläggas. Pågående processer fortsätter i backend.
