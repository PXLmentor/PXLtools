# TurnTable Tools — Running Fix List

> Punch-list of polish items raised during in-DCC testing. **Do not act until told** —
> these are collected as Cris finds them, then actioned in a batch. Tools:
> `PXLtools_TurnTable_Builder` (Maya) · `PXLtools_TurnTable_Comp_Setup` (Nuke).
> Logged 2026-06-12.

## Status
**All 5 items below shipped in `PXLtools_TurnTable_Builder_v1_0_22` (2026-06-12).** Awaiting
Cris's in-Maya verification, then close. Press the shelf **Update** button to load v1.0.22.
Items 3 (fit factor) and 5 (Lighting group naming — "Display" name, "normal render" = Arnold
Render) used my best-judgement defaults; confirm in-DCC and tweak if needed.

## Open (shipped — verify in Maya)

- [ ] **Auto-collapse Instructions when setup is already done (Maya).**
  If the prerequisites / preliminary setup are already configured correctly (i.e. the
  user has clearly read the instructions and set everything up), the **Instructions**
  section should start **collapsed**, and the UI should land directly on **Scene Setup**.
  No need to keep instructions open once everything is set up. (Apply Nuke parity after.)

- [ ] **Reword the Model empty-state / capture text (Maya).**
  Current wording is confusing — it shows something like *"No model capture yet"* and
  *"please select your model or root group"* / *"select your model root group"*.
  Replace with clearer copy, e.g. **"No model captured yet — select the model (or its
  root group) you want to capture."** (Final phrasing TBD — pick the cleanest.)

- [ ] **On Attach: switch viewport to main_CAM + frame asset with more breathing room (Maya).**
  When the model is attached to the turntable, the active viewport should switch automatically
  to `main_CAM` AND frame the asset. Current framing zooms in too tight. Compute the asset
  bounding box and fit so there's ~**10% margin top and ~10% bottom** (more breathing room).
  Note: `_frame_main_cam_to_asset()` already exists (currently fitFactor ~0.75) — loosen it /
  recompute from the bbox so the asset isn't cropped/over-zoomed. Verify the viewport actually
  switches to main_CAM on Attach.

- [ ] **"Save your scene first" reminder right before Render Turntable (Maya).**
  Add a clear reminder/note immediately above the **Render Turntable** action telling the
  user this is the moment to **save the scene** — because the render output names are derived
  automatically from the **scene file name**, so the naming convention only comes out right if
  the file is saved with the correct name. Keep it short + include a quick **example** showing
  how the file name maps to the render name (e.g. `scene file: Scion_TT_v003.ma  ->  renders:
  Scion_TT_v003_RL_hdri_01.####.exr`). Goal: nudge people to save at the right time.

- [ ] **Restructure + rename the "Lighting" section (03) (Maya).**  *(refined 2026-06-12 — this
  supersedes earlier drafts of the same item)*
  Section stays named **"Lighting"**. Current order inside it: Visibility, Size Reference,
  Backdrop, **UTILITIES** (Macbeth/color charts + reference ball), **HDRI ENVIRONMENT**.
  New layout, top → bottom:
  1. **HDRI group (FIRST, its own sub-category called "HDRI").** The HDR environment selection
     is the first thing people see/pick. **Directly under it, in the SAME group (a small card),
     put the essential "what do I want to see + run now" controls: the Backdrop toggle
     (HDRI / LIMBO) and the quick render/visibility toggle** (Cris said "backdrop and our
     normal render go on top" — CONFIRM exactly which toggle "normal render" means). Rationale:
     decide what to see and render right away; deeper options live below.
  2. **Display group** = what is now **Visibility + Size Reference** (these are not lighting).
     Pick a clearer name — candidates: **"Display"**, "Viewport Display", "Visibility &
     Reference" (Cris floated "X-ray / Info"). Sits directly under the HDRI group. Holds the
     visibility toggles + size-reference unit/measurements.
  3. **"Ref Ball & Charts"** — the old **UTILITIES** group (Macbeth/color charts + reference
     ball), kept as its own separate group.
  NOTE: Cris flagged this evolved over a few passes — confirm against the LIVE UI before
  building: exact control→group mapping, what the "normal render" toggle is, and the final
  name for the Display group.

## Notes
- More items will be added as Cris continues testing.
- Separately tracked (not from this list): Maya preliminary reorder (ACES first) — deferred
  until Nuke is fully signed off.
