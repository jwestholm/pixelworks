# Pixel Works v2.5 – Första säkra steget till EN global personalstyrka

**Git-bas:** `jwestholm/pixelworks` `dev` på `fb70d1c9a927e07e802537c83705db5b8f9876cd` (kontrollerad 2026-10-30). **Installera ovanpå v2.4.** Ingen GitHub-push. Inga riktiga Codex-/Gemini-anrop i testerna.

## Beslutet: avskeda inte de andra automatiskt

Inspelningen 2026-10-30 10:10:38 visar fem projekt och femton anställningsposter. Tre poster visas med Hackertoolkit-filtret. Dessa poster är **inte säkert femton unika verkliga personer**, men varje historisk post ska behandlas som en egen identitet tills ägaren beslutar annat. Matchning på bara namnet (t.ex. Gunnar) är förbjuden. Att behålla endast Hackertoolkits tre poster innan migrering kan göra historiska hjälpärenden och kopplingar svårare att förstå, och gör inte personalen global.

## Installation

1. Kontrollera att **v2.4** finns installerad (framför allt `src/pw-studio-roster-v24.js`).
2. Packa upp denna ZIP direkt i projektroten, skriv över `backend/server.py` och `src/main.js`. Nya filer: `backend/pw_global_staff_v25.py`, `src/pw-global-staff-v25.js`, testfiler och denna README.
3. **Starta om servern**, t.ex. `python3 backend/server.py stop` och därefter `bash start-lan.sh` (eller ditt vanliga serverkommando). Uppdatera både Firefox och telefonens webbläsare.
4. Gå till **Min studio**. Panelen **Konvertera till en global personalstyrka** visar antalet poster. Välj **Granska och skapa personregister** och kontrollera **namn + ursprungsprojekt + fullständigt studio-ID** innan du klickar **Skapa register med säkerhetskopia**.
5. Det är helt okej att **inte klicka på konverteringen**. Alla läsanrop är skrivfria och inga personer avskedas/byter spel av sig själva.

## Vad händer vid konvertering?

Med explicit klick skapas `~/.pixelworks/studio-v013/PEOPLE_V25.json` (motsvarande under din `PIXEL_WORKS_HOME` om den är anpassad). Varje post har stabilt `studio_id`, ursprungsprojekt, ursprungligt projekt-agent-ID och en lista med alias för kommande migrering. `Gunnar @ Hackertoolkit` och `Gunnar @ Skjutbanan` blir **olika poster**.

Före registerfilen skapas en lokal säkerhetskopia under `~/.pixelworks/studio-v013/staff-backups-v25/<timestamp>-<id>/` av alla befintliga `management/STAFF.json`, `SKILL_SETTINGS.json` och `STATION_ASSIGNMENTS.json` som finns. Ett MANIFEST med SHA-256-kontrollsummor sparas. Inga ursprungliga personalfiler, arbetsordrar, rapporter, Game Bible eller spelets kod ändras.

Vid ett andra godkännande är konverteringen idempotent: inga personer skapas dubbelt. Om personallistan hinner ändras mellan förhandsgranskning och klick stoppas operationen och kräver ny granskning. Vid kolliderande ID:n stoppas migreringen. En partiell säkerhetskopia kan ligga kvar om skrivningen avbryts, men projektfiler rörs inte.

## Vad gör v2.5 *inte* ännu?

**VIKTIGT:** v2.5 är en säker **identitetsmigrering**, inte en färdig övergång av exekveringssystemet. Serverns arbetsmotor (`dispatch_plan`, `staff_read`, `move_staff`, Codex/Gemini-schemaläggare, projektjobb) använder fortfarande projektlokal `STAFF.json` via sin kompatibilitetsadapter. Projektens data förblir separata. `Min studio` listar redan alla aktiva poster över projektgränser. En person tilldelas i nuläget ett projekt åt gången. Att byta **visat projekt** avskedar eller anställer ingen, men påverkar vilket projekts uppdrag som syns i kontoret.

**Radera inte** gamla `STAFF.json` eller manuellt flytta personal-ID:n. Avskedning är fortfarande ett explicit val, och tidigare arbete ska kunna hittas via arkiv. Om du avskedar någon före nästa steg är gamla rapporter fortfarande kvar, men äldre UI kan visa en försvunnen agent.

Om personal flyttas/anställs/avskedas **efter** konverteringen visar kontrollpanelen en varning om att registret och projektadaptrarna behöver synkas i nästa steg. Inget döljs eller skrivs över automatiskt.

## Test – vad är verifierat?

- 8 Python-enhetstester med fiktiva projekt: läsning utan skrivning, två personer med identiskt namn, exakta säkerhetskopior, uttryckligt godkännande, kontroll av förändrad personallista, idempotens, projekttilldelning som behåller studio-ID och kollisionsstopp.
- Chromium-test med fiktiv backend på desktop **och mobil**: ingen POST vid visning eller avbryt, fullständiga identiteter i bekräftelse, exakt en godkänd konvertering och att v2.4-personalkort finns kvar.
- `node --check` på frontendfiler samt `python -m py_compile` på backend.
- **Inte verifierat:** mot användarens faktiska Ubuntu-installation, riktiga femton anställda, faktisk LAN-session eller riktiga AI-jobb. Testerna gör inga externa AI-anrop och skriver inget i användarens spel.

## NOW / NEXT / LATER

**NOW (v2.5):** Central fil med identiteter, alias till gamla projekt-ID:n, backup, förhandsgranskning och bekräftad migrering. Inga avsked eller riskabla skrivningar under uppstart.

**NEXT (v2.6):** Gör **globala personalregistret till faktisk källa** för rekrytering, avsked, profil, skills, chefens uppdragstilldelning och synliga medarbetare i samtliga projekt; projektens personalregister blir *tillfälliga projektioner* från detta. Migrera rapport-, hjälp-, beslut- och fikarumsreferenser till `studio_id` med ursprungsprojekt och `agent_id`. Avbrotts- och rollbacktest med verklig anonymiserad kopia.

**NEXT:** En studiopanel som visar alla projekts produktionslägen och låter ägaren pausa andra projekt utan att avskeda någon. Flerklientssynk med revisionsnummer för beslut och arbetsorder.

**LATER (efter lyckad skarp verifiering):** Ta bort gamla projektlokala personal-UI:n och avveckla `STAFF.json` som primär källa. Historiska filer och identifieringsalias bevaras för spårbarhet. Ägaren väljer manuellt vilka extra personer som ska avskedas eller slås ihop efter en identitetskontroll. **Inga automatiska personalavsked eller namnbaserade sammanslagningar**.
