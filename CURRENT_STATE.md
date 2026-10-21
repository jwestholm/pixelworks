# Aktuellt läge: Pixel Works v0.11.6.1

- Isolerade Codex-arbetare kör i egna Git-worktrees under samma lokala spelprojekt.
- Efter ett lyckat Codex-jobb försöker backend integrera resultatet direkt i `work/` när det är en säker fast-forward. Ingen användarlapp behövs.
- Om arbetsgrenen skiljer sig från huvudprojektets historia och en arbetsledare är aktiv vid chefsbordet görs en vanlig automatisk **konfliktfri** Git-merge. Vid konflikt avbryts sammanfogningen.
- Blockeringar skapar en kvarvarande granskningsrapport på användarens skrivbord. Lyckade integrationer dokumenteras men arkiveras tyst.
- Vid serverstart sker en engångsgenomgång av äldre granskningsrapporter med kvarvarande worktree, aktivt mandat och utan pågående jobb.
- Rapporten från Codex är inte oberoende speltestad. Merge-framgång betyder inte funktionellt godkänd kod.
- Tester: 117 backendtester OK; JS-syntax OK. Inga riktiga Codex-körningar eller Firefox-test genomförda.
