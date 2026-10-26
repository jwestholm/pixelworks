# Pixel Works v0.12.11.1 — Gemini-korrigering och spelmenyer

**Delta på v0.12.11.** Packa upp i Pixel Works-programkatalogen med samma mappstruktur. Paketet innehåller **endast nya/ändrade käll- och testfiler** – inga installationsskript, API-nycklar, game bible-filer eller spelprojekt.

## Före uppackning

- Avsluta servern med Ctrl+C i terminalen där den körs; låt eventuella pågående AI-jobb bli färdiga först.
- Gör gärna en kopia av de filer som kommer att skrivas över: `backend/pw_v01210.py`, `src/pw-v01210.js`, `src/pw-v01211.js` och `backend/test_pw_v01210.py`.
- Den här patchen förutsätter att v0.12.11 redan fungerar. Den ändrar **inte** `backend/server.py` eller krav på Git-klon från 0.12.11.
- **Enda startkommandot:** `python3 backend/server.py`. Uppdatera Firefox med `Ctrl+Shift+R`. Kontrollera att versionen visar **v0.12.11.1**.

## Åtgärdat

1. **Gemini får flyttas till Dokumentation/Research/Mötesbord.** Den ursprungliga serverns Codex-only-gate stoppade Gemini trots att kryssrutorna i personalprofilen var markerade. Gemini får nu röra sig till dessa tre stationer om personalprofilen godkänner dem. Kod-/grafik-/musikstationer tilldelas fortfarande inte Gemini via denna ändring. Befintlig Codex-behörighet är oförändrad. Extraregeln "stationsansvar" (Codex verktygsinställning) används inte längre som extra veto för en Gemini-rådgivares förflyttning.
2. **Token sparas före Googles verifiering.** Den gamla servern avvisade alla nycklar som inte började med `AIza` (ett lokalt formatantagande) och meddelade "Ogiltig Gemini API-nyckel" utan att fråga Google. Nu sparas en token som har rimligt teckenformat/ längd. Den särskilda **Testa/verifiera anslutning**-knappen frågar därefter Googles API om den valda modellen finns. Nyckeln lämnar inte datorn förrän användaren testar eller ett riktigt Gemini-jobb får startas.
3. **Inställningar tar färre klick.** Övre knappen **Inställningar** öppnar Gemini-tokenfönstret direkt. Där finns Visa/dölj, Spara, Testa och status. Tidigare extra sidor är dolda under **Avancerade verktyg**. De är kvar för befintliga användare men inte längre som tre jämbördiga inställningsflikar.
4. **Status uppdateras efter sparande.** Gemini-kopplingen uppdaterar anställdas motorkonfiguration direkt efter en lyckad lokal sparning.

## Varför finns gamla verktygen kvar?

- **Codex × flera:** Manuellt specialläge som låter en användare starta 2–4 *separata* Codex-uppdrag med isolerade Git-worktrees. Detta är inte en förutsättning för chefens vanliga delegering och borde längre fram flyttas till Uppdrag eller tas bort från spelvyn.
- **Arbetsbilagor:** Lagring av buggbilder, dokument och videor kopplade till uppdrag, *inte* designreferenser till Game Bible. Borde flyttas in i uppdragskortens "Bifoga"-flöde. Det befintliga stödet för att släppa filer på en station och öppna bilagedialogen finns kvar.

## Tester

- 30 lokala Python-regressionstester passerade (inklusive fyra nya som testar behörighet, filrättigheter och tokenlagring utan nätverk).
- `node --check` för båda berörda JS-filerna passerade.
- Chromium offline med falska svar: Inställningar öppnas direkt, avancerade flikar är dolda, token kan sparas och verifieringsknappen återger teststatus utan JavaScript-fel.
- **Ej verifierat:** verkligt Google-konto/nyckel, riktig Firefox på din dator, live-delegering till Gemini och riktig Codex-körning.

## Kostnad och säkerhet

Geminis lokala tak på 12 anrop per Google-kvotdygn finns kvar. Ett lyckat token-test verifierar *modellåtkomst*, inte Free Tier, återstående Google-kvot eller att fakturering saknas. Använd ett separat AI Studio-projekt med fakturering avstängd om du vill utesluta oavsiktlig betalning. Inget Google-anrop görs av att bara klistra in och spara token; kontrollanrop skickas endast när **Testa anslutning** används eller en riktig agent kör ett uppdrag.
