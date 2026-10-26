# Pixel Works v0.12.11.10 – Mötesdelegering

Delta över **v0.12.11.9**. Packa upp i samma projektrot, starta med `python3 backend/server.py`, sedan Ctrl+Shift+R.

## Ändringar

- `backend/pw_v01210.py`: flytta den tilldelade rådgivande medarbetaren till rätt arbetsbord vid start utan att kö-statusen blockerar flytten; ladda ny modul.
- `backend/pw_v0121110.py`: lokalt autentiserat återkontrollanrop för mötes-/dokumentations-/forskningsstation. Använder befintlig arbetskö, chef, studioåtkomst, verifierad AI och kvotgränser. Startar inte utan verkligt jobb eller tidigare tillstånd.
- `src/pw-v012118.js`: efter att en medarbetare dragits till ett bord begär spelet omedelbart en ny kontroll av väntande arbetsorder, även om chefen är närvarande; blockeringsorsaken visas.
- `backend/test_pw_v0121110.py`: regressionskontroller utan riktiga API-anrop.

## Begränsningar

Automatisk delegering sker via den befintliga bakgrundsloopen (cirka var 12:e sekund). Manuell dragning ger direkt kontroll. Om chef, behörig medarbetare, studioåtkomst, aktivt modelltest eller lokal anropsbudget saknas startar inget riktigt API-anrop. En arbetsorder som redan är slutförd eller väntar på granskning startas inte igen. Verktyget har inte körts mot din personliga Firefox eller dina faktiska Google-uppgifter.
