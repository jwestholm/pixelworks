# Pixel Works v0.13.1 – Kontorsfolkmängd och överlappande figurer

**Installationsbas:** Pixel Works v0.13.0. Packa upp ZIP-filen ovanpå befintlig installation. Starta som vanligt med `python3 backend/server.py` och uppdatera Firefox med `Ctrl+Shift+R`.

## Varför figurerna staplades

I v0.13.0 hämtas personal från alla historiska spel. Den nya `drawScene()` lade till **en extra avatar per person från andra projekt**, upp till 35 stycken, med identiska bordsankare och endast ett fåtal pixlars förskjutning. Därför staplades namnskyltar och kantiga figurer vid chefsbordet och fikarummet. Arbetsborden och projekttillgångarna har **inte** slagits ihop; felet gäller deras visualisering.

Gamla projekt skapade automatiskt egna startteam. Inventeringen kan därför visa t.ex. 28 **personalposter** från 11 spel, även om flera heter Gunnar, Greta eller Chefen. Dessa är separata äldre poster, inte 28 nyanställda i ett välorganiserat rum. Inga data rensas eller sammanfogas vid uppdateringen.

## Ändrat

- Före aktivering av delad personal: personer från andra gamla projekt syns **bara i Min studio**, inte som om de redan satt i samma rum.
- Efter aktivering: högst **en representant** från ett annat projekt per ledig station. På redan upptagna bord visas bara en **klickbar gruppknapp** för övriga kollegor.
- Flera personer vid samma plats bildar en räknare, till exempel `☕ 12 kollegor`. Räknaren öppnar personalöversikten.
- Namnskyltar i kontoret visar bara medarbetarens **namn**, inte projektets fullständiga namn. Projekt och roll finns som titel/åtkomsttext samt i Min studio.
- Förklarande text säger nu **personalposter** i stället för att antyda att gamla projektteam redan är sammanslagna. Kontoret ritar inget förrän opt-in.
- Pollningen har samma projektfokus och använder ingen AI; arbetare flyttas inte och speldata ändras inte.

## Begränsningar

Det här är en **renderingsfix**, inte en automatisk migrering till ett kanoniskt företagsregister. Befintliga projekt fortsätter använda sina personalfiler tills du aktivt flyttar personal via `Min studio`. Det är möjligt att flera gamla personer har samma namn. Riktiga AI-arbeten, arbetsköer, Game Bible, filer och projekttilldelning påverkas inte av denna patch. En senare version behöver en genomarbetad onboarding för att välja vilka gamla startteam man faktiskt vill behålla och en gemensam scheduler.

## Testning

- Chromium-funktionstest: före/efter aktivering, projektbyte, personlig omplacering, upptagen arbetare samt stresstest med 28 simulerade personalposter fördelade på samma två arbetsbord.
- 11 befintliga backendtester för 0.13 passerade med ändrad versionsangivelse.
- JavaScript- och Python-syntax kontrollerade.
- Verkliga Firefox och dina lokala projektfiler har **inte** ändrats eller testats.

## Filer

- `src/pw-v013.js`: ny begränsad kontorsrendering och tydligare UX.
- `backend/pw_v013.py`: versionsangivelse `0.13.1`, ingen backendlogik ändrad.
- `test_browser_v0131.py`: nytt Chromium-regressionstest.
- Dokumentation och manifest.

**Återställning:** återställ föregående `src/pw-v013.js` och `backend/pw_v013.py` från 0.13.0 om så önskas; inga bestående datamigreringar utförs av patchen.
