# CURRENT STATE – tillägg 2026-10-23, v0.12.11.17

Projektets senaste levererade gränssnittspatch är `v0.12.11.17`, ovanpå `v0.12.11.16`.
Startkommando `python3 backend/server.py` från Pixel Works lokala Git-arbetskopia. Inga extra installationsskript.

**Implementerat lokalt (inte verifierat i användarens Firefox):** stabilt projektval på nytt spel; engångsåtkomstens befintliga serverbeslut med ny tydlig knapp; arbetsbeslutsöversikt; 10 fullständiga stationsnamn och dynamiska hovertexter; spelstart-introduktion; mänskliga förvalsnamn på nya medarbetare.

**Verifierat offline:** 3 nya backendtester, 33 riktade backendtester totalt, ett Chromium-simuleringstest. Ingen verklig extern AI-körning gjord.

**Återstår:** helt enhetlig transaktionell arbetskö; övriga äldre kodrevisionens kvarvarande 8 testmisslyckanden och 19 testfel; direkta granskningsknappar för alla äldre rapporttyper. Fullständig funktion i användarens Firefox och verkliga AI-motorer kräver separat test.

**Säkerhet:** ingen ny skrivrätt automatisk; befintligt studiosamtycke är revokerbart. Ingen push/merge till GitHub. Inga projektfiler eller API-nycklar i delta-ZIP.
