# Nuke Toolbox — VFX Tools
# Sub-context for J:\ClaudeCode\projects\PXLtools\nuke\
# Parent project context: J:\ClaudeCode\projects\PXLtools\CLAUDE.md (identity, versioning, engineering standards)

---

## 05 · Nuke Toolbox

**DCC:** Foundry Nuke 15 | Python 3 | PySide2 (PySide6 fallback) | ACES 1.2

### Nuke Deployment Paths
| Content          | Location                                                      |
|------------------|---------------------------------------------------------------|
| Scripts & icons  | `C:\Users\Evil Knight\.nuke\PXLmentorToolbox\scripts\` / `icons\` |
| `menu.py`        | `C:\Users\Evil Knight\.nuke\menu.py`                          |
| `init.py`        | `C:\Users\Evil Knight\.nuke\init.py`                          |

> **Deployment rule:** After updating any Nuke script, copy it to the correct deployment folder above AND update `menu.py` / `init.py` if needed. **Always ask the user for permission before copying to any live `.nuke` path.**

| Tool                    | Status | Notes                                     |
|-------------------------|--------|-------------------------------------------|
| Contact Sheet Generator | ALPHA  | v0.6.1-alpha — next step: 0.9.0-beta pass |
| Image Option Changer    | BETA   | v0.9.1-beta                               |
| TurnTable Comp Setup    | ALPHA  | v1.1.0-alpha CP042 — flat TB3DTT group, per-node JSON state, reconnect+viewer, export section, Write_TT at root |

### Contact Sheet Generator — Architecture
- **Folder structure:** `main_folder / Set_A / Item_001 / [image sequence]`
- **Node graph:** Read nodes → ContactSheet node → Write node
- **Backdrop z-order:** MUST use `z_order` knob directly (`0` = set backdrop, `1` = page backdrop) — do NOT infer from creation order
- **ContactSheet resolution** = total output frame size, NOT per-cell size
- **`frame_increment`** is a `nuke.execute()` argument — NOT a Write node knob
- **Colorspace dropdown:** filter to top-level roles only (exclude deep "Colorspaces" subfolder entries)
- **Set selection dialog:** pre-tick all sets, user deselects unwanted ones
- **Backdrop hierarchy:** each page gets inner backdrop; all pages per set wrapped in outer set backdrop
- **Dialog type:** PySide2 `QDialog` — do NOT use `nukescripts.PythonPanel` (modal stack collision)
- **Prefs stored at:** `~/.nuke/PXLmentorToolbox/`

**Next step:** Beta release pass — validate output quality end-to-end, then bump to `0.9.0-beta`.

---

## Nuke — Known Bugs & Gotchas

| Issue                   | Resolution                                                        |
|-------------------------|-------------------------------------------------------------------|
| Backdrop z-order        | Set via `z_order` knob (0=set, 1=page) — NOT creation order      |
| `frame_increment`       | Argument to `nuke.execute()` — NOT a Write node knob             |
| ContactSheet resolution | Total output frame size — NOT per-cell size                       |
| Set Selection dialog    | Pure PySide2 `QDialog` — `nukescripts.PythonPanel` causes modal collision |
| Colorspace dropdown     | Filter to top-level roles only — exclude deep subfolder entries   |
| TCL expressions / setValue | Knobs with `[value TT_Settings.xxx]` expressions silently ignore `setValue()`. ALWAYS call `_clear_expressions(k)` (which calls `k.clearAnimated(i)` per component) before any `setValue()` on a knob that may carry a TCL expression. |
| TT_Settings disable knobs | User knobs use non-standard names — use the originals: `disable_1` (link knobs), `lensDirtDisable` (Merge21), `disableLUT` (OCIOFileTransform2). Do NOT use the node's built-in `.disable`. Full map in project memory `project_ttcs_knobs.md`. |
| Group-level disable knobs | `TEXT_INFO_grp.disable_1`, `REFERENCES_grp.disable_1`, `REFERENCES_grp.disable_1_1` are set on the **group node itself** via `_set("GROUP_NAME", "knob", val)` — NOT via `_set_in()` (which enters the group context). |
| v005 flat group | All comp nodes live inside a single `TB3DTT` group — no sub-groups. `_set()` and `_get_knob_value()` enter `TB3DTT` context automatically via `_MAIN_GRP`. Node renames: `Mode_Switch` → `Switch_Mode`, `DISABLE_OCC` → `DISABLE_OCC1`. Only one `SwitchHDRI` (not two clones). Ref05/06 disable targets `ref_05.disable` / `ref_06.disable` directly. |
| Modeless PySide2 dialog | Use `show()` not `exec_()`. Store a module-level reference (`_dialog_instance`) to prevent GC. Add `WA_DeleteOnClose`. |
| SwitchHDRI in v005 | ONE node in v005 flat group — do NOT set twice. v004 had two clones. |
| Write_TT at root | Created at Nuke root level (outside TB3DTT). Access with `nuke.toNode("Write_TT")` — no group context. `create_dir=True` always set. |
| Reconnect flow | `_restore_node_state()` sets `_block_live=True` — must call `_push_ui_to_comp()` after to sync comp. `_read_write_node_state()` falls back to reading existing Write_TT node path. |
| Per-node state knob | `pxl_tt_panel_state` invisible String_Knob on TB3DTT — stores full panel state as JSON. Travels with .nk file. `_on_write_changed()` MUST call `_schedule_node_save()` or export fields are lost on reconnect. |
| Node indicator bar | Always-visible bar between header and scroll area. NOT inside the scroll widget. Reconnect also calls `nuke.connectViewer(0, grp_node)`. |
| Auto write name | `_auto_write_name()` assembles: `{TYPE}_{name}_{dept}_{ver}_{user}_TT_HDRI{XX}_{Mode}` — full comp asset name + TT suffix. Called when asset fields or HDRI/mode change. |

---

## Nuke — Environment

| Component | Details |
|-----------|---------|
| Nuke      | Foundry Nuke 15 — Python 3, PySide2 (PySide6 fallback) |
| Rendering | ACES 1.2 (official Academy OCIO config) |
| Nuke Prefs | `~/.nuke/PXLmentorToolbox/` |

---

## Nuke Tool Catalog

### Contact Sheet Generator
- **File:** `nuke/scripts/PXLmentor_ContactSheet_Generator_v0_6_1_alpha.py`
- **Status:** ALPHA (v0.6.1-alpha) — next step: 0.9.0-beta pass
- **Description:** Generate contact sheets from folder-structured image sequences. Builds Read → ContactSheet → Write node graph with hierarchical backdrop layout. Per-cell label overlay via Text2 node with configurable token-stripper.

### Image Option Changer
- **File:** `nuke/scripts/PXLmentor_ImageOption_Changer_v0_9_1_beta.py`
- **Status:** BETA (v0.9.1-beta)
- **Description:** Batch-change the colorspace (input option) on selected Read and/or Write nodes. Reads available colorspaces from the active OCIO config; ACES 1.2 curated fallback when PyOpenColorIO is unavailable.

### TurnTable Comp Setup
- **File:** `nuke/scripts/PXLmentor_TurnTable_Comp_Setup_v1_1_0_alpha.py`
- **Status:** ALPHA (v1.1.0-alpha) — CP042
- **Description:** Branded PySide2 panel — drives all comp nodes directly with real-time live updates. v005 comp (flat TB3DTT group, no sub-groups). Layout: Header → Node Indicator Bar (always visible, pinned) → Scroll area with COMP SETUP / VISUAL OPTIONS / COMP EFFECTS / TECH SETTINGS / REFERENCES / EXPORT collapsibles → Status bar → Close bar. COMP SETUP has three sequential sub-collapsibles (Import Template → Render Location → Asset Info) that auto-collapse on step completion. EXPORT closes all other sections when opened. Multi-node: Reconnect rebinds to selected Group node, restores full panel state from `pxl_tt_panel_state` JSON knob on TB3DTT, pushes all values to comp, connects viewer. Write_TT created at root level. Auto write name: `{TYPE}_{name}_{dept}_{ver}_{user}_TT_HDRI{XX}_{Mode}`. Per-node state persisted as invisible String_Knob on TB3DTT. Prefs: `~/.nuke/PXLmentorToolbox/tt_comp_setup_prefs.json`. Comp template: `D:\TB3DTT\TurnTable_ROOT\_COMP\PXLmentor_TB3DTT_COMP_v005.nk`.
