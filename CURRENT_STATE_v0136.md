# CURRENT_STATE — 0.13.6

- Installeras som delta ovanpå 0.13.5, enda produktionsfilen som förändras är `src/pw-v013.js`.
- Högerspalten prioriterar aktiva händelser och åtgärder. Produktionsdetaljer är hopfällda och dubblettpaneler gömda/flyttade till existerande huvudmenyer.
- Underliggande backend, behörigheter och jobbhantering oförändrade; tidigare risker med dubbla dispatcherfunktioner och full regressionstestsvit kvarstår.
- Chromium UI-smoketest och JS-syntax gröna; riktiga AI-anrop inte körda.
