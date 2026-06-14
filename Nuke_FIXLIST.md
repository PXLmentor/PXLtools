# Nuke TurnTable Comp Setup — Finalization Fix List

> Parity pass to match the finalized Maya TurnTable Builder. RULE: copy Maya's
> exact icons / fonts / sizes / behavior — do not reinvent. Tool:
> `PXLtools_TurnTable_Comp_Setup` (Nuke). Logged 2026-06-13 from Cris's in-Nuke review.

## Status (2026-06-13)
**Part 1 DONE in comp v1.1.15** (safe/deterministic): #2 BG white + wire cyan, #5 Asset Info
icon ->box, #8(png) PNG default, #9 create-directories robust + "double-click Write node and
click Render" instruction. Pushed + in beta v1.0.0.
**Part 2 PENDING (need live-Nuke eyes / research — do tomorrow, don't guess):** #1 combo
centre-arrow, #3 no-folder->Instructions/Preliminary, #4 Preliminary icon=Maya, #6
render-location green-when-set, #7 references load button (Cris to point at which control),
#8 MP4 export (mov/h264 + test) + RGB colourspace default (clarify meaning) + output capsule.

## Items
- [ ] **1. Combo center-arrow** — HDRI / Render Type / Background combos show an arrow
  in the CENTRE plus one on the right. Remove the centre one (keep only the right).
  (Same bug we killed in Maya — verify the Nuke `_FIELD` QComboBox down-arrow/drop-down.)
- [ ] **2. Defaults: BG Color = white, Wire Color = cyan** (set as the code defaults).
- [ ] **3. No working folder set → start at Instructions + Preliminary** (auto-expand
  them), exactly like Maya's "collapse when set / open when not" logic.
- [ ] **4. Preliminary Steps icon = same as Maya** (Maya uses `folder`). Match icon +
  font + size + functionality across the board.
- [ ] **5. Asset Info icon** — currently a picture/image icon; doesn't read as "asset
  info". Change to a better-fitting icon.
- [ ] **6. Render Location browse = guided-step colors** — browse button orange/active
  first, turns green (done) once the location is selected. Same procedure/UX as Maya.
- [ ] **7. References: remove the top-right load-image button** — loading is by clicking
  the card centre or drag-and-drop, so the button is redundant. Remove it.
- [ ] **8. Export panel:**
  - PNG = default export format.
  - Output **RGB** = default colorspace.
  - Add **MP4** as an export format (use sensible default mp4 compression settings).
  - The output-folder row shows an empty black "capsule" — either put the output path
    text INSIDE the capsule, or remove the capsule.

- [ ] **9. Write node creation:**
  - On create, enable the Write node's **"create directories"** knob (`create_directories=1`)
    so the output folder is made automatically — otherwise render errors on a missing dir.
  - Under the two Write buttons, add a short instruction line:
    **"Now double-click the Write node and click Render."**

## Notes
- After implementing: bump Nuke version, redeploy + re-cut the beta release; Cris re-tests
  in Nuke; then promote v1.0.0 -> stable (Maya + Nuke).
