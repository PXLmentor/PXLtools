# PXLtools — THE STANDARD (single source of truth)

> This is the contract. Every tool, every icon, every guide page MUST follow it.
> If two PXLtools windows sit side by side, they must look like the SAME product —
> same colours, same header, same sections, same buttons, same guided flow.
> Canonical reference implementations:
> - Maya UI + step-gating: `maya/scripts/PXLtools_TurnTable_Builder_v1_0_28.py`
> - Nuke UI + step-gating: `nuke/scripts/PXLtools_TurnTable_Comp_Setup_v1_1_27.py`
> - Shared kit: `shared/pxl_ui/` (`theme.py`, `widgets.py`, `icons.py`)
> Nothing here is optional. "Looks close" is not compliant. Render-and-look before delivering (§6).

---

## 1. Colours — the kit ONLY, never hard-code

Every colour comes from `pxl_ui.theme` via `pxlt.c("<token>")`. **Zero inline/hard-coded
colours** in any tool (`setStyleSheet("background-color: #333333")` is a BUG — delete it).
A tool styles itself by applying `pxlt.tool_qss()` once on the dialog and using the shared
`objectName`s (§3). The locked palette:

| Token | Hex | Use |
|---|---|---|
| `window` | `#333333` | dialog background |
| `header_bar` | `#262626` | top branding bar |
| `surface` | `#3a3a3a` | section body (`#sectionFrame`) |
| `surface_alt` | `#404040` | nested panels |
| `section_head` | `#454545` | collapsible header (rest) |
| `section_hover` | `#4f4f4f` | collapsible header (hover) |
| `hairline` | `#262626` | dividers / borders |
| `accent` | `#E8820C` | PXL orange — the ONE accent |
| `accent_hover` | `#FF9A2E` | orange hover |
| `accent_press` | `#C96E08` | orange pressed |
| `on_accent` | `#241606` | text/icon on an orange fill |
| `text` | `#E6E6E6` | body text |
| `text_muted` | `#A8A8A8` | secondary |
| `text_dim` | `#7A7A7A` | hint |
| `ok` | `#5BBF6A` | DONE green |
| `warn` | `#E8B84B` | warning |
| `error` | `#E4604A` | error |

Maya = apply `tool_qss()` app/dialog-level (PySide6). Nuke = same VALUES applied widget-level
(PySide2 ignores app-level objectName QSS) — use the shared widget factories; never re-tune.

---

## 2. Window structure — identical across every tool

```
QWidget#PxlRoot
 └─ pxlw.AppHeader(tool_name, version, icon_path)   # SHARED. No bespoke header. Ever.
 └─ body
     └─ pxlw.CollapsibleSection(...)   # one per logical section, grey header + 3px accent bar + icon + chevron
         └─ controls (shared widgets / shared objectNames)
```

- Header: **always** `pxlw.AppHeader`. A tool must NOT build its own header widget with its own
  colours (this is exactly the GLB bug). The header shows the tool icon + "PXLtools <Tool>" + version.
- Sections: `pxlw.CollapsibleSection` (or the shared `_make_section_frame` for always-open). Body
  objectName `sectionFrame`. Accent bar uses `accent`.
- Controls use the shared `objectName`s so `tool_qss` styles them — never per-widget colour:
  - Buttons: `btnPrimary` / `btnApply` / `btnAction`, danger `PxlDanger`/`btnDestruct`,
    segmented `PxlSeg`/`btnToggleActive`/`btnToggleInactive`.
  - Labels: `ctrlLabel` (field label), `hint` (small note), status `statusOk`/`statusIdle`/`statusWarn`/`statusErr`.
  - Step widgets: see §4.
- Combos: rely on `tool_qss` ONLY (single arrow). No per-widget `QComboBox` QSS.

---

## 3. Guided step-gating — MANDATORY for every numbered procedure (idiot-proof)

Any sequence of actions a user must do in order (browse → set → import → build → …) is a GATED,
NUMBERED flow. The user is walked through it and **cannot act out of order**. Three states, derived
from REALITY (already-satisfied steps come up green; the flow rests on the first unfinished step):

| State | Meaning | Button objectName | Badge objectName | Look |
|---|---|---|---|---|
| **LOCKED** | not this step's turn | `btnStepLocked` | `stepLocked` | muted grey, **`setEnabled(False)`** — literally un-clickable |
| **ACTIVE** | do THIS now | `btnStepActive` | `stepReady` | **orange outline**, enabled |
| **DONE** | completed | `btnStepDone` | `stepDone` | **green** + `✓` (right-side `stepConfirmDone`) |

Rules:
1. Steps are numbered `1, 2, 3 …` with a numbered badge (`stepReady`/`stepLocked`/`stepDone`) + a `stepTitle`.
2. The parent `CollapsibleSection` reflects progress: `set_state('idle' | 'active' | 'done')`
   (orange accent when active, pale-green + header ✓ when done).
3. A step advances to DONE only on **clean success** of its action (verify the real result, return bool).
4. On reset/clear, recompute all states from reality.
5. Use the shared helpers from the reference tool — do NOT reinvent:
   `_mk_step_header(...)`, `_set_step_btn(btn, state)`, `_set_badge(lbl, state)`, `_set_confirm(lbl, done)`,
   and a per-area `_update_<area>_steps()` state machine wired at each real success point.
6. Future steps are disabled (`setEnabled(False)`) — not just greyed visually.

The instruction copy must say it plainly, e.g.: "Follow the numbers — the orange step is what to do
next, and it turns green when it is done."

---

## 4. Icons — one family, built on the locked tile

- **Locked base tile** (never changes): squircle `rx 57.6`, vertical gradient `#2c2c30 → #141416`,
  2px inner edge `#3a3a40`. Source of truth: the TurnTable anchor
  `maya/scripts/icons/icon_turntable_builder.svg`. Build every icon by dropping art onto this exact tile.
- **Object = the noun** (what the tool acts on): greyscale, top-lit, family greys
  `#d6dbe2` (lit) → `#969ca6` (mid) → `#686d77` (shadow), `#ecf0f5` top-edge light.
  Letters are allowed for file-format tools (GLB, OBJ) using the same greyscale top-light gradient.
- **Accent = the verb** (what the tool DOES): exactly ONE `#E8820C` element. One idea only.
- **Sizes/format:** `icon_<slug>.png` at **96px** (DCC-facing, the legibility gate) + **256px** (hero),
  RGBA, transparent outside the squircle. SVG source kept in `maya/scripts/icons/`.
- **Every tool has its own icon.** Same tool across DCCs = the SAME icon file (e.g. TurnTable Maya +
  Nuke both use `icon_turntable_builder.png`).
- Gate at 96px first: silhouette reads, accent ≥ ~4px, nothing finer than ~3px, no text on non-format tools.

Method: author SVG on `J:\tmp\icon_family\_BASE\tile_base.svg` (verbatim base) → render 96 + 256 with Inkscape.

---

## 5. Web guide pages — one system

- Live online under the PXLsuite site `/guides/`, reusing `website/styles.css` (no new design language).
- Hub lists every tool as a card with its **tool icon** + status (Public / Private beta).
- Each tool guide: hero (name + versions) → Overview → **Status & Roadmap** (done / in progress / planned)
  → Download & Install (public links, or "join the beta" for private) → How to use (with interface
  screenshots) → Troubleshooting. Screenshots are real renders of the current UI.

---

## 6. Verification gate — never deliver approximate work

Before saying a tool/icon/page is done:
1. It compiles / parses.
2. **Render the real result and LOOK at it** — Maya offscreen render or `Nuke --tg`; for icons render
   96+256; for pages render the HTML. Compare side-by-side with the reference (TurnTable) for colour +
   structure + step-gating parity.
3. Independent review pass (code-reviewer) before commit.
4. Only then report done.

"I matched the theory / it should be the same" is NOT verification. See global CLAUDE.md §3.5.

---

## Compliance checklist (run for EVERY tool)

- [ ] Applies `pxlt.tool_qss()`; ZERO inline/hard-coded colours anywhere.
- [ ] Header is `pxlw.AppHeader` (no bespoke header).
- [ ] Sections are shared `CollapsibleSection`; controls use shared objectNames.
- [ ] Every numbered procedure is gated: LOCKED(disabled)→ACTIVE(orange)→DONE(green), state from reality.
- [ ] Combos single-arrow (tool_qss only).
- [ ] Tool has its own family icon (96 + 256) built on the locked tile.
- [ ] Has an online guide page on the standard.
- [ ] Render-and-look verified against the TurnTable reference.
