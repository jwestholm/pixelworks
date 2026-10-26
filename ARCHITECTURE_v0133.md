# Produktionsuppdrag – arkitektur 0.13.3

```text
Spelarens mål / befintlig chefsrapport
               │
         Arbetsledning (Codex read-only)
               │  Maskinläsbart JSON-förslag
       Validering: yrken, stationer, DAG
               │
    Atomic write: WORK_ORDERS.json
               │  1–8 order; ansvarig + depends_on_order_ids
    ┌──────────┼─────────┐
    ▼          ▼         ▼
 Grafik      Ljud      Design       (oberoende steg parallella)
    └──────────┼─────────┘
               ▼
         Programmering
               ▼   [integrerad kod verifieras via rapport]
          Testning
               ▼
         Granskning / Game Bible
```

Chefen redigerar aldrig `work/` under planering. Koden för exekvering och behörigheter är fortsatt den befintliga motorn. `_eligible` spärrar blockerat beroende och fel person, `dispatch_plan` spärrar fel köval och `/api/jobs` är en sista backendkontroll. Gemini-kandidat använder samma personval. Produktionspanelen hämtar read-only status från `/api/pw-v0133/production?project=...`.

**Avgränsning:** Detta är inte ännu en full omskrivning av schemaläggaren. Det är ett kompatibilitetslager som omvandlar Chefens färdiga plan till riktiga projektbundna uppdrag med säker startordning. Projektbundet ansvar kvarstår under 0.13.
