# Pixel Works v0.12.0.9 – Spela & rapporter på skrivbordet

Komplett paket ovanpå v0.12.0.7, inklusive alla tidigare yrkesanpassade isometriska skrivbord.

## Nytt
1. Toppmenyn: `🎮 Spela` direkt efter `🏢 Kontor`. Använder samma befintliga separata preview på lokal port som tidigare spelknapp (ingen GitHub-push).
2. Backend: nya färdiga Codex-jobb markeras inte längre automatiskt som lästa/arkiverade. De läggs på **Ditt skrivbord** och visar en ny notis tills de läses.
3. Samma princip gäller när en tidigare granskningsväntande arbetsyta integreras säkert.
4. Tydligare rapportlista: `Infört i spelet` skiljs från `Speltest ej verifierat`. Inga påhittade testresultat.
5. Arkiverade äldre rapporter behåller sitt tidigare tillstånd. De återuppväcks inte automatiskt.

## Uppdatering
Stoppa föregående Pixel Works-server, kopiera programfilerna över din befintliga lokala Git-arbetsmapp **utan att radera `.git`**, och starta sedan nya `backend/server.py`. Spelprojekten under `~/.pixelworks/projects/` ska bevaras.

## Viktigt
Den här versionen kräver inget manuellt godkännande för en säker integration. `Spela` öppnar en preview om spelet har en giltig `index.html`; annars ges befintligt begripligt felmeddelande. Ingen AI-körning startar bara för att du öppnar en rapport.

## Nytt i v0.12.0.9

**Ditt skrivbord:** öppna rapportpärmen och filtrera på **Nya/Lästa**, **Rapporttyp** och **Arbetsstatus**. Klicka **🗑️** intill en rapport för att arkivera endast den, eller **Arkivera visade** för det aktiva filtret. Grupparkivering kräver en bekräftelse inuti spelet. Det raderar inte projektfiler eller Git-historik.

**Utseende:** popupfönster har enhetligare träinramning; uppdragslistan presenteras som en whiteboard och personalens kort med samma designfamilj.

Du behöver bara den senaste ZIP-filen. Vid uppdatering: stoppa servern, uppdatera programfilerna men bevara `.git` och `~/.pixelworks/projects/`.
