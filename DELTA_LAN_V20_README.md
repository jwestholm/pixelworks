# Pixel Works – privat LAN-åtkomst v2.0

**Källbas:** GitHub `jwestholm/pixelworks`, `dev` commit `fb70d1c9a927e07e802537c83705db5b8f9876cd` (2026-10-29 #1), plus användarens lokalt installerade delta v1–v1.9. **Ändrade filer:** endast `backend/server.py` (två tilläggsrader). Nya: `backend/pw_lan.py`, `backend/test_pw_lan.py`, `start-lan.sh`, denna README och manifest. Inga andra projekt eller filer skrivs över. Ingen GitHub-push.

## Snabbstart från projektroten

1. Säkerhetskopiera egna lokala kodändringar. Packa upp hela delta-ZIP i mappen där `index.html` ligger.
2. Stoppa gamla servern (om den kör):

   ```bash
   python3 backend/server.py stop
   ```

3. Starta i LAN-läge:

   ```bash
   bash start-lan.sh
   ```

   Skriv ett **eget lösenord på minst 12 tecken** när terminalen frågar. Ingen text visas medan du skriver. Detta lösenord är för Pixel Works på nätverket, **inte** en API-nyckel eller ditt Google-lösenord.
4. Kontrollera att datorns LAN-IP verkligen är `192.168.0.8` (`ip -4 addr`). Om adressen ändras, starta med t.ex. `PIXEL_WORKS_LAN_IP=192.168.0.9 bash start-lan.sh`.
5. På telefonen: anslut till **samma Wi‑Fi**, stäng av mobildata/VPN vid behov och öppna **`http://192.168.0.8:8765/`**. Inloggningsrutan använder användarnamn **`pixelworks`** och det lösenord du nyss valde.
6. På Ubuntu-datorn fungerar `http://127.0.0.1:8765/` som förut utan LAN-inloggning.
7. `🎮 Spela` använder **separata port 8766** och kan begära **samma lösenord en gång till**. Det måste vara en annan origin så att spelets genererade kod inte får tillgång till Pixel Works API.

Serverprocessen kör i terminalen som tidigare; stäng via Ctrl+C eller `python3 backend/server.py stop` från en annan terminal.

### Ubuntu-brandvägg (om `ufw` är aktiv)

Kontrollera först med `sudo ufw status`. **Om** `ufw` är aktiv kan du tillåta endast hemnätet (exempel med /24):

```bash
sudo ufw allow from 192.168.0.0/24 to any port 8765 proto tcp
sudo ufw allow from 192.168.0.0/24 to any port 8766 proto tcp
```

Detta är manuella systemåtgärder. ZIP-filen ändrar **inte** Ubuntu-brandväggen eller routern. Portforwarding på routern får **inte** aktiveras. Öppna inte mot internet.

## Hur det fungerar

- Utan `PIXEL_WORKS_LAN_IP` gör patchen **ingenting**. Normalläget är fortsatt localhost-only.
- Med LAN-läge öppnas **två specifika IPv4-lyssnare per port**: localhost och angiven lokal adress (`192.168.0.8`). **Ingen bindning till 0.0.0.0** eller andra gränssnitt.
- Godkända LAN-klienter begränsas till `192.168.0.0/24` som standard (motsvarande vald IP/24), plus loopback. Ändra till ett mindre/större lokalt nät vid behov med `PIXEL_WORKS_LAN_CIDR`, minst /16.
- LAN-trafik till både app och spelpreview kräver HTTP Basic Authentication. Appens befintliga sessionstoken och ursprungskontroll behålls, API-nycklar skickas **aldrig** som autentiseringsuppgifter till telefonen.
- Lösenordet anges vid start, lagras **inte** i filer och rensas från Python-processens miljö innan AI-agenter startas; det är därför inte spritt till Codex som miljövariabel.
- `GET /api/bootstrap` med sessions-token är nu låst bakom LAN-inloggning. Cross-site POSTs, felaktiga Host-headrar och klienter utanför angivet LAN blockeras.
- Ärva `HEAD` från SimpleHTTPRequestHandler gav potentiellt oskyddad statisk åtkomst; denna metod nekas i LAN-läget.
- Adressen för projektets separata preview ändras automatiskt till LAN-adressen **enbart när förfrågan kommer via LAN**.

### Säkerhetsgräns

Det är fortfarande **HTTP och inte HTTPS**. HTTP Basic skickar credentials över nätet på ett sätt som någon som kan avlyssna trafiken potentiellt kan läsa. Använd det här **endast hemma på ett betrott WPA2/WPA3-nät**; aldrig på publikt Wi‑Fi, via routerns port forwarding eller via internet. Vill du använda spelet utanför hemnätet krävs en separat TLS/VPN-lösning med korrekt åtkomstkontroll.

### Felsökning

- **Startfel `Cannot assign requested address` / `Kan inte starta`**: datorn har inte adressen `192.168.0.8`. Kontrollera med `ip -4 addr` och välj rätt `PIXEL_WORKS_LAN_IP`.
- **Port upptagen:** stoppa gamla Pixel Works-processen genom `python3 backend/server.py stop`; prova aldrig att döda en okänd PID utan att kontrollera den.
- **Telefonen når inte servern:** samma Wi‑Fi (inte gästnät); kontrollera `sudo ufw status`; använd `http://`, inte `https://`; kontrollera att port 8765 är öppen från LAN.
- **Inloggningsruta:** användarnamn `pixelworks`; lösenordet du valde i terminalen. Ny start med nytt lösenord ersätter det gamla (ingen sparad kopia).
- **Spela fungerar inte:** även port **8766** måste nås och autentiseras, ibland separat i telefonens webbläsare.
- **Vanlig localhost-start:** `python3 backend/server.py start` utan LAN-miljövariabler återställer endast lokal åtkomst.

## Teststatus

**Verifierat i isolerade lokala tester:** dual-interface bind på två loopback-IP, lösenordsprompt via HTTP 401, åtkomst efter rätt HTTP Basic, nekad otillåten Host/origin, URL för separat preview, vägrad HEAD, nekade osäkra nätadresser och att lösenordet försvinner ur miljön.

**Inte verifierat:** faktisk mobil eller Ubuntu-brandvägg, faktisk `192.168.0.8`, något verkligt AI-anrop, och projektspel via mobil på 8766. Servern i testmiljön har inte användarens hem-LAN.

**NOW:** valbar privat LAN-åtkomst med lösenord. **NEXT:** i spelets inställningar styra LAN-läge och visa anslutna enheter. **LATER:** säkert fjärrläge via TLS/VPN, utan att direkt exponera AI-kommandon på internet.
