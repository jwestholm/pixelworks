# NOW / NEXT / LATER

## NOW (v0.12.11.6)
- Kreativa arbetare levererar konkreta förslag, inte mallar.
- Godkända dokumentationsförslag blir beslutad design i Game Bible; inte implementerat.
- Aktiva ärenden syns med personnamn, kan öppnas från arbetaren, och försvinner efter granskning.
- Arbetaren går till fikarummet när uppdraget är klart och ingen ny arbetsorder finns.

## NEXT – spelork och kvoter
- **Två skilda mätare:** karaktärens simulerade ork (spelsystem) och AI-leverantörens verifierade användning (riktig data). Ingen kvot får uppskattas eller presenteras som verifierad.
- Visa orkmätare över anställd först vid hover, klick eller nära utmattning. Simulerad vila och kaffepaus återställer ork; påverkar inte leverantörens rate limits.
- Samla `input_tokens`, `output_tokens` och `total_tokens` per faktisk session när svaren innehåller usage-data. Skilj lokal summa från leverantörens konto-/dagssaldo.
- Kartlägg Codex händelseström/CLI där token_usage kan förekomma, och Gemini usageMetadata samt eventuella kvotfel/429. Alla fält saknade i svar visas `Okänt`.
- Kontostatus/rate limit får bara visas om en leverantör har ett dokumenterat och åtkomligt API som exponerar dem. Annars `Kvot ej tillgänglig`.
- Visa en liten studioöversikt för användning, och en provider-detalj bara på personprofil/AI-inställningar.

## LATER
- Utökad ork, egenskaper och raster i simuleringen; skilda från faktiska jobb så ingen API-aktivitet påstås vid fika.
- Fler providers och förmågor med gemensamt adaptergränssnitt.
