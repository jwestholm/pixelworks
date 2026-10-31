# Pixel Works – Ett kontor, femton figurer (v2.6)

**Bygger på v2.5** och GitHub `dev` vid `fb70d1c9a927e07e802537c83705db5b8f9876cd`. Ingen GitHub-push eller ändring av användarens projekt har utförts.

## Installera

1. Kontrollera att du redan har installerat och **aktiverat personregistret v2.5** i **Min studio**. Det syns som ”Global personalstyrka registrerad”.
2. Packa upp v2.6-ZIP:en i projektroten (`index.html`, `src/`, `backend/`) och skriv över **`src/main.js`**. Lägg till **`src/pw-global-office-v26.js`**. Backend och projektlagring ändras inte.
3. Uppdatera Firefox med **Ctrl+F5**. På telefon: ladda om sidan. Normalt behövs ingen serveromstart eftersom bara webbfiler ändras.
4. Öppna ett skarpt projekt och titta i kontoret. De anställda hämtas från samma serverbaserade studioöversikt, oavsett vilket projekt som visas. **15 registrerade/aktuella anställda betyder 15 synliga figurer**.
5. Klicka på en figur så öppnas **Min studio** med just den personens kort markerat. Scrolla genom alla kort med mus/pekfinger (hela dialogen rullar). Dra en ledig figur till ett bord för att använda den befintliga stationsförflyttningen för **rätt projekt och agent-ID**. En upptagen figur kan inte dras.

## Vad fixas?

- Den gamla kontorsprojektionen visade bara **en representant per station**, med övriga anställda gömda bakom ”4 kollegor”. Den ersätts när det finns registrerad global personal. Inga nya ”agentkopior” uppstår vid projektbyte.
- Alla personer blir egna klickbara pixelfigurer med exakt **`studio_id`**, oavsett namn och äldre tilldelat projekt. Rollbaserad befintlig pixelgrafik återanvänds via `sprite-role-*` och `sprite-variant-*`.
- Ledig personal rör sig **endast visuellt** i korta promenader. Upptagen personal står vid sin angivna station och markeras som arbetande **bara när servern redovisar pågående/köat jobb**. Ingen animation genererar AI-anrop, Git-ändringar eller arbetsorder.
- *Min studio* har nu **en scrollande dialog**, inga konkurrerande inre scrollområden för registreringspanel och personalkort. Sökfältet finns överst, mobil visar en kolumn. Detta rättar scenariot där de sista 13 korten inte går att nå.
- En **gemensam fysisk kontorsvy** visas när du byter vilket spel du tittar på. Byte av fokusprojekt ska aldrig i sig flytta anställda eller starta ett uppdrag.

## Kända gränser

**V2.6 är en UI-migrering av det synliga kontoret, inte en backendmigrering av arbetsmotorn.** Serverns gamla `STAFF.json` per projekt används ännu som adapter för jobb, avskedning, profil och behörighet. Det centrala `PEOPLE_V25.json` bevaras; det ändras inte av denna fix. Om personalen ändras efter registreringen kan v2.5 visa ”Behöver synkroniseras” tills följande migreringssteg finns. Radera inga av de gamla personalfilerna.

Att dra en figur till ett bord är däremot en **uttrycklig användaråtgärd** som anropar det befintliga stations-API:et. Som tidigare kan detta utlösa automatisk jobbstart i ett projekt med godkänt mandat när projektets arbetsledare inte styr kön. Flytta personer mellan *projekt* via befintliga **Min studio → Tilldela**, inte genom att dra i den fysiska vyn. Att klicka på en figur öppnar *Min studio*, inte en gissad ”Gunnar”-session i ett annat projekt. Historiska hjälpärenden nås via **Alla hjälpärenden i studion**.

När servern inte går att nå behålls senast kända visning; det påstår inte att nya arbeten är verifierade. Vid ett ännu inte registrerat globalt personregister får den gamla kontorsvyn ligga kvar (ingen falsk konvertering).

På smala mobiler kan hela spelkontoret fortfarande vara större än skärmen. Panorering/zoom/kompakt mobilmeny är separat UX-arbete.

## Testning

- `node --check src/pw-global-office-v26.js` och `node --check src/main.js`.
- Playwright Chromium med **fiktivt** API och **15 personer** (flera Gunnar): ett separat klickbart sprite-element per ID, inga gamla gruppskyltar, `Min studio` öppnar rätt kort, projektbyte visar samma 15, mushjuls-/touchvänlig huvudscroll på desktop/mobil, ingen tyst API-POST, och en explicit dragning använder just personens projekt- och agent-ID.
- Inga verkliga AI-anrop, nätverks-/serverändringar, personavsked eller projektfiländringar utfördes.
- **Ej verifierat** på din faktiska Ubuntu-server och i din mobila webbläsare. Figuren hämtar befintliga sprite-bilder i den verkliga installationen; den isolerade browserfixturen har enklare platshållargrafik för test.

## NOW / NEXT / LATER

**NOW:** synlig global kontorsstyrka, en figur per person, klick/drag, scroll reparerad; kompatibilitet med registreringen v2.5.

**NEXT:** göra `PEOPLE_V25.json` till faktiskt personalregister för jobbtilldelning, skills, profil, avsked och projektbemanning; migrera öppna hjälpärenden och rapportalias utan namnmatchning. Synlig studioväljare för produktionsstatus **Arbetar/Pausad** per spel. Se till att backend återhämtar missmatchade arbetsorder utan eviga omförsök.

**LATER:** avveckla projektspecifik `STAFF.json` som *primär* källa efter verifierad, återställningsbar datamigrering. Full mobilkamera och samordnad status mellan samtidiga webbläsare. Ingen automatisk sammanslagning eller avskedning av gamla personer.
