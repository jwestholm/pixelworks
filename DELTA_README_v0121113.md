# Pixel Works v0.12.11.13 – Google styr Gemini-kvoten

**Bas:** v0.12.11.12. Packa upp deltafilerna över befintlig Pixel Works-installation, utan att röra projektdata. Starta fortsatt med `python3 backend/server.py`; uppdatera Firefox med Ctrl+Shift+R.

## Ändrat

- **Pixel Works lokala dygnstak för Gemini tas bort.** Värdet `owner_local_daily_limit` från äldre inställningar ignoreras; ingen data behöver raderas. Den lokala räknaren behålls som *historisk statistik över registrerade anrop* och blockerar inte fler anrop. Status anger `daily_limit: null`, `local_limit_exhausted: false`.
- **Google bestämmer RPM/TPM/RPD.** Vi antar inte att alla modeller alltid har 15 anrop/minut. Aktuella gränser varierar per modell och Google-projekt och framgår i Google AI Studio. Ett HTTP 429 från Google läses som ett verkligt kvot-/kapacitetsfel. Om svaret tydligt avser dygnskvot pausas till nästa Google-kvotdygn; för minut/token-/okänd gräns används minst 60 sekunders paus, enligt `Retry-After` / `retryDelay` när det finns (max 1 timme).
- **Ingen upprepning av misslyckat AI-arbetspass automatiskt.** En verklig 429 kan fortfarande lämna ett misslyckat arbetspass och en rapport som behöver åtgärd/requeue via spelet. Pausen förhindrar att andra automatiska anrop fortsätter direkt. Riktiga återförsök med den felade arbetsordern kräver fortfarande ett kontrollerat flöde.
- **Konsekvent hantering i alla Gemini-flöden:** även manuellt rådgivningsjobb och AI-sammanfogning av Game Bible registrerar Googles 429-paus, inte bara automatiska arbetsorder. Ett kvotstopp ändrar inte Game Bible.
- **30 sekunders minsta tidsintervall mellan schemalagda Gemini-anrop behålls**, en skyddande takt för drift, inte ett lokalt dygnstak. Ingen modellväxling, extra betaltjänst eller automatiskt inköp.
- **Inställningar:** det gamla valet 12/25/50/100 anrop/dygn är borttaget. Nu visas antal registrerade anrop, Googles kvot som *okänd* och aktuell kvotpaus med tid om den är känd. Äldre `/limit`-endpoint avvisar tydligt med HTTP 410.
- **Kompatibilitet:** äldre statuskontroller i v0.12.11.10/.11 undviker att jämföra anrop med det borttagna lokala dagstaket.

## Begränsningar och ansvar

- Googles faktiska återstående kvot kan inte kontrolleras via lokal räknare. En tidigare uppgift om 15 RPM gäller användarens modell/projekt vid den avlästa tidpunkten och garanteras inte för andra modeller eller tider. Även TPM och RPD gäller.
- Gratisnivå/fakturering kan inte verifieras från API-nyckeln. Om Googles projekt har fakturering påslagen kan anrop bli debiterade trots att Pixel Works inte höjer eller byter modell. Kontrollera Google AI Studio och projektets faktureringsinställningar.
- Äldre chefsrapporter och jobb som redan misslyckats av lokalt kapacitetstak blir inte automatiskt omskrivna eller återstartade. Du kan starta om/requeue arbetet via arbetsflödet när det är redo.
- Inga externa AI-anrop har körts vid utvecklingen. Riktiga integrationsprov i användarens miljö återstår. Den äldre fullständiga regressionssviten är inte grön på grund av föråldrade mock-/kvotförväntningar; detta paket har egna fokuserade testfall.

## Verifierat lokalt

- 9 nya Python-tester: högt historiskt räknarvärde blockerar inte, status och reservering, manuell anslutningstest utan lokalt tak, Google 429/minut och Retry-After, Google 429/dygn, okänt 429 utan påhittad siffra, bibehållen verifiering och säkerhetsgater.
- 6 befintliga personvalstester: inga regressioner.
- Chromiumtest med simulerad status: inget takval, korrekt statistik, inga externa anrop.
- Python-kompilering och JavaScript-syntax: OK.

Inga filer utanför Pixel Works eller användarprojekt ändrade. Ingen GitHub-push.
