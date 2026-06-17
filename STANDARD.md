# PXLtools — THE COMMANDMENTS (single source of truth)

> The **TurnTable tool is the reference implementation of every rule below**. If anything here is
> ambiguous, open the TurnTable tool and copy exactly what it does. "Looks close" is NOT compliant.
> Reference files:
> - Maya UI + step-gating: `maya/scripts/PXLtools_TurnTable_Builder_v1_0_28.py`
> - Nuke UI + step-gating: `nuke/scripts/PXLtools_TurnTable_Comp_Setup_v1_1_27.py`
> - Shared kit: `shared/pxl_ui/` (`theme.py`, `widgets.py`, `icons.py`)
> These rules apply to **every tool and every part of every tool** (every tab, every section). No exceptions.

---

## 0. UNDERSTAND THE WORKFLOW FIRST — ask before you design
1. Before building or restructuring ANY tool (present or future), if the **step-by-step procedure is not
   crystal clear**, STOP and ASK the user: how exactly will the artist use this tool? What are the
   important sections? What is the precise order of steps, and what does each step do? Only once the real
   artist workflow is understood do you design the gated UI per §IV. **Never guess the procedure.** A wrong
   workflow is worse than a delayed one.

---

## I. COLOURS — the kit only, never hard-coded
2. Every colour via `pxlt.c("<token>")`. **Zero hard-coded colours** (`setStyleSheet("background:#333")` is a bug).
   Style once with `pxlt.tool_qss()`; use shared `objectName`s.
3. Palette: `window #333333`, `header_bar #262626`, `surface #3a3a3a`, `surface_alt #404040`,
   `section_head #454545`, `section_hover #4f4f4f`, `hairline #262626`, **`accent #E8820C`** (PXL orange),
   `accent_hover #FF9A2E`, `on_accent #241606`, `text #E6E6E6`, `text_muted #A8A8A8`, `text_dim #7A7A7A`,
   **`ok #5BBF6A` (DONE green)**, `warn #E8B84B`, `error #E4604A`.
4. Two PXLtools windows side by side must be indistinguishable in style.

## II. WINDOW STRUCTURE
5. Always: `pxlw.AppHeader` (shared, NEVER bespoke) → body of `CollapsibleSection`s.
6. **Folder-style tabs**: tabs render as raised folder tabs (rounded top corners, orange top-accent on the
   selected tab) and are **numbered** ("1 · SETUP", "2 · RENDER").
7. An **INSTRUCTIONS** section sits at the top, collapsed by default once setup is done.

## III. CONTROLS — shared widgets, shared objectNames (never per-widget colour)
8. Buttons: `btnPrimary` (orange primary), `btnApply`, `btnAction`. Step buttons per §IV.
9. **Segmented toggles** (`btnToggleActive` orange / `btnToggleInactive`) for either/or choices (e.g. Your Model / Shader Ball).
10. **Destructive/danger actions** styled red (`btnDestruct` / `PxlDanger`), with descriptive copy ("removes X, keeps Y") and a confirm.
11. **Status pills** — rounded coloured indicators `statusOk` / `statusIdle` / `statusWarn` / `statusErr` for live state.
12. **Warning banners / reminders** — amber `warningBanner` / `frameWarn` for must-read notes (e.g. "save your scene first", "File ▸ Set Project").
13. Field labels `ctrlLabel`, notes `hint`.
14. **Sliders**: transparent track, thin orange line (`#E8820C`), white-dot handle (PNG) with an **orange ring + slight grow on hover**; the bar lightens on hover; fixed row height so the ring isn't cropped.
15. **Spin-boxes**: themed up/down arrows that go white on hover (reuse the themed style, no per-widget override).
16. **Combos**: single-arrow via `tool_qss` ONLY (no per-widget `QComboBox` QSS); arrow whitens on hover.
17. **Selectable card grid** (e.g. `HdriCell`): rounded preview cards, orange border on the active card.
18. **Hover feedback is universal** — every interactive element responds on hover (buttons lighten, arrows whiten, slider ring/bar, headers lighten). Copy TurnTable's hover set.

## IV. THE GUIDED STEP-BY-STEP — the heart of every tool (copy TurnTable exactly)
Any procedure is a NUMBERED, GATED, idiot-proof flow. The user is walked through it and cannot act out of order, yet can always go back.
19. **Numbered steps** (1, 2, 3 …): each a circular numbered badge + `stepTitle`.
20. **Three states, derived from REALITY** (already-satisfied steps come up green; the flow rests on the first unfinished step):
    - **LOCKED** — not its turn: grey badge `stepLocked` + `btnStepLocked`, control `setEnabled(False)` (un-clickable).
    - **ACTIVE** — do THIS now: badge `stepReady`, button `btnStepActive` (**orange outline**), enabled.
    - **DONE** — complete: badge `stepDone`, button `btnStepDone` (**green**) + right-side `✓` (`stepConfirmDone`).
21. A step goes DONE **only on the clean success of its action** (verify the real result; action returns bool).
22. **A completed SECTION collapses and the NEXT opens** — focus follows the active step.
23. **Any section ALWAYS reopens** (header is clickable, with a chevron) so the user can go back and change a
    parameter; a reopened section's controls stay **enabled**. Auto-collapse happens ONCE at the moment a step
    is applied — never force-collapsed on every refresh.
24. **Editing an earlier step re-locks the later ones** (they must be re-confirmed).
25. The parent section shows progress via `set_state('idle'|'active'|'done')` (orange when active, pale-green + header `✓` when done).
26. Use the shared helpers, don't reinvent: `_mk_step_header`, `_set_step_btn`, `_set_badge`, `_set_confirm`, and a per-area `_update_<area>_steps()` wired at each real success point; reset recomputes from reality.
27. Per-tab line: "Follow the numbers — the orange step is what to do next; it turns green when done."

## V. ICONS — one family, distinct everywhere
28. Built on the locked TurnTable tile (squircle, `#2c2c30→#141416` gradient, 2px `#3a3a40` edge).
29. Each tool icon = ONE greyscale top-lit object (noun) + ONE `#E8820C` accent (verb). Greys `#d6dbe2→#969ca6→#686d77`, edge `#ecf0f5`.
30. Sizes: `icon_<slug>.png` at **96px** (DCC gate) + **256px** (hero), RGBA, transparent corners.
31. **Every tool has its own icon; every SECTION inside a tool has a DISTINCT icon** — never reuse a section icon within one tool. Same tool across DCCs = the same icon file.
32. **Per-section identity accent colours**: section header bars + section icons use a *palette* of identity
    colours (orange `#E8820C`, teal `#46C2D6`/`#34B3A0`, blue `#4F9DE0`, purple `#9B7EDE`, pink `#E070A8`,
    coral `#E8694A`, gold `#F2C14E`) — NOT all orange. (Rule 29's single-orange is about the ICON glyph, not section bars.)

## VI. RENDERING CORRECTNESS (the clean look)
33. **Kill Qt's etched/embossed disabled-text** via a `_FlatTextStyle` `QProxyStyle` that reimplements
    `drawItemText()` to paint flat text; **badges are hand-painted flat** (`_FlatBadge`) so they don't emboss.
34. **Nuke / Qt5**: apply styles **widget-level** (PySide2 ignores app-level objectName QSS); icon/arrow PNGs
    must be written to a **space-free path** (Qt5 `url()` silently fails on spaces, e.g. "Evil Knight").

## VII. LAUNCH BEHAVIOUR
35. **Auto-update on launch**: every tool runs `pxl_update.check(channel="stable", dcc=...)` on open (deferred), with a one-click update offer.
36. **Version-aware window singleton**: relaunch raises the same-version window or closes+rebuilds a newer one; the window is tagged with its version (objectName/property) so "Update" always shows the latest.
37. **Standard defaults established on launch** (not restored from stale prefs) — sensible starting state every open.
38. **Naming**: `PXLtools_<Tool>_v<MAJOR>_<MINOR>_<PATCH>[_stage].py`; filename = the real version; superseded versions go to `_OLD/`. One active file per tool per scripts dir.

## VIII. GUIDE PAGE (web)
39. Every tool has an online guide under the PXLsuite site `/guides/`, reusing `website/styles.css`: hero (name + versions) → Overview → Status & Roadmap → Download/Install (or "join the beta" for private) → How to use (current screenshots) → Troubleshooting. Hub card shows the tool icon + Public/Private-beta status.

## IX. VERIFICATION GATE — never deliver approximate work
40. Before "done": it parses; **render the real result and LOOK** (Maya offscreen / `Nuke --tg`; icons at 96+256; pages in a browser); for step-gating, **drive the state machine** to prove the transitions (a static render can't exercise click handlers); compare side-by-side with TurnTable; independent review; THEN report done.

---

## PER-TOOL COMPLIANCE CHECKLIST (every tool, every tab)
- [ ] Workflow understood (asked the user if unclear) before designing.
- [ ] `pxlt.tool_qss()`; ZERO hard-coded colours.
- [ ] `pxlw.AppHeader`; folder-style numbered tabs; INSTRUCTIONS section on top.
- [ ] Collapsible sections, distinct icons, per-section accent colour; shared objectNames for all controls.
- [ ] Universal hover; themed sliders/spin-boxes/combos; segmented toggles; danger actions red; status pills; warning banners.
- [ ] Every numbered procedure gated: LOCKED(disabled grey) → ACTIVE(orange outline) → DONE(green ✓), from reality.
- [ ] Completed section collapses (once) + next opens; ANY section reopens on click; reopened controls enabled; editing re-locks later steps.
- [ ] `_FlatTextStyle` emboss-kill + flat badges; (Nuke) widget-level styles + space-free icon paths.
- [ ] Auto-update on launch; version-aware singleton; launch defaults; correct file naming.
- [ ] Tool icon + section icons distinct, on the locked tile, 96 + 256.
- [ ] Online guide page.
- [ ] Render-and-look + drive-the-state-machine verified vs TurnTable.

---

## MIGRATION MILESTONE LIST (bring every tool to these commandments, one at a time)
- [x] TurnTable Builder (Maya) — the reference.
- [x] TurnTable Comp Setup (Nuke) — the reference.
- [~] GLB Manager — IMPORT (4-step) done; EXPORT to full §IV (collapse-on-complete + reopenable) — in progress.
- [ ] PBR Material · [ ] Advanced Batch Renamer · [ ] Render Layer Creator · [ ] OBJ Exporter.
- [ ] (later) Animatic · AI Assistant (mAIa) · Camera Matchmaker · Contact Sheet (Nuke) · Image Option Changer (Nuke) · MU Bridge (Unreal).
