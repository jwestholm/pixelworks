# Testprotokoll – Pixel Works v0.11.8.4

## Genomfört
- `python -m unittest discover -s backend -p 'test_*.py' -q`: **156 test, OK**. Regressioner för hjälpärenden, säker omprövning av isolerade jobb, nya uppföljningsorder, dubbla knapptryckningar, gamla rapporter och instruktioner.
- `node --check local.js`: **OK**.
- Alla **12** `test-*.mjs`: **OK**.
- `python -m py_compile backend/server.py`: **OK**.

## Verifierade begränsningar
- Testerna använder temporära spelprojekt och ingen riktig Codex-/Gemini-körning. Dialogens handlingar startar inget Codex-anrop direkt.
- Ett rent integrationstest med flera verkliga Codex-processer på Ubuntu är inte utfört i denna version.
- Försök att kontrollera gränssnittet med headless Chromium stoppades av körmiljöns localhost-policy (`ERR_BLOCKED_BY_ADMINISTRATOR`). Därför är **Firefox-layouten och klickbarheten inte visuellt verifierade**.
- Ett upprepat jobb kan fortfarande misslyckas; felet ska då visas som ett nytt ärende. Studion skriver aldrig över en konflikt automatiskt och undviker oändliga automatiska försök.
- Fullständig transaktionssäkerhet mellan JSON-arbetsorder och rapportfiler kräver en större lagringsförändring.

## Viktiga regressioner
- Ett äldre ärende kan inte av misstag avsluta någon annans aktuella arbete.
- Verklig kollision ⇒ nytt uppdrag med skydd av senaste versionen (utan manuell Git-merge).
- Saknad gammal arbetsyta ⇒ nytt uppdrag, inte terminalinstruktion.
- Redan skapat uppföljningsjobb ⇒ ingen ny duplicerad hjälpbubbla.
- Säkerhetsblockering vid pågående jobb ⇒ ingen obehörig integration.
