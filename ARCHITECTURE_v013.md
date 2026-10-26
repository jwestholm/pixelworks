# Pixel Works 0.13 – övergångsarkitektur till en studio

```text
                       PIXEL WORKS STUDIO
                ┌──────────────────────────┐
                │ En gemensam kontorsvy     │
                │ Anställda från alla spel  │
                │ Stable studio_id per person
                └────────────┬─────────────┘
                             │ explicit manuell tilldelning
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
   Projekt A            Projekt B           Projekt C
   STAFF.json           STAFF.json          STAFF.json
   Game Bible A         Game Bible B        Game Bible C
   work/Git A           work/Git B          work/Git C
   Rapporter A          Rapporter B         Rapporter C
```

`studio_id` är ett stabilt identifierarelement som kan härledas från `original_project_id` och `agent_id` (eller läsas från överflyttad post). Den **aktuella anställningsposten** ligger fortfarande i exakt ett projekt. Vid flytt bevaras `studio_id`, men projektlokalt `agent_id` kan behöva nycklas om om ett äldre kort-ID krockar med befintlig personal.

Detta är fas **virtuell gemensam studio + kontrollerad flytt**. Den fullständiga datamigreringen av arbetsköer och automatiska schemaläggare till ett globalt kanoniskt personalregister är en separat nästa fas. Inga historiska rapporter eller spelprojekt raderas eller flyttas.

## API

- `GET /api/pw-v013/studio` – läs projekt/personlista och pågående jobbsstatus; ingen skrivning.
- `POST /api/pw-v013/studio/enable` med `{ "approval": "ENABLE_SHARED_STUDIO_V013" }` – engångsaktivering för gemensam personal.
- `POST /api/pw-v013/studio/transfer` med `{ "studio_id": "pw-...", "target_project": "...", "approval": "ASSIGN_STUDIO_EMPLOYEE_V013" }` – flyttar endast en ledig personalpost efter val i GUI.
- `POST /api/pw-v013/studio/repair` med `{ "approval": "RESTORE_STUDIO_TRANSFER_V013" }` – explicit rollback av ofullständig journal, endast om inga berörda jobb är aktiva.

POST-rutterna kräver lokal autentiseringstoken, giltigt Host/Origin och JSON-schemakontroller. Själva projektets `staff.json` följer befintligt schemakontrakt. Backend lagrar inga API-hemligheter i den nya studiorapporten.

## Kommande invariants (ej fullt verifierade i v0.13)

En enskild medarbetare får inte ha två samtidiga exekveringar om dess adapter inte stödjer det. Alla nya arbetsorder behöver explicit `project_id` och globalt `studio_employee_id`. Jobbclaim måste ske atomärt, och gamla projektschemaläggare måste kunna stängas av innan den nya globala motorn aktiveras.
