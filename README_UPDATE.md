# v0.11.5.0 – Chefens kontor

## Spelregeln

- **Arbetsledare vid chefsbordet:** lokalservern söker nya order ungefär var fjärde sekund och delegerar till en ledig behörig Codex-arbetare, med stationens skillnivå som högsta urvalskriterium. Kan själv utföra arbetet om ingen annan får göra det.
- **Arbetsledare i fika:** nya order delegeras inte automatiskt. Pågående Codex-uppdrag fortsätter till slut.
- **Utan chef:** dra en anställd manuellt till en station för att starta en väntande order, om projektmandat redan finns.
- **Arbetare efter avslutat uppdrag:** servern flyttar vanliga arbetare till fika och chef tillbaka till chefsbordet.
- **Creative Director / Storywriter:** en yrkesroll som ännu inte har en färdig idégenerator och som inte väljs för utförandeuppdrag.

## Parallell körning

Separata Git-worktrees delar historik och repository men har separata skrivbara mappar. Kräver Git och eget Git-repository i projektets `work/`. Huvudprojektet ändras inte automatiskt. De utförda jobben måste granskas och integreras senare. Verklig Codex-parallellism på användarens maskin behöver verifieras där.

För bakåtkompatibilitet ligger äldre dispatcher-kod kvar internt, men dess startknapp har tagits bort från stationsmenyn.

## v0.11.5.2 – Personal och begrepp
Synliga termer: **yrke** (Programm­erare, QA-testare, Arbetsledare, Creative Director), **station** (Chefsbord, Kodbord, QA-bord, Musikstudio osv.), **kompetenser** (kodning, grafik, testning osv.). Interna stations-ID:n ändras inte. Personallistan har bekräftat **Avskeda**, som avvisar aktiva jobb och bevarar historik. Ingen GitHub-åtgärd.


## v0.11.5.8 – Jobblistans routning
GET `/api/projects/<slug>/jobs` behandlas nu **före** generisk projektverifiering; förr misstolkades `jobs` som projektets slug och gav felaktigt "Projektkatalogen saknas eller är osäker". Ingen projektdata eller Git-historik har ändrats. Separat problem med eventuellt stillastående dispatch återstår att verifiera på riktig dator.

## v0.11.6.0
- Uppdragstavlan visar verkliga arbetsorder, personal och pågående serverjobb för aktiva projekt i stället för tomma DEMO-värden.
- Nya projekt utan index.html får ett förklarande preview-läge i stället för missvisande arbetsmappfel.
- Auto-delegering kräver en arbetsledare vid chefsbordet i just det valda projektet; det skapas inte automatiskt någon chef.
