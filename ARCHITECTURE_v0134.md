# Arkitektur v0.13.4 – planutkast och startprototyp

## Projektstart
`POST /api/projects` (befintlig session/mandatkontroll) → ursprunglig `create_project` → befintlig Game Bible/metadata/staff → `pw_v0134.bootstrap` skriver endast **nya** `work/index.html`, `work/style.css`, `work/game.js` och Game Bible-prototypavsnitt → lokal Git-baslinje för `work/`.

Gamla projekt läses via `GET /api/pw-v0134/bootstrap?project=<slug>` (endast läsning). En explicit `POST /api/pw-v0134/bootstrap` med `{project,approval:'CREATE_PLAYABLE_START_V0134'}` arbetar enbart om `work/` saknar annat innehåll än AGENTS.md, README.md och .git. Båda endpoints är session-/origin-skyddade enligt lokalserverns befintliga tokens.

## Chefens plan
Codex `read-only` JSON (1–8 steg) → JSON-schema-/DAG-validering i `pw_v0133` → atomiskt sparade arbetsordrar med `source_lead_job`, `depends_on_order_ids` och `plan_review_required=true` vid flera steg. **Ingen exekvering före godkännande**, även om jobbet startas direkt via den befintliga jobbrutten. Gränssnittet hämtar `GET /api/pw-v0133/production` och redigerar med `POST /api/pw-v0133/plan/save`, varefter `POST /api/pw-v0133/plan/release` släpper hela utkastet (samma versionskontroll och validering). Befintliga planer från äldre versioner ändras inte.

## Nya filer
- `backend/pw_v0134.py`: projektstartsmallar, Git-baslinje, valfri säker manuell komplettering i gamla projekt.
- `backend/pw_v0133.py`: planutkast, validering, redigerings- och godkännande-API, status.
- `src/pw-v013.js`: planredigerare, bemanningsgenväg, spelbar startprototypstatus.
- `backend/pw_v013.py`: laddar `pw_v0134` efter `pw_v0133`.

## Gränser
- Inga riktiga AI-anrop vid projektstart, vid kontroll av personal eller vid redigering av utkast.
- Ingen automatisk uppladdning, extern publicering eller ny betalmodell.
- Ingen ändring av redan befintlig spelkod.
- Delad studio är fortfarande först en översikt och säker personalförflyttning; fullständig gemensam arbetsmotor är framtida arbete.
