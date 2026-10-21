# Pixel Works v0.11.6.1 – Testprotokoll

## Genomfört

- `python -m unittest discover -s backend -p 'test_*.py' -q`: **117 tester OK**.
- `node --check local.js`: **OK**.
- `python -m py_compile backend/server.py`: **OK**.
- Fyra nya integrationstester med verkliga lokala Git-repositoryn och worktrees:
  1. Okomplicerad agentändring förs in med fast-forward utan arbetsledare.
  2. Två arbetsytor som ändrar olika filer: en senare ändring kräver aktiv arbetsledare och går sedan att sammanföra utan filkonflikt.
  3. Två arbetsytor som ändrar samma rad: säkerhetsstopp, befintlig spelkod bevaras och påbörjad Git-merge avbryts.
  4. Äldre färdig rapport återhämtas vid serverstart och arkiveras tyst efter säker integration.
- Inga autentiserade Codex- eller Gemini-anrop gjorda.

## Inte verifierat

- Riktig Codex CLI-session på användarens Ubuntu.
- Webbläsarspeltest och användarens existerande Minesweeper-arbetsyta.
- Integration av stora eller avancerade Git-konflikter. Dessa avbryts avsiktligt och lämnar en rapport.

## Säkerhet och begränsningar

- Inga GitHub-pushar. Ingen blind kopiering av arbetarfiler.
- Integrationsförsök stoppas vid smutsig huvudarbetskopia, symlänkar och riskabla filnamn.
- En Git-merge utan filkonflikt är **inte** ett bevis på att spelet fungerar: agentens egna testpåståenden är fortfarande overifierade.
- Tidigare rapporter i granskningsläge kan kontrolleras en gång per projekt och serverstart, **endast vid aktivt projektmandat** och när inga jobb körs.
- Vid misslyckad integration ligger rapporten kvar på ägarens skrivbord.
