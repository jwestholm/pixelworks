# Pixel Works 0.12.11.11 – Personalbaserad delegering

Installera ovanpå 0.12.11.10. Starta med `python3 backend/server.py`.

- Yrke, uppdrag och skillnivå avgör vem chefen väljer; AI-leverantör används först efter personvalet för att kontrollera faktisk körbarhet.
- En tillfälligt blockerad specialist byts inte tyst mot en annan anställd.
- Manuell stationstilldelning och automatisk dispatcher använder samma personval.
- Läsbart personalstatus-API: GET `/api/projects/<projekt>/staff-status`.
- Inga extra externa anrop på grund av statusfrågor; inga ändrade kvotgränser eller behörigheter.
- Verifierat endast med lokala automatiska tester och syntaxtest, inte verkligt AI-konto.
