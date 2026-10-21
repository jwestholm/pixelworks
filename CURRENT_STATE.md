# Pixel Works v0.11.1.1 — CURRENT STATE

## NOW — implementerat och lokalt testat
- Stationsspecifika, klickbara snabbval med egna, lokalt renderade pixel-SVG-ikoner på 24×24-rutnät. Gemensam arbetsordermotor och separat katalog per arbetsstation.
- Valfri stil/egenskap (t.ex. Jazz, Chiptune), alltid egen fri instruktion, filväljare, drag/drop och Ctrl+V-bilder i arbetsordern.
- Kompakt valvy i sidor om sex val, arbetskö på separat skärm. Färdiga (`done`) arbetsorder döljs från aktiv kö och finns under **Visa historik**. De raderas inte från disk.
- Agent-/Codex-sessioner och projektmandat vidareförda oförändrade från v0.11.0. Ingen ny automatisk AI-exekvering vid skapande av arbetsorder.
- Ingen extern ikonhämtning eller tredjepartslicens krävs vid körning: ikonerna i detta paket är egna små SVG-piktogram inspirerade av pixelrutnätsprincipen.

## NEXT
- Visuella Firefox-tester av storlek och clipboard/Firefox efter installation. Test med verklig bild från urklippet återstår.
- Stationernas specialiserade verktyg, ljudförhandslyssning, grafikgalleri, QA-felrapporter och användarredigerbara snabbval.
- Serverstyrd scheduler och agentisolerade Codex-worktrees.

## LATER
- Codex-arbetsledare via begränsade MCP-verktyg samt fler provider-adaptrar.

## Ikonriktning
- Rekommenderad fri uppsättning: [Pixelarticons](https://github.com/halfmage/pixelarticons), MIT-licens (fria baspaketet). Kan ersätta nuvarande interna ikonfunktion i ett senare steg.
- Alternativ: Tabler Icons (MIT), men deras mjukare stroke-form passar mindre väl till kontorets rena pixelgrafik.

## v0.11.1.1 GUI-hotfix
- Stationsvalen är kompaktare: 3 kolumner, 9 val per sida, mindre ikoner och lägre knappar. Mobil: 2 kolumner.
- Ingen ändring i arbetsordrar, körmotor eller projektdata.
- Visuell Firefox-verifiering återstår.
