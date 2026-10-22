# Office workstation pack – v0.12.0.7

All ten files `desk-<station>.png` are transparent **320×248 RGBA** pixel sprites, aligned to the same front-facing isometric diamond. CSS renders them via the existing `.station .station-top` element. The underlying `.station` remains the click/focus/drag target; images are cosmetic and do not determine permissions, job status or provider.

Types: `lead`, `code`, `qa`, `research`, `art`, `docs`, `voice`, `music`, `meeting`, `cafe`.

Colors and screen contents are intentionally distinct; the base footprint, camera angle, outlines and warm tabletop lighting are shared so assets may later be swapped without moving the hitboxes. The preview file linked in the delivery is a sprite comparison sheet, **not a screenshot of the running game**.
