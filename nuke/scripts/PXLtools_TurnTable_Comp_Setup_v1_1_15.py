# ==============================================================================
# Tool Name:   PXLtools TurnTable Comp Setup
# Version:     1.1.15
# Checkpoint:  CP073
# Author:      PXLsuite / BlackMamba3D
# Description: Live control panel for the TurnTable comp. Drives comp nodes
#              directly — no TT_Settings relay, no Apply button.
#
# Platform:    Nuke 15 (Python 3) | PySide2
#
# Changelog:
#   1.1.15      - CP073 - Nuke parity batch (part 1): default BG colour white +
#                         wire colour cyan; Asset Info icon image->box; Export PNG
#                         default; Write node 'create directories' set robustly (tries
#                         create_directories/create_dir) so render makes the folder; added
#                         'double-click the Write node and click Render' instruction.
#                         (Deferred to part 2: combo centre-arrow, no-folder->instructions,
#                         preliminary icon, render-location green-when-set, references load
#                         button, MP4 export, RGB colourspace default, output capsule.)
#   1.1.14      - CP072 - Rebrand/rename — file is now
#                         PXLtools_TurnTable_Comp_Setup_v1_1_14.py (PXLtools prefix +
#                         real version in filename, under the PXLsuite umbrella);
#                         header tool-name -> "PXLtools TurnTable Comp Setup".
#                         Nuke toolbox deploy folder renamed PXLmentorToolbox -> PXLtools.
#                         (drawItemText flat-paint + 92x32 buttons from earlier this version.)
#   1.1.14      - CP071 - Drop-shadow on ENABLED text killed for good: _FlatTextStyle
#                         now reimplements drawItemText() to paint flat text, so the
#                         host (Nuke) style can't add a shadow/etch to ANY font.
#                         Inline action buttons standardized to one size (Browse… /
#                         Auto / Auto-fill all 92x32) + min-width:84 floor on _BTN/_BTN2
#                         so no button renders narrower than its siblings.
#   1.1.13      - CP070 - Expandable-section triangle is now a same-size chevron
#                         ICON (identical closed/open, no glyph size jump);
#                         combo down-arrow reverted to single right arrow (centre
#                         arrow removed); preliminary Check-ACES / Set-Working-Folder
#                         buttons turn pale-green 'done' on success (Maya parity);
#                         etched disabled-text emboss ('drop shadow') removed via
#                         _FlatTextStyle proxy; Vignetting Intensity default 0.25.
#   1.1.12      - CP069 - Cross-tool consistency: combo down-arrow pinned right
#                         (no centre arrow); Tech Settings uses the same icon as
#                         Maya Utilities; Render Location is now a numbered
#                         sequence — 1 Browse Render Location, 2 Apply Project
#                         Settings — both grey+orange-border -> green+check when
#                         done (Apply button restyled from the green one-off).
#   1.1.11      - CP068 - UI sanity-check pass: node bar grey (not black) + _BTN2
#                         reconnect, taller (no crop); preliminary reordered ACES(1)
#                         -> Working Folder(2); removed confusing 'paste template'
#                         copy; Project Settings box grey + Format/FPS two-column +
#                         wider frame spinboxes; combo stray middle arrow fixed
#                         (dropped margin-right); Activate Comp Effects toggle moved
#                         under Wire Color; COMP EFFECTS -> COMP EFFECTS SETTINGS;
#                         Z-Defocus sub-panels grey; Vignetting Intensity labelled;
#                         cropped numeric fields widened (55->72, ref 70->80);
#                         Create Write Node -> shared btnStepActive style.
#   1.1.10      - CP067 - Visual Options now two columns (combos | colours) to
#                         shrink height. Standardized bluish #1a1a2a comp-effects
#                         sub-panels + stray italic notes to the shared grey/hint.
#   1.1.9       - CP066 - Preliminary steps brought to Maya parity: numbered
#                         badges (1 Set Working Folder, 2 ACES) that turn green
#                         with a check when done; Set/ACES buttons gray+orange-
#                         border (btnStepActive).
#   1.1.8       - CP065 - Parity fixes: Load Template button now gray+orange-
#                         border (Maya btnStepActive); Asset Type/Dept dropdowns
#                         show readable examples (CHR · Character) storing the
#                         bare code; Auto-fill widened for its font; standardized
#                         bluish header/version + italic info labels to the shared
#                         grey/hint values.
#   1.1.7       - CP064 - Guided-flow transpose: COMP SETUP sub-steps (1 Import
#                         Template, 2 Render Location, 3 Asset Info) now show the
#                         Maya-style section state - orange ACTIVE -> pale-green
#                         DONE (+ header check) wired into the existing sequential
#                         advance points. Full visual parity with Maya.
#   1.1.6       - CP063 - Slider bar lightens on hover (forced repaint via
#                         'hov' property); slider fixed height so the ring isn't
#                         cropped.
#   1.1.5       - CP062 - Slider handle = PNG (round): white dot + orange RING
#                         on hover; both bar halves brighten on hover.
#   1.1.4       - CP061 - Slider handle: round orange-on-hover (the bordered
#                         ring rendered square in PySide); bar lightens on hover.
#   1.1.3       - CP060 - Hover feedback parity: combo dropdown + spin
#                         buttons lighten the button area; slider handle gains
#                         an orange ring + bar lightens; section headers lighten
#                         on hover.
#   1.1.2       - CP059 - FIX: spin/combo arrows -> real PNG chevrons (border-
#                         triangles render as squares in PySide). Grey default,
#                         white on hover. self._FIELD built with the PNG paths.
#   1.1.1       - CP058 - Arrow hover parity: spin-box + combo arrows now
#                         lighten to white on mouse-over (border-triangles,
#                         same as Maya). Inherits the shared-theme arrow/folder-
#                         tab update (Nuke has no tabs, so tabs are a no-op here).
#   1.1.0       - CP057 - Maya-parity pass (foundation). Fixed the missing
#                         spin-box up/down arrows (inline triangles, reliable in
#                         Nuke) + neutralised the new __SPINUP__/__SPINDOWN__
#                         theme placeholders. Added CollapsibleSection.set_state
#                         (orange active / pale-green done + header check) and
#                         set_collapsed, plus the numbered guided-step factories
#                         (_mk_step_header/_set_badge/_set_step_btn/_set_confirm)
#                         with inline styles byte-for-byte matching the Maya
#                         theme. NEXT: wire the numbered orange->green flow into
#                         the COMP SETUP steps so the experience is identical.
#   1.0.0       - CP056 - Identical to Maya: applies the shared
#                         pxl_ui.theme.tool_qss() (same stylesheet), widget
#                         factories use the same objectNames (btnPrimary,
#                         statusOk...) and drop inline styles. Import button
#                         -> flat primary "Load Turntable Template".
#   1.0.0       - CP055 - First public release (dropped alpha/beta). Full
#                         Maya parity: identical section headers (accent
#                         bar + icon + number + name + right triangle,
#                         grey bg), shared clapperboard setup icon,
#                         de-orange combo, pxl_ui force-reload.
#   1.3.5-alpha - CP054 - Slider unfilled line now black (orange + black
#                         line, white dot separator). Distinct scene icon
#                         via shared pxl_ui (clapperboard).
#   1.3.4-alpha - CP053 - Slider track fully transparent (orange fill +
#                         white circle only). Header logo+name centre in
#                         the space right of the tool icon (spacer removed).
#   1.3.3-alpha - CP052 - Slider = transparent track (thin orange/dark
#                         line) + plain white circle handle. Header logo
#                         ~50% larger, width-scaled, name centred beneath.
#   1.3.2-alpha - CP051 - UI polish: borderless clean section headers (no
#                         under-line), refined sliders (deeper groove,
#                         bordered white handle), lighter column labels,
#                         flat header bg.
#   1.3.1-alpha - CP050 - Full body restyle to the approved pxl_ui preview.
#                         Style constants (_BTN/_FIELD/_CHK/_SLD/...) rebuilt
#                         on the theme palette; theme.build_qss() applied to
#                         the dialog; tick checkboxes; BODY_BG -> #333.
#   1.3.0-alpha - CP049 - New shared pxl_ui UI kit: AppHeader logo header
#                         and colour-coded icon section headers (parity
#                         with Maya TurnTable Builder v1.2.0). PySide2/6
#                         handled by pxl_ui.compat.
#   1.2.1-alpha - CP048 - In-tool header logo swap. _build_header() now loads
#                         PXLtools_logo.png (the PXLtools wordmark) into the
#                         220x52 logo slot instead of PixelMentor_Logo_Long.png.
#                         Fallback text label changed from "PXLsuite" to
#                         "PXLtools" to match. Tool name "TurnTable Comp Setup"
#                         and the live-mode subtitle stay as is.
#   1.2.0-alpha - CP047 - Rebrand pass — tool belongs to PXLtools (under
#                         PXLsuite, BlackMamba3D umbrella), not PXLmentor.
#                         Renamed file to
#                         PXL_TurnTable_Comp_Setup_v1_2_0_alpha.py. Internal
#                         window title, logger name, UI logo label, and
#                         icon reference swept. Icon switched from
#                         "PXLmentor_TurnTable_Comp_Setup.png" to
#                         "icon_turntable_builder.png" — same icon as the
#                         Maya tool button (one tool, one face). Internal
#                         ~/.nuke/PXLmentorToolbox/ path preserved (sibling
#                         tools depend on it). COMP_TEMPLATE_FILENAME on
#                         disk preserved.
#   1.1.4-alpha - CP046 - Working Folder restored to _COMP semantics (v1.1.1
#                         and earlier behaviour). The Working Folder field
#                         must point at TurnTable_ROOT/_COMP — every relative
#                         path the tool uses (template .nk, HDRI_previews/,
#                         Dirt/, LUT/, tt_session.json) lives directly
#                         inside that folder, so {working_folder} is the one
#                         and only root the tool needs. Nothing hardcoded:
#                         the comp template is resolved as
#                         {working_folder}/PXLmentor_TB3DTT_COMP_v005.nk on
#                         every import. UI hint, placeholder, default text
#                         and validation message restored to the _COMP wording.
#                         _session_path() no longer prepends _COMP; the
#                         session lives at {working_folder}/tt_session.json
#                         again.
#   1.1.3-alpha - CP045 - Working Folder semantics updated to match v1.1.2's
#                         template lookup: Working Folder now points to
#                         TurnTable_ROOT (the parent), not TurnTable_ROOT/_COMP.
#                         UI hint, placeholder text, default text, and the
#                         validation status message all updated. Validation
#                         now confirms the working folder contains a _COMP/
#                         subdir (sanity check for the right level). The
#                         session file tt_session.json continues to live at
#                         {working_folder}/_COMP/tt_session.json — _session_path()
#                         was updated so load and save both keep that location,
#                         preserving existing session files in place.
#   1.1.2-alpha - CP044 - Template path derived from Working Folder. The
#                         hardcoded D:/TB3DTT/... path is gone — the tool now
#                         resolves the comp template as
#                         {f_proj_dir}/_COMP/PXLmentor_TB3DTT_COMP_v005.nk on
#                         every import. Stops the "Template not found" error
#                         when the project lives on a different drive than
#                         whoever first wrote the script. The old global
#                         COMP_TEMPLATE_PATH is replaced by
#                         COMP_TEMPLATE_RELATIVE (the relative tail only).
#                         If Working Folder is empty, the import is refused
#                         with a clear status message instead of pasting from
#                         a stale path.
#   1.1.1-alpha - CP043 - LUT default OFF. Every LUT default in the tool flips to
#                         disabled: the UI checkbox starts unchecked, the prefs
#                         fallback default is False, and _push_defaults_to_comp()
#                         now sets chk_lut to False and calls
#                         live_lut_disable(True) so the OCIOFileTransform2 node
#                         is bypassed on a fresh template import. Stops the
#                         "no LUT file selected" error that was firing every
#                         build. Saved prefs with an explicit lut_en=True are
#                         still respected on next launch.
#   1.1.0-alpha - CP042 - UI REDESIGN: Step-card system replaced with flat collapsible layout.
#                         COMP SETUP collapsible groups import/folder/asset setup.
#                         Customization sections (Visual, Comp Effects, Tech, Refs) are the
#                         main body. EXPORT collapsible for Write node.
#                         MULTI-NODE: _G() / set_active_group() — Reconnect binds to the
#                         currently selected Nuke group node. Active comp shown in header bar.
#                         ZDefocus: Output dropdown (Result / Focal Plane) added.
#                         COMBO FIX: dropdown button now orange — clearly visible on dark bg.
#   1.0.0-alpha - CP041 - COMP v005 support: flat TB3DTT group replaces all sub-groups.
#                         All node accessors now enter TB3DTT context via _MAIN_GRP.
#                         Mode_Switch renamed Switch_Mode, DISABLE_OCC renamed DISABLE_OCC1.
#                         SwitchHDRI deduped (one node only). Ref05/06 disable now
#                         targets ref_05/ref_06.disable directly. COMP_TEMPLATE_PATH
#                         updated to v005. Write_TT created inside TB3DTT group.
#                         Viewer reconnects to TB3DTT group node (not END_COMP).
#   0.9.9-alpha - CP019 - FIX: Autofill now calls live_asset_text directly (bypasses
#                         _live wrapper) and reports success/failure explicitly in the
#                         status label. live_asset_text returns bool. Status shows the
#                         assembled string ("CHR_Scion_shd_v001_csp") and whether the
#                         comp Text_Info node was updated or why it wasn't.
#   0.9.8-alpha - CP018 - REMOVED: Check Connection button from Step 3. Step 3
#                         now auto-completes (collapses to ✓) as soon as Asset
#                         Name and Version are both non-empty — via manual entry
#                         or Auto-fill. The Update/Reconnect button in Step 1
#                         handles connection verification.
#   0.9.7-alpha - CP017 - UI: Step cards are now collapsible. Done steps auto-collapse
#                         to their header. Active step auto-expands. Locked steps stay
#                         closed. Click any header to re-open a completed step.
#                         Arrow indicator (▼/▶) shows expand state per card.
#   0.9.6-alpha - CP016 - FIX: Text node inside TEXT_INFO_grp is "Text_Info", not
#                         "AssetName" — live_asset_text and _read_comp_state
#                         corrected; _REQUIRED_NODES updated.
#                         FIX: Write_TT removed from _REQUIRED_NODES — it is created
#                         by the tool, not present in the imported template.
#                         NEW: Reconnect button in Step 1 — shown after import so
#                         user can re-sync UI when reopening tool on an existing scene.
#                         UI: Format + FPS visually grouped in a settings inset box.
#   0.9.5-alpha - CP015 - NEW: Step 2 now sets Format, FPS, and Frame Range in one
#                         "Apply Project Settings to Comp" button. Format combo
#                         populated dynamically from nuke.formats(), defaults to
#                         HD_1080. FPS options: 23.976/24/25/29.97/30/48/50/59.94/60,
#                         defaults to 25. Autofill now reports exact basename parsed
#                         and explains why it failed (no subfolders vs bad name).
#                         Import Template also auto-sets Nuke project directory from
#                         Preliminary Steps. Frame Range button enlarged + renamed.
#   0.9.4-alpha - CP014 - NEW: Guided 4-step UI with progressive-unlock workflow.
#                         Step 1 (Import Template) is the protagonist on first launch.
#                         Steps 2-4 are locked/dimmed and unlock sequentially.
#                         Step 4 (Make It Yours) unlocks with Step 1, not Step 3.
#                         Circle badges (①②③④ → ✓) show state per step.
#                         Check Connection moved into Step 3 (Asset Info).
#                         Import Template button enlarged to 48px primary CTA.
#   0.9.3-alpha - CP013 - FIX: Autofill now populates TYPE and DEPT (scan_render_folder
#                         was not returning type_code/dept_code).
#                         FIX: Reference images now visible — DISABLE_Multiple_REF
#                         inside REFERENCES_grp also toggled with ref images checkbox.
#                         FIX: No missing-node errors shown before template is imported;
#                         _template_loaded flag gates _refresh_connection_status.
#                         Check Connection button always force-checks.
#                         NEW: Session config saved to _COMP/tt_session.json on folder
#                         set; loaded on next launch if folder is already configured.
#                         NEW: Instructions section auto-collapses after working folder
#                         is successfully set for the first time.
#   0.9.2-alpha - CP012 - NEW: Asset Info section redesigned — TYPE combo (CHR/ENV/PRO/VHC),
#                         dept combo, user field, live color-coded naming preview.
#                         FIXED: ACES check uses nuke.root().knob('colorManagement') — if OCIO = ACES 1.2.
#                         FIXED: Naming convention assembled and pushed as single string to Text2 node.
#                         UPDATED: _parse_asset_info returns type_code and dept_code.
#   0.9.1-alpha - CP011 - FIXED: "Open Template" now creates a new Nuke script
#                         and imports the template via nuke.scriptNew() +
#                         nuke.nodePaste(), instead of nuke.scriptOpen() which
#                         was replacing the entire Nuke session. Button renamed
#                         to "Import Template".
#   0.9.0-alpha - CP010 - NEW: Reference image slots completely redesigned as
#                         a 2×3 drag-and-drop card grid (_RefCard class).
#                         Each card is 16:9 aspect ratio, shows thumbnail
#                         (JPG/PNG/TIFF), EXR placeholder, orange border when
#                         loaded, green highlight on drag-over, × clear button,
#                         slot number label. Slots 05/06 have integrated "on"
#                         toggle in the card header. Contact Sheet and Single
#                         Reference controls are now header-row toggles.
#   0.8.0-alpha - CP009 - FIXED: node names updated to match v004 comp rename:
#                           Multiply1 → DISABLE_HDRI_GRP
#                           Multiply5 → DISABLE_ALL_REF
#                         Updated _REQUIRED_NODES, live setters, _read_comp_state.
#                         IMPROVED: Preliminary working folder now has Browse button
#                         + editable field (was hardcoded Set-to-_COMP button).
#                         FIXED: ACES check uses nuke.Root() (capital R).
#                         FIXED: ACES check only auto-runs on first dialog open
#                         per Nuke session (_aces_checked_once flag). Subsequent
#                         opens only check on button click.
#                         FIXED: ACES button now auto-sizes to text (no fixed width).
#                         IMPROVED: Write_TT section description clarifies Write_TT is
#                         a node inside the comp, not the comp file itself.
#   0.7.0-alpha - CP008 - NEW: Instructions collapsible at top with step-by-step
#                         workflow guide and nested Preliminary Steps.
#                         NEW: Preliminary Steps — Nuke project directory control
#                         (Set to _COMP + Refresh + status) and ACES 1.2 check.
#                         FIXED: _parse_asset_info now reliably strips type code
#                         (seg 0) and dept code (last pre-version seg) regardless
#                         of alphanumeric content — autofill works for TB3, RND,
#                         ANM, etc.
#                         IMPROVED: Write Node section — button renamed to
#                         "Apply Output Settings to Write_TT", description clarifies
#                         Write_TT is already in the template.
#   0.6.0-alpha - CP007 - FIXED: Tech Settings inversion — all 8 connections
#                         changed from (not v) to (v); _read_comp_state updated
#                         to use bool(val) directly for tech settings (comp
#                         effects keep not bool(val) — different node semantics).
#                         FIXED: launch() now guards against multiple instances —
#                         raises existing window if alive, only creates new dialog
#                         when previous is gone. Prevents RAM accumulation.
#                         NEW: After "Open Template", viewer auto-connects to
#                         END_COMP dot node.
#                         NEW: WRITE NODE section — set output folder (absolute),
#                         format (png/exr/tiff), colorspace, live path preview,
#                         and "Create / Update Write Node" button. Persisted
#                         in prefs. Preview updates live with version/hdri/render.
#   0.5.0-alpha - CP006 - FIXED: all comp effect / tech setting controls were
#                         writing to Link_Knob stubs (disable_1, lensDirtDisable,
#                         disableLUT) whose link expressions were cleared by
#                         _clear_expressions(), leaving the actual .disable knob
#                         untouched. Now targets the real knobs directly:
#                           Ramp       → Multiply3.disable
#                           Vignette   → Multiply4.disable
#                           HDRI Prev  → DISABLE_HDRI_GRP.disable
#                           Ref Images → DISABLE_ALL_REF.disable
#                           Occlusion  → DISABLE_OCC.disable
#                           Shadow     → DISABLE_SHD.disable
#                           Ref Ball   → DISABLE_REF.disable
#                           Text Info  → TEXT_INFO_grp/DISABLE_TEXT.disable
#                           ZDefocus   → ZDefocus1.disable
#                           Lens Dirt  → Merge21.disable
#                           LUT        → OCIOFileTransform2.disable
#                         UI: Tech Settings redesigned as 2-column grid
#                         (Visual | Extra Info), all ON by default.
#                         UI: "Ramp" renamed "Back Ramp",
#                             "Reference Ball" renamed "Balls & Charts".
#   0.4.0-alpha - CP005 - UI overhaul, inverted checkbox logic fix, removed
#                         Push All button, Visual Options collapsible.
#   0.3.0-alpha - CP004 - Fixed disable knob names, added frame range, colors.
#   0.2.0-alpha - CP002 - Full redesign: live mode, direct node control.
#   0.1.0-alpha - CP001 - Initial implementation.
# ==============================================================================

import os
import re
import json
import logging

import nuke

try:
    from PySide2 import QtWidgets, QtCore, QtGui
    PYSIDE_AVAILABLE = True
except ImportError:
    try:
        from PySide6 import QtWidgets, QtCore, QtGui
        PYSIDE_AVAILABLE = True
    except ImportError:
        PYSIDE_AVAILABLE = False

# ---------------------------------------------------------------------------
# pxl_ui shared kit bootstrap (binds to the already-loaded PySide2 in Nuke)
# ---------------------------------------------------------------------------
import sys
try:
    _here = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _here = ""
for _c in (
    _here,
    os.path.abspath(os.path.join(_here, "..", "..", "shared")) if _here else "",
    r"J:\ClaudeCode\projects\PXLtools\shared",
):
    if _c and os.path.isdir(os.path.join(_c, "pxl_ui")) and _c not in sys.path:
        sys.path.insert(0, _c)
try:
    import importlib as _il
    for _m in ("pxl_ui.compat", "pxl_ui.theme", "pxl_ui.icons", "pxl_ui.widgets"):
        if _m in sys.modules:
            _il.reload(sys.modules[_m])
    from pxl_ui import widgets as pxlw, icons as pxli, theme as pxlt
    _PXLUI = True
except Exception:
    _PXLUI = False

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("PXL.TurnTableCompSetup")

# ---------------------------------------------------------------------------
# Brand tokens
# ---------------------------------------------------------------------------
BRAND_ORANGE = "#E8820C"
HEADER_BG    = "#333333"
BTN_RESET_BG = "#525252"
STATUS_OK    = "#385838"
STATUS_ERR   = "#803838"
STATUS_IDLE  = "#383838"
STATUS_WARN  = "#5a4a10"

VERSION   = "1.1.15"
TOOL_NAME = "TurnTable Comp Setup"

# Comp template is resolved at import time relative to the Working Folder
# (which is the TurnTable_ROOT/_COMP folder itself). Nothing hardcoded — the
# tool works on any drive as long as the user points Working Folder at the
# correct _COMP directory.
COMP_TEMPLATE_FILENAME = "PXLtools_TB3DTT_COMP_v005.nk"

# v005: all comp nodes live inside this single top-level group
_MAIN_GRP = "TB3DTT"

# Multi-node support: artist can have multiple TB3DTT copies in the scene.
# _active_grp_name tracks which one the panel is bound to.
_active_grp_name = _MAIN_GRP


def _G() -> str:
    """Return the name of the currently active comp group node."""
    return _active_grp_name


def set_active_group(name: str) -> None:
    """Rebind the panel to a different TB3DTT instance."""
    global _active_grp_name
    _active_grp_name = name

FPS_OPTIONS = ["23.976", "24", "25", "29.97", "30", "48", "50", "59.94", "60"]
FPS_DEFAULT = "25"

HDRI_OPTIONS = [
    "01 - Studio", "02 - Day Overcast", "03 - Direct Sun", "04 - Cloudy Sun",
    "05 - Night", "06 - Night Neon", "07", "08",
]
RENDER_OPTIONS = ["Beauty", "Clay", "UV", "Wireframe"]
BACK_OPTIONS   = ["HDRI", "Color"]

ASSET_TYPE_CODES = ["", "CHR", "ENV", "PRO", "VHC"]
DEPT_CODES       = ["", "mdl", "tex", "shd", "dtl", "grm", "rig",
                    "cfx", "fx", "anim", "comp", "lgt", "enh", "edit", "grd"]

# Readable dropdown labels (same order as the *_CODES lists so index-based
# save/restore is unchanged) — code stored as item data.
ASSET_TYPE_PAIRS = [("", "— Type —"), ("CHR", "CHR · Character"),
                    ("ENV", "ENV · Environment"), ("PRO", "PRO · Prop"),
                    ("VHC", "VHC · Vehicle")]
DEPT_PAIRS = [("", "— Dept —"), ("mdl", "mdl · Model"), ("tex", "tex · Texture"),
              ("shd", "shd · Shader"), ("dtl", "dtl · Detail"), ("grm", "grm · Groom"),
              ("rig", "rig · Rig"), ("cfx", "cfx · Cloth FX"), ("fx", "fx · FX"),
              ("anim", "anim · Animation"), ("comp", "comp · Comp"), ("lgt", "lgt · Lighting"),
              ("enh", "enh · Enhance"), ("edit", "edit · Edit"), ("grd", "grd · Grade")]

HDRI_SLOT_KEY   = "RL_hdri_{n:02d}"
CHARTS_SLOT_KEY = "RL_charts_{n:02d}"
SEQUENCE_EXT    = ".####.exr"

PREFS_PATH = os.path.join(
    os.path.expanduser("~"), ".nuke", "PXLmentorToolbox",
    "tt_comp_setup_prefs.json"
)
_ICON_DIR = os.path.join(
    os.path.expanduser("~"), ".nuke", "PXLmentorToolbox", "icons"
)


# ==============================================================================
# Node accessors
# ==============================================================================

def _node_in(group_name: str, node_name: str):
    grp = nuke.toNode(group_name)
    if grp is None:
        return None
    grp.begin()
    try:
        return nuke.toNode(node_name)
    finally:
        grp.end()


def _clear_expressions(k) -> None:
    """Clear TCL expressions so setValue() takes effect."""
    try:
        size = k.arraySize() if hasattr(k, 'arraySize') else 1
        for i in range(size):
            try:
                if k.hasExpression(i):
                    k.clearAnimated(i)
            except Exception:
                pass
    except Exception:
        pass


def _set(node_name: str, knob: str, value) -> bool:
    return _set_in(_G(), node_name, knob, value)


def _set_in(group_name: str, node_name: str, knob: str, value) -> bool:
    grp = nuke.toNode(group_name)
    if grp is None:
        log.warning("Group not found: %s", group_name)
        return False
    grp.begin()
    try:
        n = nuke.toNode(node_name)
        if n is None:
            log.warning("Node '%s' not found inside %s", node_name, group_name)
            return False
        k = n.knobs().get(knob)
        if k is None:
            log.warning("Knob '%s' not found on %s/%s", knob, group_name, node_name)
            return False
        _clear_expressions(k)
        k.setValue(value)
        return True
    except Exception as exc:
        log.warning("Error setting %s/%s.%s: %s", group_name, node_name, knob, exc)
        return False
    finally:
        grp.end()


def _set_color(node_name: str, knob: str, r: float, g: float, b: float) -> bool:
    grp = nuke.toNode(_G())
    if grp is None:
        return False
    grp.begin()
    try:
        n = nuke.toNode(node_name)
        if n is None:
            return False
        k = n.knobs().get(knob)
        if k is None:
            return False
        _clear_expressions(k)
        for i, v in enumerate((r, g, b, 1.0)):
            try:
                k.setValue(v, i)
            except Exception:
                pass
        return True
    except Exception as exc:
        log.warning("Error setting %s.%s color: %s", node_name, knob, exc)
        return False
    finally:
        grp.end()


def _get_knob_value(node_name: str, knob: str, default=None):
    return _get_knob_value_in(_G(), node_name, knob, default)


def _get_knob_value_in(group_name: str, node_name: str, knob: str, default=None):
    grp = nuke.toNode(group_name)
    if grp is None:
        return default
    grp.begin()
    try:
        n = nuke.toNode(node_name)
        if n is None:
            return default
        k = n.knobs().get(knob)
        if k is None:
            return default
        return k.value()
    except Exception:
        return default
    finally:
        grp.end()


def _get_color(node_name: str, knob: str):
    grp = nuke.toNode(_G())
    if grp is None:
        return None
    grp.begin()
    try:
        n = nuke.toNode(node_name)
        if n is None:
            return None
        k = n.knobs().get(knob)
        if k is None:
            return None
        return (k.value(0), k.value(1), k.value(2))
    except Exception:
        return None
    finally:
        grp.end()


# ==============================================================================
# Naming convention parser
# ==============================================================================

_VERSION_RE = re.compile(r'^v\d+', re.IGNORECASE)


def _parse_asset_info(folder_name: str) -> dict:
    """Parse {type}_{name}_{dept}_{version}_{user}_RL_... convention.

    Strategy: find version token (^v\\d+), collect everything before it as
    pre-version segments, then:
      - Skip segment 0 (type code — e.g. TB3, RND, ANM).
      - Skip last pre-version segment (dept code — e.g. RND, VFX, ANM).
      - Everything in between is the asset name.
    Falls back to using whatever is available when there are too few segments.
    """
    base  = re.split(r'_RL_', folder_name, maxsplit=1)[0]
    parts = base.split('_')

    version     = ""
    version_idx = -1
    for i, p in enumerate(parts):
        if _VERSION_RE.match(p):
            version     = p.lower()
            version_idx = i
            break

    if version_idx < 0:
        return {"type_code": "", "asset_name": "", "dept_code": "",
                "version": "", "user_id": ""}

    pre = parts[:version_idx]
    if len(pre) >= 3:
        type_code  = pre[0]
        dept_code  = pre[-1]
        name_parts = pre[1:-1]
    elif len(pre) == 2:
        type_code  = pre[0]
        dept_code  = ""
        name_parts = [pre[1]]
    elif len(pre) == 1:
        type_code  = ""
        dept_code  = ""
        name_parts = pre
    else:
        type_code = dept_code = ""
        name_parts = []

    asset_name = "_".join(name_parts) if name_parts else ""
    # User ID — first token after the version (e.g. TYPE_Name_dept_v001_csp)
    post    = parts[version_idx + 1:]
    user_id = post[0] if post else ""
    return {"type_code": type_code, "asset_name": asset_name,
            "dept_code": dept_code, "version": version, "user_id": user_id}


# ==============================================================================
# Folder scanner
# ==============================================================================

_FRAME_RE  = re.compile(r'^(.+?)[\._](\d+)(\.\w+)$')
IMAGE_EXTS = {".exr", ".dpx", ".tiff", ".tif", ".png", ".jpg", ".jpeg"}


def _find_sequence_pattern(folder: str) -> str:
    if not os.path.isdir(folder):
        return ""
    for fname in sorted(os.listdir(folder)):
        ext = os.path.splitext(fname)[1].lower()
        if ext not in IMAGE_EXTS:
            continue
        m = _FRAME_RE.match(fname)
        if m:
            base, num_str, fext = m.groups()
            padding = "#" * len(num_str)
            return os.path.join(folder, f"{base}.{padding}{fext}").replace("\\", "/")
    return ""


def _find_slot_folder(base_folder: str, key: str) -> str:
    try:
        for entry in sorted(os.listdir(base_folder)):
            if key.lower() in entry.lower():
                fp = os.path.join(base_folder, entry)
                if os.path.isdir(fp):
                    return fp.replace("\\", "/")
    except OSError:
        pass
    return ""


def scan_render_folder(base_folder: str) -> dict:
    base_folder    = base_folder.rstrip("/\\")
    hdri_results   = []
    charts_results = []

    for n in range(1, 9):
        hfp = _find_slot_folder(base_folder, HDRI_SLOT_KEY.format(n=n))
        cfp = _find_slot_folder(base_folder, CHARTS_SLOT_KEY.format(n=n))
        hseq = _find_sequence_pattern(hfp) if hfp else ""
        cseq = _find_sequence_pattern(cfp) if cfp else ""
        if hfp and not hseq:
            hseq = f"{hfp}/{os.path.basename(hfp)}{SEQUENCE_EXT}"
        if cfp and not cseq:
            cseq = f"{cfp}/{os.path.basename(cfp)}{SEQUENCE_EXT}"
        hdri_results.append((n, hfp, hseq))
        charts_results.append((n, cfp, cseq))

    # Parse asset info — try first HDRI subfolder, fall back to base folder name
    asset_info = {}
    for _, fp, _ in hdri_results:
        if fp:
            asset_info = _parse_asset_info(os.path.basename(fp))
            break
    if not asset_info.get("asset_name") and not asset_info.get("version"):
        asset_info = _parse_asset_info(os.path.basename(base_folder))

    return {
        "hdri":         hdri_results,
        "charts":       charts_results,
        "type_code":    asset_info.get("type_code",  ""),
        "asset_name":   asset_info.get("asset_name", ""),
        "dept_code":    asset_info.get("dept_code",  ""),
        "version":      asset_info.get("version",    ""),
        "user_id":      asset_info.get("user_id",    ""),
        "found_hdri":   sum(1 for _, fp, _ in hdri_results   if fp),
        "found_charts": sum(1 for _, fp, _ in charts_results if fp),
    }


# ==============================================================================
# Live setters — all targeting REAL knobs in v005 (flat TB3DTT group)
#
# v005: all nodes live directly inside TB3DTT — no sub-groups.
# _set() and _set_in(_MAIN_GRP, ...) both enter TB3DTT context.
# ==============================================================================

def live_render_paths_from_scan(hdri_results: list) -> int:
    count = 0
    for n, _, seq in hdri_results:
        if seq and _set_in(_G(), f"Read_HDRI_{n:02d}", "file", seq):
            count += 1
    return count


def live_charts_paths_from_scan(charts_results: list) -> int:
    count = 0
    for n, _, seq in charts_results:
        if seq and _set_in(_G(), f"Read_CHARTS_{n:02d}", "file", seq):
            count += 1
    return count


def live_frame_range(start: int, end: int):
    root = nuke.root()
    if root:
        try:
            root["first_frame"].setValue(start)
            root["last_frame"].setValue(end)
        except Exception as exc:
            log.warning("frame range root error: %s", exc)
    grp = nuke.toNode(_G())
    if grp is None:
        return
    grp.begin()
    try:
        for prefix in ("Read_HDRI_", "Read_CHARTS_"):
            for n in range(1, 9):
                node = nuke.toNode(f"{prefix}{n:02d}")
                if node is None:
                    continue
                for kname, val in (("first", start), ("last", end)):
                    k = node.knobs().get(kname)
                    if k:
                        _clear_expressions(k)
                        k.setValue(val)
    finally:
        grp.end()


def live_hdri_select(index: int):
    _set_in(_G(), "SwitchHDRI", "which", index)


def live_render_type(index: int):
    _set_in(_G(), "Switch_Mode", "which", index)


def live_back_select(index: int):
    _set("SwitchBack", "which", index)


def live_compfx(enabled: bool):
    _set_in(_G(), "COMPFX_switch", "which", int(enabled))


def live_asset_text(type_code: str, name: str, dept: str, version: str, user: str = "") -> bool:
    parts   = [p for p in [type_code, name, dept, version, user] if p]
    message = "_".join(parts)
    return _set_in(_G(), "Text_Info", "message", message)


def live_asset_name(name: str):
    _set_in(_G(), "AssetName", "message", name)


def live_asset_version(version: str):
    try:
        _set_in(_G(), "AssetVersion", "message", version)
    except Exception:
        pass


def live_font_scale(value: float):
    _set_in(_G(), "Text_Info", "global_font_scale", value)


def live_write2(version: str, hdri_index: int, render_index: int):
    ver    = version.strip() or "v000"
    hdri   = HDRI_OPTIONS[max(0, min(hdri_index,   len(HDRI_OPTIONS)   - 1))]
    render = RENDER_OPTIONS[max(0, min(render_index, len(RENDER_OPTIONS) - 1))]
    w2 = nuke.toNode("Write_TT")
    if w2 is not None:
        w2["file"].setValue(f"Output/TT_{ver}/TT_{ver}_{hdri}_{render}.####.png")


def live_lut_path(path: str):
    _set("OCIOFileTransform2", "file", path)


def live_lut_disable(disabled: bool):
    # OCIOFileTransform2.disableLUT is a Link_Knob → OCIOFileTransform2.disable
    _set("OCIOFileTransform2", "disable", disabled)


def live_zdof_disable(disabled: bool):
    # ZDefocus1.disable_1 is a Link_Knob → ZDefocus1.disable
    _set("ZDefocus1", "disable", disabled)


def live_zdof_center(value: float):
    _set("ZDefocus1", "center", value)


def live_zdof_dof(value: float):
    _set("ZDefocus1", "dof", value)


def live_zdof_size(value: float):
    _set("ZDefocus1", "size", value)


def live_zdof_output(index: int):
    # 0 = Result, 1 = Focal Plane (ZDefocus1.output knob)
    _set("ZDefocus1", "output", index)


def live_lens_dirt_disable(disabled: bool):
    _set("Merge_LensDirt", "disable", disabled)


def live_lens_dirt_mix(value: float):
    _set("Merge_LensDirt", "mix", value)


def live_lut_mix(value: float):
    _set("OCIOFileTransform2", "mix", value)


def live_bg_color(r: float, g: float, b: float):
    _set_color("BG_Color", "color", r, g, b)


def live_wireframe_color(r: float, g: float, b: float):
    _set_color("Wire_Color", "color", r, g, b)


def live_back_ramp_disable(disabled: bool):
    # Multiply3.disable_1 is a Link_Knob → Multiply3.disable
    _set("Multiply3", "disable", disabled)


def live_vignette_disable(disabled: bool):
    # Multiply4.disable_1 is a Link_Knob → Multiply4.disable
    _set("Multiply4", "disable", disabled)


def live_vignette_intensity(value: float):
    _set("Merge15", "mix", value)


def live_occlusion_disable(disabled: bool):
    # v005: renamed DISABLE_OCC → DISABLE_OCC1
    _set("DISABLE_OCC1", "disable", disabled)


def live_shadow_disable(disabled: bool):
    # DISABLE_SHD.disable_1 is a Link_Knob → DISABLE_SHD.disable
    _set("DISABLE_SHD", "disable", disabled)


def live_text_info_disable(disabled: bool):
    _set_in(_G(), "DISABLE_TEXT", "disable", disabled)


def live_ref_ball_disable(disabled: bool):
    _set("DISABLE_REF", "disable", disabled)


def live_hdri_preview_disable(disabled: bool):
    _set("DISABLE_HDRI_GRP", "disable", disabled)


def live_ref_images_disable(disabled: bool):
    _set("DISABLE_ALL_REF", "disable", disabled)


def live_ref_single(path: str):
    _set_in(_G(), "ref_single", "file", path)


def live_ref_single_disable(disabled: bool):
    _set_in(_G(), "DISABLE_Single_REF", "disable", not disabled)


def live_contact_sheet_disable(disabled: bool):
    _set_in(_G(), "DISABLE_Multiple_REF", "disable", not disabled)


def live_refs_translate(x: float, y: float):
    grp = nuke.toNode(_G())
    if grp is None:
        return
    with grp:
        n = nuke.toNode("Transform_Single_REF")
        if n is None:
            return
        k = n.knobs().get("translate")
        if k is None:
            return
        try:
            _clear_expressions(k)
            k.setValue(x, 0)
            k.setValue(y, 1)
        except Exception as exc:
            log.warning("Transform_Single_REF.translate: %s", exc)


def live_refs_scale(value: float):
    grp = nuke.toNode(_G())
    if grp is None:
        return
    with grp:
        n = nuke.toNode("Transform_Single_REF")
        if n is None:
            return
        k = n.knobs().get("scale")
        if k is not None:
            k.setValue(value)


def live_ref(slot: int, path: str):
    _set_in(_G(), f"ref_{slot:02d}", "file", path)


# ==============================================================================
# Connection check
# ==============================================================================

# v005: all nodes live inside _MAIN_GRP — no "top" level nodes
_REQUIRED_NODES = [
    (_MAIN_GRP, "SwitchBack"),
    (_MAIN_GRP, "OCIOFileTransform2"),
    (_MAIN_GRP, "Multiply3"),
    (_MAIN_GRP, "Multiply4"),
    (_MAIN_GRP, "DISABLE_HDRI_GRP"),
    (_MAIN_GRP, "DISABLE_ALL_REF"),
    (_MAIN_GRP, "DISABLE_OCC1"),
    (_MAIN_GRP, "DISABLE_SHD"),
    (_MAIN_GRP, "DISABLE_REF"),
    (_MAIN_GRP, "SwitchHDRI"),
    (_MAIN_GRP, "Switch_Mode"),
    (_MAIN_GRP, "Text_Info"),
    (_MAIN_GRP, "COMPFX_switch"),
    (_MAIN_GRP, "DISABLE_TEXT"),
    (_MAIN_GRP, "Read_HDRI_01"),
    (_MAIN_GRP, "Read_CHARTS_01"),
]


def check_comp_connected() -> tuple:
    missing = []
    grp_name = _G()
    for _, node in _REQUIRED_NODES:
        if _node_in(grp_name, node) is None:
            missing.append(f"{grp_name}/{node}")
    return len(missing) == 0, missing


# ==============================================================================
# Prefs
# ==============================================================================

def _load_prefs() -> dict:
    try:
        if os.path.isfile(PREFS_PATH):
            with open(PREFS_PATH, "r", encoding="utf-8") as fh:
                return json.load(fh)
    except Exception as exc:
        log.warning("could not load prefs: %s", exc)
    return {}


def _save_prefs(data: dict) -> None:
    try:
        os.makedirs(os.path.dirname(PREFS_PATH), exist_ok=True)
        with open(PREFS_PATH, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
    except Exception as exc:
        log.warning("could not save prefs: %s", exc)


# ── Per-node state knob ────────────────────────────────────────────────────────
# Panel state is stored as a JSON string in an invisible custom knob on the
# TB3DTT group node. This means each node instance carries its own state and
# Reconnect can fully restore the UI from whatever node is selected.

_STATE_KNOB = "pxl_tt_panel_state"


def _node_write_state(state: dict) -> None:
    grp = nuke.toNode(_G())
    if grp is None:
        return
    json_str = json.dumps(state)
    if _STATE_KNOB not in grp.knobs():
        k = nuke.String_Knob(_STATE_KNOB, "PXL Panel State")
        k.setFlag(nuke.INVISIBLE)
        grp.addKnob(k)
    grp[_STATE_KNOB].setValue(json_str)


def _node_read_state() -> dict:
    grp = nuke.toNode(_G())
    if grp is None or _STATE_KNOB not in grp.knobs():
        return {}
    try:
        raw = grp[_STATE_KNOB].getValue()
        return json.loads(raw) if raw else {}
    except Exception:
        return {}


SESSION_FILENAME = "tt_session.json"


def _session_path(working_folder: str) -> str:
    # Working Folder IS the _COMP folder, so the session file sits directly
    # inside it next to the comp template.
    return os.path.join(working_folder, SESSION_FILENAME).replace("\\", "/")


def _load_session(working_folder: str) -> dict:
    try:
        p = _session_path(working_folder)
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as fh:
                return json.load(fh)
    except Exception as exc:
        log.warning("could not load session: %s", exc)
    return {}


def _save_session(working_folder: str, data: dict) -> None:
    try:
        with open(_session_path(working_folder), "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
    except Exception as exc:
        log.warning("could not save session: %s", exc)


# ==============================================================================
# UI helpers
# ==============================================================================

def _icon_path(filename: str) -> str:
    return os.path.join(_ICON_DIR, filename).replace("\\", "/")


def _nuke_main_window():
    app = QtWidgets.QApplication.instance()
    if app:
        for w in app.topLevelWidgets():
            if w.objectName() == "Foundry::UI::DockMainWindow":
                return w
    return None


# ==============================================================================
# Reference card widget
# ==============================================================================

_IMG_EXTS_QT = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}   # formats Qt can thumbnail
_IMG_EXTS_ALL = _IMG_EXTS_QT | {".exr", ".dpx"}                      # accepted for drop/browse


class _RefCard(QtWidgets.QFrame):
    """16:9 drag-and-drop image slot.

    Shows a thumbnail when an image is loaded, a numbered placeholder when empty.
    Accepts both drag-and-drop and click-to-browse.
    """

    _BG_EMPTY    = "#141414"
    _BG_LOADED   = "#1a1a1a"
    _BDR_EMPTY   = "#3a3a3a"
    _BDR_LOADED  = "#E8820C"
    _BDR_DRAG    = "#80cc80"
    _BDR_DISABLE = "#2a2a2a"

    def __init__(self, slot: int, on_change, can_disable: bool = False,
                 on_disable=None, parent=None):
        super().__init__(parent)
        self._slot       = slot
        self._path       = ""
        self._on_change  = on_change
        self._can_disable = can_disable
        self._on_disable  = on_disable   # callable(bool) or None
        self._disabled    = False
        self._src_pixmap  = None         # full-res source, rescaled on resize

        self.setAcceptDrops(True)
        self.setMinimumHeight(80)
        self._build()
        self._style_card()

    # ── Build ──────────────────────────────────────────────────────────────

    def _build(self):
        vl = QtWidgets.QVBoxLayout(self)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)

        # ── Top bar: slot number + (optional) disable toggle + clear ──────
        top = QtWidgets.QWidget()
        top.setStyleSheet("background:transparent;")
        top.setFixedHeight(22)
        tl = QtWidgets.QHBoxLayout(top)
        tl.setContentsMargins(5, 2, 4, 0)
        tl.setSpacing(3)

        self.lbl_num = QtWidgets.QLabel(f"{self._slot:02d}")
        self.lbl_num.setStyleSheet(
            f"color:#E8820C;font-size:10px;font-weight:bold;background:transparent;")
        tl.addWidget(self.lbl_num)
        tl.addStretch()

        if self._can_disable:
            self.chk_dis = QtWidgets.QCheckBox("on")
            self.chk_dis.setChecked(True)
            self.chk_dis.setStyleSheet(
                "QCheckBox{color:#888;font-size:9px;background:transparent;spacing:3px;}"
                "QCheckBox::indicator{width:10px;height:10px;"
                "border:1px solid #555;background:#1e1e1e;border-radius:2px;}"
                "QCheckBox::indicator:checked{background:#E8820C;border:1px solid #E8820C;}"
            )
            self.chk_dis.toggled.connect(self._on_dis_toggled)
            tl.addWidget(self.chk_dis)
        else:
            self.chk_dis = None

        btn_clr = QtWidgets.QPushButton("×")
        btn_clr.setFixedSize(16, 16)
        btn_clr.setStyleSheet(
            "QPushButton{background:#333;color:#888;border:none;font-size:11px;"
            "border-radius:3px;padding:0;}"
            "QPushButton:hover{background:#E8820C;color:#fff;}"
        )
        btn_clr.clicked.connect(self._clear)
        btn_clr.setCursor(QtCore.Qt.ArrowCursor)
        tl.addWidget(btn_clr)
        vl.addWidget(top)

        # ── Thumbnail / placeholder area ───────────────────────────────────
        self.lbl_thumb = QtWidgets.QLabel()
        self.lbl_thumb.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_thumb.setStyleSheet("background:transparent;border:none;")
        self.lbl_thumb.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )
        vl.addWidget(self.lbl_thumb, 1)

        # ── Bottom filename bar ────────────────────────────────────────────
        self.lbl_fname = QtWidgets.QLabel()
        self.lbl_fname.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_fname.setStyleSheet(
            "color:#888;font-size:8px;background:transparent;"
            "border:none;padding:1px 4px;")
        self.lbl_fname.setFixedHeight(14)
        vl.addWidget(self.lbl_fname)

        self._refresh_display()

    # ── Internal state ─────────────────────────────────────────────────────

    def _style_card(self):
        if self._disabled:
            css = (f"QFrame{{background:{self._BG_EMPTY};border:1px solid {self._BDR_DISABLE};"
                   "border-radius:4px;}")
        elif self._path:
            css = (f"QFrame{{background:{self._BG_LOADED};border:1px solid {self._BDR_LOADED};"
                   "border-radius:4px;}")
        else:
            css = (f"QFrame{{background:{self._BG_EMPTY};border:1px solid {self._BDR_EMPTY};"
                   "border-radius:4px;}")
        self.setStyleSheet(css)

    def _refresh_display(self):
        if not self._path:
            self._src_pixmap = None
            self.lbl_thumb.setPixmap(QtGui.QPixmap())
            self.lbl_thumb.setText(
                f'<span style="font-size:18px;color:#2e2e2e;font-weight:bold;">'
                f'{self._slot:02d}</span><br>'
                f'<span style="font-size:8px;color:#3a3a3a;">'
                f'drop or click to browse</span>'
            )
            self.lbl_fname.setText("")
        else:
            self.lbl_thumb.setText("")
            fname = os.path.basename(self._path)
            self.lbl_fname.setText(fname)
            self._load_thumbnail()
        self._style_card()

    def _load_thumbnail(self):
        ext = os.path.splitext(self._path)[1].lower()
        if ext in _IMG_EXTS_QT:
            pix = QtGui.QPixmap(self._path)
            if not pix.isNull():
                self._src_pixmap = pix
                self._apply_thumbnail()
                return
        # Fallback for EXR / unsupported — orange placeholder
        self._src_pixmap = None
        self.lbl_thumb.setPixmap(QtGui.QPixmap())
        self.lbl_thumb.setText(
            f'<span style="font-size:11px;color:#E8820C;">EXR</span><br>'
            f'<span style="font-size:8px;color:#888;">preview not available</span>'
        )

    def _apply_thumbnail(self):
        if self._src_pixmap is None or self._src_pixmap.isNull():
            return
        w = self.lbl_thumb.width()  or self.width()
        h = self.lbl_thumb.height() or (self.height() - 36)
        if w < 2 or h < 2:
            return
        scaled = self._src_pixmap.scaled(
            w, h,
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation,
        )
        self.lbl_thumb.setPixmap(scaled)

    # ── Public interface ───────────────────────────────────────────────────

    def path(self) -> str:
        return self._path

    def set_path(self, path: str):
        self._path = path.replace("\\", "/") if path else ""
        self._refresh_display()

    def set_disabled_state(self, disabled: bool):
        """Update the visual disabled state (does NOT emit on_disable)."""
        self._disabled = disabled
        if self.chk_dis is not None:
            self.chk_dis.blockSignals(True)
            self.chk_dis.setChecked(not disabled)
            self.chk_dis.blockSignals(False)
        self._style_card()

    # ── Qt events ─────────────────────────────────────────────────────────

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._src_pixmap:
            QtCore.QTimer.singleShot(0, self._apply_thumbnail)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._browse()
        super().mousePressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            paths = [u.toLocalFile() for u in event.mimeData().urls()]
            if any(os.path.splitext(p)[1].lower() in _IMG_EXTS_ALL for p in paths):
                event.acceptProposedAction()
                self.setStyleSheet(
                    f"QFrame{{background:#1e2b1e;border:2px solid {self._BDR_DRAG};"
                    "border-radius:4px;}")
                return
        event.ignore()

    def dragLeaveEvent(self, event):
        self._style_card()
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        self._style_card()
        paths = [u.toLocalFile() for u in event.mimeData().urls()]
        imgs  = [p for p in paths
                 if os.path.splitext(p)[1].lower() in _IMG_EXTS_ALL]
        if imgs:
            self.set_path(imgs[0])
            self._on_change(self._slot, self._path)
        event.acceptProposedAction()

    # ── Private slots ──────────────────────────────────────────────────────

    def _browse(self):
        start = os.path.dirname(self._path) if self._path else ""
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, f"Select Reference {self._slot:02d}", start,
            "Images (*.jpg *.jpeg *.png *.exr *.tif *.tiff *.dpx);;All (*)"
        )
        if path:
            self.set_path(path)
            self._on_change(self._slot, self._path)

    def _clear(self):
        self.set_path("")
        self._on_change(self._slot, "")

    def _on_dis_toggled(self, checked: bool):
        """'on' checkbox toggled — checked = slot enabled, unchecked = disabled."""
        self._disabled = not checked
        self._style_card()
        if self._on_disable:
            self._on_disable(not checked)


# ==============================================================================
# Main dialog
# ==============================================================================

class _FlatTextStyle(QtWidgets.QProxyStyle):
    """Kills any text drop-shadow / etch the host (Nuke) style draws.

    Two layers:
      - styleHint() disables the etched/dithered DISABLED-text effect.
      - drawItemText() re-implements text drawing FLAT, so even ENABLED text
        gets no shadow no matter what the underlying style does. This is the
        single point every label/button/combo text passes through."""
    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint in (QtWidgets.QStyle.SH_EtchDisabledText,
                    QtWidgets.QStyle.SH_DitherDisabledText):
            return 0
        return super().styleHint(hint, option, widget, returnData)

    def drawItemText(self, painter, rect, flags, pal, enabled, text,
                     textRole=QtGui.QPalette.NoRole):
        if not text:
            return
        painter.save()
        if textRole != QtGui.QPalette.NoRole:
            painter.setPen(pal.color(textRole))
        painter.drawText(rect, int(flags), text)
        painter.restore()


class TurnTableCompSetupDialog(QtWidgets.QDialog):

    BODY_BG = "#333333"

    _BTN = (
        "QPushButton{background:#E8820C;color:#241606;border:1px solid #C96E08;"
        "border-radius:5px;font-size:13px;font-weight:700;letter-spacing:1px;"
        "padding:8px 14px;min-height:32px;min-width:84px;}"
        "QPushButton:hover{background:#FF9A2E;}"
        "QPushButton:pressed{background:#C96E08;}"
        "QPushButton:disabled{background:#404040;color:#7A7A7A;border:1px solid #262626;}"
    )
    _BTN2 = (
        "QPushButton{background:#4a4a4a;color:#E6E6E6;border:1px solid #262626;"
        "border-radius:5px;font-size:12px;font-weight:bold;letter-spacing:0.6px;"
        "padding:0 14px;min-height:32px;min-width:84px;}"
        "QPushButton:hover{background:#555555;color:#ffffff;}"
        "QPushButton:pressed{background:#414141;}"
        "QPushButton:disabled{background:#404040;color:#7A7A7A;border:1px solid #262626;}"
    )
    _FIELD = (
        "QLineEdit,QSpinBox,QDoubleSpinBox{"
        "background:#2c2c2c;color:#E6E6E6;"
        "border:1px solid #262626;padding:5px 8px;font-size:11px;border-radius:4px;}"
        "QLineEdit:focus,QSpinBox:focus,QDoubleSpinBox:focus{border:1px solid #E8820C;}"
        # Spin-box up/down arrows (inline triangles — reliable in Nuke, matches combo)
        "QSpinBox::up-button,QDoubleSpinBox::up-button{subcontrol-origin:border;"
        "subcontrol-position:top right;width:17px;border-left:1px solid #262626;"
        "background:#404040;border-top-right-radius:4px;}"
        "QSpinBox::down-button,QDoubleSpinBox::down-button{subcontrol-origin:border;"
        "subcontrol-position:bottom right;width:17px;border-left:1px solid #262626;"
        "background:#404040;border-bottom-right-radius:4px;}"
        "QSpinBox::up-button:hover,QDoubleSpinBox::up-button:hover,"
        "QSpinBox::down-button:hover,QDoubleSpinBox::down-button:hover{background:#5a5a5a;}"
        "QSpinBox::up-arrow,QDoubleSpinBox::up-arrow{image:url(__SPINUP__);width:9px;height:9px;}"
        "QSpinBox::up-arrow:hover,QDoubleSpinBox::up-arrow:hover{image:url(__SPINUPH__);}"
        "QSpinBox::down-arrow,QDoubleSpinBox::down-arrow{image:url(__SPINDOWN__);width:9px;height:9px;}"
        "QSpinBox::down-arrow:hover,QDoubleSpinBox::down-arrow:hover{image:url(__SPINDOWNH__);}"
        "QComboBox{"
        "background:#2c2c2c;color:#E6E6E6;"
        "border:1px solid #262626;padding:5px 8px;padding-right:26px;"
        "font-size:11px;border-radius:4px;}"
        "QComboBox::drop-down{"
        "subcontrol-origin:padding;subcontrol-position:top right;"
        "width:20px;border:none;border-left:1px solid #262626;background:#404040;"
        "border-top-right-radius:4px;border-bottom-right-radius:4px;}"
        "QComboBox::drop-down:hover{background:#5a5a5a;}"
        "QComboBox::down-arrow{image:url(__SPINDOWN__);width:11px;height:11px;}"
        "QComboBox:hover::down-arrow,QComboBox::down-arrow:hover{image:url(__SPINDOWNH__);}"
        "QComboBox:on{border:1px solid #E8820C;}"
        "QComboBox:hover{border:1px solid #E8820C;}"
        "QComboBox QAbstractItemView{"
        "background:#404040;color:#E6E6E6;border:1px solid #262626;outline:0;"
        "selection-background-color:#E8820C;selection-color:#241606;}"
        "QComboBox QAbstractItemView::item{padding:5px 8px;min-height:24px;}"
        "QComboBox QAbstractItemView::item:disabled{"
        "color:#cc4444;font-style:italic;}"
    )
    _LBL  = "QLabel{color:#A8A8A8;font-size:11px;background:transparent;}"
    _STAT = ("QLabel{color:#A8A8A8;font-size:10px;font-style:italic;"
             "background:#2c2c2c;border:1px solid #262626;padding:5px 10px;"
             "border-radius:11px;}")
    _CHK  = (
        "QCheckBox{color:#E6E6E6;font-size:11px;background:transparent;spacing:7px;}"
        "QCheckBox::indicator{width:15px;height:15px;"
        "border:1px solid #7A7A7A;background:#2c2c2c;border-radius:3px;}"
        "QCheckBox::indicator:checked{background:#E8820C;"
        "border:1px solid #C96E08;image:url(__CHECK__);}"
        "QCheckBox::indicator:unchecked:hover{border:1px solid #E8820C;}"
    )
    _COL_HDR = (
        "QLabel{color:#BFBFBF;font-size:10px;font-weight:bold;"
        "letter-spacing:1px;background:transparent;padding-bottom:3px;}"
    )
    _SLD = (
        "QSlider{background:transparent;}"
        "QSlider::groove:horizontal{background:transparent;height:4px;border:none;}"
        "QSlider::sub-page:horizontal{background:#E8820C;border-radius:2px;}"
        "QSlider::add-page:horizontal{background:#0a0a0a;border-radius:2px;}"
        "QSlider::handle:horizontal{image:url(__SLH__);background:transparent;border:none;"
        "width:20px;height:20px;margin:-8px 0;}"
        "QSlider::handle:horizontal:hover{image:url(__SLHH__);}"
        "QSlider[hov=true]::sub-page:horizontal{background:#FFA838;}"
        "QSlider[hov=true]::add-page:horizontal{background:#2c2c2c;}"
    )

    # ── Guided-step styles (inline — byte-for-byte parity with Maya theme) ──────
    _STEP_BADGE = {
        "locked": "QLabel{background:#363636;color:#6A6A6A;border:1px solid #2c2c2c;"
                  "border-radius:13px;font-size:12px;font-weight:bold;}",
        "active": "QLabel{background:#E8820C;color:#241606;border:1px solid #C96E08;"
                  "border-radius:13px;font-size:12px;font-weight:bold;}",
        "done":   "QLabel{background:#24331f;color:#5BBF6A;border:1px solid #3a5a3a;"
                  "border-radius:13px;font-size:12px;font-weight:bold;}",
    }
    _STEP_BTN = {
        "locked": "QPushButton{background:#383838;color:#6A6A6A;border:1px solid #2c2c2c;"
                  "border-radius:5px;font-size:12px;font-weight:bold;letter-spacing:0.6px;"
                  "padding:0 14px;min-height:32px;}",
        "active": "QPushButton{background:#4a4a4a;color:#ffffff;border:1px solid #E8820C;"
                  "border-radius:5px;font-size:12px;font-weight:bold;letter-spacing:0.6px;"
                  "padding:0 14px;min-height:32px;}"
                  "QPushButton:hover{background:#555555;border:1px solid #FF9A2E;}",
        "done":   "QPushButton{background:#333a33;color:#8FB890;border:1px solid #3a5a3a;"
                  "border-radius:5px;font-size:12px;font-weight:bold;letter-spacing:0.6px;"
                  "padding:0 14px;min-height:32px;}"
                  "QPushButton:hover{background:#3a443a;color:#A8CBA8;}",
    }
    _STEP_TITLE   = ("QLabel{color:#D6D6D6;font-size:11px;font-weight:bold;"
                     "letter-spacing:0.5px;background:transparent;}")
    _STEP_CONFIRM = "QLabel{color:#5BBF6A;font-size:11px;font-weight:bold;background:transparent;}"

    def __init__(self, parent=None):
        super().__init__(parent or _nuke_main_window())
        self._prefs           = _load_prefs()
        self._block_live      = True
        self._scan_data       = None
        self._template_loaded = False

        self.setWindowTitle(f"PXL {TOOL_NAME}  v{VERSION}")
        self.setMinimumSize(680, 500)
        self.resize(720, 960)
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowMinMaxButtonsHint |
            QtCore.Qt.WindowCloseButtonHint |
            QtCore.Qt.WindowStaysOnTopHint
        )
        _qss = ""
        _chkpath = ""
        _arrow = {"up": "", "dn": "", "uph": "", "dnh": ""}
        _slh = {"n": "", "h": ""}
        try:
            if _PXLUI:
                import tempfile as _tf
                _td = _tf.gettempdir()
                _chkpath = os.path.join(_td, "_pxlui_check_nk.png")
                pxli.save_png("check", 11, pxlt.c("on_accent"), _chkpath)
                _chkpath = _chkpath.replace("\\", "/")
                # PNG chevrons (PySide does NOT render CSS border-triangles);
                # grey default + white on hover.
                for _k, _name, _col in (("up", "chevron-up", "#B8B8B8"),
                                        ("dn", "chevron-down", "#B8B8B8"),
                                        ("uph", "chevron-up", "#ffffff"),
                                        ("dnh", "chevron-down", "#ffffff")):
                    _p = os.path.join(_td, f"_pxlui_arrow_{_k}_nk.png")
                    pxli.save_png(_name, 9, _col, _p)
                    _arrow[_k] = _p.replace("\\", "/")
                # Slider handle PNGs: white dot, + orange RING on hover (stays round)
                def _mk_handle(out_path, ring):
                    _D = 20
                    _pm = QtGui.QPixmap(_D, _D); _pm.fill(QtCore.Qt.transparent)
                    _pn = QtGui.QPainter(_pm)
                    _pn.setRenderHint(QtGui.QPainter.Antialiasing, True)
                    _c = _D / 2.0
                    _pn.setPen(QtCore.Qt.NoPen); _pn.setBrush(QtGui.QColor("#ffffff"))
                    _pn.drawEllipse(QtCore.QPointF(_c, _c), 6.5, 6.5)
                    if ring:
                        _pen = QtGui.QPen(QtGui.QColor("#E8820C")); _pen.setWidthF(2.0)
                        _pn.setPen(_pen); _pn.setBrush(QtCore.Qt.NoBrush)
                        _pn.drawEllipse(QtCore.QPointF(_c, _c), 8.0, 8.0)
                    _pn.end(); _pm.save(out_path, "PNG")
                _hn = os.path.join(_td, "_pxlui_slh_nk.png")
                _hh = os.path.join(_td, "_pxlui_slh_h_nk.png")
                _mk_handle(_hn, False); _mk_handle(_hh, True)
                _slh["n"] = _hn.replace("\\", "/"); _slh["h"] = _hh.replace("\\", "/")
                _qss = (pxlt.tool_qss().replace("__CHECK__", _chkpath)
                        .replace("__SPINUP__", "").replace("__SPINDOWN__", "")
                        .replace("__SPINUPH__", "").replace("__SPINDOWNH__", "")
                        .replace("__SLH__", "").replace("__SLHH__", ""))
        except Exception:
            _qss = ""
        self._CHK = self.__class__._CHK.replace("__CHECK__", _chkpath if _chkpath else "")
        self._FIELD = (self.__class__._FIELD
                       .replace("__SPINUP__", _arrow["up"]).replace("__SPINDOWN__", _arrow["dn"])
                       .replace("__SPINUPH__", _arrow["uph"]).replace("__SPINDOWNH__", _arrow["dnh"]))
        self._SLD = (self.__class__._SLD
                     .replace("__SLH__", _slh["n"]).replace("__SLHH__", _slh["h"]))
        self.setStyleSheet(_qss if _qss else f"QDialog{{background:{self.BODY_BG};}}")
        # Remove Qt's etched disabled-text emboss (looks like a text drop-shadow).
        try:
            self.setStyle(_FlatTextStyle(self.style()))
        except Exception:
            pass

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_header())
        root.addWidget(self._build_node_indicator())
        root.addWidget(self._build_scroll_body(), 1)
        root.addWidget(self._build_status_bar())
        root.addWidget(self._build_close_bar())

        self._restore_prefs()
        try:
            wf = self.f_proj_dir.text().strip()
            if wf and os.path.isfile(_session_path(wf)):
                session = _load_session(wf)
                if session:
                    self._prefs.update(session)
                    self._restore_prefs()
        except Exception:
            pass
        self._block_live = False
        already_connected, _ = check_comp_connected()
        if already_connected:
            self._template_loaded = True
            self._refresh_connection_status()
            self._update_node_indicator()
        else:
            self._update_node_indicator()

    # ── HEADER ────────────────────────────────────────────────────────────

    def _build_header(self):
        if _PXLUI:
            try:
                return pxlw.AppHeader(
                    TOOL_NAME, "v" + VERSION,
                    icon_path=_icon_path("icon_turntable_builder.png"))
            except Exception:
                pass
        hdr = QtWidgets.QWidget()
        hdr.setFixedHeight(100)
        hdr.setStyleSheet(f"background:{HEADER_BG};")
        hl = QtWidgets.QHBoxLayout(hdr)
        hl.setContentsMargins(12, 8, 12, 8)
        hl.setSpacing(0)

        lbl_icon = QtWidgets.QLabel()
        lbl_icon.setFixedSize(80, 80)
        lbl_icon.setAlignment(QtCore.Qt.AlignCenter)
        lbl_icon.setStyleSheet(f"background:{HEADER_BG};")
        tp = _icon_path("icon_turntable_builder.png")
        if os.path.exists(tp):
            lbl_icon.setPixmap(QtGui.QPixmap(tp).scaled(
                80, 80, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            lbl_icon.setText("[ icon ]")
            lbl_icon.setStyleSheet(
                f"color:#555;font-size:10px;border:1px solid #444;background:{HEADER_BG};")
        hl.addWidget(lbl_icon)

        col = QtWidgets.QVBoxLayout()
        col.setAlignment(QtCore.Qt.AlignCenter)
        col.setSpacing(2)

        lbl_logo = QtWidgets.QLabel()
        lbl_logo.setAlignment(QtCore.Qt.AlignCenter)
        lbl_logo.setStyleSheet(f"background:{HEADER_BG};")
        lp = _icon_path("PXLtools_logo.png")
        if os.path.exists(lp):
            lbl_logo.setPixmap(QtGui.QPixmap(lp).scaled(
                220, 52, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            lbl_logo.setText("PXLtools")
            lbl_logo.setStyleSheet(
                f"color:#D7005A;font-size:22px;font-weight:bold;"
                f"letter-spacing:3px;background:{HEADER_BG};")
        col.addWidget(lbl_logo)

        lbl_name = QtWidgets.QLabel(TOOL_NAME)
        lbl_name.setAlignment(QtCore.Qt.AlignCenter)
        lbl_name.setStyleSheet(
            f"color:#e0e0e0;font-size:12px;font-weight:bold;background:{HEADER_BG};")
        col.addWidget(lbl_name)

        lbl_ver = QtWidgets.QLabel(f"v{VERSION}  —  Live Mode")
        lbl_ver.setAlignment(QtCore.Qt.AlignCenter)
        lbl_ver.setStyleSheet(f"color:#888888;font-size:10px;background:{HEADER_BG};")
        col.addWidget(lbl_ver)

        hl.addLayout(col, 1)
        sp = QtWidgets.QWidget()
        sp.setFixedSize(80, 80)
        sp.setStyleSheet(f"background:{HEADER_BG};")
        hl.addWidget(sp)
        return hdr

    # ── SCROLL BODY ───────────────────────────────────────────────────────

    def _build_scroll_body(self):
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea{{border:none;background:{self.BODY_BG};}}"
            "QScrollBar:vertical{background:#222;width:10px;}"
            "QScrollBar::handle:vertical{background:#555;border-radius:4px;}"
        )
        body = QtWidgets.QWidget()
        body.setStyleSheet(f"background:{self.BODY_BG};")
        vl = QtWidgets.QVBoxLayout(body)
        vl.setContentsMargins(16, 12, 16, 20)
        vl.setSpacing(8)

        _cs = self._collapsible
        _sec_comp   = _cs("COMP SETUP",     self._build_comp_setup_body(), starts_expanded=True, icon_name="scene",      accent="#4F9DE0", number="01")
        _sec_visual = _cs("VISUAL OPTIONS", self._build_visual_options(),  starts_expanded=True, icon_name="visibility", accent="#9B7EDE", number="02")
        _sec_fx     = _cs("COMP EFFECTS SETTINGS", self._build_comp_effects(),    icon_name="magic",      accent="#F2C14E", number="03")
        _sec_tech   = _cs("TECH SETTINGS",  self._build_tech_settings(),   icon_name="utilities",  accent="#34B3A0", number="04")
        _sec_refs   = _cs("REFERENCES",     self._build_references(),      icon_name="image",      accent="#E8694A", number="05")
        _sec_export = _cs("EXPORT",         self._build_write_node(),      icon_name="install",    accent="#E070A8", number="06")

        vl.addWidget(self._section_instructions())
        for _sec in (_sec_comp, _sec_visual, _sec_fx, _sec_tech, _sec_refs, _sec_export):
            vl.addWidget(_sec)
        vl.addStretch()

        # Store refs so EXPORT can close all others when expanded
        self._all_sec_btns = [
            s.findChildren(QtWidgets.QPushButton)[0]
            for s in (_sec_comp, _sec_visual, _sec_fx, _sec_tech, _sec_refs)
        ]
        _sec_export.findChildren(QtWidgets.QPushButton)[0].toggled.connect(
            self._on_export_toggled)

        scroll.setWidget(body)
        return scroll

    # ── STATUS / CLOSE BARS ───────────────────────────────────────────────

    def _build_status_bar(self):
        wrap = QtWidgets.QWidget()
        wrap.setStyleSheet(f"background:{self.BODY_BG};")
        wl = QtWidgets.QVBoxLayout(wrap)
        wl.setContentsMargins(20, 4, 20, 4)
        self.lbl_conn = QtWidgets.QLabel()
        self.lbl_conn.setWordWrap(True)
        self._set_status(self.lbl_conn, "Import the comp template to begin.", "idle")
        wl.addWidget(self.lbl_conn)
        return wrap

    def _build_close_bar(self):
        bar = QtWidgets.QWidget()
        bar.setStyleSheet("background:#222222; border-top:1px solid #3a3a3a;")
        bar.setFixedHeight(50)
        hl = QtWidgets.QHBoxLayout(bar)
        hl.setContentsMargins(16, 8, 16, 8)
        hl.addStretch()
        btn = QtWidgets.QPushButton("Close")
        btn.setFixedSize(88, 30)
        btn.setStyleSheet(self._BTN2)
        btn.clicked.connect(self.close)
        hl.addWidget(btn)
        return bar

    # ── NODE INDICATOR BAR ────────────────────────────────────────────────

    def _build_node_indicator(self) -> QtWidgets.QWidget:
        """Small bar: [dot] Active comp: TB3DTT  [Reconnect]"""
        bar = QtWidgets.QWidget()
        bar.setStyleSheet(
            "background:#383838;border:1px solid #2c2c2c;"
            "border-radius:5px;")
        bar.setFixedHeight(44)
        hl = QtWidgets.QHBoxLayout(bar)
        hl.setContentsMargins(10, 6, 8, 6)
        hl.setSpacing(8)

        self.lbl_node_dot = QtWidgets.QLabel("●")
        self.lbl_node_dot.setFixedWidth(12)
        self.lbl_node_dot.setStyleSheet("color:#555;font-size:10px;background:transparent;")
        hl.addWidget(self.lbl_node_dot)

        self.lbl_node_name = QtWidgets.QLabel("No comp loaded")
        self.lbl_node_name.setStyleSheet(
            "color:#A8A8A8;font-size:11px;background:transparent;")
        hl.addWidget(self.lbl_node_name, 1)

        self.btn_reconnect = QtWidgets.QPushButton("Reconnect")
        self.btn_reconnect.setStyleSheet(self._BTN2)   # standard grey button (no bluish)
        self.btn_reconnect.setToolTip(
            "If a TB3DTT group node is selected in Nuke, rebind the panel to it.\n"
            "Otherwise re-reads the current active comp node.")
        self.btn_reconnect.clicked.connect(self._do_reconnect)
        hl.addWidget(self.btn_reconnect)

        return bar

    def _update_node_indicator(self):
        """Refresh the node indicator bar to reflect _G() and connection state."""
        grp_name = _G()
        connected, _ = check_comp_connected()
        dot = self.lbl_node_dot
        lbl = self.lbl_node_name
        if connected:
            dot.setStyleSheet("color:#44cc44;font-size:10px;background:transparent;")
            lbl.setText(f"Active comp: {grp_name}")
            lbl.setStyleSheet("color:#cccccc;font-size:10px;background:transparent;")
        else:
            grp_exists = nuke.toNode(grp_name) is not None
            if grp_exists:
                dot.setStyleSheet("color:#ccaa00;font-size:10px;background:transparent;")
                lbl.setText(f"Partial: {grp_name}  (some nodes missing)")
                lbl.setStyleSheet("color:#ccaa44;font-size:10px;background:transparent;")
            else:
                dot.setStyleSheet("color:#555;font-size:10px;background:transparent;")
                lbl.setText("No comp loaded")
                lbl.setStyleSheet("color:#888;font-size:10px;background:transparent;")

    # ── COMP SETUP BODY ───────────────────────────────────────────────────

    def _build_comp_setup_body(self) -> QtWidgets.QWidget:
        """Import Template + Render Location + Asset Info — sequential step collapsibles."""
        w = QtWidgets.QWidget()
        w.setStyleSheet(f"background:{self.BODY_BG};")
        vl = QtWidgets.QVBoxLayout(w)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)

        sec_tmpl   = self._collapsible("1   IMPORT TEMPLATE",
                                        self._section_template_body(),
                                        starts_expanded=True,
                                        icon_name="install", accent="#4F9DE0")
        sec_folder = self._collapsible("2   RENDER LOCATION & FRAMES",
                                        self._section_folder_body(),
                                        starts_expanded=False,
                                        icon_name="folder", accent="#E8820C")
        sec_asset  = self._collapsible("3   ASSET INFO",
                                        self._section_asset_body(),
                                        starts_expanded=False,
                                        icon_name="box", accent="#9B7EDE")

        self._cs_btn_tmpl   = sec_tmpl.findChildren(QtWidgets.QPushButton)[0]
        self._cs_btn_folder = sec_folder.findChildren(QtWidgets.QPushButton)[0]
        self._cs_btn_asset  = sec_asset.findChildren(QtWidgets.QPushButton)[0]

        # Guided-flow section refs + initial state (parity with Maya): step 1
        # active (orange), steps 2 & 3 idle until reached.
        self._cs_sec_tmpl   = sec_tmpl
        self._cs_sec_folder = sec_folder
        self._cs_sec_asset  = sec_asset
        sec_tmpl.set_state("active")
        sec_folder.set_state("idle")
        sec_asset.set_state("idle")

        vl.addWidget(sec_tmpl)
        vl.addWidget(sec_folder)
        vl.addWidget(sec_asset)
        return w

    def _cs_after_import(self):
        """Advance COMP SETUP to step 2 after a successful template import."""
        if not self._template_loaded:
            return
        self._cs_btn_tmpl.setChecked(False)
        self._cs_btn_folder.setChecked(True)
        if hasattr(self, "_cs_sec_tmpl"):
            self._cs_sec_tmpl.set_state("done")      # step 1 -> green
            self._cs_sec_folder.set_state("active")  # step 2 -> orange

    def _cs_after_folder(self):
        """Advance COMP SETUP to step 3 after Apply Project Settings succeeds."""
        self._cs_btn_folder.setChecked(False)
        self._cs_btn_asset.setChecked(True)
        if hasattr(self, "_cs_sec_folder"):
            self._cs_sec_folder.set_state("done")    # step 2 -> green
            self._cs_sec_asset.set_state("active")   # step 3 -> orange

    def _cs_collapse_asset(self):
        """Collapse step 3 after a successful Auto-fill."""
        if hasattr(self, "_cs_btn_asset"):
            self._cs_btn_asset.setChecked(False)
        if hasattr(self, "_cs_sec_asset"):
            self._cs_sec_asset.set_state("done")     # step 3 -> green

    # ── UI PRIMITIVES ─────────────────────────────────────────────────────

    def _divider(self):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setStyleSheet("color:#3a3a3a;background:#3a3a3a;max-height:1px;")
        return line

    def _row(self, label_text, widget, lw=140):
        w = QtWidgets.QWidget()
        w.setStyleSheet("background:transparent;")
        hl = QtWidgets.QHBoxLayout(w)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(10)
        lbl = QtWidgets.QLabel(label_text)
        lbl.setFixedWidth(lw)
        lbl.setStyleSheet(self._LBL)
        hl.addWidget(lbl)
        hl.addWidget(widget, 1)
        return w

    def _set_status(self, label, text, state="idle"):
        prefix = {"ok": "✓ ", "err": "✕ ", "idle": "— ", "warn": "! "}.get(state, "— ")
        css = {"ok":   "color:#5BBF6A;background:#24331f;border:1px solid #3a5a3a;",
               "err":  "color:#E4604A;background:#3a2020;border:1px solid #5a3030;",
               "warn": "color:#E8B84B;background:#3a2c00;border:1px solid #5a4a1a;",
               "idle": "color:#7A7A7A;background:#2c2c2c;border:1px solid #262626;"
               }.get(state, "color:#7A7A7A;background:#2c2c2c;border:1px solid #262626;")
        label.setText(prefix + text)
        label.setStyleSheet(
            "QLabel{%sborder-radius:11px;padding:4px 10px;font-size:11px;}" % css)

    def _stat(self, text=""):
        lbl = QtWidgets.QLabel(text)
        lbl.setStyleSheet(self._STAT)
        lbl.setWordWrap(True)
        return lbl

    def _btn(self, text, primary=True):
        b = QtWidgets.QPushButton(text)
        b.setStyleSheet(self._BTN if primary else self._BTN2)
        b.setCursor(QtCore.Qt.PointingHandCursor)
        return b

    def _field(self, text="", placeholder=""):
        f = QtWidgets.QLineEdit(text)
        f.setStyleSheet(self._FIELD)
        if placeholder:
            f.setPlaceholderText(placeholder)
        return f

    def _combo(self, items):
        c = QtWidgets.QComboBox()
        c.addItems(items)
        c.setStyleSheet(self._FIELD)
        return c

    def _code_combo(self, pairs):
        """Combo whose items show a readable example ('CHR · Character') but
        store the bare code as item data, so naming logic is unchanged."""
        c = QtWidgets.QComboBox()
        for code, label in pairs:
            c.addItem(label, code)
        c.setStyleSheet(self._FIELD)
        return c

    @staticmethod
    def _combo_code(combo):
        d = combo.currentData()
        return (d if d is not None else combo.currentText()).strip()

    def _chk(self, text, checked=True):
        c = QtWidgets.QCheckBox(text)
        c.setChecked(checked)
        c.setStyleSheet(self._CHK)
        return c

    def _spinbox(self, minimum=0.0, maximum=100.0, step=1.0, value=0.0,
                 decimals=2, width=None):
        sb = QtWidgets.QDoubleSpinBox()
        sb.setRange(minimum, maximum)
        sb.setSingleStep(step)
        sb.setValue(value)
        sb.setDecimals(decimals)
        sb.setStyleSheet(self._FIELD)
        if width:
            sb.setFixedWidth(width)
        return sb

    def _slider(self, minimum=0, maximum=100, value=100):
        sld = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        sld.setRange(minimum, maximum)
        sld.setValue(value)
        sld.setStyleSheet(self._SLD)
        sld.setFixedHeight(24)   # room for the 20px handle/ring (no crop)
        # Qt repaints only the handle on hover, not the bar -> force a full
        # repaint via a property toggle so the bar lightens too.
        def _enter(_e, _s=sld):
            _s.setProperty("hov", True)
            _s.style().unpolish(_s); _s.style().polish(_s)
        def _leave(_e, _s=sld):
            _s.setProperty("hov", False)
            _s.style().unpolish(_s); _s.style().polish(_s)
        sld.enterEvent = _enter
        sld.leaveEvent = _leave
        return sld

    # ── Guided-step factories (parity with Maya) ──────────────────────────────
    def _mk_step_badge(self, text):
        b = QtWidgets.QLabel(str(text))
        b.setFixedSize(22, 22)
        b.setAlignment(QtCore.Qt.AlignCenter)
        b.setStyleSheet(self._STEP_BADGE["locked"])
        return b

    def _mk_step_confirm(self):
        c = QtWidgets.QLabel("")
        c.setFixedWidth(58)
        c.setStyleSheet(self._STEP_CONFIRM)
        return c

    def _mk_step_header(self, num, title):
        """[badge] TITLE .......... [✓ done]  ->  (row, badge, confirm)."""
        badge   = self._mk_step_badge(num)
        confirm = self._mk_step_confirm()
        lbl = QtWidgets.QLabel(title)
        lbl.setStyleSheet(self._STEP_TITLE)
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(8)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(badge)
        row.addWidget(lbl, 1)
        row.addWidget(confirm)
        return row, badge, confirm

    def _set_badge(self, badge, state):
        if badge:
            badge.setStyleSheet(self._STEP_BADGE[state])

    def _set_step_btn(self, btn, state, gate_enable=True):
        if not btn:
            return
        btn.setStyleSheet(self._STEP_BTN[state])
        if gate_enable:
            btn.setEnabled(state != "locked")

    def _set_confirm(self, confirm, done):
        if confirm:
            confirm.setText("✓ done" if done else "")

    def _color_btn(self, r=0.0, g=0.0, b=0.0):
        btn = QtWidgets.QPushButton()
        btn.setFixedSize(40, 24)
        btn._rgb = (r, g, b)
        self._update_color_btn(btn)
        return btn

    def _update_color_btn(self, btn):
        r, g, b = btn._rgb
        ri, gi, bi = int(r * 255), int(g * 255), int(b * 255)
        btn.setStyleSheet(
            f"QPushButton{{background:rgb({ri},{gi},{bi});"
            "border:1px solid #666;border-radius:2px;min-width:40px;}}"
            "QPushButton:hover{border:1px solid #E8820C;}"
        )

    def _pick_color(self, btn, callback):
        r, g, b = btn._rgb
        color = QtWidgets.QColorDialog.getColor(
            QtGui.QColor(int(r * 255), int(g * 255), int(b * 255)), self, "Pick Color")
        if color.isValid():
            nr, ng, nb = color.redF(), color.greenF(), color.blueF()
            btn._rgb = (nr, ng, nb)
            self._update_color_btn(btn)
            if not self._block_live:
                callback(nr, ng, nb)

    def _path_row(self, parent_layout, label, folder=False, file_filter="All (*)"):
        ed  = self._field()
        btn = self._btn("Browse…", False)
        btn.setFixedSize(92, 32)   # standard inline-action button size
        wrap = QtWidgets.QWidget()
        wrap.setStyleSheet("background:transparent;")
        wl = QtWidgets.QHBoxLayout(wrap)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(6)
        wl.addWidget(ed, 1)
        wl.addWidget(btn)
        parent_layout.addWidget(self._row(label, wrap))
        if folder:
            btn.clicked.connect(lambda _=False, e=ed: self._browse_folder(e))
        else:
            btn.clicked.connect(lambda _=False, e=ed, ff=file_filter:
                                self._browse_file(e, ff))
        return ed

    def _browse_folder(self, edit):
        start = edit.text().strip() or os.path.expanduser("~")
        path  = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder", start)
        if path:
            edit.setText(path.replace("\\", "/"))
            edit.editingFinished.emit()

    def _browse_file(self, edit, file_filter):
        start = (os.path.dirname(edit.text())
                 if edit.text().strip() else os.path.expanduser("~"))
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select File", start, file_filter)
        if path:
            edit.setText(path.replace("\\", "/"))
            edit.editingFinished.emit()

    def _collapsible(self, title: str, body_widget: QtWidgets.QWidget,
                     bg: str = None, fg: str = None,
                     starts_expanded: bool = False, icon_name=None,
                     accent=None, number=None) -> QtWidgets.QWidget:
        # Maya-parity header: grey bar + accent icon + number + name + right
        # triangle. bg/fg kept for call compatibility but ignored (uniform grey).
        HEAD_BG = "#3f3f3f"
        _accent = accent or BRAND_ORANGE
        wrap = QtWidgets.QWidget()
        wrap.setStyleSheet(f"background:{self.BODY_BG};")
        wl = QtWidgets.QVBoxLayout(wrap)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(0)

        header = QtWidgets.QFrame()
        header.setFixedHeight(32)
        header.setStyleSheet(
            f"QFrame{{background:{HEAD_BG};border:none;border-radius:5px;}}"
            "QFrame:hover{background:#4a4a4a;}")   # clickable -> lighten on hover
        hr = QtWidgets.QHBoxLayout(header)
        hr.setContentsMargins(0, 0, 10, 0)
        hr.setSpacing(7)

        _bar = QtWidgets.QFrame()
        _bar.setFixedWidth(3)
        _bar.setStyleSheet(f"background:{_accent};border:none;")
        hr.addWidget(_bar)

        if icon_name:
            try:
                from pxl_ui import icons as _pi
                _icl = QtWidgets.QLabel()
                _icl.setFixedWidth(18)
                _icl.setStyleSheet("background:transparent;")
                _icl.setPixmap(_pi.pixmap(icon_name, 18, _accent))
                hr.addWidget(_icl)
            except Exception:
                pass

        if number:
            _nl = QtWidgets.QLabel(number)
            _nl.setStyleSheet("color:#aaaaaa;font-size:12px;"
                              "font-family:'Courier New';background:transparent;")
            hr.addWidget(_nl)

        btn = QtWidgets.QPushButton(title.replace("&", "&&"))
        btn.setCheckable(True)
        btn.setChecked(starts_expanded)
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton{background:transparent;color:#dcdcdc;font-size:12px;"
            "font-weight:bold;letter-spacing:1px;border:none;text-align:left;"
            "padding:0;}")
        hr.addWidget(btn, 1)

        # section progress check (parity with Maya CollapsibleSection.set_state)
        _state_chk = QtWidgets.QLabel("")
        _state_chk.setStyleSheet(
            "color:#5BBF6A;font-weight:bold;font-size:12px;background:transparent;")
        hr.addWidget(_state_chk)

        # Chevron icon (NOT a text glyph) so closed/open are exactly the same size.
        tri = QtWidgets.QLabel()
        tri.setFixedSize(14, 14)
        tri.setAlignment(QtCore.Qt.AlignCenter)

        def _tri_style(exp):
            try:
                from pxl_ui import icons as _pi
                name = "expanded" if exp else "collapsed"   # chevron-down / chevron-right
                tri.setPixmap(_pi.pixmap(name, 12, _accent if exp else "#888888"))
            except Exception:
                tri.setText("▼" if exp else "▶")
        _tri_style(starts_expanded)
        hr.addWidget(tri)

        body_widget.setVisible(starts_expanded)

        def _toggle(checked):
            body_widget.setVisible(checked)
            _tri_style(checked)
        btn.toggled.connect(_toggle)
        header.mousePressEvent = lambda _e: btn.click()

        body_widget.setStyleSheet("background:#383838;")
        wl.addWidget(header)
        wl.addWidget(body_widget)

        # Parity with Maya: programmatic state + collapse on the section widget.
        def _set_state(state):
            if state == "done":
                bg, bar, hov = "#33402d", "#5BBF6A", "#3d4a37"   # pale-green complete
            elif state == "active":
                bg, bar, hov = "#46413a", "#E8820C", "#524d44"   # orange current step
            else:
                bg, bar, hov = HEAD_BG, _accent, "#4a4a4a"
            header.setStyleSheet(
                f"QFrame{{background:{bg};border:none;border-radius:5px;}}"
                f"QFrame:hover{{background:{hov};}}")
            _bar.setStyleSheet(f"background:{bar};border:none;")
            _state_chk.setText("✓" if state == "done" else "")
        wrap.set_state = _set_state
        wrap.set_collapsed = lambda collapsed: btn.setChecked(not collapsed)
        return wrap

    # ── SECTIONS ──────────────────────────────────────────────────────────

    def _section_hdr(self, text):
        lbl = QtWidgets.QLabel(text)
        lbl.setStyleSheet(
            f"QLabel{{color:{BRAND_ORANGE};font-size:11px;font-weight:bold;"
            "letter-spacing:1px;background:transparent;}}")
        return lbl

    # ── INSTRUCTIONS & PRELIMINARY ────────────────────────────────────────

    def _section_instructions(self):
        """Collapsible instructions + nested preliminary steps block."""
        instr_body = QtWidgets.QWidget()
        instr_body.setStyleSheet(f"background:{self.BODY_BG};")
        vl = QtWidgets.QVBoxLayout(instr_body)
        vl.setContentsMargins(12, 8, 12, 8)
        vl.setSpacing(6)

        steps_text = (
            "This panel drives the TurnTable comp in real-time — "
            "all controls update the Nuke comp live, no Apply button needed.\n\n"
            "Workflow:\n"
            "  0.  Preliminary — set working folder, verify ACES 1.2.\n"
            "  1.  Import the comp template into a new script (or Check Connection if already loaded).\n"
            "  2.  Set the Render Location (folder with RL_hdri_XX subfolders).\n"
            "  3.  Use Auto-fill to populate Asset Name and Version.\n"
            "  4.  Adjust Visual Options, Comp Effects, and Tech Settings.\n"
            "  5.  Set the Write Node output folder and hit Apply.\n\n"
            "The Check Connection button verifies all required comp nodes are "
            "present in the current Nuke session."
        )
        lbl = QtWidgets.QLabel(steps_text)
        lbl.setStyleSheet("color:#aaaaaa;font-size:10px;background:transparent;")
        lbl.setWordWrap(True)
        vl.addWidget(lbl)

        vl.addWidget(self._divider())

        # Preliminary steps — nested sub-section
        prelim_widget = self._section_preliminary_content()
        prelim_title = QtWidgets.QPushButton("▶   PRELIMINARY STEPS")
        prelim_title.setCheckable(True)
        prelim_title.setChecked(True)
        prelim_title.setStyleSheet(
            f"QPushButton{{color:#E8820C;font-size:10px;font-weight:bold;"
            "text-align:left;background:transparent;border:none;"
            "letter-spacing:1px;padding:4px 0;}}"
            "QPushButton:checked{color:#E8820C;}"
        )
        prelim_title.toggled.connect(
            lambda checked: (
                prelim_widget.setVisible(checked),
                prelim_title.setText(("▼" if checked else "▶") + "   PRELIMINARY STEPS")
            )
        )
        vl.addWidget(prelim_title)
        vl.addWidget(prelim_widget)

        wrap = self._collapsible("INSTRUCTIONS", instr_body,
                                 starts_expanded=False,
                                 icon_name="info", accent="#46C2D6")
        # Store the toggle button so we can auto-collapse after preliminary setup
        self._instr_btn = wrap.findChildren(QtWidgets.QPushButton)[0]
        return wrap

    def _section_preliminary_content(self) -> QtWidgets.QWidget:
        """ACES 1.2 check (technical, do once) -> Set working folder."""
        global _aces_checked_once
        w = QtWidgets.QWidget()
        w.setStyleSheet(f"background:{self.BODY_BG};")
        vl = QtWidgets.QVBoxLayout(w)
        vl.setContentsMargins(0, 4, 0, 4)
        vl.setSpacing(8)

        # ── Step 1 — ACES 1.2 COLOUR MANAGEMENT (technical check) ─────────
        row1, self._prelim_aces_badge, self._prelim_aces_confirm = self._mk_step_header(
            "1", "ACES 1.2 COLOUR MANAGEMENT")
        vl.addLayout(row1)
        self._set_badge(self._prelim_aces_badge, "active")

        aces_hint = QtWidgets.QLabel(
            "Verifies that Nuke is using the ACES 1.2 OCIO config. "
            "Checked automatically on first launch; click the button to re-check.")
        aces_hint.setStyleSheet(
            "color:#B0B0B0;font-size:11px;background:transparent;")
        aces_hint.setWordWrap(True)
        vl.addWidget(aces_hint)

        self.lbl_aces_status = self._stat()
        vl.addWidget(self.lbl_aces_status)

        btn_check_aces = self._btn("Check ACES 1.2 Config", False)
        btn_check_aces.setStyleSheet(self._STEP_BTN["active"])   # gray + orange border
        vl.addWidget(btn_check_aces)

        def _check_aces():
            try:
                cm = nuke.root().knob('colorManagement').value()
                if cm == "OCIO":
                    self._set_status(self.lbl_aces_status,
                                     "ACES 1.2 active — OCIO color management confirmed.", "ok")
                    self._set_badge(self._prelim_aces_badge, "done")
                    self._set_confirm(self._prelim_aces_confirm, True)
                    btn_check_aces.setStyleSheet(self._STEP_BTN["done"])   # pale-green done (Maya parity)
                else:
                    self._set_status(self.lbl_aces_status,
                                     f"Color management is '{cm}' — set to OCIO in "
                                     "Edit > Project Settings > Color.", "err")
                    self._set_badge(self._prelim_aces_badge, "active")
                    self._set_confirm(self._prelim_aces_confirm, False)
                    btn_check_aces.setStyleSheet(self._STEP_BTN["active"])
            except Exception as exc:
                self._set_status(self.lbl_aces_status, f"Could not check: {exc}", "err")

        btn_check_aces.clicked.connect(_check_aces)
        if not _aces_checked_once:
            _check_aces()
            _aces_checked_once = True

        vl.addWidget(self._divider())

        # ── Step 2 — NUKE WORKING FOLDER ──────────────────────────────────
        row2, self._prelim_folder_badge, self._prelim_folder_confirm = self._mk_step_header(
            "2", "SET NUKE WORKING FOLDER")
        vl.addLayout(row2)
        self._set_badge(self._prelim_folder_badge, "active")

        folder_hint = QtWidgets.QLabel(
            "The project directory controls where Nuke resolves relative paths. "
            "Set it to  TurnTable_ROOT/_COMP  — every asset the tool uses "
            "(comp template, HDRI_previews, Dirt, LUT, session) lives directly "
            "inside that folder.")
        folder_hint.setStyleSheet(
            "color:#B0B0B0;font-size:11px;background:transparent;")
        folder_hint.setWordWrap(True)
        vl.addWidget(folder_hint)

        # Browse row: editable field + Browse button
        browse_row = QtWidgets.QWidget()
        browse_row.setStyleSheet(f"background:{self.BODY_BG};")
        brl = QtWidgets.QHBoxLayout(browse_row)
        brl.setContentsMargins(0, 0, 0, 0)
        brl.setSpacing(6)
        self.f_proj_dir = self._field(placeholder="Path to TurnTable_ROOT/_COMP…")
        self.f_proj_dir.setText("")
        btn_browse_proj = self._btn("Browse…", False)
        btn_browse_proj.setFixedSize(92, 32)   # standard inline-action button size
        brl.addWidget(self.f_proj_dir, 1)
        brl.addWidget(btn_browse_proj)
        vl.addWidget(browse_row)

        # Action row: Set + Refresh
        action_row = QtWidgets.QWidget()
        action_row.setStyleSheet(f"background:{self.BODY_BG};")
        arl = QtWidgets.QHBoxLayout(action_row)
        arl.setContentsMargins(0, 0, 0, 0)
        arl.setSpacing(6)
        btn_set_proj     = self._btn("Set Working Folder", False)
        btn_set_proj.setStyleSheet(self._STEP_BTN["active"])   # gray + orange border (Maya parity)
        btn_refresh_proj = self._btn("Refresh", False)
        btn_refresh_proj.setMinimumWidth(84)
        arl.addWidget(btn_set_proj, 1)
        arl.addWidget(btn_refresh_proj)
        vl.addWidget(action_row)

        self.lbl_proj_status = self._stat()
        vl.addWidget(self.lbl_proj_status)

        def _browse_proj():
            start = self.f_proj_dir.text().strip() or "D:/"
            path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Working Folder", start)
            if path:
                self.f_proj_dir.setText(path.replace("\\", "/"))

        def _set_proj():
            path = self.f_proj_dir.text().strip().replace("\\", "/")
            if not path:
                self._set_status(self.lbl_proj_status, "Enter a folder path first.", "warn")
                return
            try:
                nuke.root()["project_directory"].setValue(path)
                _refresh_proj()
                # Auto-collapse Instructions after first successful setup
                if hasattr(self, "_instr_btn") and self._instr_btn.isChecked():
                    self._instr_btn.setChecked(False)
                # Save session config (lives under {working_folder}/_COMP/)
                _save_session(path, self._collect_prefs())
            except Exception as exc:
                self._set_status(self.lbl_proj_status, f"Could not set: {exc}", "err")

        def _refresh_proj():
            try:
                cur = nuke.root()["project_directory"].value() or "(not set)"
            except Exception:
                cur = "(not available — open a comp first)"
            # Update field if current differs from what Nuke actually has
            if cur not in ("(not set)", "(not available — open a comp first)"):
                self.f_proj_dir.setText(cur.replace("\\", "/"))
            cur_norm = cur.replace("\\", "/")
            ok = "_COMP" in cur_norm
            if ok:
                self._set_status(self.lbl_proj_status,
                                 f"Working folder: {cur_norm}", "ok")
                self._set_badge(self._prelim_folder_badge, "done")
                self._set_confirm(self._prelim_folder_confirm, True)
                btn_set_proj.setStyleSheet(self._STEP_BTN["done"])   # pale-green done (Maya parity)
            else:
                self._set_status(self.lbl_proj_status,
                                 "Working folder is NOT set to _COMP. Browse and click Set.",
                                 "warn")
                self._set_badge(self._prelim_folder_badge, "active")
                self._set_confirm(self._prelim_folder_confirm, False)
                btn_set_proj.setStyleSheet(self._STEP_BTN["active"])

        btn_browse_proj.clicked.connect(_browse_proj)
        btn_set_proj.clicked.connect(_set_proj)
        btn_refresh_proj.clicked.connect(_refresh_proj)
        _refresh_proj()  # populate on build

        return w

    def _section_template_body(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet(f"background:{self.BODY_BG};")
        vl = QtWidgets.QVBoxLayout(w)
        vl.setContentsMargins(14, 12, 14, 14)
        vl.setSpacing(10)

        self.btn_import = QtWidgets.QPushButton("Load Turntable Template")
        self.btn_import.setStyleSheet(self._STEP_BTN["active"])   # gray + orange border (Maya parity)
        self.btn_import.setMinimumHeight(42)
        self.btn_import.setCursor(QtCore.Qt.PointingHandCursor)
        vl.addWidget(self.btn_import)

        self.btn_import.clicked.connect(self._do_open_template)
        self.btn_import.clicked.connect(
            lambda: QtCore.QTimer.singleShot(400, self._cs_after_import))

        return w

    def _section_folder_body(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet(f"background:{self.BODY_BG};")
        vl = QtWidgets.QVBoxLayout(w)
        vl.setContentsMargins(14, 12, 14, 14)
        vl.setSpacing(8)

        # ── Step 1 — Browse the render location ───────────────────────────
        row1, self._fld_browse_badge, self._fld_browse_confirm = self._mk_step_header(
            "1", "BROWSE RENDER LOCATION")
        vl.addLayout(row1)
        self._set_badge(self._fld_browse_badge, "active")

        info = QtWidgets.QLabel(
            "Folder with the render-layer subfolders — "
            "RL_hdri_01…RL_hdri_08  |  RL_charts_01…RL_charts_08. "
            "Asset name and version are auto-detected.")
        info.setStyleSheet(
            "color:#B0B0B0;font-size:11px;background:transparent;")
        info.setWordWrap(True)
        vl.addWidget(info)

        self.f_render_folder = self._path_row(vl, "Render Location", folder=True)

        vl.addWidget(self._divider())

        # ── Project settings inset box ────────────────────────────────────
        settings_box = QtWidgets.QFrame()
        settings_box.setStyleSheet(
            "QFrame{background:#383838;border:1px solid #2c2c2c;border-radius:6px;}"
        )
        sbl = QtWidgets.QVBoxLayout(settings_box)
        sbl.setContentsMargins(10, 8, 10, 10)
        sbl.setSpacing(7)

        # ── Step 2 — Apply project settings (Format / FPS / Frame Range) ──
        row2, self._fld_apply_badge, self._fld_apply_confirm = self._mk_step_header(
            "2", "APPLY PROJECT SETTINGS")
        sbl.addLayout(row2)
        self._set_badge(self._fld_apply_badge, "active")

        # Format
        self.combo_project_fmt = QtWidgets.QComboBox()
        self.combo_project_fmt.setStyleSheet(self._FIELD)
        default_fmt_idx = 0
        try:
            fmts = sorted(nuke.formats(), key=lambda f: -(f.width() * f.height()))
            for i, f in enumerate(fmts):
                label = f"{f.width()} \u00d7 {f.height()}  \u2014  {f.name()}"
                self.combo_project_fmt.addItem(label, f.name())
                if f.name() == "HD_1080":
                    default_fmt_idx = i
        except Exception:
            for name, w_, h_ in [
                ("HD_1080", 1920, 1080), ("HD_720", 1280, 720),
                ("UHD_4K", 3840, 2160), ("DCI_4K", 4096, 2160),
                ("DCI_2K", 2048, 1080), ("2K", 2048, 1556),
                ("PAL", 720, 576), ("NTSC", 720, 486),
            ]:
                self.combo_project_fmt.addItem(
                    f"{w_} \u00d7 {h_}  \u2014  {name}", name)
        self.combo_project_fmt.setCurrentIndex(default_fmt_idx)

        # Top row — Format (left) + FPS (right): two columns to save height
        self.combo_fps = self._combo(FPS_OPTIONS)
        self.combo_fps.setMinimumWidth(88)
        fps_idx = FPS_OPTIONS.index(FPS_DEFAULT) if FPS_DEFAULT in FPS_OPTIONS else 0
        self.combo_fps.setCurrentIndex(fps_idx)

        top_row = QtWidgets.QWidget()
        top_row.setStyleSheet("background:transparent;border:none;")
        trl = QtWidgets.QHBoxLayout(top_row)
        trl.setContentsMargins(0, 0, 0, 0)
        trl.setSpacing(10)
        fmt_lbl = QtWidgets.QLabel("Format")
        fmt_lbl.setStyleSheet("color:#aaa;font-size:10px;background:transparent;border:none;")
        fmt_lbl.setFixedWidth(56)
        trl.addWidget(fmt_lbl)
        trl.addWidget(self.combo_project_fmt, 1)
        fps_lbl = QtWidgets.QLabel("FPS")
        fps_lbl.setStyleSheet("color:#aaa;font-size:10px;background:transparent;border:none;")
        fps_lbl.setFixedWidth(30)
        trl.addWidget(fps_lbl)
        trl.addWidget(self.combo_fps)
        sbl.addWidget(top_row)

        # Frame Range
        fr_wrap = QtWidgets.QWidget()
        fr_wrap.setStyleSheet("background:transparent;border:none;")
        frl = QtWidgets.QHBoxLayout(fr_wrap)
        frl.setContentsMargins(0, 0, 0, 0)
        frl.setSpacing(6)

        self.sp_frame_start = QtWidgets.QSpinBox()
        self.sp_frame_start.setRange(0, 999999)
        self.sp_frame_start.setValue(1001)
        self.sp_frame_start.setStyleSheet(self._FIELD)
        self.sp_frame_start.setFixedWidth(80)

        lbl_dash = QtWidgets.QLabel("—")
        lbl_dash.setStyleSheet("color:#888;background:transparent;font-size:11px;border:none;")

        self.sp_frame_end = QtWidgets.QSpinBox()
        self.sp_frame_end.setRange(0, 999999)
        self.sp_frame_end.setValue(1100)
        self.sp_frame_end.setStyleSheet(self._FIELD)
        self.sp_frame_end.setFixedWidth(80)

        frl.addWidget(self.sp_frame_start)
        frl.addWidget(lbl_dash)
        frl.addWidget(self.sp_frame_end)
        frl.addStretch()

        fr_row = QtWidgets.QWidget()
        fr_row.setStyleSheet("background:transparent;border:none;")
        frrl = QtWidgets.QHBoxLayout(fr_row)
        frrl.setContentsMargins(0, 0, 0, 0)
        frrl.setSpacing(8)
        fr_lbl = QtWidgets.QLabel("Frame Range")
        fr_lbl.setStyleSheet("color:#aaa;font-size:10px;background:transparent;border:none;")
        fr_lbl.setFixedWidth(72)
        frrl.addWidget(fr_lbl)
        frrl.addWidget(fr_wrap, 1)
        sbl.addWidget(fr_row)

        vl.addWidget(settings_box)

        vl.addWidget(self._divider())

        self.btn_apply_settings = QtWidgets.QPushButton("Apply Project Settings to Comp")
        self.btn_apply_settings.setMinimumHeight(38)
        self.btn_apply_settings.setStyleSheet(self._STEP_BTN["active"])   # gray + orange border
        vl.addWidget(self.btn_apply_settings)

        self.lbl_scan_status = self._stat("No render location set yet.")
        vl.addWidget(self.lbl_scan_status)

        # Step badges: 1 done when a render folder is set; 2 done on Apply.
        def _mark_browse(*_):
            ok = bool(self.f_render_folder.text().strip())
            self._set_badge(self._fld_browse_badge, "done" if ok else "active")
            self._set_confirm(self._fld_browse_confirm, ok)

        def _mark_applied(*_):
            self._set_badge(self._fld_apply_badge, "done")
            self._set_confirm(self._fld_apply_confirm, True)
            self.btn_apply_settings.setStyleSheet(self._STEP_BTN["done"])

        self.f_render_folder.textChanged.connect(_mark_browse)
        self.btn_apply_settings.clicked.connect(self._do_apply_project_settings)
        self.btn_apply_settings.clicked.connect(_mark_applied)
        self.btn_apply_settings.clicked.connect(
            lambda: QtCore.QTimer.singleShot(400, self._cs_after_folder))
        self.btn_apply_settings.clicked.connect(
            lambda: QtCore.QTimer.singleShot(500, self._save_node_state))
        self.f_render_folder.editingFinished.connect(self._on_folder_changed)
        _mark_browse()  # initial badge state
        return w

    def _section_asset_body(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet(f"background:{self.BODY_BG};")
        vl = QtWidgets.QVBoxLayout(w)
        vl.setContentsMargins(14, 12, 14, 14)
        vl.setSpacing(8)

        # ── Type + Auto-fill row ───────────────────────────────────────────
        type_wrap = QtWidgets.QWidget()
        type_wrap.setStyleSheet(f"background:{self.BODY_BG};")
        twl = QtWidgets.QHBoxLayout(type_wrap)
        twl.setContentsMargins(0, 0, 0, 0)
        twl.setSpacing(6)
        self.combo_asset_type = self._code_combo(ASSET_TYPE_PAIRS)
        self.combo_asset_type.setFixedWidth(150)
        self.btn_af = self._btn("Auto-fill", False)
        self.btn_af.setFixedSize(92, 32)   # standard inline-action button size
        twl.addWidget(self.combo_asset_type)
        twl.addStretch()
        twl.addWidget(self.btn_af)
        vl.addWidget(self._row("Type", type_wrap))

        # ── Asset name ────────────────────────────────────────────────────
        self.f_asset_name = self._field(placeholder="e.g. Scion")
        vl.addWidget(self._row("Asset Name", self.f_asset_name))

        # ── Dept ─────────────────────────────────────────────────────────
        self.combo_asset_dept = self._code_combo(DEPT_PAIRS)
        self.combo_asset_dept.setFixedWidth(150)
        dept_wrap = QtWidgets.QWidget()
        dept_wrap.setStyleSheet(f"background:{self.BODY_BG};")
        dwl = QtWidgets.QHBoxLayout(dept_wrap)
        dwl.setContentsMargins(0, 0, 0, 0)
        dwl.addWidget(self.combo_asset_dept)
        dwl.addStretch()
        vl.addWidget(self._row("Dept", dept_wrap))

        # ── Version ───────────────────────────────────────────────────────
        self.f_asset_version = self._field(placeholder="e.g. v001")
        vl.addWidget(self._row("Version", self.f_asset_version))

        # ── User (optional) ───────────────────────────────────────────────
        self.f_asset_user = self._field(placeholder="e.g. csp  (WIP only)")
        vl.addWidget(self._row("User", self.f_asset_user))

        # ── Color-coded naming preview ────────────────────────────────────
        self.lbl_naming_preview = QtWidgets.QLabel()
        self.lbl_naming_preview.setTextFormat(QtCore.Qt.RichText)
        self.lbl_naming_preview.setStyleSheet(
            "background:#0e0e0e;border:1px solid #2a2a2a;"
            "padding:6px 10px;font-size:12px;font-family:monospace;")
        self.lbl_naming_preview.setWordWrap(True)
        vl.addWidget(self.lbl_naming_preview)

        # ── Font Scale ────────────────────────────────────────────────────
        fs_wrap = QtWidgets.QWidget()
        fs_wrap.setStyleSheet(f"background:{self.BODY_BG};")
        fswl = QtWidgets.QHBoxLayout(fs_wrap)
        fswl.setContentsMargins(0, 0, 0, 0)
        self.sp_font_scale = self._spinbox(0.1, 5.0, 0.1, 1.0, decimals=2, width=80)
        fswl.addWidget(self.sp_font_scale)
        fswl.addStretch()
        vl.addWidget(self._row("Font Scale", fs_wrap))

        # ── Connections ───────────────────────────────────────────────────
        def _push_text():
            t = self._combo_code(self.combo_asset_type)
            n = self.f_asset_name.text().strip()
            d = self._combo_code(self.combo_asset_dept)
            v = self.f_asset_version.text().strip()
            u = self.f_asset_user.text().strip()
            self._update_naming_preview(t, n, d, v, u)
            self._live(live_asset_text, t, n, d, v, u)

        def _push_and_check():
            _push_text()
            pass  # no-op: step gating removed in v1.1.0

        self.combo_asset_type.currentIndexChanged.connect(lambda _: _push_and_check())
        self.f_asset_name.editingFinished.connect(_push_and_check)
        self.combo_asset_dept.currentIndexChanged.connect(lambda _: _push_and_check())
        self.f_asset_version.editingFinished.connect(self._on_version_changed)
        self.f_asset_version.editingFinished.connect(_push_and_check)
        self.f_asset_user.editingFinished.connect(_push_text)
        self.sp_font_scale.valueChanged.connect(lambda v: self._live(live_font_scale, v))
        self.btn_af.clicked.connect(self._do_autofill)

        self._update_naming_preview("", "", "", "", "")

        return w

    def _update_naming_preview(self, type_code, name, dept, version, user):
        SEP  = '<span style="color:#8a6a00;">_</span>'
        DIM  = "color:#555555;"

        def _tok(text, color):
            t = text or "…"
            return f'<span style="color:{color};">{t}</span>'

        parts_html = []
        parts_html.append(_tok(type_code, "#4A90D9"))
        parts_html.append(_tok(name,      "#CCCCCC"))
        parts_html.append(_tok(dept,      "#5EC47A"))
        parts_html.append(_tok(version,   "#F2B705"))
        if user:
            parts_html.append(_tok(user, "#888888"))

        html = SEP.join(parts_html)
        self.lbl_naming_preview.setText(html)

    # ── SECTION BODIES ────────────────────────────────────────────────────

    def _build_visual_options(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        w.setStyleSheet(f"background:{self.BODY_BG};")
        vl = QtWidgets.QVBoxLayout(w)
        vl.setContentsMargins(12, 10, 12, 10)
        vl.setSpacing(8)

        self.combo_hdri   = self._combo(HDRI_OPTIONS)
        self.combo_hdri.view().setStyleSheet(
            "QListView::item:disabled { color: #cc4444; font-style: italic; }"
        )
        self.combo_render = self._combo(RENDER_OPTIONS)
        self.combo_back   = self._combo(BACK_OPTIONS)
        self.combo_back.setCurrentIndex(1)

        # BG color widget
        bgw = QtWidgets.QWidget()
        bgw.setStyleSheet(f"background:{self.BODY_BG};")
        bgl = QtWidgets.QHBoxLayout(bgw)
        bgl.setContentsMargins(0, 0, 0, 0)
        self.btn_bg_color = self._color_btn(1.0, 1.0, 1.0)   # default: white
        bgl.addWidget(self.btn_bg_color)
        bgl.addStretch()
        # Wire color widget
        wfw = QtWidgets.QWidget()
        wfw.setStyleSheet(f"background:{self.BODY_BG};")
        wfl = QtWidgets.QHBoxLayout(wfw)
        wfl.setContentsMargins(0, 0, 0, 0)
        self.btn_wf_color = self._color_btn(0.0, 1.0, 1.0)   # default: cyan
        wfl.addWidget(self.btn_wf_color)
        wfl.addStretch()

        # Two columns to save vertical space: combos | colours
        two = QtWidgets.QHBoxLayout()
        two.setSpacing(18)
        col_l = QtWidgets.QVBoxLayout(); col_l.setSpacing(8)
        col_r = QtWidgets.QVBoxLayout(); col_r.setSpacing(8)
        col_l.addWidget(self._row("HDRI",        self.combo_hdri,   lw=92))
        col_l.addWidget(self._row("Render Type", self.combo_render, lw=92))
        col_l.addWidget(self._row("Background",  self.combo_back,   lw=92))
        col_r.addWidget(self._row("BG Color",    bgw, lw=92))
        col_r.addWidget(self._row("Wire Color",  wfw, lw=92))
        # Master Comp-Effects toggle sits right under the colours.
        self.chk_compfx = self._chk("Activate Comp Effects", checked=False)
        col_r.addWidget(self.chk_compfx)
        col_r.addStretch()
        two.addLayout(col_l, 1)
        two.addLayout(col_r, 1)
        vl.addLayout(two)

        # Connections
        self.combo_hdri.currentIndexChanged.connect(
            lambda _: self._on_hdri_or_render_changed())
        self.combo_render.currentIndexChanged.connect(
            lambda _: self._on_hdri_or_render_changed())
        self.combo_back.currentIndexChanged.connect(
            lambda i: self._live(live_back_select, i))
        self.btn_bg_color.clicked.connect(
            lambda: self._pick_color(self.btn_bg_color,
                                     lambda r, g, b: live_bg_color(r, g, b)))
        self.btn_wf_color.clicked.connect(
            lambda: self._pick_color(self.btn_wf_color,
                                     lambda r, g, b: live_wireframe_color(r, g, b)))
        self.chk_compfx.toggled.connect(lambda v: self._live(live_compfx, v))
        return w

    def _build_comp_effects(self) -> QtWidgets.QWidget:
        """Z Defocus → Lens Dirt → LUT  (checked = feature enabled)."""
        w = QtWidgets.QWidget()
        w.setStyleSheet(f"background:{self.BODY_BG};")
        vl = QtWidgets.QVBoxLayout(w)
        vl.setContentsMargins(12, 10, 12, 10)
        vl.setSpacing(6)

        # ── Z Defocus ─────────────────────────────────────────────────────
        self.chk_zdof = self._chk("Z Defocus", checked=False)
        vl.addWidget(self.chk_zdof)

        zdof_note = QtWidgets.QLabel(
            "Switch View Output to ‘Focal Plane’ to visualise the depth map, "
            "then dial in Focus Plane Distance (cm) until the subject sits on the plane. "
            "Switch back to ‘Result’ and tune Depth of Field and Blur Size.")
        zdof_note.setWordWrap(True)
        zdof_note.setStyleSheet(
            "QLabel{color:#B0B0B0;font-size:11px;"
            "background:transparent;padding:2px 0 4px 0;}")
        vl.addWidget(zdof_note)

        zdof_sub = QtWidgets.QWidget()
        zdof_sub.setStyleSheet("background:#383838;border-radius:6px;")
        zvl = QtWidgets.QVBoxLayout(zdof_sub)
        zvl.setContentsMargins(8, 6, 8, 6)
        zvl.setSpacing(5)
        self.sp_zdof_center = self._spinbox(0.0, 100000.0, 10.0, 100.0, decimals=1)
        self.sp_zdof_dof    = self._spinbox(0.0, 100.0,    0.05, 0.1,   decimals=3)
        self.sp_zdof_size   = self._spinbox(0.0, 200.0,    1.0,  10.0,  decimals=1)
        for lbl_txt, sb in (("Focus Plane (cm)", self.sp_zdof_center),
                            ("Depth of Field",   self.sp_zdof_dof),
                            ("Blur Size",        self.sp_zdof_size)):
            rw = QtWidgets.QWidget()
            rw.setStyleSheet("background:transparent;")
            rl = QtWidgets.QHBoxLayout(rw)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(8)
            l = QtWidgets.QLabel(lbl_txt)
            l.setFixedWidth(110)
            l.setStyleSheet("QLabel{color:#aaaaaa;font-size:10px;background:transparent;}")
            rl.addWidget(l)
            rl.addWidget(sb, 1)
            zvl.addWidget(rw)

        # Output mode — switch between defocused result and focal plane view
        out_rw = QtWidgets.QWidget()
        out_rw.setStyleSheet("background:transparent;")
        out_rl = QtWidgets.QHBoxLayout(out_rw)
        out_rl.setContentsMargins(0, 0, 0, 0)
        out_rl.setSpacing(8)
        out_lbl = QtWidgets.QLabel("View Output")
        out_lbl.setFixedWidth(110)
        out_lbl.setStyleSheet("QLabel{color:#aaaaaa;font-size:10px;background:transparent;}")
        self.combo_zdof_output = self._combo(["Result", "Focal Plane"])
        out_rl.addWidget(out_lbl)
        out_rl.addWidget(self.combo_zdof_output, 1)
        zvl.addWidget(out_rw)

        vl.addWidget(zdof_sub)

        # ── Lens Dirt ─────────────────────────────────────────────────────
        vl.addWidget(self._divider())
        dirt_row = QtWidgets.QWidget()
        dirt_row.setStyleSheet(f"background:{self.BODY_BG};")
        drl = QtWidgets.QHBoxLayout(dirt_row)
        drl.setContentsMargins(0, 2, 0, 2)
        drl.setSpacing(6)
        self.chk_lens_dirt    = self._chk("Lens Dirt", checked=True)
        self.chk_lens_dirt.setFixedWidth(82)
        self.sld_lens_dirt    = self._slider(0, 100, 35)
        self.sp_lens_dirt_mix = self._spinbox(0.0, 1.0, 0.05, 0.35, decimals=2, width=72)
        drl.addWidget(self.chk_lens_dirt)
        drl.addWidget(self.sld_lens_dirt, 1)
        drl.addWidget(self.sp_lens_dirt_mix)
        vl.addWidget(dirt_row)

        # ── LUT ───────────────────────────────────────────────────────────
        vl.addWidget(self._divider())
        lut_row = QtWidgets.QWidget()
        lut_row.setStyleSheet(f"background:{self.BODY_BG};")
        lrl = QtWidgets.QHBoxLayout(lut_row)
        lrl.setContentsMargins(0, 2, 0, 2)
        lrl.setSpacing(6)
        self.chk_lut    = self._chk("LUT", checked=False)
        self.chk_lut.setFixedWidth(82)
        self.sld_lut    = self._slider(0, 100, 35)
        self.sp_lut_mix = self._spinbox(0.0, 1.0, 0.05, 0.35, decimals=2, width=72)
        lrl.addWidget(self.chk_lut)
        lrl.addWidget(self.sld_lut, 1)
        lrl.addWidget(self.sp_lut_mix)
        vl.addWidget(lut_row)
        self.f_lut_path = self._path_row(
            vl, "LUT File", file_filter="LUT files (*.cube *.lut);;All (*)")

        # ── Connections ───────────────────────────────────────────────────
        self.chk_zdof.toggled.connect(
            lambda v: self._live(live_zdof_disable, not v))
        self.sp_zdof_center.valueChanged.connect(
            lambda v: self._live(live_zdof_center, v))
        self.sp_zdof_dof.valueChanged.connect(
            lambda v: self._live(live_zdof_dof, v))
        self.sp_zdof_size.valueChanged.connect(
            lambda v: self._live(live_zdof_size, v))
        self.combo_zdof_output.currentIndexChanged.connect(
            lambda i: self._live(live_zdof_output, i))
        self.chk_lens_dirt.toggled.connect(
            lambda v: self._live(live_lens_dirt_disable, not v))
        self.chk_lut.toggled.connect(
            lambda v: self._live(live_lut_disable, not v))
        self.f_lut_path.editingFinished.connect(
            lambda: self._live(live_lut_path, self.f_lut_path.text().strip()))

        def _on_dirt_slider(val):
            self.sp_lens_dirt_mix.blockSignals(True)
            self.sp_lens_dirt_mix.setValue(val / 100.0)
            self.sp_lens_dirt_mix.blockSignals(False)
            self._live(live_lens_dirt_mix, val / 100.0)

        def _on_dirt_spin(val):
            self.sld_lens_dirt.blockSignals(True)
            self.sld_lens_dirt.setValue(int(round(val * 100)))
            self.sld_lens_dirt.blockSignals(False)
            self._live(live_lens_dirt_mix, val)

        def _on_lut_slider(val):
            self.sp_lut_mix.blockSignals(True)
            self.sp_lut_mix.setValue(val / 100.0)
            self.sp_lut_mix.blockSignals(False)
            self._live(live_lut_mix, val / 100.0)

        def _on_lut_spin(val):
            self.sld_lut.blockSignals(True)
            self.sld_lut.setValue(int(round(val * 100)))
            self.sld_lut.blockSignals(False)
            self._live(live_lut_mix, val)

        self.sld_lens_dirt.valueChanged.connect(_on_dirt_slider)
        self.sp_lens_dirt_mix.valueChanged.connect(_on_dirt_spin)
        self.sld_lut.valueChanged.connect(_on_lut_slider)
        self.sp_lut_mix.valueChanged.connect(_on_lut_spin)
        return w

    def _build_tech_settings(self) -> QtWidgets.QWidget:
        """
        Two-column grid — all ON by default (checked = feature enabled).

        Visual        |  Extra Info
        Occlusion     |  Text Info
        Shadows       |  Balls & Charts
        Back Ramp     |  HDRI Preview
        Vignetting    |  Reference Images
        [===intensity slider 0-1===]
        """
        w = QtWidgets.QWidget()
        w.setStyleSheet(f"background:{self.BODY_BG};")
        vl = QtWidgets.QVBoxLayout(w)
        vl.setContentsMargins(12, 10, 12, 10)
        vl.setSpacing(8)

        # Checkboxes
        self.chk_occlusion  = self._chk("Occlusion",        checked=False)
        self.chk_shadow     = self._chk("Shadow",           checked=True)
        self.chk_back_ramp  = self._chk("BG Ramp",         checked=True)
        self.chk_vignette   = self._chk("Vignetting",       checked=True)
        self.chk_text_info  = self._chk("Asset Info",       checked=True)
        self.chk_ref_ball   = self._chk("Balls & Charts",   checked=True)
        self.chk_hdri_prev  = self._chk("HDRI Previews",    checked=True)
        self.chk_ref_images = self._chk("Reference Images", checked=True)

        def _note(text):
            lbl = QtWidgets.QLabel(text)
            lbl.setStyleSheet(
                "color:#555;font-size:9px;font-style:italic;background:transparent;")
            return lbl

        # Two-column widget
        cols_w = QtWidgets.QWidget()
        cols_w.setStyleSheet(f"background:{self.BODY_BG};")
        cols_l = QtWidgets.QHBoxLayout(cols_w)
        cols_l.setContentsMargins(0, 0, 0, 0)
        cols_l.setSpacing(16)

        # ── Left / VISUAL column ──────────────────────────────────────────
        left_w = QtWidgets.QWidget()
        left_w.setStyleSheet(f"background:{self.BODY_BG};")
        left_v = QtWidgets.QVBoxLayout(left_w)
        left_v.setContentsMargins(0, 0, 0, 0)
        left_v.setSpacing(4)

        _lhdr = QtWidgets.QLabel("VISUAL")
        _lhdr.setStyleSheet(self._COL_HDR)
        left_v.addWidget(_lhdr)

        def _chk_row(chk, note_text=None):
            if not note_text:
                return chk
            rw = QtWidgets.QWidget()
            rw.setStyleSheet(f"background:{self.BODY_BG};")
            rl = QtWidgets.QHBoxLayout(rw)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(4)
            rl.addWidget(chk)
            rl.addWidget(_note(note_text))
            rl.addStretch()
            return rw

        left_v.addWidget(_chk_row(self.chk_occlusion))
        left_v.addWidget(_chk_row(self.chk_shadow,    "Only for Colored BG"))
        left_v.addWidget(_chk_row(self.chk_back_ramp, "Only for Colored BG"))
        left_v.addWidget(_chk_row(self.chk_vignette,  "Only for Colored BG"))

        # Slider immediately under Vignetting, confined to this column
        vig_int_lbl = QtWidgets.QLabel("Vignetting Intensity")
        vig_int_lbl.setStyleSheet("color:#A8A8A8;font-size:10px;background:transparent;")
        left_v.addWidget(vig_int_lbl)
        self.sld_vignette    = self._slider(0, 100, 25)
        self.sp_vignette_mix = self._spinbox(0.0, 1.0, 0.05, 0.25, decimals=2, width=72)
        vig_sld_row = QtWidgets.QWidget()
        vig_sld_row.setStyleSheet(f"background:{self.BODY_BG};")
        vig_srl = QtWidgets.QHBoxLayout(vig_sld_row)
        vig_srl.setContentsMargins(0, 0, 0, 0)
        vig_srl.setSpacing(6)
        vig_srl.addWidget(self.sld_vignette, 1)
        vig_srl.addWidget(self.sp_vignette_mix)
        left_v.addWidget(vig_sld_row)

        left_v.addStretch()

        # ── Right / EXTRA INFO column ─────────────────────────────────────
        right_w = QtWidgets.QWidget()
        right_w.setStyleSheet(f"background:{self.BODY_BG};")
        right_v = QtWidgets.QVBoxLayout(right_w)
        right_v.setContentsMargins(0, 0, 0, 0)
        right_v.setSpacing(4)

        _rhdr = QtWidgets.QLabel("EXTRA INFO")
        _rhdr.setStyleSheet(self._COL_HDR)
        right_v.addWidget(_rhdr)
        for chk in (self.chk_text_info, self.chk_ref_images,
                    self.chk_hdri_prev, self.chk_ref_ball):
            right_v.addWidget(chk)
        right_v.addStretch()

        cols_l.addWidget(left_w,  1)
        cols_l.addWidget(right_w, 1)
        vl.addWidget(cols_w)

        # Connections — checked = enabled → pass v directly to disable setter
        self.chk_occlusion.toggled.connect(
            lambda v: self._live(live_occlusion_disable, v))
        self.chk_shadow.toggled.connect(
            lambda v: self._live(live_shadow_disable, v))
        self.chk_back_ramp.toggled.connect(
            lambda v: self._live(live_back_ramp_disable, v))
        self.chk_vignette.toggled.connect(
            lambda v: self._live(live_vignette_disable, v))
        self.chk_text_info.toggled.connect(
            lambda v: self._live(live_text_info_disable, v))
        self.chk_ref_ball.toggled.connect(
            lambda v: self._live(live_ref_ball_disable, v))
        self.chk_hdri_prev.toggled.connect(
            lambda v: self._live(live_hdri_preview_disable, v))
        self.chk_ref_images.toggled.connect(
            lambda v: self._live(live_ref_images_disable, v))

        # Slider ↔ spinbox
        def _on_vig_slider(val):
            self.sp_vignette_mix.blockSignals(True)
            self.sp_vignette_mix.setValue(val / 100.0)
            self.sp_vignette_mix.blockSignals(False)
            self._live(live_vignette_intensity, val / 100.0)

        def _on_vig_spin(val):
            self.sld_vignette.blockSignals(True)
            self.sld_vignette.setValue(int(round(val * 100)))
            self.sld_vignette.blockSignals(False)
            self._live(live_vignette_intensity, val)

        self.sld_vignette.valueChanged.connect(_on_vig_slider)
        self.sp_vignette_mix.valueChanged.connect(_on_vig_spin)
        return w

    def _build_references(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        w.setStyleSheet(f"background:{self.BODY_BG};")
        vl = QtWidgets.QVBoxLayout(w)
        vl.setContentsMargins(12, 10, 12, 10)
        vl.setSpacing(10)

        IMG_FILTER = "Images (*.jpg *.jpeg *.png *.exr *.tif *.tiff *.dpx);;All (*)"

        # ── Translate / Scale ─────────────────────────────────────────────
        tr_w = QtWidgets.QWidget()
        tr_w.setStyleSheet(f"background:{self.BODY_BG};")
        trl = QtWidgets.QHBoxLayout(tr_w)
        trl.setContentsMargins(0, 0, 0, 0)
        trl.setSpacing(6)
        self.sp_ref_tx = self._spinbox(-10000.0, 10000.0, 10.0, 0.0, decimals=1, width=80)
        self.sp_ref_ty = self._spinbox(-10000.0, 10000.0, 10.0, 0.0, decimals=1, width=80)
        _ls = "color:#888;font-size:10px;background:transparent;"
        lx = QtWidgets.QLabel("X"); lx.setStyleSheet(_ls)
        ly = QtWidgets.QLabel("Y"); ly.setStyleSheet(_ls)
        trl.addWidget(lx); trl.addWidget(self.sp_ref_tx)
        trl.addWidget(ly); trl.addWidget(self.sp_ref_ty)
        trl.addStretch()
        vl.addWidget(self._row("Translate", tr_w))

        sc_w = QtWidgets.QWidget()
        sc_w.setStyleSheet(f"background:{self.BODY_BG};")
        scl = QtWidgets.QHBoxLayout(sc_w)
        scl.setContentsMargins(0, 0, 0, 0)
        self.sp_ref_scale = self._spinbox(0.01, 10.0, 0.05, 1.0, decimals=2, width=80)
        scl.addWidget(self.sp_ref_scale)
        scl.addStretch()
        vl.addWidget(self._row("Scale", sc_w))

        vl.addWidget(self._divider())

        # ── Single Reference ──────────────────────────────────────────────
        hdr_single = QtWidgets.QWidget()
        hdr_single.setStyleSheet(f"background:{self.BODY_BG};")
        hsl = QtWidgets.QHBoxLayout(hdr_single)
        hsl.setContentsMargins(0, 0, 0, 0)
        hsl.setSpacing(8)
        lbl_s = QtWidgets.QLabel("SINGLE REFERENCE")
        lbl_s.setStyleSheet(self._COL_HDR)
        self.chk_ref_single_dis = self._chk("Enable", checked=True)
        hsl.addWidget(lbl_s)
        hsl.addStretch()
        hsl.addWidget(self.chk_ref_single_dis)
        vl.addWidget(hdr_single)

        def _on_single_ref_change(_, path):
            self._live(live_ref_single, path)

        self.single_ref_card = _RefCard(0, _on_single_ref_change, can_disable=False)
        self.single_ref_card.lbl_num.setText("IMG")
        self.single_ref_card.setMinimumHeight(120)
        self.single_ref_card.setMaximumHeight(160)
        vl.addWidget(self.single_ref_card)

        vl.addWidget(self._divider())

        # ── Contact Sheet — 2×3 card grid ────────────────────────────────
        hdr_cs = QtWidgets.QWidget()
        hdr_cs.setStyleSheet(f"background:{self.BODY_BG};")
        hcl = QtWidgets.QHBoxLayout(hdr_cs)
        hcl.setContentsMargins(0, 0, 0, 0)
        hcl.setSpacing(8)
        lbl_c = QtWidgets.QLabel("CONTACT SHEET  —  6 SLOTS")
        lbl_c.setStyleSheet(self._COL_HDR)
        self.chk_cs_dis = self._chk("Enable", checked=False)
        hcl.addWidget(lbl_c)
        hcl.addStretch()
        hcl.addWidget(self.chk_cs_dis)
        vl.addWidget(hdr_cs)

        hint = QtWidgets.QLabel("Drop images onto slots or click to browse. "
                                "Slots 05–06 have individual enable toggles.")
        hint.setStyleSheet(
            "color:#666;font-size:9px;font-style:italic;background:transparent;")
        hint.setWordWrap(True)
        vl.addWidget(hint)

        # Grid: 2 columns × 3 rows
        grid_w = QtWidgets.QWidget()
        grid_w.setStyleSheet(f"background:{self.BODY_BG};")
        grid = QtWidgets.QGridLayout(grid_w)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(6)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        self.ref_cards: list[_RefCard] = []

        def _on_ref_change(slot: int, path: str):
            self._live(live_ref, slot, path)

        def _on_slot05_disable(disabled: bool):
            self._live(self._set_refs_grp_knob, "disableRef05", disabled)

        def _on_slot06_disable(disabled: bool):
            self._live(self._set_refs_grp_knob, "disableRef06", disabled)

        for i in range(6):
            slot = i + 1
            row_idx, col_idx = divmod(i, 2)
            can_dis  = slot in (5, 6)
            on_dis   = _on_slot05_disable if slot == 5 else (_on_slot06_disable if slot == 6 else None)
            card = _RefCard(slot, _on_ref_change,
                            can_disable=can_dis, on_disable=on_dis)
            # Fixed height preserving ~16:9; width is flexible via grid stretch
            card.setMinimumHeight(96)
            card.setMaximumHeight(120)
            grid.addWidget(card, row_idx, col_idx)
            self.ref_cards.append(card)

        # Keep f_refs as a compatibility shim (used in prefs)
        self.f_refs = self.ref_cards
        # And backward-compat checkboxes expected by prefs code
        self.chk_ref05_dis = self.ref_cards[4].chk_dis   # slot 05
        self.chk_ref06_dis = self.ref_cards[5].chk_dis   # slot 06

        vl.addWidget(grid_w)

        # ── Connections ───────────────────────────────────────────────────
        self.sp_ref_tx.valueChanged.connect(
            lambda _: self._live(live_refs_translate,
                                 self.sp_ref_tx.value(), self.sp_ref_ty.value()))
        self.sp_ref_ty.valueChanged.connect(
            lambda _: self._live(live_refs_translate,
                                 self.sp_ref_tx.value(), self.sp_ref_ty.value()))
        self.sp_ref_scale.valueChanged.connect(
            lambda v: self._live(live_refs_scale, v))
        def _on_single_toggled(v):
            self._live(live_ref_single_disable, not v)
            if v:  # single enabled — disable contact sheet
                self.chk_cs_dis.blockSignals(True)
                self.chk_cs_dis.setChecked(False)
                self.chk_cs_dis.blockSignals(False)
                self._live(live_contact_sheet_disable, True)

        def _on_cs_toggled(v):
            self._live(live_contact_sheet_disable, not v)
            if v:  # contact sheet enabled — disable single
                self.chk_ref_single_dis.blockSignals(True)
                self.chk_ref_single_dis.setChecked(False)
                self.chk_ref_single_dis.blockSignals(False)
                self._live(live_ref_single_disable, True)

        self.chk_ref_single_dis.toggled.connect(_on_single_toggled)
        self.chk_cs_dis.toggled.connect(_on_cs_toggled)
        return w

    # ── HELPERS ───────────────────────────────────────────────────────────

    @staticmethod
    def _set_refs_grp_knob(knob: str, value):
        # v005: REFERENCES_grp gone; disable knobs live on ref_05/ref_06 directly
        slot_map = {"disableRef05": "ref_05", "disableRef06": "ref_06"}
        node_name = slot_map.get(knob)
        if node_name:
            _set_in(_G(), node_name, "disable", value)

    def _live(self, fn, *args):
        if self._block_live:
            return
        try:
            fn(*args)
        except Exception as exc:
            log.warning("live update error in %s: %s",
                        getattr(fn, "__name__", fn), exc)
        self._schedule_node_save()

    # ── READ COMP STATE ───────────────────────────────────────────────────

    def _read_comp_state(self):
        """Read current comp values → initialise UI (called on connection)."""
        self._block_live = True
        try:
            # ── Render folder: derive from first Read node in _MAIN_GRP ──
            try:
                render_file = _get_knob_value_in(_G(), "Read_HDRI_01", "file")
                if render_file:
                    # Path is like: base/RL_hdri_01/name.####.exr — go up two levels
                    base = os.path.dirname(os.path.dirname(
                        render_file.replace("\\", "/")))
                    if base and not self.f_render_folder.text().strip():
                        self.f_render_folder.setText(base)
            except Exception:
                pass

            # ── Asset name from Text_Info node message ─────────────────────
            try:
                text_msg = _get_knob_value_in(_G(), "Text_Info", "message")
                if text_msg and not self.f_asset_name.text().strip():
                    # Parse convention: TYPE_Name_dept_vXXX_usr
                    toks = text_msg.split("_")
                    if len(toks) >= 4:
                        type_tok = toks[0]
                        ver_idx  = next((i for i, t in enumerate(toks)
                                         if re.match(r'^v\d+', t, re.I)), -1)
                        if ver_idx > 0:
                            name = "_".join(toks[1:ver_idx - 1]) if ver_idx > 2 else (toks[1] if ver_idx > 1 else "")
                            dept = toks[ver_idx - 1] if ver_idx > 1 else ""
                            ver  = toks[ver_idx]
                            user = toks[ver_idx + 1] if ver_idx + 1 < len(toks) else ""
                            if type_tok in ASSET_TYPE_CODES:
                                self.combo_asset_type.setCurrentIndex(ASSET_TYPE_CODES.index(type_tok))
                            self.f_asset_name.setText(name)
                            if dept in DEPT_CODES:
                                self.combo_asset_dept.setCurrentIndex(DEPT_CODES.index(dept))
                            self.f_asset_version.setText(ver)
                            self.f_asset_user.setText(user)
                            self._update_naming_preview(type_tok, name, dept, ver, user)
            except Exception:
                pass

            col = _get_color("BG_Color", "color")
            if col:
                self.btn_bg_color._rgb = col
                self._update_color_btn(self.btn_bg_color)

            col = _get_color("Wire_Color", "color")
            if col:
                self.btn_wf_color._rgb = col
                self._update_color_btn(self.btn_wf_color)

            # Comp effects: checked=ON → node must be active → disable=False
            # So: disable=True(bypassed)=OFF → setChecked(not True)=False ← correct
            def _chk_from_disable(node_name, knob_name, chk):
                val = _get_knob_value(node_name, knob_name)
                if val is not None:
                    chk.setChecked(not bool(val))

            _chk_from_disable("Merge_LensDirt",    "disable", self.chk_lens_dirt)
            _chk_from_disable("ZDefocus1",         "disable", self.chk_zdof)
            _chk_from_disable("OCIOFileTransform2","disable", self.chk_lut)

            dirt_mix = _get_knob_value("Merge_LensDirt", "mix")
            if dirt_mix is not None:
                self.sp_lens_dirt_mix.setValue(float(dirt_mix))
                self.sld_lens_dirt.setValue(int(round(float(dirt_mix) * 100)))
            lut_mix = _get_knob_value("OCIOFileTransform2", "mix")
            if lut_mix is not None:
                self.sp_lut_mix.setValue(float(lut_mix))
                self.sld_lut.setValue(int(round(float(lut_mix) * 100)))
            zdof_out = _get_knob_value("ZDefocus1", "output")
            if zdof_out is not None:
                idx = int(zdof_out) if isinstance(zdof_out, (int, float)) else 0
                self.combo_zdof_output.setCurrentIndex(max(0, min(idx, 1)))

            # Tech settings: checked=ON → connection passes v directly to disable
            # So: checkbox=True → disable=True. Read: disable=True → setChecked(True)
            def _chk_tech(node_name, knob_name, chk):
                val = _get_knob_value(node_name, knob_name)
                if val is not None:
                    chk.setChecked(bool(val))

            _chk_tech("Multiply3",    "disable", self.chk_back_ramp)
            _chk_tech("Multiply4",    "disable", self.chk_vignette)
            _chk_tech("DISABLE_OCC1", "disable", self.chk_occlusion)
            _chk_tech("DISABLE_SHD",  "disable", self.chk_shadow)
            _chk_tech("DISABLE_REF",  "disable", self.chk_ref_ball)
            _chk_tech("DISABLE_HDRI_GRP", "disable", self.chk_hdri_prev)
            _chk_tech("DISABLE_ALL_REF",  "disable", self.chk_ref_images)

            # v005: DISABLE_TEXT is flat inside _MAIN_GRP
            val = _get_knob_value_in(_G(), "DISABLE_TEXT", "disable")
            if val is not None:
                self.chk_text_info.setChecked(bool(val))

            mix = _get_knob_value("Merge15", "mix")
            if mix is not None:
                self.sp_vignette_mix.setValue(float(mix))
                self.sld_vignette.setValue(int(round(float(mix) * 100)))

        finally:
            self._block_live = False

    # ── WRITE NODE SECTION ────────────────────────────────────────────────

    def _build_write_node(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        w.setStyleSheet(f"background:{self.BODY_BG};")
        vl = QtWidgets.QVBoxLayout(w)
        vl.setContentsMargins(12, 10, 12, 10)
        vl.setSpacing(8)

        # Output folder
        self.f_write_base = self._path_row(vl, "Output Folder", folder=True)

        # Name field + Auto button
        name_wrap = QtWidgets.QWidget()
        name_wrap.setStyleSheet(f"background:{self.BODY_BG};")
        nwl = QtWidgets.QHBoxLayout(name_wrap)
        nwl.setContentsMargins(0, 0, 0, 0)
        nwl.setSpacing(6)
        self.f_write_name = self._field(placeholder="e.g. Scion_HDRI01_Beauty")
        self.btn_write_name_auto = self._btn("Auto", primary=False)
        self.btn_write_name_auto.setFixedSize(92, 32)   # matches Browse… (paired size)
        nwl.addWidget(self.f_write_name, 1)
        nwl.addWidget(self.btn_write_name_auto)
        vl.addWidget(self._row("Name", name_wrap))

        # Optional version suffix
        ver_wrap = QtWidgets.QWidget()
        ver_wrap.setStyleSheet(f"background:{self.BODY_BG};")
        vwl = QtWidgets.QHBoxLayout(ver_wrap)
        vwl.setContentsMargins(0, 0, 0, 0)
        vwl.setSpacing(6)
        self.chk_write_ver = QtWidgets.QCheckBox("Add version")
        self.chk_write_ver.setStyleSheet(self._CHK)
        self.chk_write_ver.setChecked(False)
        self.f_write_ver = self._field(placeholder="v001")
        self.f_write_ver.setFixedWidth(70)
        self.f_write_ver.setEnabled(False)
        vwl.addWidget(self.chk_write_ver)
        vwl.addWidget(self.f_write_ver)
        vwl.addStretch()
        vl.addWidget(ver_wrap)

        vl.addWidget(self._divider())

        # Format
        fmt_wrap = QtWidgets.QWidget()
        fmt_wrap.setStyleSheet(f"background:{self.BODY_BG};")
        fwl = QtWidgets.QHBoxLayout(fmt_wrap)
        fwl.setContentsMargins(0, 0, 0, 0)
        fwl.setSpacing(6)
        self.combo_write_fmt = QtWidgets.QComboBox()
        self.combo_write_fmt.setStyleSheet(self._FIELD)
        for fmt in ["png", "exr", "tiff"]:
            self.combo_write_fmt.addItem(fmt)
        self.combo_write_fmt.setCurrentText("png")   # default export format
        # TODO (tomorrow): add "mp4" — needs file_type=mov + h264 codec config + testing.
        fwl.addWidget(self.combo_write_fmt)
        fwl.addStretch()
        vl.addWidget(self._row("Format", fmt_wrap))

        # Colorspace
        cs_wrap = QtWidgets.QWidget()
        cs_wrap.setStyleSheet(f"background:{self.BODY_BG};")
        cswl = QtWidgets.QHBoxLayout(cs_wrap)
        cswl.setContentsMargins(0, 0, 0, 0)
        self.combo_write_cs = QtWidgets.QComboBox()
        self.combo_write_cs.setStyleSheet(self._FIELD)
        for cs in ["Output - Rec.709", "Output - sRGB", "ACES - ACEScg",
                   "Utility - Linear - sRGB", "scene_linear"]:
            self.combo_write_cs.addItem(cs)
        cswl.addWidget(self.combo_write_cs)
        cswl.addStretch()
        vl.addWidget(self._row("Colorspace", cs_wrap))

        vl.addWidget(self._divider())

        # Path preview
        self.lbl_write_preview = QtWidgets.QLabel("—")
        self.lbl_write_preview.setStyleSheet(
            "color:#888;font-size:10px;font-style:italic;"
            "background:transparent;padding:2px 0;")
        self.lbl_write_preview.setWordWrap(True)
        vl.addWidget(self.lbl_write_preview)

        self.lbl_write_status = self._stat()
        vl.addWidget(self.lbl_write_status)

        # CREATE + APPLY buttons
        btn_row = QtWidgets.QWidget()
        btn_row.setStyleSheet(f"background:{self.BODY_BG};")
        brl = QtWidgets.QHBoxLayout(btn_row)
        brl.setContentsMargins(0, 0, 0, 0)
        brl.setSpacing(8)
        btn_create = self._btn("Create Write Node", primary=False)
        btn_create.setStyleSheet(self._STEP_BTN["active"])   # prominent action, shared style
        btn_create.setMinimumHeight(34)
        btn_apply  = self._btn("Apply to Selected", primary=False)   # secondary (_BTN2)
        brl.addWidget(btn_create, 1)
        brl.addWidget(btn_apply,  1)
        vl.addWidget(btn_row)

        # Final step instruction (the Write node has create-directories enabled, so
        # the output folder is made automatically on render).
        write_hint = QtWidgets.QLabel("Now double-click the Write node and click Render.")
        write_hint.setStyleSheet(
            "color:#E8B84B;font-size:11px;background:transparent;padding:4px 0;")
        write_hint.setWordWrap(True)
        vl.addWidget(write_hint)

        # Connections
        self.f_write_base.editingFinished.connect(self._on_write_changed)
        self.f_write_name.editingFinished.connect(self._on_write_changed)
        self.combo_write_fmt.currentIndexChanged.connect(lambda _: self._on_write_changed())
        self.combo_write_cs.currentIndexChanged.connect(lambda _: self._on_write_changed())
        self.chk_write_ver.toggled.connect(self.f_write_ver.setEnabled)
        self.chk_write_ver.toggled.connect(lambda _: self._on_write_changed())
        self.f_write_ver.editingFinished.connect(self._on_write_changed)
        self.btn_write_name_auto.clicked.connect(self._auto_write_name)
        btn_create.clicked.connect(self._do_create_write_node)
        btn_apply.clicked.connect(self._do_apply_write_node)

        # Seed the name from current asset state
        QtCore.QTimer.singleShot(0, self._auto_write_name)
        return w

    def _write_resolved_path(self) -> str:
        base = self.f_write_base.text().strip() if hasattr(self, "f_write_base") else ""
        name = self.f_write_name.text().strip() if hasattr(self, "f_write_name") else "TT_output"
        if not name:
            name = "TT_output"
        ver_suffix = ""
        if hasattr(self, "chk_write_ver") and self.chk_write_ver.isChecked():
            ver = self.f_write_ver.text().strip() if hasattr(self, "f_write_ver") else ""
            if ver:
                ver_suffix = f"_{ver}"
        fmt = self.combo_write_fmt.currentText() if hasattr(self, "combo_write_fmt") else "exr"
        filename = f"{name}{ver_suffix}.####.{fmt}"
        if base:
            return f"{base.rstrip('/').rstrip(chr(92))}/{filename}"
        return filename

    def _on_write_changed(self):
        if hasattr(self, "lbl_write_preview"):
            self.lbl_write_preview.setText(f"->  {self._write_resolved_path()}")
        self._schedule_node_save()

    def _auto_write_name(self):
        """Auto-generate output name: full_asset_name_TT_HDRIXX_Mode."""
        if not hasattr(self, "f_write_name"):
            return
        # Assemble full asset name (mirrors the comp Text_Info string)
        parts = [p for p in [
            self._combo_code(self.combo_asset_type),
            self.f_asset_name.text().strip(),
            self._combo_code(self.combo_asset_dept),
            self.f_asset_version.text().strip(),
            self.f_asset_user.text().strip(),
        ] if p]
        full_asset = "_".join(parts) if parts else "TT"
        hdri_n = self.combo_hdri.currentIndex() + 1
        mode   = RENDER_OPTIONS[max(0, min(self.combo_render.currentIndex(),
                                          len(RENDER_OPTIONS) - 1))]
        self.f_write_name.setText(f"{full_asset}_TT_HDRI{hdri_n:02d}_{mode}")
        self._on_write_changed()

    def _on_export_toggled(self, checked: bool):
        if checked:
            for btn in self._all_sec_btns:
                btn.setChecked(False)

    def _apply_write_settings(self, node, path: str, fmt: str, cs: str):
        node["file"].setValue(path)
        node["file_type"].setValue(fmt)
        try:
            node["colorspace"].setValue(cs)
        except Exception:
            pass
        # Enable "create directories" so render makes the output folder automatically
        # (knob name differs across Nuke versions — set whichever exists).
        for _kn in ("create_directories", "create_dir"):
            try:
                node[_kn].setValue(True)
                break
            except Exception:
                continue
        if hasattr(self, "lbl_write_preview"):
            self.lbl_write_preview.setText(f"->  {path}")

    def _do_create_write_node(self):
        path = self._write_resolved_path()
        fmt  = self.combo_write_fmt.currentText()
        cs   = self.combo_write_cs.currentText()

        # Find a unique root-level name
        node_name = "Write_TT"
        n = 1
        while nuke.toNode(node_name) is not None:
            n += 1
            node_name = f"Write_TT_{n}"

        w = nuke.nodes.Write(name=node_name)
        grp = nuke.toNode(_G())
        if grp:
            w.setInput(0, grp)

        self._apply_write_settings(w, path, fmt, cs)
        self._set_status(self.lbl_write_status,
                         f"'{node_name}' created — {fmt.upper()}, {cs}.", "ok")

    def _do_apply_write_node(self):
        path = self._write_resolved_path()
        fmt  = self.combo_write_fmt.currentText()
        cs   = self.combo_write_cs.currentText()

        # Prefer a Write node selected in the Nuke graph
        w = None
        try:
            for n in nuke.selectedNodes():
                if n.Class() == "Write":
                    w = n
                    break
        except Exception:
            pass

        if w is None:
            w = nuke.toNode("Write_TT")

        if w is None:
            self._set_status(self.lbl_write_status,
                             "Select a Write node in Nuke first, or use Create.", "err")
            return

        self._apply_write_settings(w, path, fmt, cs)
        self._set_status(self.lbl_write_status,
                         f"Applied to '{w.name()}' — {fmt.upper()}, {cs}.", "ok")

    # ── SLOTS ─────────────────────────────────────────────────────────────

    def _on_folder_changed(self):
        folder = self.f_render_folder.text().strip()
        if not folder:
            return
        self._set_status(self.lbl_scan_status, "Scanning…", "idle")
        QtWidgets.QApplication.processEvents()

        data = scan_render_folder(folder)
        self._scan_data = data
        self._update_hdri_combo(data["hdri"])
        fh, fc = data["found_hdri"], data["found_charts"]

        if fh == 0 and fc == 0:
            self._set_status(self.lbl_scan_status,
                             "No render layers found — check folder structure.", "err")
        else:
            parts = []
            if fh: parts.append(f"HDRI: {fh}/8")
            if fc: parts.append(f"Charts: {fc}/8")
            warn = ""
            if fh < 8 or fc < 8:
                warn = f"  ({8-fh} HDRI + {8-fc} charts slots empty)"
            self._set_status(self.lbl_scan_status,
                             "Scan complete — " + ",  ".join(parts) + warn,
                             "ok" if (fh == 8 and fc == 8) else "warn")

        if not self._block_live:
            live_render_paths_from_scan(data["hdri"])
            live_charts_paths_from_scan(data["charts"])

        if data["asset_name"] and not self.f_asset_name.text().strip():
            self.f_asset_name.setText(data["asset_name"])
        if data.get("type_code") and not self.combo_asset_type.currentIndex():
            tc = data["type_code"]
            if tc in ASSET_TYPE_CODES:
                self.combo_asset_type.setCurrentIndex(ASSET_TYPE_CODES.index(tc))
        if data.get("dept_code") and not self.combo_asset_dept.currentIndex():
            dc = data["dept_code"]
            if dc in DEPT_CODES:
                self.combo_asset_dept.setCurrentIndex(DEPT_CODES.index(dc))
        if data["version"] and not self.f_asset_version.text().strip():
            self.f_asset_version.setText(data["version"])
            self._auto_write_name()

    def _do_autofill(self):
        import nuke as _nuke
        import os
        folder = self.f_render_folder.text().strip()
        if not folder:
            _nuke.message("Auto-fill: Set a Render Location first.")
            return

        info        = {}
        parsed_from = ""

        # Strategy 1: walk path segments deepest-first
        # Works when the render folder IS the asset folder: .../CHR_IO_rig_v001_csp
        for seg in reversed(folder.replace("\\", "/").rstrip("/").split("/")):
            if not seg:
                continue
            parsed = _parse_asset_info(seg)
            if parsed.get("version"):
                info        = parsed
                parsed_from = seg
                break

        # Strategy 2: scan RL_* subfolders and read the filename inside
        # Works when folder is the render output root:
        #   images/RL_hdri_01/CHR_IO_rig_v001_csp_RL_hdri_01.1001.exr
        if not info and os.path.isdir(folder):
            try:
                for entry in sorted(os.listdir(folder)):
                    full = os.path.join(folder, entry)
                    if not os.path.isdir(full):
                        continue
                    # Subfolder named RL_* — look at a file inside it
                    if entry.upper().startswith("RL_") or "_RL_" in entry:
                        try:
                            files = sorted(f for f in os.listdir(full)
                                           if not f.startswith("."))
                        except OSError:
                            continue
                        for fname in files:
                            # Strip frame number and extension: foo.1001.exr → foo
                            base = fname.split(".")[0]
                            parsed = _parse_asset_info(base)
                            if parsed.get("version"):
                                info        = parsed
                                parsed_from = base
                                break
                    if info:
                        break
            except OSError:
                pass

        if not info:
            _nuke.message(
                "Auto-fill: Cannot parse asset from path.\n\n"
                f"{folder}\n\n"
                "Point to either:\n"
                "  The asset folder:  CHR_IO_rig_v001_csp\n"
                "  Or the parent folder containing RL_hdri_XX subfolders")
            return

        type_code = info.get("type_code",  "")
        name      = info.get("asset_name", "")
        dept_code = info.get("dept_code",  "")
        ver       = info.get("version",    "")
        user_id   = info.get("user_id",    "")

        # Populate UI fields
        if type_code in ASSET_TYPE_CODES:
            self.combo_asset_type.setCurrentIndex(ASSET_TYPE_CODES.index(type_code))
        self.f_asset_name.setText(name)
        if dept_code in DEPT_CODES:
            self.combo_asset_dept.setCurrentIndex(DEPT_CODES.index(dept_code))
        self.f_asset_version.setText(ver)
        if user_id:
            self.f_asset_user.setText(user_id)

        user = user_id or self.f_asset_user.text().strip()
        self._update_naming_preview(type_code, name, dept_code, ver, user)

        # Push to comp Text_Info node with HTML colors
        if self._template_loaded:
            live_asset_text(type_code, name, dept_code, ver, user)

        # Refresh auto write name from current asset state
        self._auto_write_name()

        # Scan RL subfolders for sequence paths only
        data = scan_render_folder(folder)
        self._scan_data = data
        self._update_hdri_combo(data["hdri"])
        if not self._block_live:
            live_render_paths_from_scan(data["hdri"])
            live_charts_paths_from_scan(data["charts"])

        parts = [p for p in [type_code, name, dept_code, ver, user] if p]
        self._set_status(self.lbl_scan_status,
                         f"Filled: {'_'.join(parts)}  (from: {parsed_from})", "ok")

        QtCore.QTimer.singleShot(300, self._cs_collapse_asset)
        self._save_node_state()
        self._check_step3_complete()

    def _update_hdri_combo(self, hdri_results):
        """Color-code HDRI combo items based on scan availability."""
        model = self.combo_hdri.model()
        for i in range(self.combo_hdri.count()):
            n     = i + 1
            found = any(slot_n == n and fp for slot_n, fp, _ in hdri_results)
            item  = model.item(i)
            if item is None:
                continue
            base_label = HDRI_OPTIONS[i]
            if found:
                item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                item.setText(base_label)
                item.setForeground(QtGui.QBrush(QtGui.QColor("#d4d4d4")))
                item.setBackground(QtGui.QBrush(QtGui.QColor("#1e1e1e")))
            else:
                item.setFlags(QtCore.Qt.NoItemFlags)
                item.setText(f"{base_label}  —  not available")
                item.setForeground(QtGui.QBrush(QtGui.QColor("#8b3a3a")))
                item.setBackground(QtGui.QBrush(QtGui.QColor("#1a1212")))
        # If selected slot is now unavailable, jump to first available
        cur      = self.combo_hdri.currentIndex()
        cur_item = model.item(cur)
        if cur_item and not (cur_item.flags() & QtCore.Qt.ItemIsEnabled):
            for i in range(self.combo_hdri.count()):
                it = model.item(i)
                if it and (it.flags() & QtCore.Qt.ItemIsEnabled):
                    self.combo_hdri.setCurrentIndex(i)
                    break

    def _on_hdri_or_render_changed(self):
        if self._block_live:
            return
        hi = self.combo_hdri.currentIndex()
        ri = self.combo_render.currentIndex()
        live_hdri_select(hi)
        live_render_type(ri)
        self._auto_write_name()

    def _on_version_changed(self):
        ver = self.f_asset_version.text().strip()
        live_asset_version(ver)
        self._auto_write_name()

    def _do_open_template(self):
        self._set_status(self.lbl_conn, "Importing comp template…", "idle")
        QtWidgets.QApplication.processEvents()

        # Resolve the template path from the Working Folder field so the tool
        # works on any drive without code edits.
        proj_dir = self.f_proj_dir.text().strip().replace("\\", "/").rstrip("/")
        if not proj_dir:
            self._set_status(self.lbl_conn,
                "Set the Working Folder before importing the template.", "err")
            return
        path = "{}/{}".format(proj_dir, COMP_TEMPLATE_FILENAME)
        if not os.path.isfile(path):
            self._set_status(self.lbl_conn, f"Template not found:  {path}", "err")
            return
        try:
            # Paste template nodes into the current Nuke session.
            # Do NOT use scriptNew() or scriptOpen() — both clear the session.
            # nodePaste() reads the .nk file and inserts all its nodes into the
            # current script without touching session-level state.
            nuke.nodePaste(path)
            # Fix all relative paths that depend on proj_dir.
            try:
                if proj_dir:
                    nuke.root()["project_directory"].setValue(proj_dir)

                    # Fix HDRI preview Read nodes (flat inside _MAIN_GRP in v005)
                    _HDRI_PRW_FILES = [
                        ("Read_HDRI_PRW_01", "01 - Studio.jpg"),
                        ("Read_HDRI_PRW_02", "02 - Day Overcast.jpg"),
                        ("Read_HDRI_PRW_03", "03 - Direct Sun.jpg"),
                        ("Read_HDRI_PRW_04", "04 - Cloudy Sun.jpg"),
                        ("Read_HDRI_PRW_05", "05 - Night.jpg"),
                        ("Read_HDRI_PRW_06", "06 - Night Neon.jpg"),
                    ]
                    prw_base = proj_dir + "/HDRI_previews"
                    for node_name, fname in _HDRI_PRW_FILES:
                        _set_in(_G(), node_name, "file",
                                f"{prw_base}/{fname}")

                    # Fix Dirt texture Read nodes (top-level)
                    dirt_base = proj_dir + "/Dirt"
                    _set("Read13", "file", f"{dirt_base}/Scratches_Mixed.jpg")
                    _set("Read14", "file",
                         f"{dirt_base}/Small Scratches And Dirt.png")
            except Exception as exc:
                log.warning("Could not fix template paths: %s", exc)
            self._template_loaded = True
            # v005: connect viewer to TB3DTT group node (END_COMP is inside the group)
            grp_node = nuke.toNode(_G())
            if grp_node:
                nuke.connectViewer(0, grp_node)
            self._push_defaults_to_comp()
            self._refresh_connection_status()
        except Exception as exc:
            self._set_status(self.lbl_conn, f"Could not import template: {exc}", "err")

    def _push_defaults_to_comp(self):
        """Reset comp to default state after a fresh template import.
        UI widgets are set to defaults first, then all values are pushed live.
        HDRI defaults to '01 - Studio'; falls back to index 0 if not in list.
        """
        hdri_idx = (HDRI_OPTIONS.index("01 - Studio")
                    if "01 - Studio" in HDRI_OPTIONS else 0)

        self._block_live = True
        try:
            self.combo_hdri.setCurrentIndex(hdri_idx)
            self.combo_render.setCurrentIndex(0)
            self.combo_back.setCurrentIndex(0)
            self.chk_compfx.setChecked(False)
            self.chk_lens_dirt.setChecked(True)
            self.sp_lens_dirt_mix.setValue(0.35)
            self.sld_lens_dirt.setValue(35)
            self.chk_lut.setChecked(False)
            self.sp_lut_mix.setValue(0.35)
            self.sld_lut.setValue(35)
            self.chk_zdof.setChecked(False)
            self.combo_zdof_output.setCurrentIndex(0)
            self.chk_vignette.setChecked(True)
            self.sp_vignette_mix.setValue(0.25)
            self.sld_vignette.setValue(25)
            self.chk_shadow.setChecked(True)
            self.chk_back_ramp.setChecked(True)
            self.chk_occlusion.setChecked(False)
            self.chk_text_info.setChecked(True)
            self.chk_ref_ball.setChecked(True)
            self.chk_hdri_prev.setChecked(True)
            self.chk_ref_images.setChecked(True)
        finally:
            self._block_live = False

        # Push to comp — note disable semantics:
        # tech checkboxes: checked=True → live_xxx_disable(True) → bypass disable-switch → ON
        # lens dirt / lut / zdof use "not v" in their toggled connections, so pass directly
        live_hdri_select(hdri_idx)
        live_render_type(0)
        live_back_select(0)
        live_compfx(False)
        live_lens_dirt_disable(False)   # chk=True → not True → False → node active
        live_lens_dirt_mix(0.35)
        live_lut_disable(True)          # chk=False → not False → True → LUT node bypassed
        live_lut_mix(0.35)
        live_zdof_disable(True)         # chk=False → not False → True → zdof disabled
        live_vignette_disable(True)     # chk=True → bypass disable switch → vignette ON
        live_vignette_intensity(1.0)
        live_shadow_disable(True)
        live_back_ramp_disable(True)
        live_occlusion_disable(False)
        live_text_info_disable(True)
        live_ref_ball_disable(True)
        live_hdri_preview_disable(True)
        live_ref_images_disable(True)

    def _push_ui_to_comp(self):
        """Push every current UI control value to the comp. Called after reconnect
        so the restored panel state is fully reflected in the live comp nodes."""
        if not self._template_loaded:
            return
        try:
            live_hdri_select(self.combo_hdri.currentIndex())
            live_render_type(self.combo_render.currentIndex())
            live_back_select(self.combo_back.currentIndex())
            live_compfx(self.chk_compfx.isChecked())

            ld_en = self.chk_lens_dirt.isChecked()
            live_lens_dirt_disable(not ld_en)
            live_lens_dirt_mix(self.sp_lens_dirt_mix.value())

            lut_en = self.chk_lut.isChecked()
            live_lut_disable(not lut_en)
            live_lut_mix(self.sp_lut_mix.value())
            live_lut_path(self.f_lut_path.text().strip())

            zdof_en = self.chk_zdof.isChecked()
            live_zdof_disable(not zdof_en)
            live_zdof_center(self.sp_zdof_center.value())
            live_zdof_dof(self.sp_zdof_dof.value())
            live_zdof_size(self.sp_zdof_size.value())
            live_zdof_output(self.combo_zdof_output.currentIndex())

            live_vignette_disable(self.chk_vignette.isChecked())
            live_vignette_intensity(self.sp_vignette_mix.value())
            live_shadow_disable(self.chk_shadow.isChecked())
            live_back_ramp_disable(self.chk_back_ramp.isChecked())
            live_occlusion_disable(self.chk_occlusion.isChecked())
            live_text_info_disable(self.chk_text_info.isChecked())
            live_ref_ball_disable(self.chk_ref_ball.isChecked())
            live_hdri_preview_disable(self.chk_hdri_prev.isChecked())
            live_ref_images_disable(self.chk_ref_images.isChecked())

            r, g, b = self.btn_bg_color._rgb
            live_bg_color(r, g, b)
            r, g, b = self.btn_wf_color._rgb
            live_wireframe_color(r, g, b)

            live_font_scale(self.sp_font_scale.value())

            t = self._combo_code(self.combo_asset_type)
            n = self.f_asset_name.text().strip()
            d = self._combo_code(self.combo_asset_dept)
            v = self.f_asset_version.text().strip()
            u = self.f_asset_user.text().strip()
            if any([t, n, d, v]):
                live_asset_text(t, n, d, v, u)
                live_asset_version(v)

            live_refs_translate(self.sp_ref_tx.value(), self.sp_ref_ty.value())
            live_refs_scale(self.sp_ref_scale.value())
        except Exception as exc:
            log.warning("_push_ui_to_comp: %s", exc)

    def _read_write_node_state(self):
        """If export fields are empty, populate them from the first Write_TT node found at root."""
        if not hasattr(self, "f_write_base"):
            return
        if self.f_write_base.text().strip() and self.f_write_name.text().strip():
            return  # already populated from saved state

        # Find Write_TT or Write_TT_N at root level
        write_node = None
        for n in nuke.allNodes("Write"):
            if n.name() == "Write_TT" or n.name().startswith("Write_TT_"):
                write_node = n
                break
        if write_node is None:
            return

        try:
            path = write_node["file"].getValue()
            if not path:
                return
            path = path.replace("\\", "/")

            # Split into folder + filename (filename is last component)
            last_slash = path.rfind("/")
            if last_slash >= 0:
                base = path[:last_slash]
                filename = path[last_slash + 1:]
            else:
                base = ""
                filename = path

            # Strip frame token and extension: name.####.exr → name, exr
            parts = filename.rsplit(".", 2)
            name = parts[0] if parts else filename
            fmt  = parts[-1] if len(parts) >= 2 else "exr"

            self.f_write_base.setText(base)
            self.f_write_name.setText(name)

            # Restore format combo
            for i in range(self.combo_write_fmt.count()):
                if self.combo_write_fmt.itemText(i).lower() == fmt.lower():
                    self.combo_write_fmt.setCurrentIndex(i)
                    break

            self._on_write_changed()
        except Exception as exc:
            log.warning("_read_write_node_state: %s", exc)

    def _do_apply_project_settings(self):
        start = self.sp_frame_start.value()
        end   = self.sp_frame_end.value()
        fps_str  = self.combo_fps.currentText()
        fmt_name = self.combo_project_fmt.currentData()

        errors = []

        # Frame range
        try:
            live_frame_range(start, end)
        except Exception as exc:
            errors.append(f"frame range: {exc}")

        # FPS
        try:
            nuke.root()["fps"].setValue(float(fps_str))
        except Exception as exc:
            errors.append(f"fps: {exc}")

        # Format
        try:
            applied = False
            for f in nuke.formats():
                if f.name() == fmt_name:
                    nuke.root()["format"].setValue(f)
                    applied = True
                    break
            if not applied:
                errors.append(f"format '{fmt_name}' not found")
        except Exception as exc:
            errors.append(f"format: {exc}")

        if errors:
            self._set_status(self.lbl_scan_status,
                             "Partial apply — " + "; ".join(errors), "warn")
        else:
            fmt_label = self.combo_project_fmt.currentText().split("\u2014")[-1].strip()
            self._set_status(self.lbl_scan_status,
                             f"Applied: {fmt_label} | {fps_str} fps | frames {start}\u2013{end}", "ok")
    def _do_reconnect(self):
        # If a group node is selected in Nuke, rebind to it
        try:
            sel = nuke.selectedNodes()
            for n in sel:
                if n.Class() == "Group":
                    set_active_group(n.name())
                    break
        except Exception:
            pass
        self._refresh_connection_status(force=True)
        if self._template_loaded:
            # Restore full panel state from the node's JSON knob (if present),
            # then push the restored UI state back to the comp.
            self._restore_node_state()
            self._read_write_node_state()
            self._push_ui_to_comp()
            grp_node = nuke.toNode(_G())
            if grp_node:
                nuke.connectViewer(0, grp_node)

    def _refresh_connection_status(self, force=False):
        if not self._template_loaded and not force:
            return
        connected, missing = check_comp_connected()
        if connected:
            self._template_loaded = True
            self._set_status(self.lbl_conn,
                             f"All comp nodes found in {_G()} — live mode active.", "ok")
            self._read_comp_state()
        else:
            short = ", ".join(missing[:4])
            if len(missing) > 4:
                short += f" … (+{len(missing) - 4} more)"
            self._set_status(self.lbl_conn,
                             f"Missing nodes: {short}  |  Import the comp template first.", "err")
        self._update_node_indicator()

    # ── PREFS ─────────────────────────────────────────────────────────────

    def _collect_prefs(self) -> dict:
        return {
            "render_folder":   self.f_render_folder.text().strip(),
            "frame_start":     self.sp_frame_start.value(),
            "frame_end":       self.sp_frame_end.value(),
            "project_format":  self.combo_project_fmt.currentData() or "",
            "project_fps":     self.combo_fps.currentText(),
            "asset_type":    self.combo_asset_type.currentIndex(),
            "asset_name":    self.f_asset_name.text().strip(),
            "asset_dept":    self.combo_asset_dept.currentIndex(),
            "asset_version": self.f_asset_version.text().strip(),
            "asset_user":    self.f_asset_user.text().strip(),
            "font_scale":    self.sp_font_scale.value(),
            "hdri_index":    self.combo_hdri.currentIndex(),
            "render_index":  self.combo_render.currentIndex(),
            "back_index":    self.combo_back.currentIndex(),
            "bg_color":      list(self.btn_bg_color._rgb),
            "wf_color":      list(self.btn_wf_color._rgb),
            "compfx":        self.chk_compfx.isChecked(),
            "lut_path":          self.f_lut_path.text().strip(),
            "lut_en":            self.chk_lut.isChecked(),
            "lut_mix":           self.sp_lut_mix.value(),
            "zdof_en":           self.chk_zdof.isChecked(),
            "zdof_center":       self.sp_zdof_center.value(),
            "zdof_dof":          self.sp_zdof_dof.value(),
            "zdof_size":         self.sp_zdof_size.value(),
            "zdof_output":       self.combo_zdof_output.currentIndex(),
            "lens_dirt_en":      self.chk_lens_dirt.isChecked(),
            "lens_dirt_mix":     self.sp_lens_dirt_mix.value(),
            "back_ramp_en":  self.chk_back_ramp.isChecked(),
            "vignette_en":   self.chk_vignette.isChecked(),
            "vignette_mix":  self.sp_vignette_mix.value(),
            "occlusion_en":  self.chk_occlusion.isChecked(),
            "shadow_en":     self.chk_shadow.isChecked(),
            "text_info_en":  self.chk_text_info.isChecked(),
            "ref_ball_en":   self.chk_ref_ball.isChecked(),
            "hdri_prev_en":  self.chk_hdri_prev.isChecked(),
            "ref_images_en": self.chk_ref_images.isChecked(),
            "ref_tx":        self.sp_ref_tx.value(),
            "ref_ty":        self.sp_ref_ty.value(),
            "ref_scale":     self.sp_ref_scale.value(),
            "ref_single":    self.single_ref_card.path(),
            "ref_single_dis":self.chk_ref_single_dis.isChecked(),
            "cs_dis":        self.chk_cs_dis.isChecked(),
            "refs":          [c.path() for c in self.ref_cards],
            "ref05_dis":     self.ref_cards[4]._disabled,
            "ref06_dis":     self.ref_cards[5]._disabled,
            "write_base":    self.f_write_base.text().strip(),
            "write_name":    self.f_write_name.text().strip(),
            "write_ver_en":  self.chk_write_ver.isChecked(),
            "write_ver":     self.f_write_ver.text().strip(),
            "write_fmt":     self.combo_write_fmt.currentIndex(),
            "write_cs":      self.combo_write_cs.currentIndex(),
        }

    def _restore_prefs(self):
        p = self._prefs
        if not p:
            return

        def _sl(edit, key):
            if p.get(key):
                edit.setText(p[key])
        def _sc(combo, key):
            v = p.get(key)
            if isinstance(v, int) and 0 <= v < combo.count():
                combo.setCurrentIndex(v)
        def _sb(chk, key, default=True):
            chk.setChecked(bool(p.get(key, default)))
        def _sv(sb, key):
            v = p.get(key)
            if v is not None:
                try:
                    sb.setValue(float(v))
                except (TypeError, ValueError):
                    pass
        def _si(sb, key):
            v = p.get(key)
            if v is not None:
                try:
                    sb.setValue(int(v))
                except (TypeError, ValueError):
                    pass

        # render_folder and asset fields are NOT restored from prefs —
        # they are populated by Check Connection from the live comp state.
        _si(self.sp_frame_start,  "frame_start")
        _si(self.sp_frame_end,    "frame_end")

        # Restore project format by stored name (index may shift if format list changes)
        saved_fmt = p.get("project_format", "")
        if saved_fmt:
            for i in range(self.combo_project_fmt.count()):
                if self.combo_project_fmt.itemData(i) == saved_fmt:
                    self.combo_project_fmt.setCurrentIndex(i)
                    break
        # Restore FPS
        saved_fps = p.get("project_fps", FPS_DEFAULT)
        fps_idx = FPS_OPTIONS.index(saved_fps) if saved_fps in FPS_OPTIONS else FPS_OPTIONS.index(FPS_DEFAULT)
        self.combo_fps.setCurrentIndex(fps_idx)
        _sv(self.sp_font_scale,   "font_scale")
        _sc(self.combo_hdri,      "hdri_index")
        _sc(self.combo_render,    "render_index")
        _sc(self.combo_back,      "back_index")

        bg = p.get("bg_color")
        if isinstance(bg, (list, tuple)) and len(bg) == 3:
            self.btn_bg_color._rgb = tuple(bg)
            self._update_color_btn(self.btn_bg_color)
        wf = p.get("wf_color")
        if isinstance(wf, (list, tuple)) and len(wf) == 3:
            self.btn_wf_color._rgb = tuple(wf)
            self._update_color_btn(self.btn_wf_color)

        _sb(self.chk_compfx,       "compfx",       False)
        _sl(self.f_lut_path,        "lut_path")
        _sb(self.chk_lut,           "lut_en",        False)
        _sv(self.sp_lut_mix,        "lut_mix")
        self.sld_lut.setValue(int(round(self.sp_lut_mix.value() * 100)))
        _sb(self.chk_zdof,          "zdof_en",       False)
        _sv(self.sp_zdof_center,    "zdof_center")
        _sv(self.sp_zdof_dof,       "zdof_dof")
        _sv(self.sp_zdof_size,      "zdof_size")
        _sc(self.combo_zdof_output, "zdof_output")
        _sb(self.chk_lens_dirt,     "lens_dirt_en",  True)
        _sv(self.sp_lens_dirt_mix,  "lens_dirt_mix")
        self.sld_lens_dirt.setValue(int(round(self.sp_lens_dirt_mix.value() * 100)))
        _sb(self.chk_back_ramp,    "back_ramp_en",  True)
        _sb(self.chk_vignette,     "vignette_en",   True)
        _sv(self.sp_vignette_mix,  "vignette_mix")
        self.sld_vignette.setValue(int(round(self.sp_vignette_mix.value() * 100)))
        _sb(self.chk_occlusion,    "occlusion_en",  False)
        _sb(self.chk_shadow,       "shadow_en",     True)
        _sb(self.chk_text_info,    "text_info_en",  True)
        _sb(self.chk_ref_ball,     "ref_ball_en",   True)
        _sb(self.chk_hdri_prev,    "hdri_prev_en",  True)
        _sb(self.chk_ref_images,   "ref_images_en", True)
        _sv(self.sp_ref_tx,        "ref_tx")
        _sv(self.sp_ref_ty,        "ref_ty")
        _sv(self.sp_ref_scale,     "ref_scale")
        if p.get("ref_single"):
            self.single_ref_card.set_path(p["ref_single"])
        _sb(self.chk_ref_single_dis,"ref_single_dis", True)
        _sb(self.chk_cs_dis,       "cs_dis",        False)
        refs = p.get("refs", [])
        for i, card in enumerate(self.ref_cards):
            if i < len(refs) and refs[i]:
                card.set_path(refs[i])
        # ref05/06 disable state is embedded in the cards' chk_dis toggles
        ref05_dis = p.get("ref05_dis", False)
        ref06_dis = p.get("ref06_dis", False)
        self.ref_cards[4].set_disabled_state(ref05_dis)
        self.ref_cards[5].set_disabled_state(ref06_dis)
        _sl(self.f_write_base,     "write_base")
        _sl(self.f_write_name,     "write_name")
        _sb(self.chk_write_ver,    "write_ver_en", False)
        _sl(self.f_write_ver,      "write_ver")
        _sc(self.combo_write_fmt,  "write_fmt")
        _sc(self.combo_write_cs,   "write_cs")
        self._on_write_changed()

        if p.get("render_folder"):
            self._on_folder_changed()

    # ── NODE STATE (per-instance, stored on the TB3DTT group knob) ────────────

    def _save_node_state(self):
        if not self._template_loaded:
            return
        try:
            _node_write_state(self._collect_prefs())
        except Exception as exc:
            log.warning("_save_node_state: %s", exc)

    def _schedule_node_save(self):
        """Debounced: write state to the node knob 2 s after the last control change."""
        if not self._template_loaded:
            return
        if not hasattr(self, "_node_save_timer"):
            self._node_save_timer = QtCore.QTimer()
            self._node_save_timer.setSingleShot(True)
            self._node_save_timer.timeout.connect(self._save_node_state)
        self._node_save_timer.start(2000)

    def _restore_node_state(self):
        """Restore full panel state from the active TB3DTT group node knob."""
        state = _node_read_state()
        if not state:
            return
        self._block_live = True
        try:
            p = state

            def _sl(edit, key):
                v = p.get(key)
                if v:
                    edit.setText(str(v))

            def _sc(combo, key):
                v = p.get(key)
                if isinstance(v, int) and 0 <= v < combo.count():
                    combo.setCurrentIndex(v)

            def _sb(chk, key, default=True):
                chk.setChecked(bool(p.get(key, default)))

            def _sv(sb, key):
                v = p.get(key)
                if v is not None:
                    try:
                        sb.setValue(float(v))
                    except (TypeError, ValueError):
                        pass

            def _si(sb, key):
                v = p.get(key)
                if v is not None:
                    try:
                        sb.setValue(int(v))
                    except (TypeError, ValueError):
                        pass

            # Comp setup
            _sl(self.f_render_folder, "render_folder")
            _si(self.sp_frame_start,  "frame_start")
            _si(self.sp_frame_end,    "frame_end")
            saved_fmt = p.get("project_format", "")
            if saved_fmt:
                for i in range(self.combo_project_fmt.count()):
                    if self.combo_project_fmt.itemData(i) == saved_fmt:
                        self.combo_project_fmt.setCurrentIndex(i)
                        break
            saved_fps = p.get("project_fps", FPS_DEFAULT)
            if saved_fps in FPS_OPTIONS:
                self.combo_fps.setCurrentIndex(FPS_OPTIONS.index(saved_fps))

            # Asset info
            _sc(self.combo_asset_type, "asset_type")
            _sl(self.f_asset_name,     "asset_name")
            _sc(self.combo_asset_dept, "asset_dept")
            _sl(self.f_asset_version,  "asset_version")
            _sl(self.f_asset_user,     "asset_user")
            _sv(self.sp_font_scale,    "font_scale")

            # Visual options
            _sc(self.combo_hdri,   "hdri_index")
            _sc(self.combo_render, "render_index")
            _sc(self.combo_back,   "back_index")
            bg = p.get("bg_color")
            if isinstance(bg, (list, tuple)) and len(bg) == 3:
                self.btn_bg_color._rgb = tuple(bg)
                self._update_color_btn(self.btn_bg_color)
            wf = p.get("wf_color")
            if isinstance(wf, (list, tuple)) and len(wf) == 3:
                self.btn_wf_color._rgb = tuple(wf)
                self._update_color_btn(self.btn_wf_color)

            # Comp effects
            _sb(self.chk_compfx,        "compfx",       False)
            _sl(self.f_lut_path,        "lut_path")
            _sb(self.chk_lut,           "lut_en",        False)
            _sv(self.sp_lut_mix,        "lut_mix")
            self.sld_lut.setValue(int(round(self.sp_lut_mix.value() * 100)))
            _sb(self.chk_zdof,          "zdof_en",       False)
            _sv(self.sp_zdof_center,    "zdof_center")
            _sv(self.sp_zdof_dof,       "zdof_dof")
            _sv(self.sp_zdof_size,      "zdof_size")
            _sc(self.combo_zdof_output, "zdof_output")
            _sb(self.chk_lens_dirt,     "lens_dirt_en",  True)
            _sv(self.sp_lens_dirt_mix,  "lens_dirt_mix")
            self.sld_lens_dirt.setValue(int(round(self.sp_lens_dirt_mix.value() * 100)))

            # Tech settings
            _sb(self.chk_back_ramp,    "back_ramp_en",  True)
            _sb(self.chk_vignette,     "vignette_en",   True)
            _sv(self.sp_vignette_mix,  "vignette_mix")
            self.sld_vignette.setValue(int(round(self.sp_vignette_mix.value() * 100)))
            _sb(self.chk_occlusion,    "occlusion_en",  False)
            _sb(self.chk_shadow,       "shadow_en",     True)
            _sb(self.chk_text_info,    "text_info_en",  True)
            _sb(self.chk_ref_ball,     "ref_ball_en",   True)
            _sb(self.chk_hdri_prev,    "hdri_prev_en",  True)
            _sb(self.chk_ref_images,   "ref_images_en", True)

            # References
            _sv(self.sp_ref_tx,    "ref_tx")
            _sv(self.sp_ref_ty,    "ref_ty")
            _sv(self.sp_ref_scale, "ref_scale")
            if p.get("ref_single"):
                self.single_ref_card.set_path(p["ref_single"])
            _sb(self.chk_ref_single_dis, "ref_single_dis", True)
            _sb(self.chk_cs_dis,         "cs_dis",         False)
            refs = p.get("refs", [])
            for i, card in enumerate(self.ref_cards):
                if i < len(refs) and refs[i]:
                    card.set_path(refs[i])
            self.ref_cards[4].set_disabled_state(p.get("ref05_dis", False))
            self.ref_cards[5].set_disabled_state(p.get("ref06_dis", False))

            # Export
            _sl(self.f_write_base,    "write_base")
            _sl(self.f_write_name,    "write_name")
            _sb(self.chk_write_ver,   "write_ver_en", False)
            _sl(self.f_write_ver,     "write_ver")
            _sc(self.combo_write_fmt, "write_fmt")
            _sc(self.combo_write_cs,  "write_cs")
            self._on_write_changed()

            # Refresh naming preview
            t = self._combo_code(self.combo_asset_type)
            n_txt = self.f_asset_name.text().strip()
            d = self._combo_code(self.combo_asset_dept)
            v = self.f_asset_version.text().strip()
            u = self.f_asset_user.text().strip()
            self._update_naming_preview(t, n_txt, d, v, u)

            if p.get("render_folder"):
                self._on_folder_changed()

        finally:
            self._block_live = False

    def closeEvent(self, event):
        _save_prefs(self._collect_prefs())
        self._save_node_state()
        super().closeEvent(event)


# ==============================================================================
# Fallback
# ==============================================================================

def _fallback():
    p = nuke.Panel("TurnTable Comp Setup")
    p.addFilenameSearch("Render Location", "")
    p.addSingleLineInput("Asset Name", "")
    p.addSingleLineInput("Version",    "")
    p.addEnumerationPulldown("HDRI",       " ".join(HDRI_OPTIONS[:6]))
    p.addEnumerationPulldown("Render Type", " ".join(RENDER_OPTIONS))
    p.addEnumerationPulldown("Background",  " ".join(BACK_OPTIONS))
    p.addBooleanCheckBox("Enable COMP FX", False)
    if not p.show():
        return
    folder = p.value("Render Location")
    if folder:
        data = scan_render_folder(folder)
        live_render_paths_from_scan(data["hdri"])
        live_charts_paths_from_scan(data["charts"])
    live_asset_name(p.value("Asset Name"))
    live_asset_version(p.value("Version"))
    live_hdri_select(HDRI_OPTIONS[:6].index(p.value("HDRI")))
    live_render_type(RENDER_OPTIONS.index(p.value("Render Type")))
    live_back_select(BACK_OPTIONS.index(p.value("Background")))
    live_compfx(p.value("Enable COMP FX"))


# ==============================================================================
# Entry point
# ==============================================================================

_dialog_instance  = None
_aces_checked_once = False   # run OCIO check automatically only on the first dialog open


def launch():
    global _dialog_instance
    if PYSIDE_AVAILABLE:
        # Guard against accumulating instances — reuse if still alive
        if _dialog_instance is not None:
            try:
                if _dialog_instance.isVisible():
                    _dialog_instance.raise_()
                    _dialog_instance.activateWindow()
                    return
                # Window exists but is hidden — show it again
                _dialog_instance.show()
                _dialog_instance.raise_()
                _dialog_instance.activateWindow()
                return
            except RuntimeError:
                pass  # C++ object was already deleted by Qt; fall through to create new
        _dialog_instance = TurnTableCompSetupDialog()
        _dialog_instance.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        _dialog_instance.show()
        _dialog_instance.raise_()
        _dialog_instance.activateWindow()
    else:
        nuke.warning(
            "PXL TurnTable Comp Setup: PySide2/6 not available — fallback mode.")
        _fallback()
