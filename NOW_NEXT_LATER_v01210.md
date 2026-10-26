# Pixel Works – NOW / NEXT / LATER efter v0.12.10.1

## NOW – kodad testkandidat
- Fysiska dubblerade Projektstatus-/DEMO-tavlan är borttagen från kontoret; riktiga Uppdrag-menyn finns kvar.
- Gemini-API-nyckel visas som sparad efter uppdaterat statusfält.
- Valfri arbetsledarstyrd Gemini-delegering, per projekt med uttryckligt godkännande, gemensam arbetsorderkö och ordinarie rapportpärm.
- Gemini får bara docs/research/meeting och producerar granskningsförslag, inte implementerad kod eller verifierade Game Bible-sidor.
- Lokalt tak på 1–12 anrop per kvotdygn, en åt gången, minst 30 sekunders mellanrum; paus vid fel, ingen retry, verklig kvot okänd.
- Arbetsbilagor till Codex-worktrees fortsatt utanför Game Bible.

## NEXT – måste prioriteras
- **En normal startväg:** integrera tillägg direkt i vanliga `backend/server.py`; versionstal ska inte ligga i startfilens namn. Ingen installationspatch, bara filer att ersätta.
- Testa riktiga Gemini Free Tier-nyckeln, `429`, riktiga väntande ordrar, normala rapporter och återstart av servern i Firefox på Ubuntu.
- Låt Gemini föreslå nästa steg och chefen skapa/utvärdera uppföljningsordrar, men endast inom användarens mandat.
- Genomgång av synlig chefstatus och gamla "Gemini sjukskriven"-texter i modalfönstren.
- Menystädning/DEMO-text; diskutera nyttan innan fler knappar tas bort.
- Låt vanliga arbetsordrar använda nya arbetsbilagor; testa bildläsning i verklig Codex CLI.

## LATER
- Ytterligare fria motorer via leverantörsoberoende adaptrar, utan gissade kvoter.
- Säker och spårbar uppföljning av agentrapporter, förslag, tester och användarbeslut.
- Mer levande spelstudio, tio personliga skrivbord, fler animationer och karaktärsroller.
