# Pixel Works v0.11.2 – CURRENT STATE

## NOW – implementerat
- **Studio Dispatch**: servern föreslår nästa väntande arbetsorder enligt P1→P3, agentens `work_mode`, `allowed_stations`, hemmabord för specialister samt exklusiva stationsägare.
- Klicka på ett bord → **🤖 Autoarbete** → granska föreslaget jobb → starta med ett uttryckligt klick och bekräftelse. Ett giltigt projektmandat krävs. Autoarbetet fortsätter till nästa väntande arbetsorder efter ett *avslutat* arbetspass, men **pausar vid fel**.
- Studio Dispatch startar aldrig en Codex-process utan användarens aktivering. Läget finns bara i den aktiva webbläsarfliken och återaktiveras aldrig automatiskt vid omstart.
- Backendens befintliga säkerhetsspärr behålls: högst ett skrivande Codex-arbetspass per projekt. Befintliga arbetsorder och Game Bible ändras inte vid installation.
- Manuell agent hämtas aldrig automatiskt. Specialist får bara matchas till hemmabordet. Självständig agent får ta uppdrag vid uttryckligen tillåtna bord.
- Validering för uppdragsstart, agent-ID, arbetsstation, arbetsmandat och bilagor görs fortfarande server-side.

## Viktiga begränsningar
- Dispatch är **webbläsarstyrd efter aktivt godkännande**, inte en beständig central serverscheduler. Stänger användaren fliken startas inga nya arbetspass; ett redan startat Codex-jobb kan fortfarande slutföras av servern.
- Matchning baseras på faktiskt stationsansvar + arbetsbeteende, **inte** simulerade skillstjärnor. Ingen AI-arbetsledare eller MCP-server finns ännu.
- En fungerande Codex CLI-installation behövs för verklig exekvering. Inga Codex-jobb kördes i utvecklingsmiljön.
- Två agenter kan inte samtidigt skriva i samma projektarbetsyta; för parallellitet krävs isolerade Git-worktrees och kontrollerad merge.
- Rekommendationen är en ögonblicksbild; servern återkontrollerar rättigheter vid varje riktig uppdragsstart.

## NEXT
- Central och beständig scheduler med atomär reservation, jobbrecovery och körning oberoende av öppet GUI.
- Samlad live-översikt och pausknapp med tydlig UX; synliga rollkläder och mer levande status.
- Regressionstest i riktig Firefox, inklusive kön och automatisk fortsättning.

## LATER
- Codex som arbetsledare genom säker MCP-adapter, tilldelningsverktyg och rapportgranskning.
- Flera providers, agentisolerade worktrees och granskat integrationsflöde.
