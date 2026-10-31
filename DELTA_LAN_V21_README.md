# Pixel Works – Hemma-LAN utan inloggning v2.1

**Bas:** tidigare installerad LAN-delta v2.0 på Pixel Works `dev` (`fb70d1c`, 2026-10-29 #1). Den här deltan ändrar bara `backend/pw_lan.py`, `backend/test_pw_lan.py` och `start-lan.sh`. Ingen ändring i `backend/server.py`, övriga API:er, projektfiler eller Git-repot. Inga brandväggs-/routerändringar görs automatiskt.

## Snabbstart

1. Packa upp ZIP i Pixel Works **projektrot** (mappen med `index.html`), skriv över de tre filerna.
2. Stoppa gammal server: `python3 backend/server.py stop`.
3. Starta lösenordsfritt hemmanät: `bash start-lan.sh`.
4. Telefon, samma hem-Wi-Fi (inte gästnät): **http://192.168.0.8:8765/**. På datorn fungerar **http://127.0.0.1:8765/** som vanligt.
5. När du trycker **Spela** används **port 8766** för spelets isolerade förhandsvisning.

Om datorns LAN-IP ändras: `PIXEL_WORKS_LAN_IP=192.168.0.9 bash start-lan.sh` (byt till din verkliga LAN-IP). Kontrollera aktuell adress med `ip -4 addr` eller `hostname -I`.

### Bara om Ubuntus brandvägg är aktiv

Kolla först: `sudo ufw status`. Om **active** kan du, från datorn, tillåta **endast** det betrodda hemnätet (anpassa `/24` om ditt nät skiljer sig):

```bash
sudo ufw allow from 192.168.0.0/24 to any port 8765 proto tcp
sudo ufw allow from 192.168.0.0/24 to any port 8766 proto tcp
```

**Öppna INTE routerns port forwarding.** All trafik stannar på LAN så länge du inte redan har extern exponering via router, proxy, VPN eller annat. Att ange en privat IP för lyssning ger inte i sig en garanti för att nätet är säkert.

### Skyddat läge finns kvar, om du vill

`bash start-lan.sh --protected` frågar efter lösenord, precis som v2.0. Vanlig `python3 backend/server.py start` utan LAN-miljövariabler fortsätter att lyssna på enbart localhost.

## Tekniskt

- Servern lyssnar fortsatt på `127.0.0.1:8765` och, endast i valt LAN-läge, på `192.168.0.8:8765`. Preview har egna motsvarande lyssnare på `:8766`. **Ingen** bindning till `0.0.0.0`.
- Standardtillåtet nät är IP-adressens `/24` (t.ex. `192.168.0.0/24`). Andra klient-IP-adresser blockeras; anpassa vid behov med `PIXEL_WORKS_LAN_CIDR`.
- `Host` och `Origin` kontrolleras fortfarande, liksom befintliga CSRF-, routnings- och tokenkontroller. `HEAD` nekas. Nycklar för Gemini/Freesound och Codex skickas inte som LAN-lösenord.
- **Varning:** I lösenordsfritt läge kan **alla betrodda enheter på samma tillåtna nät** läsa projektinformation och skicka arbetsorder som använder AI/ändrar projekt. Den inbyggda webbsessionens token är inte en separat inloggning. Använd bara på ett betrott lokalt nät utan okända enheter; använd inte på publikt Wi-Fi. Trafiken är vanlig HTTP, inte krypterad HTTPS.

## Teststatus

Verifierat här med lokala loopback-testadresser: 6 Python-tester, inklusive två lyssnare, lösenordsfri LAN-åtkomst, skyddat LAN-läge, felaktig Origin, felaktig Host, separat preview och nekad HEAD. `bash -n` och `py_compile` passerade. **Inte testat i användarens Ubuntu-installation eller på faktisk telefon/IP 192.168.0.8.** Inga nätverks-, brandväggs- eller AI-operationer har utförts utanför testmiljön.

**NOW**: enkelt lösenordsfritt LAN. **NEXT**: generisk nätverksinställning i spelets Inställningar, om det behövs. **LATER**: TLS eller VPN för extern åtkomst; ingen exponering direkt på internet.
