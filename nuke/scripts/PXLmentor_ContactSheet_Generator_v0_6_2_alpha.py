# ==============================================================================
# Tool Name:   PXLmentor Contact Sheet Generator
# Version:     0.6.2-alpha
# Author:      PXLmentor AI Pipeline TD
# Description: Automated contact sheet generator for turntable / multi-set
#              render sequences. Scans folder hierarchies, detects discrepancies,
#              builds Read → ContactSheet → Write node graphs in Nuke 15.
#              Supports optional per-cell label overlay via Text2 node injection
#              with configurable token-stripper for any naming convention.
#
# Platform:    Nuke 15 (Python 3)
# Icon:        PXLmentor_ContactSheet_Generator.png
#              (place in ~/.nuke/PXLmentorToolbox/icons/)
#
# Installation:
#   1. Copy this file to ~/.nuke/PXLmentorToolbox/scripts/
#   2. Add to menu.py:
#        import PXLmentor_ContactSheet_Generator_v0_6_1_alpha as cs_gen
#        toolbar = nuke.toolbar("Nodes")
#        pxl = toolbar.addMenu("PXLmentor",
#                  icon="PXLmentor_ContactSheet_Generator.png")
#        pxl.addCommand("Contact Sheet Generator", cs_gen.launch,
#                  icon="PXLmentor_ContactSheet_Generator.png")
#   3. Add to init.py:
#        import nuke, os
#        toolbox = os.path.join(os.path.expanduser("~"), ".nuke",
#                               "PXLmentorToolbox")
#        nuke.pluginAddPath(os.path.join(toolbox, "scripts"))
#        nuke.pluginAddPath(os.path.join(toolbox, "icons"))
#
# Folder Structure:
#   main_folder/
#       Set_A/
#           Item_001/  [image sequence]
#           Item_002/  [image sequence]
#       Set_B/
#           ...
#
# CHANGELOG:
#   0.6.1-alpha  - UI polish + code cleanup pass:
#                  Applied PXLmentor brand color tokens (BRAND_ORANGE, HEADER_BG,
#                  BTN_RESET_BG, STATUS_OK, STATUS_ERR, STATUS_IDLE) as module-level
#                  constants. Primary action buttons updated to brand orange #E8820C.
#                  Reset/clear buttons updated to neutral dark grey #525252.
#                  Status bar background updates dynamically (green/red/idle).
#                  Status messages prefixed with checkmark/cross/dash.
#                  Section headers set to bold. Field labels set to bold.
#                  Consistent 10px outer / 8px inner spacing throughout.
#                  Removed all print() calls — logging module only.
#                  Removed dead code and duplicate scout call in _browse_main_folder.
#                  Fixed missing blank line before _build_button_bar helper methods.
#                  try/except on all external operations already present — verified.
#                  Colorspace read dynamically from OCIO config — unchanged (correct).
#   0.6.0-alpha  - Label Overlay: optional Text2 node injected after each Read
#                  node, burned bottom-center. Toggleable via 'Show Layer Name'
#                  checkbox (on by default)
#                - Token Stripper UI: Separator / Token From / Token To controls
#                  to adapt to any naming convention without code changes
#                - Live Preview: resolves and displays the label from the first
#                  scanned sequence — updates on scout and on control change
#                - TCL expression on Text2 uses [topnode] for live DAG resolution
#                - Migrated main window to PySide2 QDialog (ContactSheetWindow)
#                  with branded header: tool icon left, PixelMentor_Logo_Long
#                  center, tool name + version, collapsible Instructions panel
#                - menu.py: PixelMentor_Logo_SQUARE_64 as toolbar icon,
#                  PXLmentor_ContactSheet_Generator as subtool icon
#                - Fixed stale self.k_status reference in _do_build (was crashing
#                  on empty selection)
#   0.5.0-alpha  - Auto-select all sets after scout
#                - Colorspace list filtered to ACES 1.2 role entries only
#                  (excludes ' - ' subfolder entries)
#                - Page Suffix and File Extension knobs added to Step 4
#                - Write node output_transform set to "display"
#                - Backdrop label font size increased to 50
#   0.4.0-alpha  - Backdrop organisation: inner per-page + outer per-set
#                - All sets laid out left-to-right with consistent spacing
#                - Set selection dialog pre-ticks all sets by default
#   0.3.1-alpha  - Fixed nested-modal conflict on 'Choose Sets' button
#                  (replaced PythonPanel dialog with pure PySide2 QDialog)
#   0.3.0-alpha  - Replaced Multiline_Eval_String_Knob with scrollable
#                  PySide2 report windows
#   0.2.1-alpha  - Fixed SyntaxError: backslash inside f-string (Python 3.9)
#   0.2.0-alpha  - Fixed ContactSheet node wiring; colorspace from OCIO config;
#                  HD/4K/Custom resolution presets; discrepancy checker
#   0.1.0-alpha  - Initial prototype
# ==============================================================================

import nuke
import os
import re
import math
import json
import logging

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
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("PXLmentor.ContactSheet")

# ---------------------------------------------------------------------------
# Brand color tokens
# ---------------------------------------------------------------------------
BRAND_ORANGE  = "#E8820C"
HEADER_BG     = "#0D1F24"
BTN_RESET_BG  = "#525252"
STATUS_OK     = "#385838"
STATUS_ERR    = "#803838"
STATUS_IDLE   = "#383838"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VERSION   = "0.6.2-alpha"
TOOL_NAME = "PXLmentor Contact Sheet Generator"

PREFS_PATH = os.path.join(
    os.path.expanduser("~"), ".nuke", "PXLmentorToolbox",
    "contact_sheet_prefs.json"
)

ERROR_HANDLING_OPTIONS = ["nearest", "black", "hold", "mirror"]

RESOLUTION_PRESETS = {
    "HD  1920x1080":  (1920, 1080),
    "4K  3840x2160":  (3840, 2160),
    "Custom":         None,
}

DEFAULT_CELL_W = 1920
DEFAULT_CELL_H = 1080


# ==============================================================================
# MODULE 1 — DATA STRUCTURES
# ==============================================================================

class SequenceInfo:
    def __init__(self, folder_path: str, name: str):
        self.folder_path    = folder_path
        self.name           = name
        self.frames         = []
        self.first_frame    = 0
        self.last_frame     = 0
        self.frame_step     = 1
        self.width          = 0
        self.height         = 0
        self.file_pattern   = ""
        self.missing_frames = []

    @property
    def frame_count(self):
        return len(self.frames)

    def __repr__(self):
        return (f"<Seq '{self.name}'  "
                f"{self.first_frame}-{self.last_frame}  "
                f"step={self.frame_step}  "
                f"{self.width}x{self.height}>")


class SetInfo:
    def __init__(self, folder_path: str, name: str):
        self.folder_path = folder_path
        self.name        = name
        self.sequences   = []

    @property
    def sequence_count(self):
        return len(self.sequences)

    def __repr__(self):
        return f"<Set '{self.name}'  seqs={self.sequence_count}>"


# ==============================================================================
# MODULE 2 — FOLDER SCOUT
# ==============================================================================

class FolderScout:

    IMAGE_EXTENSIONS = {".exr", ".dpx", ".tiff", ".tif", ".png",
                        ".jpg", ".jpeg", ".hdr", ".cin"}
    FRAME_RE = re.compile(r"^(.+?)[\._](\d+)(\.\w+)$")

    def __init__(self, main_folder: str):
        self.main_folder = main_folder
        self.sets        = []

    def scout(self):
        self.sets = []
        if not os.path.isdir(self.main_folder):
            raise ValueError(f"Folder does not exist: {self.main_folder}")

        for set_name in sorted(os.listdir(self.main_folder)):
            set_path = os.path.join(self.main_folder, set_name)
            if not os.path.isdir(set_path):
                continue

            set_info = SetInfo(folder_path=set_path, name=set_name)

            for item_name in sorted(os.listdir(set_path)):
                item_path = os.path.join(set_path, item_name)
                if not os.path.isdir(item_path):
                    continue
                seq = self._scan_seq(item_path, item_name)
                if seq:
                    set_info.sequences.append(seq)

            if set_info.sequences:
                self.sets.append(set_info)

        log.info("Scout: %d set(s) found.", len(self.sets))
        return self.sets

    def _scan_seq(self, folder_path: str, name: str):
        seq       = SequenceInfo(folder_path=folder_path, name=name)
        frame_map = {}

        for fname in os.listdir(folder_path):
            ext = os.path.splitext(fname)[1].lower()
            if ext not in self.IMAGE_EXTENSIONS:
                continue
            m = self.FRAME_RE.match(fname)
            if not m:
                continue
            _, num_str, _ = m.groups()
            frame_map[int(num_str)] = fname

        if not frame_map:
            return None

        seq.frames      = sorted(frame_map.keys())
        seq.first_frame = seq.frames[0]
        seq.last_frame  = seq.frames[-1]

        if len(seq.frames) > 1:
            steps          = [seq.frames[i + 1] - seq.frames[i]
                              for i in range(min(5, len(seq.frames) - 1))]
            seq.frame_step = min(steps)
        else:
            seq.frame_step = 1

        expected           = set(range(seq.first_frame,
                                       seq.last_frame + seq.frame_step,
                                       seq.frame_step))
        seq.missing_frames = sorted(expected - set(seq.frames))

        sample = frame_map[seq.frames[0]]
        m2     = self.FRAME_RE.match(sample)
        if m2:
            base, num_str, ext = m2.groups()
            seq.file_pattern   = os.path.join(
                folder_path,
                f"{base}.{'#' * len(num_str)}{ext}"
            ).replace("\\", "/")

        # Resolution — read via temp Read node, delete immediately
        sample_path = os.path.join(folder_path, sample).replace("\\", "/")
        try:
            tmp        = nuke.nodes.Read(file=sample_path,
                                         first=seq.frames[0],
                                         last=seq.frames[0])
            seq.width  = tmp.width()
            seq.height = tmp.height()
            nuke.delete(tmp)
        except Exception as e:
            log.warning("Could not read resolution for %s: %s", folder_path, e)

        return seq


# ==============================================================================
# MODULE 3 — DISCREPANCY CHECKER
# ==============================================================================

def _base_name(name: str) -> str:
    """
    Strip trailing set-specific suffixes so names can be compared across sets.
    e.g. 'Head_SCAN_01_EyesUp_Day_Overcast' → 'Head_SCAN_01_EyesUp'
    This is a best-effort heuristic: strip the last 1–2 underscore tokens
    if they look like a set name fragment (all caps or title-case words).
    """
    parts = name.split("_")
    while len(parts) > 1 and re.match(r"^[A-Z][a-zA-Z]*$", parts[-1]):
        parts.pop()
    return "_".join(parts)


class DiscrepancyReport:
    def __init__(self):
        self.warnings = []
        self.errors   = []

    @property
    def has_issues(self):
        return bool(self.warnings or self.errors)

    def summary(self):
        lines = []
        if self.errors:
            lines.append(f"ERRORS ({len(self.errors)}):")
            lines.extend(f"  [E]  {e}" for e in self.errors)
        if self.warnings:
            lines.append(f"WARNINGS ({len(self.warnings)}):")
            lines.extend(f"  [W]  {w}" for w in self.warnings)
        if not lines:
            lines.append("No issues detected.")
        return "\n".join(lines)


def check_discrepancies(selected_sets):
    report = DiscrepancyReport()
    if not selected_sets:
        report.errors.append("No sets selected.")
        return report

    ref            = selected_sets[0]
    ref_count      = ref.sequence_count
    ref_base_names = {_base_name(s.name) for s in ref.sequences}

    for s in selected_sets[1:]:
        if s.sequence_count != ref_count:
            report.warnings.append(
                f"'{s.name}' has {s.sequence_count} sequences; "
                f"'{ref.name}' has {ref_count}."
            )
        s_base_names = {_base_name(seq.name) for seq in s.sequences}
        for missing in sorted(ref_base_names - s_base_names):
            report.warnings.append(
                f"'{s.name}' appears to be missing a sequence matching '{missing}'."
            )

    for s in selected_sets:
        resolutions  = set()
        frame_counts = set()
        for seq in s.sequences:
            if seq.missing_frames:
                report.warnings.append(
                    f"'{s.name}/{seq.name}': "
                    f"{len(seq.missing_frames)} missing frame(s)."
                )
            if seq.width and seq.height:
                resolutions.add((seq.width, seq.height))
            frame_counts.add(seq.frame_count)
        if len(resolutions) > 1:
            report.warnings.append(
                f"'{s.name}' has mixed resolutions: "
                + ", ".join(f"{w}x{h}" for w, h in resolutions)
            )
        if len(frame_counts) > 1:
            report.warnings.append(
                f"'{s.name}' has mixed frame counts: "
                + ", ".join(str(c) for c in sorted(frame_counts))
            )

    return report


# ==============================================================================
# MODULE 4 — CONFIG
# ==============================================================================

class ContactSheetConfig:
    def __init__(self):
        self.items_per_page  = 12
        self.colorspace      = "scene_linear"
        self.on_error        = "nearest"
        self.output_width    = DEFAULT_CELL_W   # ContactSheet node total width
        self.output_height   = DEFAULT_CELL_H   # ContactSheet node total height
        self.output_dir      = "/tmp/contact_sheets"
        self.output_prefix   = "cs"
        self.output_suffix   = "_Board"
        self.output_ext      = "png"
        # Label overlay
        self.show_label      = True
        self.label_separator = "_"
        self.label_tok_from  = 2
        self.label_tok_to    = 4


# ==============================================================================
# MODULE 5 — NUKE NODE BUILDER  (with Backdrop organisation)
# ==============================================================================

def _resolve_label_preview(filename: str, separator: str,
                           tok_from: int, tok_to: int) -> str:
    """
    Python-side mirror of the TCL token-stripper logic.
    Strips frame number + extension, splits on separator,
    slices [tok_from : tok_to+1], rejoins with separator.

    e.g. "cs_DayLight_Head_SCAN_01_EyesUp.0001.exr", "_", 2, 4
         → "Head_SCAN_01"
    """
    base   = os.path.basename(filename)
    base   = re.sub(r'[\._]\d+\.\w+$', '', base)
    parts  = base.split(separator)
    sliced = parts[tok_from: tok_to + 1]
    return separator.join(sliced) if sliced else base


def _make_tcl_label_expr(separator: str, tok_from: int, tok_to: int) -> str:
    """
    Build the TCL expression for the Text node message knob.
    Uses [topnode] so it stays live even if the Read node is renamed.

    TCL lrange is inclusive on both ends and 0-based.
    """
    sep_tcl = separator.replace('"', '\\"')
    return (
        f'[join '
        f'[lrange '
        f'[split '
        f'[regsub -all {{[\\._]\\d+\\.\\w+$}} '
        f'[file tail [knob [topnode].file]] {{}}] '
        f'"{sep_tcl}"] '
        f'{tok_from} {tok_to}] '
        f'"{sep_tcl}"]'
    )


def _optimal_grid(n: int):
    """Return (cols, rows) for a square-ish grid fitting n items."""
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    return cols, rows


# Backdrop colour palette — one per set index, cycles if more sets than colours
_BACKDROP_OUTER_COLORS = [
    0x3a2a4aff,  # dark purple
    0x2a3a4aff,  # dark blue
    0x2a4a3aff,  # dark green
    0x4a3a2aff,  # dark orange
    0x4a2a2aff,  # dark red
    0x2a4a4aff,  # dark teal
    0x3a4a2aff,  # dark olive
]
_BACKDROP_INNER_COLOR = 0x1a1a1aff   # near-black for page backdrops


def _make_backdrop(label: str, nodes: list, color: int,
                   pad_x: int = 40, pad_y: int = 60,
                   font_size: int = 42,
                   z_order: int = 0) -> "nuke.Node":
    """
    Create a BackdropNode that tightly wraps the given list of nodes.

    z_order knob is set directly:
      0 = behind (set backdrop)
      1 = in front (page backdrop)
    Nuke's z_order knob overrides creation-order stacking.
    """
    if not nodes:
        return None

    min_x = min(n.xpos() for n in nodes) - pad_x
    min_y = min(n.ypos() for n in nodes) - pad_y * 2   # extra top space for label
    max_x = max(n.xpos() + n.screenWidth()  for n in nodes) + pad_x
    max_y = max(n.ypos() + n.screenHeight() for n in nodes) + pad_y

    bd = nuke.nodes.BackdropNode(
        xpos           = min_x,
        ypos           = min_y,
        bdwidth        = max_x - min_x,
        bdheight       = max_y - min_y,
        tile_color     = color,
        note_font_size = font_size,
        label          = label,
        z_order        = z_order,
    )
    return bd


class NukeNodeBuilder:
    """
    Build order per set
    ───────────────────
    For each page (left → right):
      1. Create nodes (Read, Text2, ContactSheet, Write)
      2. Position them at (x_cursor, y_origin)
      3. Create page backdrop IMMEDIATELY around those nodes
      4. Read backdrop right-edge  →  advance x_cursor by (right_edge + PAGE_GAP)

    After all pages are done:
      5. Create set backdrop around ALL page backdrops + their nodes

    Backdrop z_order:
      set backdrop  → z_order = 0  (behind)
      page backdrops → z_order = 1 (in front)
    These are set via the z_order knob directly, NOT inferred from creation order.

    Solution:
      Phase A  — build + layout + collect bboxes (NO backdrops yet)
      Phase B  — create set backdrop first (z_order=0, behind),
                 using collected bbox from all pages
      Phase C  — create page backdrops (z_order=1, in front),
                 using per-page bbox

    ContactSheet width/height = total output resolution — NOT per-cell size.
    frame_increment is a nuke.execute() argument — NOT a Write node knob.

    Pages : LEFT → RIGHT
    Sets  : TOP  → BOTTOM
    """

    COL_STEP = 150    # x between node columns
    ROW_STEP = 150    # y between node rows
    PAGE_GAP = 400    # gap between page backdrops (right edge to left edge)
    SET_GAP  = 800    # gap between set backdrops  (bottom edge to top edge)

    _PAGE_PAD_X = 60   # page backdrop padding
    _PAGE_PAD_Y = 80
    _SET_PAD_X  = 120  # set backdrop padding
    _SET_PAD_Y  = 140

    # Approximate node tile dimensions in DAG units
    _NODE_W = 80
    _NODE_H = 28

    def __init__(self, config: ContactSheetConfig):
        self.config        = config
        self._set_y_cursor = 0   # top of the next set

    # ── PUBLIC ────────────────────────────────────────────────────────────
    def build_all_sets(self, set_list: list) -> dict:
        self._set_y_cursor = 0
        result = {}
        for set_info in set_list:
            result[set_info.name] = self.build_set(set_info)

        # Set project frame range to span of the longest sequence
        all_seqs = [sq for si in set_list for sq in si.sequences]
        if all_seqs:
            global_first = min(sq.first_frame for sq in all_seqs)
            global_last  = max(sq.last_frame  for sq in all_seqs)
            try:
                nuke.root()["first_frame"].setValue(global_first)
                nuke.root()["last_frame"].setValue(global_last)
                log.info("Project frame range set to %d–%d.", global_first, global_last)
            except Exception as e:
                log.warning("Could not set project frame range: %s", e)

        return result

    def build_set(self, set_info: SetInfo) -> list:
        cfg     = self.config
        seqs    = set_info.sequences
        ipp     = max(1, cfg.items_per_page)
        n_pages = math.ceil(len(seqs) / ipp)

        writes      = []
        page_record = []   # (page_nodes, label) — backdrops done in phase B/C

        # Nodes start below the set backdrop top-padding so the label is visible
        y_origin = self._set_y_cursor + self._SET_PAD_Y * 2

        # x_cursor: left edge of the NEXT page's nodes
        x_cursor = self._SET_PAD_X

        # ── Phase A: build + layout all pages ────────────────────────────
        for page_idx in range(n_pages):
            chunk     = seqs[page_idx * ipp : (page_idx + 1) * ipp]
            n         = len(chunk)

            reads = [self._make_read(s) for s in chunk]
            texts = ([self._make_text(reads[i], chunk[i]) for i in range(n)]
                     if cfg.show_label else [])
            tops  = texts if texts else reads
            cs    = self._make_contact_sheet(tops, n)

            first_fr = chunk[0].first_frame if chunk else 1
            last_fr  = chunk[0].last_frame  if chunk else 1

            w = self._make_write(cs, set_info.name, page_idx + 1, n_pages,
                                 first_frame=first_fr, last_frame=last_fr)
            writes.append(w)

            # Position nodes
            self._layout_page(reads, texts, cs, w,
                               x_origin=x_cursor, y_origin=y_origin)

            page_nodes = reads + texts + [cs, w]
            label      = f"Page {page_idx + 1}/{n_pages}  ·  {n} items"
            page_record.append((page_nodes, label))

            # Advance x_cursor to clear this page's backdrop right edge + gap
            nodes_right = max(nd.xpos() for nd in page_nodes) + self._NODE_W
            x_cursor    = nodes_right + self._PAGE_PAD_X + self.PAGE_GAP

        # Collect all nodes across all pages for the set backdrop
        all_set_nodes = [nd for page_nodes, _ in page_record for nd in page_nodes]

        # ── Phase B: set backdrop FIRST → z_order=0 (behind) ─────────────
        safe_name = re.sub(r"[^\w ]", " ", set_info.name)
        set_bd = _make_backdrop(
            f"◆  {safe_name}",
            all_set_nodes,
            color     = _BACKDROP_OUTER_COLORS[hash(set_info.name) % len(_BACKDROP_OUTER_COLORS)],
            font_size = 60,
            pad_x     = self._SET_PAD_X,
            pad_y     = self._SET_PAD_Y,
            z_order   = 0,
        )

        # ── Phase C: page backdrops AFTER → z_order=1 (in front) ─────────
        for page_nodes, page_label in page_record:
            _make_backdrop(
                page_label,
                page_nodes,
                color     = _BACKDROP_INNER_COLOR,
                font_size = 30,
                pad_x     = self._PAGE_PAD_X,
                pad_y     = self._PAGE_PAD_Y,
                z_order   = 1,
            )

        # ── Advance y cursor past this set's backdrop ─────────────────────
        if set_bd:
            bd_bottom = set_bd.ypos() + int(set_bd["bdheight"].value())
        else:
            bd_bottom = max(nd.ypos() + self._NODE_H for nd in all_set_nodes)
        self._set_y_cursor = bd_bottom + self.SET_GAP

        log.info("Built %d page(s) for set '%s'.", n_pages, set_info.name)
        return writes

    # ── NODE FACTORIES ────────────────────────────────────────────────────
    def _make_read(self, seq: SequenceInfo):
        cfg  = self.config
        safe = re.sub(r'[^\w]', '_', seq.name)
        r = nuke.nodes.Read(
            name  = f"Read_{safe}",
            file  = seq.file_pattern,
            first = seq.first_frame,
            last  = seq.last_frame,
        )
        try:
            r["colorspace"].setValue(cfg.colorspace)
        except Exception as e:
            log.warning("colorspace: %s", e)
        try:
            r["on_error"].setValue(cfg.on_error)
        except Exception as e:
            log.warning("on_error: %s", e)
        r["label"].setValue(seq.name)
        return r

    def _make_text(self, read_node, seq: SequenceInfo):
        """
        Text2 directly below Read — label burned bottom-centre.

        Box is sized to the Read node's actual output resolution so centering
        is correct regardless of source format. A 5% bottom margin keeps the
        text off the very edge of the frame.
        """
        cfg      = self.config
        safe     = re.sub(r'[^\w]', '_', seq.name)
        tcl_expr = _make_tcl_label_expr(
            cfg.label_separator, cfg.label_tok_from, cfg.label_tok_to)

        src_w = read_node.width()  if read_node.width()  > 0 else (seq.width  or 1920)
        src_h = read_node.height() if read_node.height() > 0 else (seq.height or 1080)

        font_size = max(20, int(src_h * 0.04))
        margin_y  = int(src_h * 0.05)
        box_top    = margin_y
        box_bottom = int(src_h * 0.20) + margin_y
        box = [0, box_top, src_w, box_bottom]

        txt = nuke.nodes.Text2(name=f"Label_{safe}")
        txt["message"].setValue(tcl_expr)
        try:
            txt["box"].setValue(box)
        except Exception:
            pass
        try:
            txt["xjustify"].setValue("center")
        except Exception:
            pass
        try:
            txt["yjustify"].setValue("bottom")
        except Exception:
            pass
        try:
            txt["font_size_toolbar"].setValue(font_size)
        except Exception:
            try:
                txt["size"].setValue(font_size)
            except Exception:
                pass
        txt.setInput(0, read_node)
        return txt

    def _make_contact_sheet(self, top_nodes: list, n_items: int):
        """
        ContactSheet width/height = total output resolution (NOT per-cell).
        center=True: each input is centred within its cell.
        gap=5: 5px gap between cells.
        """
        cfg        = self.config
        cols, rows = _optimal_grid(n_items)
        cs = nuke.nodes.ContactSheet(
            width    = cfg.output_width,
            height   = cfg.output_height,
            rows     = rows,
            columns  = cols,
            roworder = "TopBottom",
        )
        try:
            cs["center"].setValue(True)
        except Exception as e:
            log.warning("ContactSheet center: %s", e)
        try:
            cs["gap"].setValue(5)
        except Exception as e:
            log.warning("ContactSheet gap: %s", e)

        for i, node in enumerate(top_nodes):
            if i >= cs.inputs():
                cs.setInput(i, None)
            cs.setInput(i, node)
        return cs

    def _make_write(self, cs_node, set_name: str, page: int, total: int,
                    first_frame: int = 1, last_frame: int = 1):
        """
        Output path:  <output_dir>/<set_name>/<prefix>_<set_name><suffix><page##>.####.<ext>
        Frame range:  use_limit enabled, clamped to first_frame–last_frame of the
                      upstream Read node.
        frame_increment is passed to nuke.execute() — it is NOT a Write node knob.
        """
        cfg    = self.config
        ext    = cfg.output_ext.lstrip(".")
        suffix = f"{cfg.output_suffix}{page:02d}" if total > 1 else cfg.output_suffix

        subdir   = os.path.join(cfg.output_dir, set_name)
        filename = f"{cfg.output_prefix}_{set_name}{suffix}.####.{ext}"
        path     = os.path.join(subdir, filename).replace("\\", "/")
        try:
            os.makedirs(subdir, exist_ok=True)
        except Exception as e:
            log.warning("Could not create output directory %s: %s", subdir, e)

        safe = re.sub(r"[^\w]", "_", set_name)
        w = nuke.nodes.Write(file=path, name=f"Write_{safe}_p{page:02d}")
        try:
            w["create_directories"].setValue(True)
        except Exception as e:
            log.warning("Write create_directories: %s", e)
        try:
            w["colorspace"].setValue(cfg.colorspace)
        except Exception as e:
            log.warning("Write colorspace: %s", e)
        try:
            w["transform_type"].setValue("display")
        except Exception:
            try:
                w["output_transform"].setValue("display")
            except Exception as e:
                log.warning("Write transform: %s", e)

        # Limit frame range to the upstream sequence duration
        try:
            w["use_limit"].setValue(True)
            w["first"].setValue(first_frame)
            w["last"].setValue(last_frame)
        except Exception as e:
            log.warning("Could not set Write frame range: %s", e)

        w.setInput(0, cs_node)
        w["label"].setValue(f"{set_name}  {page}/{total}")
        return w

    # ── LAYOUT ────────────────────────────────────────────────────────────
    def _layout_page(self, reads, texts, cs, write,
                     x_origin: int = 0, y_origin: int = 0):
        """
        Place every node for one page on a strict grid.

          col_x = x_origin + col_index * COL_STEP
          row_y = y_origin + row_index * ROW_STEP

          row 0  →  Reads
          row 1  →  Texts  (only if labels enabled)
          row 2  →  ContactSheet  centred  (row 1 if no labels)
          row 3  →  Write         centred  (row 2 if no labels)

        centre_x = x_origin + ((n-1) * COL_STEP) / 2
        """
        sx = self.COL_STEP
        sy = self.ROW_STEP
        n  = len(reads)

        for i, r in enumerate(reads):
            r.setXpos(x_origin + i * sx)
            r.setYpos(y_origin)

        for i, t in enumerate(texts):
            t.setXpos(x_origin + i * sx)
            t.setYpos(y_origin + sy)

        centre_x  = x_origin + ((n - 1) * sx) // 2
        cs_row    = 2 if texts else 1
        write_row = cs_row + 1

        cs.setXpos(centre_x)
        cs.setYpos(y_origin + cs_row * sy)
        write.setXpos(centre_x)
        write.setYpos(y_origin + write_row * sy)


# ==============================================================================
# MODULE 5b — SCROLLABLE REPORT WINDOW (PySide2)
# ==============================================================================

class ScrollableReportWindow:
    """
    Opens a resizable, scrollable plain-text window via PySide2/6.
    Falls back to nuke.message() if PySide is unavailable.

    Usage:
        ScrollableReportWindow("Scan Result", text).show()
    """

    def __init__(self, title: str, content: str, width: int = 800, height: int = 600):
        self.title   = title
        self.content = content
        self.width   = width
        self.height  = height

    def show(self):
        if not PYSIDE_AVAILABLE:
            preview = self.content[:2000]
            if len(self.content) > 2000:
                preview += "\n\n... (truncated — PySide2 not available)"
            nuke.message(preview)
            return

        app    = QtWidgets.QApplication.instance()
        parent = None
        if app:
            for widget in app.topLevelWidgets():
                if widget.objectName() == "Foundry::UI::DockMainWindow":
                    parent = widget
                    break

        dialog = QtWidgets.QDialog(parent)
        dialog.setWindowTitle(f"PXLmentor  —  {self.title}")
        dialog.resize(self.width, self.height)
        dialog.setMinimumSize(400, 300)
        dialog.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowMinMaxButtonsHint |
            QtCore.Qt.WindowCloseButtonHint
        )

        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        title_label = QtWidgets.QLabel(f"<b>{self.title}</b>")
        title_label.setStyleSheet("font-size: 13px; color: #cccccc; padding: 4px;")
        layout.addWidget(title_label)

        text_edit = QtWidgets.QPlainTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(self.content)
        text_edit.setStyleSheet(
            "QPlainTextEdit {"
            "  background-color: #1a1a1a;"
            "  color: #d4d4d4;"
            "  font-family: Consolas, 'Courier New', monospace;"
            "  font-size: 11px;"
            "  border: 1px solid #444;"
            "  padding: 6px;"
            "}"
        )
        layout.addWidget(text_edit)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch()
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.setFixedWidth(90)
        close_btn.setStyleSheet(
            f"QPushButton {{ background: {BTN_RESET_BG}; color: #ccc; "
            "border: 1px solid #666; padding: 4px 10px; border-radius: 3px; }"
            f"QPushButton:hover {{ background: #686868; }}"
        )
        close_btn.clicked.connect(dialog.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        dialog.exec_()


# ==============================================================================
# MODULE 6 — SET SELECTION DIALOG (PySide2 QDialog — avoids modal conflict)
# ==============================================================================

class SetSelectionDialog:
    """
    Pure PySide2 QDialog checkbox list for set selection.
    Does NOT use nukescripts.PythonPanel — avoids the nested-modal conflict
    that occurs when calling showModalDialog() from inside a knobChanged callback
    of another PythonPanel.

    All sets pre-ticked by default; user deselects unwanted ones.

    Usage:
        dlg = SetSelectionDialog(sets)
        if dlg.exec_():
            selected = dlg.selected_sets()
    """

    def __init__(self, sets: list):
        self._sets       = sets
        self._checkboxes = []
        self._dialog     = None
        self._build()

    def _build(self):
        if not PYSIDE_AVAILABLE:
            return

        app    = QtWidgets.QApplication.instance()
        parent = None
        if app:
            for w in app.topLevelWidgets():
                if w.objectName() == "Foundry::UI::DockMainWindow":
                    parent = w
                    break

        self._dialog = QtWidgets.QDialog(parent)
        self._dialog.setWindowTitle("PXLmentor  —  Select Sets")
        self._dialog.setMinimumSize(420, 300)
        self._dialog.resize(500, max(300, 80 + len(self._sets) * 34))
        self._dialog.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowCloseButtonHint
        )
        self._dialog.setStyleSheet("QDialog { background: #2b2b2b; }")

        layout = QtWidgets.QVBoxLayout(self._dialog)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        hdr = QtWidgets.QLabel(
            "<b>All sets selected by default.</b><br>"
            "<span style='color:#888; font-size:11px;'>"
            "Deselect any sets you want to exclude.</span>"
        )
        hdr.setStyleSheet("color: #cccccc; font-size: 12px;")
        layout.addWidget(hdr)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { border: 1px solid #444; background: #1e1e1e; }"
        )
        container = QtWidgets.QWidget()
        container.setStyleSheet("background: #1e1e1e;")
        cb_layout = QtWidgets.QVBoxLayout(container)
        cb_layout.setContentsMargins(10, 8, 10, 8)
        cb_layout.setSpacing(4)

        for s in self._sets:
            cb = QtWidgets.QCheckBox(
                f"{s.name}   ({s.sequence_count} items)"
            )
            cb.setChecked(True)
            cb.setStyleSheet(
                "QCheckBox { color: #d4d4d4; font-size: 11px; padding: 3px; }"
                "QCheckBox::indicator { width: 14px; height: 14px; }"
            )
            cb_layout.addWidget(cb)
            self._checkboxes.append((cb, s))

        cb_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

        sel_row = QtWidgets.QHBoxLayout()
        all_btn  = QtWidgets.QPushButton("Select All")
        none_btn = QtWidgets.QPushButton("Select None")
        for btn in (all_btn, none_btn):
            btn.setFixedHeight(26)
            btn.setStyleSheet(
                f"QPushButton {{ background: {BTN_RESET_BG}; color: #ccc; "
                "border: 1px solid #666; padding: 2px 10px; border-radius: 3px; }"
                f"QPushButton:hover {{ background: #686868; }}"
            )
        all_btn.clicked.connect(lambda: [cb.setChecked(True)
                                         for cb, _ in self._checkboxes])
        none_btn.clicked.connect(lambda: [cb.setChecked(False)
                                          for cb, _ in self._checkboxes])
        sel_row.addWidget(all_btn)
        sel_row.addWidget(none_btn)
        sel_row.addStretch()
        layout.addLayout(sel_row)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch()
        ok_btn     = QtWidgets.QPushButton("OK")
        cancel_btn = QtWidgets.QPushButton("Cancel")
        ok_btn.setFixedWidth(80)
        ok_btn.setFixedHeight(28)
        ok_btn.setStyleSheet(
            f"QPushButton {{ background: {BRAND_ORANGE}; color: white; "
            "border: none; padding: 2px 10px; border-radius: 3px; }"
            "QPushButton:hover { background: #f09020; }"
        )
        cancel_btn.setFixedWidth(80)
        cancel_btn.setFixedHeight(28)
        cancel_btn.setStyleSheet(
            f"QPushButton {{ background: {BTN_RESET_BG}; color: #ccc; "
            "border: 1px solid #666; padding: 2px 10px; border-radius: 3px; }"
            f"QPushButton:hover {{ background: #686868; }}"
        )
        ok_btn.clicked.connect(self._dialog.accept)
        cancel_btn.clicked.connect(self._dialog.reject)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def exec_(self) -> bool:
        """Show dialog. Returns True if user clicked OK."""
        if not PYSIDE_AVAILABLE or self._dialog is None:
            return True
        result = self._dialog.exec_()
        return result == QtWidgets.QDialog.Accepted

    def selected_sets(self) -> list:
        return [s for cb, s in self._checkboxes if cb.isChecked()]


# ==============================================================================
# MODULE 7 — ICON / WINDOW HELPERS
# ==============================================================================

_ICON_DIR = os.path.join(
    os.path.expanduser("~"), ".nuke", "PXLmentorToolbox", "icons"
)


def _icon_path(filename: str) -> str:
    return os.path.join(_ICON_DIR, filename).replace("\\", "/")


def _nuke_main_window():
    app = QtWidgets.QApplication.instance()
    if app:
        for w in app.topLevelWidgets():
            if w.objectName() == "Foundry::UI::DockMainWindow":
                return w
    return None


def _get_colorspaces_static():
    """Query OCIO colorspace roles from a temp Read node.
    Filters to top-level role entries only — excludes deep 'Colorspaces'
    subfolder entries (those containing ' - ').
    Falls back to ACES 1.2 defaults on failure.
    """
    ROLE_ORDER = [
        "default (matte_paint)", "color_picking", "color_timing",
        "compositing_linear", "compositing_log", "data", "default",
        "matte_paint", "reference", "rendering", "scene_linear", "texture_paint",
    ]
    try:
        tmp        = nuke.nodes.Read()
        raw        = tmp['colorspace'].values()
        all_spaces = [v.split('\t')[0] for v in raw]
        nuke.delete(tmp)
        available = set(all_spaces)
        # Top-level roles only — exclude anything containing ' - ' (subfolder entries)
        ordered   = [r for r in ROLE_ORDER if r in available]
        if not ordered:
            ordered = [cs for cs in all_spaces if " - " not in cs]
        return ordered if ordered else all_spaces
    except Exception as e:
        log.warning("Could not query colorspaces: %s", e)
    return ROLE_ORDER


# ==============================================================================
# MODULE 8 — MAIN WINDOW  (pure PySide2 — no PythonPanel)
# ==============================================================================

class ContactSheetWindow(QtWidgets.QDialog):
    """
    Full PySide2 QDialog — branded header + collapsible instructions + scrollable form.
    No nukescripts.PythonPanel dependency.
    """

    BODY_BG = "#2b2b2b"

    # Button stylesheets
    _BTN = (
        f"QPushButton{{background:{BRAND_ORANGE};color:#fff;border:none;"
        "padding:6px 14px;font-size:11px;border-radius:3px;}"
        "QPushButton:hover{background:#f09020;}"
        "QPushButton:pressed{background:#c06a00;}"
    )
    _BTN2 = (
        f"QPushButton{{background:{BTN_RESET_BG};color:#ccc;border:1px solid #686868;"
        "padding:5px 12px;font-size:11px;border-radius:3px;}"
        "QPushButton:hover{background:#686868;}"
    )
    _FIELD = (
        "QLineEdit,QSpinBox,QComboBox{background:#1e1e1e;color:#d4d4d4;"
        "border:1px solid #444;padding:4px;font-size:11px;border-radius:2px;}"
        "QComboBox::drop-down{border:none;}"
        "QComboBox QAbstractItemView{background:#1e1e1e;color:#d4d4d4;}"
    )
    _LBL  = "QLabel{color:#cccccc;font-size:11px;font-weight:bold;background:transparent;}"
    _STAT = ("QLabel{color:#aaaaaa;font-size:10px;font-style:italic;"
             f"background:{STATUS_IDLE};border:1px solid #4a4a4a;padding:4px;"
             "border-radius:2px;}")
    _SECT = ("QLabel{color:#e0e0e0;font-size:12px;font-weight:bold;"
             f"border-bottom:1px solid {BRAND_ORANGE};padding-bottom:3px;"
             "background:transparent;}")
    _CHK  = ("QCheckBox{color:#cccccc;font-size:11px;background:transparent;}"
             "QCheckBox::indicator{width:14px;height:14px;}")

    def __init__(self, parent=None):
        super().__init__(parent or _nuke_main_window())

        self._scout_data        = []
        self._selected_sets     = []
        self._scout_result_text = ""
        self._report_text       = ""
        self._build_log_text    = ""

        self.setWindowTitle(f"{TOOL_NAME}  v{VERSION}")
        self.setMinimumSize(700, 950)
        self.resize(720, 1110)
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowMinMaxButtonsHint |
            QtCore.Qt.WindowCloseButtonHint
        )
        self.setStyleSheet(f"QDialog{{background:{self.BODY_BG};}}")

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addWidget(self._build_instructions())
        root.addWidget(self._build_scroll_body(), 1)
        root.addWidget(self._build_button_bar())

        self._load_prefs()

    # ── HEADER ────────────────────────────────────────────────────────────
    def _build_header(self):
        hdr = QtWidgets.QWidget()
        hdr.setFixedHeight(100)
        hdr.setStyleSheet(f"background:{HEADER_BG};")
        hl = QtWidgets.QHBoxLayout(hdr)
        hl.setContentsMargins(12, 8, 12, 8)
        hl.setSpacing(0)

        # Left — tool icon 80×80
        lbl_icon = QtWidgets.QLabel()
        lbl_icon.setFixedSize(80, 80)
        lbl_icon.setAlignment(QtCore.Qt.AlignCenter)
        lbl_icon.setStyleSheet(f"background:{HEADER_BG};")
        tp = _icon_path("PXLmentor_ContactSheet_Generator.png")
        if os.path.exists(tp):
            lbl_icon.setPixmap(QtGui.QPixmap(tp).scaled(
                80, 80, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            lbl_icon.setText("[ icon ]")
            lbl_icon.setStyleSheet("color:#555;font-size:10px;border:1px solid #444;")
        hl.addWidget(lbl_icon)

        # Center — logo + name + version
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
                "color:#fff;font-size:22px;font-weight:bold;letter-spacing:3px;")
        col.addWidget(lbl_logo)

        lbl_name = QtWidgets.QLabel("Contact Sheet Generator")
        lbl_name.setAlignment(QtCore.Qt.AlignCenter)
        lbl_name.setStyleSheet(
            f"color:#e0e0e0;font-size:12px;font-weight:bold;background:{HEADER_BG};")
        col.addWidget(lbl_name)

        lbl_ver = QtWidgets.QLabel(f"v{VERSION}")
        lbl_ver.setAlignment(QtCore.Qt.AlignCenter)
        lbl_ver.setStyleSheet(f"color:#778899;font-size:10px;background:{HEADER_BG};")
        col.addWidget(lbl_ver)

        hl.addLayout(col, 1)

        # Right spacer (mirrors icon width for balance)
        sp = QtWidgets.QWidget()
        sp.setFixedSize(80, 80)
        sp.setStyleSheet(f"background:{HEADER_BG};")
        hl.addWidget(sp)

        return hdr

    # ── INSTRUCTIONS ──────────────────────────────────────────────────────
    def _build_instructions(self):
        wrap = QtWidgets.QWidget()
        wrap.setStyleSheet(f"background:{self.BODY_BG};")
        wl = QtWidgets.QVBoxLayout(wrap)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(0)

        btn = QtWidgets.QPushButton("▶   Instructions")
        btn.setCheckable(True)
        btn.setStyleSheet(
            f"QPushButton{{background:#7a4f1e;color:#f0c080;font-size:11px;"
            "font-weight:bold;border:none;padding:6px 14px;text-align:left;}"
            "QPushButton:checked{background:#6a3f10;}"
            "QPushButton:hover{background:#8a5f2e;}"
        )
        wl.addWidget(btn)

        body = QtWidgets.QWidget()
        body.setVisible(False)
        body.setStyleSheet("background:#3a2a14;")
        bl = QtWidgets.QVBoxLayout(body)
        bl.setContentsMargins(16, 8, 16, 8)
        bl.setSpacing(3)
        for line in [
            "1.  Enter the main folder path and click  Scout Folder.",
            "2.  All sets are auto-selected.  Use  Choose Sets…  to refine.",
            "3.  Click  Analyse Selection  to check for discrepancies.",
            "4.  Configure resolution, colorspace, label and output options.",
            "5.  Click  Build Node Graph  to build. Click  OK  to confirm or  Cancel  to close.",
        ]:
            lbl = QtWidgets.QLabel(line)
            lbl.setStyleSheet("color:#d4b080;font-size:11px;background:#3a2a14;")
            bl.addWidget(lbl)
        wl.addWidget(body)

        def _toggle(checked):
            body.setVisible(checked)
            btn.setText(("▼" if checked else "▶") + "   Instructions")
        btn.toggled.connect(_toggle)
        return wrap

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
        vl.setContentsMargins(20, 16, 20, 20)
        vl.setSpacing(16)

        vl.addWidget(self._step1())
        vl.addWidget(self._step2())
        vl.addWidget(self._step3())
        vl.addWidget(self._step4())
        vl.addWidget(self._step_label())
        vl.addWidget(self._step5())
        vl.addStretch()

        scroll.setWidget(body)
        return scroll

    # ── OK / CANCEL BAR ───────────────────────────────────────────────────
    def _build_button_bar(self):
        bar = QtWidgets.QWidget()
        bar.setStyleSheet("background:#222222; border-top:1px solid #3a3a3a;")
        bar.setFixedHeight(50)
        hl = QtWidgets.QHBoxLayout(bar)
        hl.setContentsMargins(16, 8, 16, 8)
        hl.setSpacing(8)
        hl.addStretch()

        self.btn_ok = QtWidgets.QPushButton("OK")
        self.btn_ok.setFixedWidth(90)
        self.btn_ok.setStyleSheet(self._BTN)
        self.btn_ok.setEnabled(False)   # only enabled after a successful build

        btn_cancel = QtWidgets.QPushButton("Cancel")
        btn_cancel.setFixedWidth(90)
        btn_cancel.setStyleSheet(self._BTN2)

        hl.addWidget(self.btn_ok)
        hl.addWidget(btn_cancel)

        self.btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        return bar

    # ── UI HELPERS ────────────────────────────────────────────────────────
    def _sec(self, text):
        lbl = QtWidgets.QLabel(text)
        lbl.setStyleSheet(self._SECT)
        return lbl

    def _row(self, label_text, widget):
        w = QtWidgets.QWidget()
        w.setStyleSheet(f"background:{self.BODY_BG};")
        hl = QtWidgets.QHBoxLayout(w)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(10)
        lbl = QtWidgets.QLabel(label_text)
        lbl.setFixedWidth(150)
        lbl.setStyleSheet(self._LBL)
        hl.addWidget(lbl)
        hl.addWidget(widget, 1)
        return w

    def _stat(self, text=""):
        lbl = QtWidgets.QLabel(text)
        lbl.setStyleSheet(self._STAT)
        lbl.setWordWrap(True)
        return lbl

    def _set_status(self, label: QtWidgets.QLabel, text: str, state: str = "idle"):
        """Update a status label text and background colour.

        Args:
            label: The QLabel to update.
            text:  Message to display (prefix is applied automatically).
            state: 'ok' | 'err' | 'idle'
        """
        prefix = {"ok": "✓ ", "err": "✕ ", "idle": "— "}.get(state, "— ")
        bg     = {"ok": STATUS_OK, "err": STATUS_ERR, "idle": STATUS_IDLE}.get(state, STATUS_IDLE)
        label.setText(prefix + text)
        label.setStyleSheet(
            f"QLabel{{color:#cccccc;font-size:10px;"
            f"background:{bg};border:1px solid #4a4a4a;padding:4px;"
            "border-radius:2px;word-wrap:true;}"
        )

    def _btn(self, text, primary=True):
        b = QtWidgets.QPushButton(text)
        b.setStyleSheet(self._BTN if primary else self._BTN2)
        return b

    def _field(self, text="", placeholder=""):
        f = QtWidgets.QLineEdit(text)
        f.setStyleSheet(self._FIELD)
        if placeholder:
            f.setPlaceholderText(placeholder)
        return f

    def _spin(self, val=1, lo=0, hi=9999):
        s = QtWidgets.QSpinBox()
        s.setMinimum(lo)
        s.setMaximum(hi)
        s.setValue(val)
        s.setStyleSheet(self._FIELD)
        return s

    def _combo(self, items):
        c = QtWidgets.QComboBox()
        c.addItems(items)
        c.setStyleSheet(self._FIELD)
        return c

    def _btn_row(self, *btns):
        w = QtWidgets.QWidget()
        w.setStyleSheet(f"background:{self.BODY_BG};")
        hl = QtWidgets.QHBoxLayout(w)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(8)
        for b in btns:
            hl.addWidget(b)
        hl.addStretch()
        return w

    # ── STEP 1 — FOLDER ───────────────────────────────────────────────────
    def _step1(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet(f"background:{self.BODY_BG};")
        vl = QtWidgets.QVBoxLayout(w)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(6)
        vl.addWidget(self._sec("━━  STEP 1 — FOLDER"))

        self.f_folder     = self._field(placeholder="Path to main folder containing sets…")
        btn_browse_folder = self._btn("Browse…", False)
        btn_browse_folder.setFixedWidth(90)
        folder_wrap = QtWidgets.QWidget()
        folder_wrap.setStyleSheet(f"background:{self.BODY_BG};")
        fw = QtWidgets.QHBoxLayout(folder_wrap)
        fw.setContentsMargins(0, 0, 0, 0)
        fw.setSpacing(6)
        fw.addWidget(self.f_folder, 1)
        fw.addWidget(btn_browse_folder)
        vl.addWidget(self._row("Main Folder", folder_wrap))
        btn_browse_folder.clicked.connect(self._browse_main_folder)
        self.f_folder.textChanged.connect(self._auto_populate_output_dir)

        self.btn_scout      = self._btn("Scout Folder")
        self.btn_scout_view = self._btn("View Scan Result…", False)
        vl.addWidget(self._btn_row(self.btn_scout, self.btn_scout_view))

        self.lbl_scout_status = self._stat()
        self._set_status(self.lbl_scout_status, "No scan run yet.")
        vl.addWidget(self.lbl_scout_status)

        self.btn_scout.clicked.connect(self._do_scout)
        self.btn_scout_view.clicked.connect(
            lambda: ScrollableReportWindow("Scan Result", self._scout_result_text).show())
        return w

    # ── STEP 2 — SELECT SETS ──────────────────────────────────────────────
    def _step2(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet(f"background:{self.BODY_BG};")
        vl = QtWidgets.QVBoxLayout(w)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(6)
        vl.addWidget(self._sec("━━  STEP 2 — SELECT SETS"))

        self.lbl_sel_info = self._stat()
        self._set_status(self.lbl_sel_info, "No sets selected yet.")
        vl.addWidget(self.lbl_sel_info)

        self.btn_pick_sets = self._btn("Choose Sets…")
        self.btn_clear_sel = self._btn("Clear Selection", False)
        vl.addWidget(self._btn_row(self.btn_pick_sets, self.btn_clear_sel))

        self.btn_pick_sets.clicked.connect(self._do_pick_sets)
        self.btn_clear_sel.clicked.connect(self._do_clear_selection)
        return w

    # ── STEP 3 — ANALYSE ──────────────────────────────────────────────────
    def _step3(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet(f"background:{self.BODY_BG};")
        vl = QtWidgets.QVBoxLayout(w)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(6)
        vl.addWidget(self._sec("━━  STEP 3 — ANALYSE"))

        self.btn_analyse     = self._btn("Analyse Selection")
        self.btn_report_view = self._btn("View Discrepancy Report…", False)
        vl.addWidget(self._btn_row(self.btn_analyse, self.btn_report_view))

        self.lbl_report_status = self._stat()
        self._set_status(self.lbl_report_status, "No analysis run yet.")
        vl.addWidget(self.lbl_report_status)

        self.btn_analyse.clicked.connect(self._do_analyse)
        self.btn_report_view.clicked.connect(
            lambda: ScrollableReportWindow("Discrepancy Report", self._report_text).show())
        return w

    # ── STEP 4 — CONFIGURE ────────────────────────────────────────────────
    def _step4(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet(f"background:{self.BODY_BG};")
        vl = QtWidgets.QVBoxLayout(w)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(6)
        vl.addWidget(self._sec("━━  STEP 4 — CONFIGURE"))

        # Resolution
        self.combo_res = self._combo(list(RESOLUTION_PRESETS.keys()))
        vl.addWidget(self._row("Resolution", self.combo_res))

        # Custom resolution — hidden unless Custom selected
        cw = QtWidgets.QWidget()
        cw.setStyleSheet(f"background:{self.BODY_BG};")
        chl = QtWidgets.QHBoxLayout(cw)
        chl.setContentsMargins(0, 0, 0, 0)
        chl.setSpacing(8)
        lw = QtWidgets.QLabel("Width (px)")
        lw.setStyleSheet(self._LBL)
        lw.setFixedWidth(150)
        self.spin_cw = self._spin(1920, 1, 16384)
        lh = QtWidgets.QLabel("Height (px)")
        lh.setStyleSheet(self._LBL)
        self.spin_ch = self._spin(1080, 1, 16384)
        chl.addWidget(lw)
        chl.addWidget(self.spin_cw)
        chl.addWidget(lh)
        chl.addWidget(self.spin_ch)
        chl.addStretch()
        self.w_custom_res = cw
        self.w_custom_res.setVisible(False)
        vl.addWidget(self.w_custom_res)
        self.combo_res.currentTextChanged.connect(
            lambda t: self.w_custom_res.setVisible(t == "Custom"))

        # Items per page
        self.spin_ipp = self._spin(12, 1, 200)
        vl.addWidget(self._row("Items Per Page", self.spin_ipp))

        # Color space — read dynamically from OCIO config
        cs_list = _get_colorspaces_static()
        self.combo_cs = self._combo(cs_list)
        if "scene_linear" in cs_list:
            self.combo_cs.setCurrentText("scene_linear")
        vl.addWidget(self._row("Color Space", self.combo_cs))

        # Missing frames
        self.combo_on_error = self._combo(ERROR_HANDLING_OPTIONS)
        vl.addWidget(self._row("Missing Frames", self.combo_on_error))

        # Output directory + Browse
        self.f_out_dir = self._field(placeholder="Output directory…")
        btn_browse = self._btn("Browse…", False)
        btn_browse.setFixedWidth(90)
        out_wrap = QtWidgets.QWidget()
        out_wrap.setStyleSheet(f"background:{self.BODY_BG};")
        ow = QtWidgets.QHBoxLayout(out_wrap)
        ow.setContentsMargins(0, 0, 0, 0)
        ow.setSpacing(6)
        ow.addWidget(self.f_out_dir, 1)
        ow.addWidget(btn_browse)
        vl.addWidget(self._row("Output Directory", out_wrap))
        btn_browse.clicked.connect(self._browse_out)

        # Prefix / suffix / extension
        self.f_prefix = self._field("cs")
        vl.addWidget(self._row("File Prefix", self.f_prefix))

        self.f_suffix = self._field("_Board")
        vl.addWidget(self._row("Page Suffix", self.f_suffix))

        self.combo_ext = self._combo(["png", "exr", "tiff", "jpg", "dpx"])
        vl.addWidget(self._row("File Extension", self.combo_ext))

        return w

    # ── LABEL OVERLAY ─────────────────────────────────────────────────────
    def _step_label(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet(f"background:{self.BODY_BG};")
        vl = QtWidgets.QVBoxLayout(w)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(6)
        vl.addWidget(self._sec("━━  LABEL OVERLAY"))

        self.chk_show_label = QtWidgets.QCheckBox("Show Layer Name")
        self.chk_show_label.setChecked(True)
        self.chk_show_label.setStyleSheet(self._CHK)
        vl.addWidget(self.chk_show_label)

        self.w_label_ctrl = QtWidgets.QWidget()
        self.w_label_ctrl.setStyleSheet(f"background:{self.BODY_BG};")
        lc = QtWidgets.QVBoxLayout(self.w_label_ctrl)
        lc.setContentsMargins(0, 0, 0, 0)
        lc.setSpacing(6)

        self.f_sep = self._field("_")
        self.f_sep.setMaximumWidth(60)
        lc.addWidget(self._row("Separator", self.f_sep))

        tk = QtWidgets.QWidget()
        tk.setStyleSheet(f"background:{self.BODY_BG};")
        tkl = QtWidgets.QHBoxLayout(tk)
        tkl.setContentsMargins(0, 0, 0, 0)
        tkl.setSpacing(8)
        l1 = QtWidgets.QLabel("Token From")
        l1.setStyleSheet(self._LBL)
        l1.setFixedWidth(150)
        self.spin_from = self._spin(2, 0, 99)
        l2 = QtWidgets.QLabel("To")
        l2.setStyleSheet(self._LBL)
        self.spin_to = self._spin(4, 0, 99)
        tkl.addWidget(l1)
        tkl.addWidget(self.spin_from)
        tkl.addWidget(l2)
        tkl.addWidget(self.spin_to)
        tkl.addStretch()
        lc.addWidget(tk)

        self.lbl_preview = self._stat()
        self._set_status(self.lbl_preview, "Scout a folder to see label preview.")
        lc.addWidget(self.lbl_preview)

        vl.addWidget(self.w_label_ctrl)

        self.chk_show_label.toggled.connect(self.w_label_ctrl.setVisible)
        self.f_sep.textChanged.connect(self._update_label_preview)
        self.spin_from.valueChanged.connect(self._update_label_preview)
        self.spin_to.valueChanged.connect(self._update_label_preview)

        return w

    # ── STEP 5 — BUILD ────────────────────────────────────────────────────
    def _step5(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet(f"background:{self.BODY_BG};")
        vl = QtWidgets.QVBoxLayout(w)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(6)
        vl.addWidget(self._sec("━━  STEP 5 — BUILD"))

        self.btn_build      = self._btn("Build Node Graph")
        self.btn_build_view = self._btn("View Build Log…", False)
        vl.addWidget(self._btn_row(self.btn_build, self.btn_build_view))

        self.lbl_build_status = self._stat()
        self._set_status(self.lbl_build_status, "Not built yet.")
        vl.addWidget(self.lbl_build_status)

        self.btn_build.clicked.connect(self._do_build)
        self.btn_build_view.clicked.connect(
            lambda: ScrollableReportWindow("Build Log", self._build_log_text).show())
        return w

    # ── SLOTS ─────────────────────────────────────────────────────────────
    def _browse_out(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Output Directory",
            self.f_out_dir.text() or os.path.expanduser("~"))
        if path:
            self.f_out_dir.setText(path)

    def _browse_main_folder(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Main Folder",
            self.f_folder.text() or os.path.expanduser("~"))
        if path:
            self.f_folder.setText(path)
            self._do_scout()  # auto-scout immediately on browse

    # ── PREFS ─────────────────────────────────────────────────────────────
    def _load_prefs(self):
        """Restore last-used settings from JSON file (silent on failure)."""
        try:
            if not os.path.exists(PREFS_PATH):
                return
            with open(PREFS_PATH, "r") as f:
                p = json.load(f)
            if p.get("main_folder"):    self.f_folder.setText(p["main_folder"])
            if p.get("out_dir"):        self.f_out_dir.setText(p["out_dir"])
            if p.get("prefix"):         self.f_prefix.setText(p["prefix"])
            if p.get("suffix"):         self.f_suffix.setText(p["suffix"])
            if p.get("separator"):      self.f_sep.setText(p["separator"])
            if p.get("resolution"):
                idx = self.combo_res.findText(p["resolution"])
                if idx >= 0:
                    self.combo_res.setCurrentIndex(idx)
            if p.get("custom_w"):       self.spin_cw.setValue(int(p["custom_w"]))
            if p.get("custom_h"):       self.spin_ch.setValue(int(p["custom_h"]))
            if p.get("items_per_page"): self.spin_ipp.setValue(int(p["items_per_page"]))
            if p.get("colorspace"):
                idx = self.combo_cs.findText(p["colorspace"])
                if idx >= 0:
                    self.combo_cs.setCurrentIndex(idx)
            if p.get("on_error"):
                idx = self.combo_on_error.findText(p["on_error"])
                if idx >= 0:
                    self.combo_on_error.setCurrentIndex(idx)
            if p.get("extension"):
                idx = self.combo_ext.findText(p["extension"])
                if idx >= 0:
                    self.combo_ext.setCurrentIndex(idx)
            if "show_label" in p:
                self.chk_show_label.setChecked(bool(p["show_label"]))
            if p.get("tok_from") is not None: self.spin_from.setValue(int(p["tok_from"]))
            if p.get("tok_to")   is not None: self.spin_to.setValue(int(p["tok_to"]))
            log.info("Prefs loaded.")
        except Exception as e:
            log.warning("Could not load prefs: %s", e)

    def _save_prefs(self):
        """Persist current settings to JSON file (silent on failure)."""
        try:
            os.makedirs(os.path.dirname(PREFS_PATH), exist_ok=True)
            p = {
                "main_folder":    self.f_folder.text().strip(),
                "out_dir":        self.f_out_dir.text().strip(),
                "prefix":         self.f_prefix.text().strip(),
                "suffix":         self.f_suffix.text().strip(),
                "separator":      self.f_sep.text().strip(),
                "resolution":     self.combo_res.currentText(),
                "custom_w":       self.spin_cw.value(),
                "custom_h":       self.spin_ch.value(),
                "items_per_page": self.spin_ipp.value(),
                "colorspace":     self.combo_cs.currentText(),
                "on_error":       self.combo_on_error.currentText(),
                "extension":      self.combo_ext.currentText(),
                "show_label":     self.chk_show_label.isChecked(),
                "tok_from":       self.spin_from.value(),
                "tok_to":         self.spin_to.value(),
            }
            with open(PREFS_PATH, "w") as f:
                json.dump(p, f, indent=2)
            log.info("Prefs saved.")
        except Exception as e:
            log.warning("Could not save prefs: %s", e)

    def _auto_populate_output_dir(self, folder_text: str):
        """Derive output dir from main folder — only if output field is empty or was auto-set."""
        folder = folder_text.strip()
        if not folder:
            return
        suggested = os.path.join(folder, "ContactSheet").replace("\\", "/")
        current   = self.f_out_dir.text().strip()
        if not current or current.endswith("/ContactSheet") or current.endswith("\\ContactSheet"):
            self.f_out_dir.setText(suggested)

    def _update_label_preview(self):
        if not self._scout_data:
            self._set_status(self.lbl_preview, "Scout a folder to see label preview.")
            return
        sample = None
        for s in self._scout_data:
            if s.sequences and s.sequences[0].file_pattern:
                sample = s.sequences[0].file_pattern
                break
        if not sample:
            self._set_status(self.lbl_preview, "No valid sequence found.", "err")
            return
        sep  = self.f_sep.text().strip() or "_"
        frm  = max(0, self.spin_from.value())
        to   = max(frm, self.spin_to.value())
        name = os.path.basename(os.path.dirname(sample)) or os.path.basename(sample)
        out  = _resolve_label_preview(name, sep, frm, to)
        if out:
            self._set_status(self.lbl_preview, f"Input: {name}  →  Label: {out}", "ok")
        else:
            self._set_status(self.lbl_preview,
                             f"Input: {name}  →  (empty — adjust token range)", "idle")

    def _do_scout(self):
        folder = self.f_folder.text().strip()
        if not folder or not os.path.isdir(folder):
            self._set_status(self.lbl_scout_status, "Folder not found.", "err")
            self._scout_result_text = "ERROR: folder not found."
            return
        try:
            self._scout_data = FolderScout(folder).scout()
        except Exception as e:
            self._set_status(self.lbl_scout_status, str(e), "err")
            self._scout_result_text = f"ERROR:\n{e}"
            log.exception("Scout failed.")
            return

        if not self._scout_data:
            self._set_status(self.lbl_scout_status,
                             "No sets found — check folder structure.", "err")
            self._scout_result_text = (
                "No sets found.\nExpected: main/ → set_folder/ → item_folder/ → frames")
            return

        lines = [f"Found {len(self._scout_data)} set(s):\n"]
        for s in self._scout_data:
            lines.append(f"  {s.name}  —  {s.sequence_count} item(s)")
            if s.sequences:
                sq = s.sequences[0]
                lines.append(
                    f"      frames {sq.first_frame}–{sq.last_frame}"
                    f"  step={sq.frame_step}  {sq.width}x{sq.height}")
        self._scout_result_text = "\n".join(lines)
        self._selected_sets = list(self._scout_data)
        self._set_status(
            self.lbl_scout_status,
            f"Found {len(self._scout_data)} set(s). Click 'View Scan Result…' for details.",
            "ok")
        self._set_status(
            self.lbl_sel_info,
            f"All {len(self._selected_sets)} set(s) auto-selected. Use 'Choose Sets…' to refine.",
            "ok")
        self._update_label_preview()

    def _do_pick_sets(self):
        if not self._scout_data:
            nuke.message("No sets available. Run 'Scout Folder' first.")
            return
        dlg = SetSelectionDialog(self._scout_data)
        if dlg.exec_():
            self._selected_sets = dlg.selected_sets()
            if self._selected_sets:
                self._set_status(
                    self.lbl_sel_info,
                    f"{len(self._selected_sets)} set(s) selected: "
                    + ", ".join(s.name for s in self._selected_sets),
                    "ok")
            else:
                self._set_status(self.lbl_sel_info, "No sets selected.", "err")

    def _do_clear_selection(self):
        self._selected_sets = []
        self._set_status(self.lbl_sel_info, "Selection cleared.")
        self._set_status(self.lbl_report_status, "")
        self._report_text = ""

    def _do_analyse(self):
        if not self._selected_sets:
            self._set_status(self.lbl_report_status, "No sets selected.", "err")
            return
        report = check_discrepancies(self._selected_sets)
        self._report_text = report.summary()
        if report.errors:
            self._set_status(
                self.lbl_report_status,
                f"{len(report.errors)} error(s), {len(report.warnings)} warning(s). "
                f"Click 'View Discrepancy Report…'",
                "err")
        elif report.warnings:
            self._set_status(
                self.lbl_report_status,
                f"{len(report.warnings)} warning(s). Click 'View Discrepancy Report…'",
                "idle")
        else:
            self._set_status(self.lbl_report_status, "No issues detected.", "ok")

    def _do_build(self):
        if not self._selected_sets:
            self._set_status(self.lbl_build_status, "No sets selected.", "err")
            return

        res_text = self.combo_res.currentText()
        if res_text == "Custom":
            cell_w, cell_h = self.spin_cw.value(), self.spin_ch.value()
        else:
            cell_w, cell_h = RESOLUTION_PRESETS.get(res_text, (1920, 1080))

        cfg                 = ContactSheetConfig()
        cfg.items_per_page  = self.spin_ipp.value()
        cfg.colorspace      = self.combo_cs.currentText()
        cfg.on_error        = self.combo_on_error.currentText()
        cfg.output_width    = cell_w
        cfg.output_height   = cell_h
        cfg.output_dir      = self.f_out_dir.text().strip() or "/tmp/contact_sheets"
        cfg.output_prefix   = self.f_prefix.text().strip() or "cs"
        cfg.output_suffix   = self.f_suffix.text().strip() or "_Board"
        cfg.output_ext      = self.combo_ext.currentText()
        cfg.show_label      = self.chk_show_label.isChecked()
        cfg.label_separator = self.f_sep.text().strip() or "_"
        cfg.label_tok_from  = max(0, self.spin_from.value())
        cfg.label_tok_to    = max(cfg.label_tok_from, self.spin_to.value())

        builder = NukeNodeBuilder(cfg)
        status  = []

        try:
            results = builder.build_all_sets(self._selected_sets)
            for set_name, writes in results.items():
                status.append(f"[OK]   '{set_name}'  →  {len(writes)} page(s) built.")
        except Exception as e:
            status.append(f"[ERR]  Build failed  →  {e}")
            log.exception("build_all_sets failed.")

        self._build_log_text = "\n".join(status)
        ok  = sum(1 for ln in status if ln.startswith("[OK]"))
        err = sum(1 for ln in status if ln.startswith("[ERR]"))

        if err > 0:
            self._set_status(
                self.lbl_build_status,
                f"Done: {ok} set(s) built, {err} error(s). Click 'View Build Log…'",
                "err")
        else:
            self._set_status(
                self.lbl_build_status,
                f"Done: {ok} set(s) built successfully. Click 'View Build Log…'",
                "ok")

        # Enable OK only if at least one set built without errors
        if ok > 0 and err == 0:
            self.btn_ok.setEnabled(True)

        self._save_prefs()


# ==============================================================================
# ENTRY POINT
# ==============================================================================

def launch():
    """Launch the PXLmentor Contact Sheet Generator."""
    if not PYSIDE_AVAILABLE:
        nuke.message(
            "PXLmentor Contact Sheet Generator requires PySide2 or PySide6.")
        return
    win = ContactSheetWindow()
    win.exec_()


if __name__ == "__main__":
    launch()
