# Pixel Works v0.13.9 – Du är med i fikasamtalet

**Installeras ovanpå v0.13.8**. Endast ändrade/nya filer i ZIP; inga projekt, speldata, hemligheter, externa API-anrop, GitHub-ändringar eller installationsskript.

## Problem i v0.13.8

- Spelägarens text i fikarummets ämnesfält skickades som `owner_note`, men fanns inte i det synliga transkriptet som ett eget inlägg. Det kunde leda till att en anställd AI tog upp spelarens idé som sin egen utan att nämna spelägaren.
- Samtalet kunde sluta utan arbetsorder. Det saknades ett enkelt sätt att gilla/avfärda ett enskilt förslag, omvandla det till ett uppdrag eller delta igen efter avslutad diskussion.

## Nytt i v0.13.9

1. **Spelägaren deltar på riktigt:** Text i startämnet blir en egen sparad replik märkt `source=owner_message`, `name=Du` och `agent_id=None`. Den är tydligt märkt som **skriven av spelägaren**, inte som ett AI-svar. Kommande modellprompter får `source` för varje tidigare replik samt uttrycklig instruktion att aldrig tillskriva spelägarens text en anställd.
2. **Skriv under samtalet:** Ett fält under replikerna låter användaren hoppa in. Texten sparas i projektets fikaarkiv. Inför varje kommande AI-anrop läses den senaste diskussionen från disk, så att användarinlägg och andra svar inte skrivs över när flera uppdateringar sker samtidigt.
3. **Fortsätt efteråt:** Om diskussionen har avslutats startar en inskickad följdfråga en **ny verklig svarstur från två tillgängliga AI-anställda**. Max två sådana extra turer (två AI-anrop per följdfråga). Tillgängligheten och projektmandatet kontrolleras igen. Ingen fiktiv replik produceras vid fel.
4. **👍/👎 på AI-inlägg:** Feedback sparas på rätt replikindex; går att ändra eller avmarkera. Inga AI-anrop startas och ingen arbetsorder skapas automatiskt av en tumme.
5. **🛠️ Gör till uppdrag:** Klicka på ett AI-förslag, välj rätt skrivbord och välj **Lägg i arbetskön**. En riktig projektbunden arbetsorder skapas med citatet och källans namn som underlag. Teamets befintliga kompetensplanering används för tilldelning. Samma inlägg kan inte skapa dubblettordrar vid upprepade klick; gamla automatiska chefsuppdrag störs inte.
6. **UI:** Din replik visas med eget ljusgult kort, kollegornas repliker med separata knappar. Frivillig planering ersätter inte tidigare automatiska uppföljningsorder (exempelvis QA efter fikadiskussion).

## Viktiga gränser

- Ett fikasamtal eller din feedback är **inte** verifierat genomfört kodarbete. En skapad arbetsorder får status **väntar**, och den befintliga schemaläggaren måste faktiskt genomföra arbetet.
- Flera AI-anrop använder verkliga leverantörskvoter; en uppföljningsrunda kan göra två extra verkliga anrop. Ingen lokal artificiell daglig Gemini-spärr återinförs.
- En kommentar som skickas medan ett AI-anrop redan håller på att formuleras kan först påverka **nästa** AI-anrop. Vid avslutat samtal kan spelägaren ställa en uppföljningsfråga.
- Feedback påverkar framtida promptkontext men kan inte dra tillbaka redan utförda arbeten eller arbetsorder.
- Fikarummet begränsas fortsatt till nuvarande projekt, lokalt åtkomstmandat och tillgängliga anställda. Inget automatiskt godkännande av spelvision eller offentlig publicering.
- Äldre arkiverade fikadiskussioner i `management/cafe-sessions/` är fortfarande läsbara; nya `reactions` och `followup_count` är bakåtkompatibla fält.

## Installation

1. Säkerställ att Pixel Works **v0.13.8** finns installerat.
2. Packa upp deltapaketet ovanpå installationen, utan att radera befintliga filer.
3. Starta med `python3 backend/server.py` och uppdatera Firefox med `Ctrl + Shift + R`.
4. Öppna **Fikarummet** → starta en diskussion → skriv själv, använd tummar eller skapa en enskild arbetsorder.

## Verifiering

- **88 riktade backendtester passerar tillsammans** (inklusive nio nya tester för användarinlägg, feedback, uppföljning och idempotent arbetsorder).
- **Två Chromium-röktester passerar**: det tidigare fikaflödet och nytt interaktivt flöde med tilldelning, röstning och en extra replikrunda.
- JavaScript-syntax och Python-kompilering godkända; ZIP/SHA256-kontroll vid paketering.
- Testerna använder simulerade provider-svar. **Inga verkliga Codex- eller Gemini-anrop har gjorts.** Den äldre fullständiga speltestsviten är inte verifierad som helt grön.

## Förändrade/nya filer

- `backend/pw_v0138.py` – fikarumsmotor och nya säkra sessionactions på befintlig API-adress.
- `backend/pw_v013.py` – versionsmärke 0.13.9 (befintlig modul-installationsordning bibehålls).
- `src/pw-v0121118.js` – samtalsfält, röstning, implementering, status och korrekt författaridentitet.
- `src/pw-v013.js` – synligt versionsmärke.
- `backend/test_pw_v0139.py` och `test_browser_0139.py` – nya regressionstester.
