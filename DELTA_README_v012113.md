# Pixel Works v0.12.11.3 — Gemini textmodell och arbetsledarstatus

**Delta mot v0.12.11.2.** Packa upp ZIP-filen i Pixel Works-programmappen och behåll katalogstrukturen. Bara filerna i manifestet ersätts/tillkommer. Ingen ändring av existerande spelprojekt, inga nya startfiler, ingen installation/skriptkörning. Ingen GitHub-push.

**Starta oförändrat:** `python3 backend/server.py`.

## Vad som rättats

1. **Felaktigt grönt Gemini-test:** Gamla testet kunde visa »ansluten« efter enbart `GET /models`, samtidigt som `POST :generateContent` svarade `404`. Enligt Google kan gamla Gemini 2.5 visas i modellistan men nekas på API-anrop för nyare projekt.
2. **Modell:** Standardmodellen byts från `gemini-2.5-flash` till `gemini-3.5-flash-lite`, som Google har dokumenterat med *Free Tier — free of charge* den 23 oktober 2026. Det är **inte ett bevis på att användarens Google-projekt saknar aktiverad fakturering**. Appen byter inte automatiskt modell vid fel.
3. **Verklig anslutningsverifiering:** »Testa/verifiera anslutning« gör nu **ett kort riktigt `generateContent`-anrop** mot den modell som sedan används för jobb. Det förbrukar **ett anrop av Pixel Works lokala dagstak (12)**. Automatiken kan inte köra förrän ett faktiskt textsvar verifierats för den sparade token och den aktuella modellen.
4. **Efter 404:** Vid modellfel pausas automatiken; den upprepar inte anropet på egen hand. Ett nytt manuellt **lyckat** test på den nya modellen häver en tidigare API-paus men återställer inte förbrukad dagskvot.
5. **Arbetsledarens status:** För väntande dokumentations-/research-/mötesjobb med behörig Gemini-specialist visas ett relevant Gemini-fel eller testbehov istället för vilseledande Codex-brist.
6. **Personalstatus:** Gemini-profilen kan visa »TESTA ANSLUTNING« i stället för att felaktigt kalla token ensam »ansluten«. Ingen »sjukskriven«-text införs.

## Testa i spelet

1. Stoppa den gamla servern; packa upp deltafilen; starta `python3 backend/server.py`.
2. Ladda om sidan med Ctrl+Shift+R.
3. Välj **Inställningar → Google Gemini → Testa/verifiera anslutning**. Token ska redan finnas lokalt, så du ska normalt inte behöva klistra in den igen.
4. Ny status **»🟢 Ansluten · textsvar verifierat«** innebär att Google *verkligen besvarade* testet med `gemini-3.5-flash-lite`. Det säger **inte** något om betalsaldo eller verklig gratiskvot.
5. Ett tidigare misslyckat uppdrag ändras **inte retroaktivt**. Efter godkänt test kan uppdraget återföras till kön via hjälpdialogen (»Låt studion försöka igen«). Kontrollera att projektets arbetsledare sitter vid chefsbordet och att Gemini har station Dokumentation/Research/Mötesbord.
6. För uppdrag som kräver att filer på spelplanen skrivs om behövs fortfarande en kodskrivande arbetare (Codex). Gemini levererar endast textförslag att granska.

## Säkerhet och verifiering

- **42 Python-backendtester** passerade lokalt, inklusive simulering av Googles `404`, kvot och korrekt delegeringsstatus.
- **Chromium med simulerade API-svar** och JavaScript-syntaxtest godkända.
- **Inget verkligt Gemini-anrop** har körts under paketbygget. Konto, verklig kvot och spelmiljö är **ej verifierade**.
- Ingen betalmodell väljs automatiskt. För *noll kronor* måste API-nyckelns projekt vara på Free Tier **utan aktiverad fakturering**. Pixel Works kan inte verifiera det via nyckeln.

Källor: https://ai.google.dev/gemini-api/docs/models.md och https://ai.google.dev/gemini-api/docs/pricing
