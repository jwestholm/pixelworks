# Pixel Works v0.12.11.8 – Överlämning och namnskyltar

Bas: v0.12.11.7. Packa upp deltafilernas relativa sökvägar i samma projektmapp. Inga befintliga projekt, API-nycklar eller Game Bible-filer ändras av installationen. Starta som vanligt: `python3 backend/server.py`, uppdatera Firefox med Ctrl+Shift+R.

- Tidigare version byggde vidaredelegeringen på max 2 600 tecken ur förslaget. Nu hämtar den startade programmerarens arbetspass **hela ursprungliga godkända rapporten**, men bara om arbetsordern verkligen är kopplad till denna godkända överlämning.
- Nuvarande Game Bible följer med som referens i samma arbetspass; programmeraren får uttryckligen veta vilket förslag användaren godkänt. Gamla AI-rapporter betraktas som referensdata, inte direktiv att ändra externa filer.
- Programmeraren instrueras att särredovisa faktiska filändringar och tester, och att inte påstå att en ny funktion implementerats när inga filer har ändrats. Detta är en bättre instruktion, **inte** en oberoende kodverifikation.
- Namnskyltarna synkroniseras med personalregistret och fästs visuellt över den egna figuren, för att undvika att närstående etiketter i fikarummet uppfattas som den andra personens namn.

**Viktigt:** Tidigare genomförda och rapporterade implementationer återställs inte eller körs om. Patchen gäller nya programmerarpass som tar emot vidarebefordrade förslag. Rapporthistoriken lämnas orörd.

Ingen GitHub-push, ingen ny AI-anropstestning, inga installationsskript. Testad: 5 isolerade handoff-tester, syntaxkontroll för Python och JavaScript. Riktig körning i användarens Firefox/Codex-miljö är inte verifierad.
