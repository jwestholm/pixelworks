# CURRENT STATE – 0.13.3

Pixel Works 0.13.3 utökar 0.13.2 utan att migrera befintliga spelprojekt.

- En Chefen-session vid Arbetsledning kan nu leverera maskinläsbar plan som skapar verkliga arbetsorder (1–8), med personförslag och beroenden.
- Order ligger i respektive projekts `management/WORK_ORDERS.json` och körs av existerande schema/API med extra servrarvalidering av beroenden/ansvarig.
- Äldre chefsrapporter kan väljas i den nya produktionsöversikten och skickas som underlag för ett nytt arbetsplaneringsuppdrag.
- Säkra arbetsytor, Codex-read-only för Chefen, Gemini-kvoter, Game Bible och faktiska utförarjobb är oförändrade.
- Verifierat med offline Python- och Chromium-tester. Äkta AI-anrop har inte körts; äldre fullsvit är fortfarande inte grön.
