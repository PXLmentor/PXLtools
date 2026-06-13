# Tool Name: PXLmentor Camera Matchmaker
# Version: 0.2.1-alpha
# Checkpoint: CP27
# Author: PXLmentor AI Pipeline TD
# Description: Interactive camera matching for Maya, inspired by fSpy.
#              Load a reference photo, draw axis lines, solve camera
#              FOV/rotation/position, and apply to a Maya camera with image plane.
# Changelog:
#   0.2.1-alpha - PXLtools branding pass: in-tool header logo swapped
#                 from PixelMentor_Logo_Long.png to PXLtools_logo.png.
#                 Fallback text label changed to "PXLtools".
#   0.2.0-alpha CP026 - Consistency: VP estimation upgraded from median-of-pairwise-
#              intersections (one bad line biased everything) to weighted least-squares
#              in homogeneous line coords. Status bar now reports per-axis angular fit
#              residual ('fit X 0.23° Z 0.41°') — values > 2° mean the lines don't
#              converge cleanly and the solve will be unreliable. Also warns on
#              implausible FOV (<20° or >110°).
#   0.2.0-alpha CP025 - UX revision: replaced the 'Load New…' toolbar button with a
#              small X overlay pinned to the top-right corner of the image canvas
#              (standard close-widget pattern). The canvas now also accepts dropped
#              image files directly — dropping a new image while one is already
#              loaded automatically clears lines/origin/ref before loading.
#   0.2.0-alpha CP024 - UX: 'Load New…' button unloads current image (and all lines/
#              origin/ref state) and prompts for a new reference photo. Creating a
#              camera now automatically switches the active 3D viewport to look
#              through it via `cmds.lookThru`.
#   0.2.0-alpha CP023 - REAL bug fixed: `_pixel_to_image_plane` had the wrong Y formula
#              (missing factor of 2) for wide images (and mirrored bug in X for tall).
#              It placed the image-plane origin at the bottom edge instead of the center,
#              so the solver's pixel-to-ray mapping DIDN'T match Maya's rendering — the
#              forward-projection diagnostic still read [OK] because it round-tripped
#              through the same wrong convention. Fix: derive the formula from scratch
#              (principal point at image center, longer side [-1,+1]).
#              Self-test now includes a Maya-independent cross-check that computes the
#              expected pixel via Maya's own pinhole-plus-gate math and compares to the
#              solver's projection — this catches this class of round-trip false-pass.
#              20/20 random poses: worst Maya-match pixel error = 0.000000px.
#   0.2.0-alpha CP022 - Complete rewrite of the solver following fSpy's exact algorithm
#              (ref: https://github.com/stuffmatic/fSpy, Guillou et al. 2000). All math
#              now runs in normalised Image Plane coordinates instead of pixels+focal_px.
#              Focal length via the Guillou perpendicular-foot formula; rotation matrix
#              built from column rays with proper axis assignment (VP1→X, VP2→Z, Y=Z×X).
#              `_estimate_position` now consumes R_ctw directly (no Euler reconstruction)
#              and FORWARD-PROJECTS world origin (0,0,0) back to the image, printing the
#              pixel delta vs. the origin marker — turns "camera looks wrong, keep guessing"
#              into a precise numeric verdict. Analytical self-test under __main__.
#   0.2.0-alpha CP021 - Auto-created image plane now sets displayMode=2 (visible overlay)
#              and fit=2 (horizontal fill). Previously the image plane was invisible in
#              viewport because displayMode was never set. Reverts fit=1 from CP019.
#   0.2.0-alpha CP020 - Height checkbox no longer forced ON (respects sidecar/default=off).
#              Position fallback when origin not set now uses image center via ray-cast
#              instead of tilt-only formula (correct for any pan/tilt/roll). Debug print
#              in Maya Script Editor shows computed camera position on each solve.
#   0.2.0-alpha CP019 - Film aperture fix: set camera horizontalFilmAperture=36mm and
#              verticalFilmAperture proportional to image aspect ratio. Image plane fit
#              changed to horizontal (fit=1) so FOV and image align exactly.
#              Fixes origin marker / world-origin misalignment when looking through camera.
#   0.2.0-alpha CP018 - Scene Data panel: Camera Height/Lens/Measurement Ref all optional,
#              off by default. Image plane alphaGain=0.5 on create. Lens override
#              uses 36mm full-frame sensor to compute focal_px from mm input.
#   0.2.0-alpha CP017 - Exact position solve: ray-cast from camera through origin pixel
#              to Y=0 ground plane using R_ctw = Rx(tilt)*Ry(pan)*Rz(roll). Replaces
#              first-order tilt-only approximation that ignored pan, roll, and origin Y.
#   0.2.0-alpha CP016 - Two-step sign resolution: negate d1 if VP_X is left of center,
#              then negate d2 if d3.y<0. Also fixed pan/tilt return order swap.
#   0.2.0-alpha CP015 - Fixed flip axis: negate d2 (world Z) not d1 (world X) when d3.y<0.
#              Depth lines go into scene = world -Z, so d2 from VP is inverted.
#   0.2.0-alpha CP014 - Complete math rewrite: fixed camera convention (-Z forward),
#              corrected XYZ Euler matrix element extraction, position now uses
#              solved tilt angle directly instead of re-deriving from VPs.
#   0.2.0-alpha CP013 - Grid rewritten as VP-fan (always works regardless of camera angle).
#              Added Clear All toolbar button — wipes lines/origin/ref, keeps image.
#              Backup files now named with CP number (e.g. _CP012.py) not timestamp.
#   0.2.0-alpha CP012 - Real-time perspective floor grid overlay on canvas.
#              Updates live as axis lines are moved. Toggle button in toolbar.
#              Grid uses the solved camera matrix to project a true 3D floor
#              plane — X lines (red) and Z lines (blue) match axis colors.
#   0.2.0-alpha CP011 - Restructured Output section into Apply/Verify tabs.
#              ADD IMAGE PLANE and APPLY TO CAMERA moved inside Apply tab.
#              Add image plane checkbox (on by default) next to CREATE NEW CAMERA.
#              Verify Camera Match section moved to dedicated Verify tab.
#   0.2.0-alpha CP010 - Fixed FOV setAttr crash: horizontalFieldOfView is a computed
#              attribute in Maya and must be set via cmds.camera(shape, edit=True,
#              horizontalFieldOfView=fov) — not cmds.setAttr. Applies to both
#              _apply_solve_to and _create_camera.
#   0.2.0-alpha CP009 - Auto-save sidecar on every change (debounced 500ms timer).
#              Sidecar is always current so drag-and-drop reload restores setup.
#   0.2.0-alpha CP008 - Removed redundant Load Image button (drag-and-drop covers it).
#   0.2.0-alpha CP007 - Save/load line setup as JSON sidecar (.matchmaker.json) next to image.
#              Auto-restores on image load when sidecar exists.
#              Loupe zoom now active during Set Origin placement.
#   0.2.0-alpha CP006 - Fixed create-camera crash: apply all setAttr calls BEFORE
#              cmds.rename() so the original camera1/cameraShape1 names are used.
#              No listRelatives lookup needed after rename — fully reliable.
#   0.2.0-alpha CP005 - Fixed create-camera crash: all listRelatives calls now use
#              fullPath=True so shape names are unambiguous after cmds.rename().
#   0.2.0-alpha CP004 - Removed QScrollArea; dialog sizes to content via SetMinimumSize.
#              Canvas minimum height reduced to 300px (fits 1080p).
#              Reads Maya scene units (cmds.currentUnit) and shows them in all spinboxes.
#              Added missing camera height input in Output section.
#   0.2.0-alpha CP003 - Fixed create-camera crash (shape lookup after rename).
#              Added scene origin marker (click-to-set on canvas, used in position estimate).
#              Added Place Test Object button (locator + cube at origin for match verification).
#   0.2.0-alpha CP002 - Instructions section renamed to match suite ("Instructions" not "How To Use").
#              Scale Reference + Output start collapsed so canvas is visible on open.
#              Minimum window height raised to 960 to guarantee canvas visibility.
#   0.2.0-alpha CP001 - Feature pack:
#              Zoom magnifier loupe on handle drag.
#              X/Y/Z axis naming with Maya axis colors (red/green/blue).
#              Drag-and-drop image loading onto canvas.
#              Scale reference line for real-world scene scale calibration.
#              Create New Camera from solve result (does not overwrite persp).
#              Improved always-visible step guide and axis legend strip.
#              Window sized to show all controls without scrolling.
#   0.1.0-alpha CP003 - Fixed launch crash: toolbar buttons connected to self._canvas
#              before canvas was created — changed to lambdas.
#   0.1.0-alpha CP002 - Fixed singleton guard: moved from __init__ to run() so
#              the dialog is always fully initialized before show() is called.
#   0.1.0-alpha CP001 - Initial implementation.

import json
import logging
import math
import os

import maya.cmds as cmds

from PySide6 import QtCore, QtGui, QtWidgets

logger = logging.getLogger(__name__)

WINDOW_OBJECT_NAME = "PXLmentorCameraMatchmaker"
VERSION = "0.2.0-alpha CP026"
_IMAGE_EXTENSIONS = "Images (*.jpg *.jpeg *.png *.tif *.tiff *.bmp *.exr *.hdr)"
_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".exr", ".hdr"}


# ---------------------------------------------------------------------------
# Color tokens
# ---------------------------------------------------------------------------

class _C:
    BG_DARK         = "#333333"
    BG_WINDOW       = "#464646"
    BG_SECTION_HDR  = "#393939"
    BG_SECTION_BOD  = "#4a4a4a"
    BG_INPUT        = "#3a3a3a"
    BG_HEADER       = "#0D1F24"
    BORDER          = "#2b2b2b"
    ORANGE          = "#E8820C"
    TEXT_PRIMARY    = "#dcdcdc"
    TEXT_MUTED      = "#b0b0b0"
    STATUS_OK_BG    = "#2a402a"
    STATUS_OK_TEXT  = "#7acc7a"
    STATUS_ERR_BG   = "#4a3030"
    STATUS_ERR_TEXT = "#e07070"
    INFO_BG         = "#2a2a3a"
    INFO_TEXT       = "#9090c0"
    # Maya axis colors
    AX_X            = "#FF4040"   # world X — red
    AX_Y            = "#40CC40"   # world Y — green
    AX_Z            = "#4080FF"   # world Z — blue
    REF_COLOR       = "#FFD040"   # scale reference — gold


MAIN_QSS = """
QDialog, QWidget {
    background: #464646;
    color: #dcdcdc;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
}
QFrame#collapsibleBody {
    background: #4a4a4a; border: 1px solid #2b2b2b;
    border-top: 1px solid #3a3a3a; border-radius: 0 0 3px 3px;
}
QFrame#sectionFrame {
    background: #4a4a4a; border: 1px solid #2b2b2b;
    border-top: 1px solid #3a3a3a; border-radius: 0 0 3px 3px;
}
QScrollBar:vertical { background: #3a3a3a; width: 8px; }
QScrollBar::handle:vertical { background: #606060; border-radius: 4px; }
QScrollBar:horizontal { background: #3a3a3a; height: 8px; }
QScrollBar::handle:horizontal { background: #606060; border-radius: 4px; }
QPushButton {
    background: #555555; color: #dcdcdc;
    border: 1px solid #2b2b2b; border-radius: 3px;
    font-size: 12px; font-weight: bold; letter-spacing: 0.8px;
    padding: 0 14px; min-height: 34px;
}
QPushButton:hover { background: #606060; color: #f0f0f0; }
QPushButton:pressed { background: #404040; }
QPushButton:disabled { background: #404040; color: #686868; border-color: #333333; }
QPushButton#btnPrimary {
    background: #E8820C; color: white; border: none;
    font-size: 13px; letter-spacing: 1.2px; min-height: 42px;
}
QPushButton#btnPrimary:hover { background: #f09020; }
QPushButton#btnPrimary:pressed { background: #c06008; }
QPushButton#btnPrimary:disabled { background: #5a4000; color: #9a7020; }
QPushButton#btnSmall {
    background: #505050; color: #c0c0c0;
    border: 1px solid #3a3a3a; border-radius: 2px;
    font-size: 11px; font-weight: bold; letter-spacing: 0.5px;
    padding: 0 10px; min-height: 24px; max-height: 24px;
}
QPushButton#btnSmall:hover { background: #606060; color: #f0f0f0; }
QPushButton#btnSmall:pressed { background: #3a3a3a; }
QPushButton#btnAxisX {
    background: #5a2020; color: #ff9090; border: 1px solid #8a3030;
    font-size: 11px; font-weight: bold; letter-spacing: 0.5px;
    padding: 0 10px; min-height: 24px; max-height: 24px; border-radius: 2px;
}
QPushButton#btnAxisX:checked { background: #FF4040; color: white; border-color: #FF4040; }
QPushButton#btnAxisX:hover:!checked { background: #703030; }
QPushButton#btnAxisY {
    background: #205020; color: #80e080; border: 1px solid #307830;
    font-size: 11px; font-weight: bold; letter-spacing: 0.5px;
    padding: 0 10px; min-height: 24px; max-height: 24px; border-radius: 2px;
}
QPushButton#btnAxisY:checked { background: #40CC40; color: #0a200a; border-color: #40CC40; }
QPushButton#btnAxisY:hover:!checked { background: #306030; }
QPushButton#btnAxisZ {
    background: #203050; color: #90b0e0; border: 1px solid #304880;
    font-size: 11px; font-weight: bold; letter-spacing: 0.5px;
    padding: 0 10px; min-height: 24px; max-height: 24px; border-radius: 2px;
}
QPushButton#btnAxisZ:checked { background: #4080FF; color: white; border-color: #4080FF; }
QPushButton#btnAxisZ:hover:!checked { background: #304070; }
QPushButton#btnAxisRef {
    background: #4a4020; color: #ffd080; border: 1px solid #6a6030;
    font-size: 11px; font-weight: bold; letter-spacing: 0.5px;
    padding: 0 10px; min-height: 24px; max-height: 24px; border-radius: 2px;
}
QPushButton#btnAxisRef:checked { background: #FFD040; color: #1a1400; border-color: #FFD040; }
QPushButton#btnAxisRef:hover:!checked { background: #5a5030; }
QLabel#statusOk {
    background: #2a402a; color: #7acc7a;
    border: 1px solid #3a5a3a; border-radius: 2px;
    padding: 5px 10px; font-size: 11px;
}
QLabel#statusIdle {
    background: #404040; color: #888888;
    border: 1px solid #333333; border-radius: 2px;
    padding: 5px 10px; font-size: 11px;
}
QLabel#statusErr {
    background: #4a3030; color: #e07070;
    border: 1px solid #6a3a3a; border-radius: 2px;
    padding: 5px 10px; font-size: 11px;
}
QLabel#statusWarn {
    background: #463a20; color: #e8c060;
    border: 1px solid #6a5030; border-radius: 2px;
    padding: 5px 10px; font-size: 11px;
}
QLabel#infoLabel {
    background: #2a2a3a; color: #9090c0;
    border: 1px solid #3a3a5a; border-radius: 2px;
    padding: 5px 10px; font-size: 11px;
}
QLabel#ctrlLabel { color: #aaaaaa; font-size: 11px; font-weight: bold; letter-spacing: 1.5px; }
QLabel#hint { color: #888888; font-size: 11px; }
QLabel#solveVal {
    color: #E8820C; font-size: 14px; font-weight: bold;
    background: transparent; letter-spacing: 0.5px;
}
QLabel#solveKey { color: #888888; font-size: 11px; background: transparent; }
QLineEdit, QDoubleSpinBox, QSpinBox {
    background: #3a3a3a; color: #dcdcdc;
    border: 1px solid #2b2b2b; border-radius: 2px;
    padding: 2px 6px; font-size: 12px;
}
QComboBox {
    background: #3a3a3a; color: #dcdcdc;
    border: 1px solid #2b2b2b; border-radius: 2px;
    padding: 2px 8px; font-size: 12px; min-height: 26px;
}
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView { background: #3a3a3a; color: #dcdcdc; selection-background-color: #E8820C; }
QCheckBox { color: #dcdcdc; font-size: 12px; spacing: 8px; }
QCheckBox:hover { color: #ffffff; }
QCheckBox::indicator {
    width: 16px; height: 16px; border-radius: 2px;
    background: #3a3a3a; border: 1px solid #2b2b2b;
}
QCheckBox::indicator:hover { background: #484848; border-color: #888888; }
QCheckBox::indicator:checked { background: #E8820C; border: 1px solid #c06000; }
QCheckBox::indicator:checked:hover { background: #f09020; border-color: #E8820C; }
QCheckBox:disabled { color: #686868; }
QCheckBox::indicator:disabled { background: #404040; border-color: #333333; }
QFrame#divider { background: #2b2b2b; border: none; max-height: 1px; min-height: 1px; }
QPushButton#btnOrigin {
    background: #3a3040; color: #c0a0e0; border: 1px solid #5a4870;
    font-size: 11px; font-weight: bold; letter-spacing: 0.5px;
    padding: 0 10px; min-height: 24px; max-height: 24px; border-radius: 2px;
}
QPushButton#btnOrigin:checked { background: #9060d0; color: white; border-color: #9060d0; }
QPushButton#btnOrigin:hover:!checked { background: #4a3a60; }
QGraphicsView {
    background: #1a1a1a; border: 1px solid #2b2b2b; border-radius: 2px;
}
"""


# ---------------------------------------------------------------------------
# Pure geometry helpers
# ---------------------------------------------------------------------------

def _line_intersect(p1, p2, p3, p4):
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-10:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def _compute_vp(lines):
    """Weighted least-squares vanishing point.

    Each line through (x1,y1)-(x2,y2) has the homogeneous equation a*x + b*y + c = 0
    with a = y2-y1, b = x1-x2, c = x2*y1 - x1*y2.  The VP V=(vx,vy) minimises
        sum_i w_i * (a_i*vx + b_i*vy + c_i)^2  /  (a_i^2 + b_i^2)
    where w_i = line length (longer lines = more reliable).  Normalising by the
    line's squared coefficient magnitude makes the residual a true pixel distance.

    This replaces the old median-of-pairwise-intersections which was unstable —
    a single mis-drawn line contaminated N-1 pairs and biased the result.
    """
    if len(lines) < 2:
        return None
    S_aa = S_ab = S_bb = S_ac = S_bc = 0.0
    used = 0
    for (x1, y1), (x2, y2) in lines:
        a = y2 - y1
        b = x1 - x2
        c = x2 * y1 - x1 * y2
        norm_sq = a * a + b * b
        if norm_sq < 1e-12:
            continue  # degenerate zero-length line
        length = math.sqrt(norm_sq)
        # weight = length / norm_sq = 1 / length   (so residual scales as pixel distance)
        w = 1.0 / length
        S_aa += w * a * a
        S_ab += w * a * b
        S_bb += w * b * b
        S_ac += w * a * c
        S_bc += w * b * c
        used += 1
    if used < 2:
        return None
    # Solve 2x2 system: [[S_aa, S_ab], [S_ab, S_bb]] [vx, vy]^T = [-S_ac, -S_bc]^T
    det = S_aa * S_bb - S_ab * S_ab
    if abs(det) < 1e-10:
        return None  # lines all near-parallel in the normal direction → VP at infinity
    vx = (-S_ac * S_bb + S_bc * S_ab) / det
    vy = (-S_bc * S_aa + S_ac * S_ab) / det
    return (vx, vy)


def _vp_fit_error_deg(lines, vp):
    """Mean angular deviation (degrees) between each line's drawn direction and
    the direction from that line's midpoint to the VP.  < 0.5° = excellent fit;
    > 2° = one or more lines are badly placed.
    """
    if vp is None or len(lines) < 1:
        return None
    vx, vy = vp
    total = 0.0
    n = 0
    for (x1, y1), (x2, y2) in lines:
        dx = x2 - x1
        dy = y2 - y1
        dl = math.sqrt(dx * dx + dy * dy)
        if dl < 1e-6:
            continue
        dx /= dl; dy /= dl
        mx = (x1 + x2) * 0.5
        my = (y1 + y2) * 0.5
        vdx = vx - mx
        vdy = vy - my
        vl = math.sqrt(vdx * vdx + vdy * vdy)
        if vl < 1e-6:
            continue
        vdx /= vl; vdy /= vl
        # Absolute angle between the two directions (line is symmetric, so |dot|)
        dot = abs(dx * vdx + dy * vdy)
        dot = max(-1.0, min(1.0, dot))
        total += math.degrees(math.acos(dot))
        n += 1
    return total / n if n else None


# ─────────────────────────────────────────────────────────────────────────────
# Solver (CP022): fSpy-exact 2-VP camera calibration.
# Reference: https://github.com/stuffmatic/fSpy/blob/develop/src/gui/solver/solver.ts
# Paper:     Guillou, Meneveaux, Maisel, Bouatouch (2000).
# All solver math runs in fSpy's "Image Plane" frame:
#   - origin at principal point (image center)
#   - Y axis flipped vs. pixel coords (Y-up)
#   - normalised so the LONGER image side spans [-1, +1]
# Camera space is Maya-standard: +X right, +Y up, -Z forward.
# ─────────────────────────────────────────────────────────────────────────────

def _normalize3(v):
    l = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    if l < 1e-12:
        return (0.0, 0.0, 1.0)
    return (v[0] / l, v[1] / l, v[2] / l)


def _cross3(a, b):
    return (a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0])


def _pixel_to_image_plane(px, py, w, h):
    """Scene pixel (Y-down, top-left origin) → Image Plane coords (Y-up, principal
    point at image CENTER, longer side spans [-1, +1]).

    CP023 fix: the previous formula was missing a factor of 2 on the Y term for wide
    images (and X term for tall), which placed the "origin" at the bottom edge instead
    of the center. Mathematically equivalent to the old code under round-trip (hence
    the self-test passed) but mismatched Maya's pixel-to-camera-ray mapping.

    Verified: principal point (w/2, h/2) → (0, 0).  Corners → (±1, ±h/w) for wide.
    """
    if w >= h:   # wide: long side horizontal, x ∈ [-1,+1], y ∈ [-h/w, +h/w]
        return (2.0 * px / w - 1.0, (h - 2.0 * py) / w)
    else:        # tall: long side vertical, y ∈ [-1,+1], x ∈ [-w/h, +w/h]
        return ((2.0 * px - w) / h, 1.0 - 2.0 * py / h)


def _image_plane_to_pixel(x_ip, y_ip, w, h):
    """Inverse of _pixel_to_image_plane."""
    if w >= h:
        px = (x_ip + 1.0) * w / 2.0
        py = (h - y_ip * w) / 2.0
    else:
        px = (x_ip * h + w) / 2.0
        py = (1.0 - y_ip) * h / 2.0
    return (px, py)


def _compute_focal_relative(Fu, Fv, P=(0.0, 0.0)):
    """Guillou 2000 §3.2 — focal length in Image Plane units from two orthogonal VPs.

    Returns None if the VPs are degenerate or on the same side of the principal point
    (dot product positive ⇒ no real solution).
    """
    dx, dy = Fu[0] - Fv[0], Fu[1] - Fv[1]
    d = math.sqrt(dx*dx + dy*dy)
    if d < 1e-10:
        return None
    dir_uv = (dx / d, dy / d)
    FvP = (P[0] - Fv[0], P[1] - Fv[1])
    proj = dir_uv[0] * FvP[0] + dir_uv[1] * FvP[1]
    Puv = (proj * dir_uv[0] + Fv[0], proj * dir_uv[1] + Fv[1])
    PPuv  = math.sqrt((P[0]  - Puv[0])**2 + (P[1]  - Puv[1])**2)
    FvPuv = math.sqrt((Fv[0] - Puv[0])**2 + (Fv[1] - Puv[1])**2)
    FuPuv = math.sqrt((Fu[0] - Puv[0])**2 + (Fu[1] - Puv[1])**2)
    f_sq = FvPuv * FuPuv - PPuv * PPuv
    return math.sqrt(f_sq) if f_sq > 0 else None


def _compute_fov_deg_from_frel(f_rel, w, h):
    """Horizontal FOV in degrees from relative focal length."""
    if w >= h:
        return math.degrees(2.0 * math.atan(1.0 / f_rel))
    else:
        return math.degrees(2.0 * math.atan((h / w) / f_rel))


def _compute_camera_rotation(Fu, Fv, f_rel):
    """fSpy §3.3 — returns camera-to-world rotation matrix R_ctw as a 3x3 list of lists.

    VP1 → world +X, VP2 → world +Z. World +Y derived by Y = Z × X (right-hand world).
    Two-step sign resolution ensures world +Y points up in camera space and world +X
    lies in the camera's right hemisphere (the typical indoor-photography assumption).
    Returns None on degenerate input.
    """
    # Rays from camera origin to VPs in camera space (image plane at z = -f_rel,
    # principal point at origin so no (px - cx) offset).
    ofu_mag = math.sqrt(Fu[0]*Fu[0] + Fu[1]*Fu[1] + f_rel*f_rel)
    ofv_mag = math.sqrt(Fv[0]*Fv[0] + Fv[1]*Fv[1] + f_rel*f_rel)
    if ofu_mag < 1e-12 or ofv_mag < 1e-12:
        return None
    u = (Fu[0] / ofu_mag, Fu[1] / ofu_mag, -f_rel / ofu_mag)  # world +X in cam
    v = (Fv[0] / ofv_mag, Fv[1] / ofv_mag, -f_rel / ofv_mag)  # world +Z in cam

    def _build(u_in, v_in):
        y = _cross3(v_in, u_in)                 # world +Y in cam = Z × X
        ym = math.sqrt(y[0]*y[0] + y[1]*y[1] + y[2]*y[2])
        if ym < 1e-10:
            return None, None
        y = (y[0]/ym, y[1]/ym, y[2]/ym)
        # Camera-to-world: rows = world axes expressed in camera space
        return y, [list(u_in), list(y), list(v_in)]

    y, R = _build(u, v)
    if y is None:
        return None

    # Of the four possible (±u, ±v) sign choices, only one yields the physically
    # correct R_ctw. Constraints: (1) world +Y points up in camera (y[1] > 0),
    # and (2) world +X lies in the camera's right hemisphere (u[0] > 0).
    #
    # Step 1: flip JUST v to satisfy (1) — this negates y = cross(v,u), flipping y[1].
    # Step 2: if u[0] still < 0, flip BOTH u AND v (which preserves y = cross(v,u)
    #         because cross(-v,-u) = cross(v,u)). Flipping u alone would re-invert y.

    if y[1] < 0:
        v = (-v[0], -v[1], -v[2])
        y, R = _build(u, v)
        if y is None:
            return None

    if R[0][0] < 0:
        u = (-u[0], -u[1], -u[2])
        v = (-v[0], -v[1], -v[2])
        y, R = _build(u, v)
        if y is None:
            return None

    return R


def _maya_xyz_euler_from_rctw(R):
    """Standard XYZ intrinsic Euler decomposition for Maya's default rotate order.
       R = Rx(rx) * Ry(ry) * Rz(rz).  Returns (rx, ry, rz) in degrees.
    """
    sin_b = max(-1.0, min(1.0, R[0][2]))
    ry = math.asin(sin_b)
    if abs(math.cos(ry)) > 1e-6:
        rx = math.atan2(-R[1][2], R[2][2])
        rz = math.atan2(-R[0][1], R[0][0])
    else:  # gimbal lock at ry = ±90°
        rx = math.atan2(R[2][1], R[1][1])
        rz = 0.0
    return (math.degrees(rx), math.degrees(ry), math.degrees(rz))


def _project_world_point(world_pt, cam_pos, R_ctw, f_rel, w, h):
    """Forward-project a world-space point to a scene pixel.
       Returns (px, py) in scene pixel coords, or None if the point is at/behind the camera.
       This is the keystone verification of CP022: applying it to (0,0,0) should yield
       exactly the origin-marker pixel when the solve is correct.
    """
    rel = (world_pt[0] - cam_pos[0],
           world_pt[1] - cam_pos[1],
           world_pt[2] - cam_pos[2])
    # p_cam = R_wtc @ rel = R_ctw^T @ rel → p_cam[i] = sum_j R_ctw[j][i] * rel[j]
    p_cam = (
        R_ctw[0][0]*rel[0] + R_ctw[1][0]*rel[1] + R_ctw[2][0]*rel[2],
        R_ctw[0][1]*rel[0] + R_ctw[1][1]*rel[1] + R_ctw[2][1]*rel[2],
        R_ctw[0][2]*rel[0] + R_ctw[1][2]*rel[1] + R_ctw[2][2]*rel[2],
    )
    if p_cam[2] >= -1e-9:  # at or behind camera
        return None
    x_ip = f_rel * p_cam[0] / (-p_cam[2])
    y_ip = f_rel * p_cam[1] / (-p_cam[2])
    return _image_plane_to_pixel(x_ip, y_ip, w, h)


def _clip_ray_to_rect(px, py, dx, dy, rect_w, rect_h):
    t_vals = []
    eps = 1e-9
    if abs(dx) > eps:
        t_vals.append((0 - px) / dx)
        t_vals.append((rect_w - px) / dx)
    if abs(dy) > eps:
        t_vals.append((0 - py) / dy)
        t_vals.append((rect_h - py) / dy)
    pts = []
    for t in t_vals:
        x = px + t * dx; y = py + t * dy
        if -1 <= x <= rect_w + 1 and -1 <= y <= rect_h + 1:
            pts.append((x, y))
    pts = sorted(set((round(x, 1), round(y, 1)) for x, y in pts))
    if len(pts) < 2:
        return None
    return pts[0], pts[-1]


# ---------------------------------------------------------------------------
# CollapsibleSection
# ---------------------------------------------------------------------------

class CollapsibleSection:
    def __init__(self, title, parent=None, compact=False, start_collapsed=False):
        self._collapsed = False
        self._compact = compact
        self._container = QtWidgets.QWidget(parent)
        self._container.setObjectName("collapsibleContainer")
        outer = QtWidgets.QVBoxLayout(self._container)
        outer.setContentsMargins(0, 0, 0, 2)
        outer.setSpacing(0)

        self._header = QtWidgets.QFrame()
        self._header.setFixedHeight(26 if compact else 38)
        self._header.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self._header.setStyleSheet(
            "QFrame { background: #393939; border: 1px solid #2b2b2b; "
            "border-bottom: none; border-radius: 3px 3px 0 0; }"
        )
        hbox = QtWidgets.QHBoxLayout(self._header)
        hbox.setContentsMargins(10, 0, 10, 0)
        hbox.setSpacing(6)

        asiz = "11px" if compact else "16px"
        self._arrow = QtWidgets.QLabel("▾")
        self._arrow.setStyleSheet(f"color: #E8820C; font-size: {asiz}; background: transparent;")
        hbox.addWidget(self._arrow)

        tsiz = "9px" if compact else "12px"
        lbl = QtWidgets.QLabel(title.upper())
        lbl.setStyleSheet(
            f"color: #dcdcdc; font-weight: bold; font-size: {tsiz}; "
            "letter-spacing: 1px; background: transparent;"
        )
        hbox.addWidget(lbl)
        hbox.addStretch()
        outer.addWidget(self._header)

        self._body = QtWidgets.QFrame()
        self._body.setObjectName("collapsibleBody")
        self._body_layout = QtWidgets.QVBoxLayout(self._body)
        if compact:
            self._body_layout.setContentsMargins(6, 5, 6, 7)
            self._body_layout.setSpacing(3)
        else:
            self._body_layout.setContentsMargins(10, 10, 10, 12)
            self._body_layout.setSpacing(6)
        outer.addWidget(self._body)

        self._header.mousePressEvent = lambda _e: self.set_collapsed(not self._collapsed)
        if start_collapsed:
            self.set_collapsed(True)

    @property
    def widget(self): return self._container
    @property
    def body_layout(self): return self._body_layout
    def add_widget(self, w): self._body_layout.addWidget(w)
    def add_layout(self, lay): self._body_layout.addLayout(lay)
    def add_spacing(self, n): self._body_layout.addSpacing(n)

    def set_collapsed(self, collapsed):
        self._collapsed = collapsed
        self._body.setVisible(not collapsed)
        asiz = "11px" if self._compact else "16px"
        if collapsed:
            self._arrow.setText("▸")
            self._header.setStyleSheet(
                "QFrame { background: #3a3a3a; border: 1px solid #2b2b2b; border-radius: 3px; }"
            )
            self._arrow.setStyleSheet(f"color: #888888; font-size: {asiz}; background: transparent;")
        else:
            self._arrow.setText("▾")
            self._header.setStyleSheet(
                "QFrame { background: #393939; border: 1px solid #2b2b2b; "
                "border-bottom: none; border-radius: 3px 3px 0 0; }"
            )
            self._arrow.setStyleSheet(f"color: #E8820C; font-size: {asiz}; background: transparent;")
        self._container.updateGeometry()


# ---------------------------------------------------------------------------
# Canvas graphics items
# ---------------------------------------------------------------------------

class VPHandle(QtWidgets.QGraphicsEllipseItem):
    RADIUS = 6

    def __init__(self, x, y, color, on_moved_cb):
        r = self.RADIUS
        super().__init__(-r, -r, r * 2, r * 2)
        self._on_moved = on_moved_cb
        pen = QtGui.QPen(QtGui.QColor(color), 1.5)
        brush = QtGui.QBrush(QtGui.QColor(color).darker(150))
        self.setPen(pen)
        self.setBrush(brush)
        self.setPos(x, y)
        self.setFlags(
            QtWidgets.QGraphicsItem.ItemIsMovable |
            QtWidgets.QGraphicsItem.ItemSendsGeometryChanges |
            QtWidgets.QGraphicsItem.ItemIgnoresTransformations
        )
        self.setCursor(QtCore.Qt.SizeAllCursor)
        self.setZValue(10)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
            if self._on_moved:
                self._on_moved()
        return super().itemChange(change, value)


class VPLineItem:
    def __init__(self, scene, x1, y1, x2, y2, color, on_changed_cb, img_w, img_h):
        self._scene = scene
        self._color = color
        self._on_changed = on_changed_cb
        self._img_w = img_w
        self._img_h = img_h

        qc = QtGui.QColor(color)
        pen_main = QtGui.QPen(qc, 2.0, QtCore.Qt.SolidLine)
        pen_guide = QtGui.QPen(QtGui.QColor(qc.red(), qc.green(), qc.blue(), 90), 1.0, QtCore.Qt.DashLine)

        self._line = QtWidgets.QGraphicsLineItem(x1, y1, x2, y2)
        self._line.setPen(pen_main)
        self._line.setZValue(2)
        scene.addItem(self._line)

        self._guide = QtWidgets.QGraphicsLineItem(x1, y1, x2, y2)
        self._guide.setPen(pen_guide)
        self._guide.setZValue(1)
        scene.addItem(self._guide)

        self._h1 = VPHandle(x1, y1, color, self._handle_moved)
        self._h2 = VPHandle(x2, y2, color, self._handle_moved)
        scene.addItem(self._h1)
        scene.addItem(self._h2)

        self._update_graphics()

    def _handle_moved(self):
        self._update_graphics()
        if self._on_changed:
            self._on_changed()

    def _update_graphics(self):
        p1 = self._h1.pos(); p2 = self._h2.pos()
        self._line.setLine(p1.x(), p1.y(), p2.x(), p2.y())
        dx = p2.x() - p1.x(); dy = p2.y() - p1.y()
        clipped = _clip_ray_to_rect(p1.x(), p1.y(), dx, dy, self._img_w, self._img_h)
        if clipped:
            self._guide.setLine(clipped[0][0], clipped[0][1], clipped[1][0], clipped[1][1])
            self._guide.setVisible(True)
        else:
            self._guide.setVisible(False)

    def endpoints(self):
        p1 = self._h1.pos(); p2 = self._h2.pos()
        return ((p1.x(), p1.y()), (p2.x(), p2.y()))

    def px_length(self):
        p1 = self._h1.pos(); p2 = self._h2.pos()
        return math.sqrt((p2.x() - p1.x())**2 + (p2.y() - p1.y())**2)

    def set_second_endpoint(self, x, y):
        self._h2.setPos(x, y)
        self._update_graphics()

    def update_image_size(self, w, h):
        self._img_w = w; self._img_h = h
        self._update_graphics()

    def remove(self):
        for item in (self._line, self._guide, self._h1, self._h2):
            self._scene.removeItem(item)


class VPMarker(QtWidgets.QGraphicsItem):
    SIZE = 14

    def __init__(self, color):
        super().__init__()
        self._pen = QtGui.QPen(QtGui.QColor(color), 2.5)
        self.setZValue(20)
        self.setVisible(False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)

    def boundingRect(self):
        s = self.SIZE
        return QtCore.QRectF(-s, -s, s * 2, s * 2)

    def paint(self, painter, option, widget=None):
        s = self.SIZE
        painter.setPen(self._pen)
        painter.drawLine(-s, -s, s, s)
        painter.drawLine(s, -s, -s, s)


# ---------------------------------------------------------------------------
# OriginMarker — scene-origin crosshair drawn on the canvas
# ---------------------------------------------------------------------------

class OriginMarker(QtWidgets.QGraphicsItem):
    SIZE = 14

    def __init__(self):
        super().__init__()
        self._color = QtGui.QColor("#9060d0")
        self.setZValue(25)
        self.setVisible(False)

    def boundingRect(self):
        s = self.SIZE + 10
        return QtCore.QRectF(-s, -s, s * 2, s * 2)

    def paint(self, painter, option, widget=None):
        s = self.SIZE
        e = s + 8
        # Circle
        painter.setPen(QtGui.QPen(self._color, 2.0))
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawEllipse(-s, -s, s * 2, s * 2)
        # Crosshair arms outside circle
        painter.setPen(QtGui.QPen(self._color, 1.5))
        painter.drawLine(-e, 0, -s, 0)
        painter.drawLine(s, 0, e, 0)
        painter.drawLine(0, -e, 0, -s)
        painter.drawLine(0, s, 0, e)
        # Small center dot
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(self._color))
        painter.drawEllipse(-3, -3, 6, 6)


# ---------------------------------------------------------------------------
# MatchCanvas — interactive QGraphicsView
# ---------------------------------------------------------------------------

class MatchCanvas(QtWidgets.QGraphicsView):

    solveChanged     = QtCore.Signal()
    refLineChanged   = QtCore.Signal()
    originChanged    = QtCore.Signal()
    imageDropped     = QtCore.Signal(str)   # emitted when user drops a file on the canvas
    unloadRequested  = QtCore.Signal()      # emitted when user clicks the X overlay

    _LOUPE_SIZE  = 180
    _LOUPE_CROP  = 36   # source pixels at 5× zoom

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setMinimumHeight(300)

        self._pixmap_item = None
        self._orig_pixmap = None
        self._img_w = 1; self._img_h = 1
        self._image_path = None

        # Axis line groups
        self._ax_x_lines = []
        self._ax_y_lines = []
        self._ax_z_lines = []
        self._ref_lines  = []
        self._ref_labels = []   # QGraphicsSimpleTextItem overlay per ref line
        self._active_axis = "X"

        # Vanishing point markers
        self._marker_x = VPMarker(_C.AX_X)
        self._marker_y = VPMarker(_C.AX_Y)
        self._marker_z = VPMarker(_C.AX_Z)
        for m in (self._marker_x, self._marker_y, self._marker_z):
            self._scene.addItem(m)

        # Scene origin marker
        self._origin_marker = OriginMarker()
        self._scene.addItem(self._origin_marker)
        self._origin_set = False

        self._drawing   = False
        self._draw_mode = None   # "axis" | "ref" | "origin"
        self._draw_line = None

        self._solve_timer = QtCore.QTimer(self)
        self._solve_timer.setSingleShot(True)
        self._solve_timer.setInterval(40)
        self._solve_timer.timeout.connect(self.solveChanged)

        self._zoom_level = 1.0

        # Loupe
        L = self._LOUPE_SIZE
        self._loupe = QtWidgets.QLabel(self)
        self._loupe.setFixedSize(L, L)
        self._loupe.setAlignment(QtCore.Qt.AlignCenter)
        self._loupe.setStyleSheet(
            "background: #111111; border: 2px solid #909090; border-radius: 90px;"
        )
        bm = QtGui.QBitmap(L, L)
        bm.fill(QtCore.Qt.color0)
        p = QtGui.QPainter(bm)
        p.setBrush(QtCore.Qt.color1)
        p.setPen(QtCore.Qt.NoPen)
        p.drawEllipse(0, 0, L - 1, L - 1)
        p.end()
        self._loupe.setMask(bm)
        self._loupe.hide()

        # Accept dropped image files directly on the canvas (replaces current image)
        self.setAcceptDrops(True)

        # Unload-image overlay: small X button in the top-right corner of the view,
        # visible only when an image is loaded. Click to wipe image + all canvas state.
        self._unload_btn = QtWidgets.QPushButton("✕", self)   # ✕
        self._unload_btn.setFixedSize(24, 24)
        self._unload_btn.setToolTip("Unload image and clear all lines/origin/ref.")
        self._unload_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self._unload_btn.setStyleSheet(
            "QPushButton {"
            "  background: rgba(30,30,30,200); color: #cccccc;"
            "  border: 1px solid #555555; border-radius: 12px;"
            "  font-size: 13px; font-weight: bold; padding: 0px;"
            "} "
            "QPushButton:hover { background: rgba(180,50,50,220); color: #ffffff;"
            "  border-color: #d0d0d0; }"
        )
        self._unload_btn.clicked.connect(self.unloadRequested.emit)
        self._unload_btn.hide()
        self._reposition_unload_btn()

        # Perspective floor grid overlay
        self._grid_lines   = []   # QGraphicsLineItem objects in scene
        self._grid_visible = False

    # ── Image ─────────────────────────────────────────────────────────────

    def load_image(self, path):
        pm = QtGui.QPixmap(path)
        if pm.isNull():
            return False
        self._image_path = path
        self._orig_pixmap = pm
        self._img_w = pm.width(); self._img_h = pm.height()
        if self._pixmap_item:
            self._scene.removeItem(self._pixmap_item)
        self._pixmap_item = self._scene.addPixmap(pm)
        self._pixmap_item.setZValue(0)
        self._scene.setSceneRect(0, 0, self._img_w, self._img_h)
        for line in self._ax_x_lines + self._ax_y_lines + self._ax_z_lines:
            line.update_image_size(self._img_w, self._img_h)
        for rl in self._ref_lines:
            rl.update_image_size(self._img_w, self._img_h)
        self.fitInView(self._pixmap_item, QtCore.Qt.KeepAspectRatio)
        self._unload_btn.show()
        self._unload_btn.raise_()
        self._reposition_unload_btn()
        return True

    def _reposition_unload_btn(self):
        """Keep the unload X pinned to the top-right of the viewport."""
        if hasattr(self, "_unload_btn") and self._unload_btn is not None:
            margin = 6
            self._unload_btn.move(
                max(0, self.viewport().width() - self._unload_btn.width() - margin),
                margin,
            )

    @property
    def image_path(self): return self._image_path
    @property
    def image_size(self): return (self._img_w, self._img_h)

    def unload_image(self):
        """Remove the current image from the scene and reset dimensions.
        Caller is responsible for also clearing lines/origin via clear_all_lines."""
        if self._pixmap_item is not None:
            self._scene.removeItem(self._pixmap_item)
            self._pixmap_item = None
        self._orig_pixmap = None
        self._image_path = None
        self._img_w = 0
        self._img_h = 0
        self._scene.setSceneRect(0, 0, 1, 1)
        self.clear_grid()
        self._unload_btn.hide()

    # ── Axis control ──────────────────────────────────────────────────────

    def set_active_axis(self, axis):
        self._active_axis = axis  # "X" | "Y" | "Z" | "REF"

    def _active_lines(self):
        return {"X": self._ax_x_lines, "Y": self._ax_y_lines, "Z": self._ax_z_lines}.get(
            self._active_axis, self._ax_x_lines)

    def _axis_color(self, axis):
        return {"X": _C.AX_X, "Y": _C.AX_Y, "Z": _C.AX_Z, "REF": _C.REF_COLOR}.get(axis, _C.AX_X)

    # ── Line management ───────────────────────────────────────────────────

    def start_add_line(self):
        if self._pixmap_item is None:
            return
        self._drawing = True
        self._draw_mode = "ref" if self._active_axis == "REF" else "axis"
        self.setCursor(QtCore.Qt.CrossCursor)

    def remove_last_line(self):
        if self._active_axis == "REF":
            if self._ref_lines:
                self._ref_lines.pop().remove()
                self.refLineChanged.emit()
            return
        lines = self._active_lines()
        if len(lines) <= 2:
            return
        lines.pop().remove()
        self._schedule_solve()

    def _schedule_solve(self):
        self._solve_timer.start()

    def _on_line_changed(self):
        self._update_markers()
        self._schedule_solve()

    def _on_ref_changed(self):
        self.refLineChanged.emit()

    def _update_markers(self):
        for marker, lines in (
            (self._marker_x, self._ax_x_lines),
            (self._marker_y, self._ax_y_lines),
            (self._marker_z, self._ax_z_lines),
        ):
            segs = [l.endpoints() for l in lines]
            vp = _compute_vp(segs)
            if vp:
                marker.setPos(vp[0], vp[1])
                marker.setVisible(True)
            else:
                marker.setVisible(False)

    def get_axis_lines(self):
        return (
            [l.endpoints() for l in self._ax_x_lines],
            [l.endpoints() for l in self._ax_y_lines],
            [l.endpoints() for l in self._ax_z_lines],
        )

    def get_ref_lines_px(self):
        return [rl.px_length() for rl in self._ref_lines]

    # ── Scene origin ──────────────────────────────────────────────────────

    def start_set_origin(self):
        if self._pixmap_item is None:
            return
        self._drawing   = True
        self._draw_mode = "origin"
        self.setCursor(QtCore.Qt.CrossCursor)

    def clear_origin(self):
        self._origin_marker.setVisible(False)
        self._origin_set = False
        self.originChanged.emit()

    def get_origin_scene_pos(self):
        """Returns (x, y) in scene/image coordinates, or None if not set."""
        if not self._origin_set:
            return None
        p = self._origin_marker.pos()
        return (p.x(), p.y())

    def set_origin(self, x, y):
        """Place the origin marker at scene coordinates without entering draw mode."""
        self._origin_marker.setPos(x, y)
        self._origin_marker.setVisible(True)
        self._origin_set = True
        self.originChanged.emit()

    # ── Save / restore full canvas state ─────────────────────────────────

    def clear_all_lines(self):
        """Remove all axis lines, ref lines, and origin marker from the scene."""
        for line in self._ax_x_lines + self._ax_y_lines + self._ax_z_lines:
            line.remove()
        self._ax_x_lines.clear()
        self._ax_y_lines.clear()
        self._ax_z_lines.clear()
        for rl in self._ref_lines:
            rl.remove()
        self._ref_lines = []
        for lbl in self._ref_labels:
            self._scene.removeItem(lbl)
        self._ref_labels = []
        self.clear_origin()
        self._update_markers()
        self._schedule_solve()

    def add_axis_line(self, axis, x1, y1, x2, y2):
        """Add a line to a specific axis group (used when restoring a saved setup)."""
        prev = self._active_axis
        self._active_axis = axis
        self._add_line(x1, y1, x2, y2)
        self._active_axis = prev

    def add_ref_line_endpoints(self, x1, y1, x2, y2):
        """Append a ref line (used when restoring from saved setup)."""
        rl = VPLineItem(
            self._scene, x1, y1, x2, y2,
            _C.REF_COLOR, self._on_ref_changed, self._img_w, self._img_h
        )
        self._ref_lines.append(rl)
        self.refLineChanged.emit()

    def remove_ref_line(self, index):
        if 0 <= index < len(self._ref_lines):
            self._ref_lines[index].remove()
            self._ref_lines.pop(index)
            if index < len(self._ref_labels):
                self._scene.removeItem(self._ref_labels[index])
                self._ref_labels.pop(index)
            self.refLineChanged.emit()

    def update_ref_labels(self, texts):
        """Create/update/remove canvas text overlays showing the ref line real-world values."""
        # Remove excess labels
        while len(self._ref_labels) > len(texts):
            self._scene.removeItem(self._ref_labels.pop())
        # Create missing labels
        while len(self._ref_labels) < len(texts):
            lbl = QtWidgets.QGraphicsSimpleTextItem("")
            lbl.setBrush(QtGui.QBrush(QtGui.QColor(_C.REF_COLOR)))
            f = lbl.font(); f.setPointSize(9); f.setBold(True)
            lbl.setFont(f)
            lbl.setZValue(50)
            self._scene.addItem(lbl)
            self._ref_labels.append(lbl)
        # Update text and position
        for i, (text, lbl) in enumerate(zip(texts, self._ref_labels)):
            lbl.setText(text)
            ep = self._ref_lines[i].endpoints()
            mx = (ep[0][0] + ep[1][0]) / 2
            my = (ep[0][1] + ep[1][1]) / 2
            lbl.setPos(mx + 6, my - 18)
            lbl.setVisible(True)

    # ── Default lines ────────────────────────────────────────────────────

    def add_default_lines(self):
        w, h = self._img_w, self._img_h
        cx, cy = w / 2, h / 2
        self._add_line(cx - w*0.30, cy - h*0.12, cx + w*0.30, cy - h*0.08, "X")
        self._add_line(cx - w*0.30, cy + h*0.12, cx + w*0.30, cy + h*0.08, "X")
        self._add_line(cx - w*0.05, cy - h*0.10, cx + w*0.15, cy - h*0.15, "Z")
        self._add_line(cx - w*0.05, cy + h*0.10, cx + w*0.15, cy + h*0.15, "Z")
        self._update_markers()
        self._schedule_solve()

    def _add_line(self, x1, y1, x2, y2, axis=None):
        if axis is None:
            axis = self._active_axis
        color = self._axis_color(axis)
        target = {"X": self._ax_x_lines, "Y": self._ax_y_lines, "Z": self._ax_z_lines}.get(axis)
        if target is None:
            return None
        li = VPLineItem(self._scene, x1, y1, x2, y2, color,
                        self._on_line_changed, self._img_w, self._img_h)
        target.append(li)
        return li

    # ── Loupe ─────────────────────────────────────────────────────────────

    def _update_loupe(self, view_pos, scene_pos):
        if self._orig_pixmap is None:
            return
        pm = self._orig_pixmap
        L = self._LOUPE_SIZE
        C = self._LOUPE_CROP
        sx = scene_pos.x() - C / 2; sy = scene_pos.y() - C / 2
        crop = pm.copy(int(sx), int(sy), C, C)
        if crop.isNull() or crop.width() == 0 or crop.height() == 0:
            self._loupe.hide()
            return
        scaled = crop.scaled(L, L, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        # Draw crosshair
        painter = QtGui.QPainter(scaled)
        cx2, cy2 = scaled.width() // 2, scaled.height() // 2
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 160), 1, QtCore.Qt.DashLine))
        painter.drawLine(cx2, 0, cx2, scaled.height())
        painter.drawLine(0, cy2, scaled.width(), cy2)
        painter.end()
        self._loupe.setPixmap(scaled)
        # Position upper-right of cursor, clamped to widget
        lx = view_pos.x() + 18
        ly = view_pos.y() - L - 18
        lx = min(lx, self.width()  - L - 4)
        ly = max(ly, 4)
        self._loupe.move(lx, ly)
        self._loupe.show()
        self._loupe.raise_()

    # ── Mouse events ─────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if self._drawing and event.button() == QtCore.Qt.LeftButton:
            sp = self.mapToScene(event.pos())
            if self._draw_mode == "origin":
                self._origin_marker.setPos(sp.x(), sp.y())
                self._origin_marker.setVisible(True)
                self._origin_set = True
                self._drawing   = False
                self._draw_mode = None
                self.setCursor(QtCore.Qt.ArrowCursor)
                self.originChanged.emit()
                return
            if self._draw_mode == "ref":
                new_rl = VPLineItem(
                    self._scene, sp.x(), sp.y(), sp.x() + 1, sp.y() + 1,
                    _C.REF_COLOR, self._on_ref_changed, self._img_w, self._img_h
                )
                self._ref_lines.append(new_rl)
                self._draw_line = new_rl
            else:
                self._draw_line = self._add_line(sp.x(), sp.y(), sp.x() + 1, sp.y() + 1)
            return
        if event.button() == QtCore.Qt.MiddleButton:
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            fake = QtGui.QMouseEvent(
                event.type(), event.pos(), QtCore.Qt.LeftButton,
                QtCore.Qt.LeftButton, event.modifiers()
            )
            super().mousePressEvent(fake)
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drawing and self._draw_line:
            sp = self.mapToScene(event.pos())
            self._draw_line.set_second_endpoint(sp.x(), sp.y())
            self._update_loupe(event.pos(), sp)
            return
        # Show loupe while hovering in origin-placement mode
        if self._drawing and self._draw_mode == "origin" and self._orig_pixmap is not None:
            sp = self.mapToScene(event.pos())
            self._update_loupe(event.pos(), sp)
            super().mouseMoveEvent(event)
            return
        grabber = self._scene.mouseGrabberItem()
        if isinstance(grabber, VPHandle) and self._orig_pixmap is not None:
            sp = self.mapToScene(event.pos())
            self._update_loupe(event.pos(), sp)
        else:
            self._loupe.hide()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drawing and event.button() == QtCore.Qt.LeftButton:
            was_ref = (self._draw_mode == "ref")
            self._drawing = False
            self._draw_mode = None
            self._draw_line = None
            self.setCursor(QtCore.Qt.ArrowCursor)
            self._update_markers()
            self._schedule_solve()
            self._loupe.hide()
            if was_ref:
                self.refLineChanged.emit()
            return
        if event.button() == QtCore.Qt.MiddleButton:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._loupe.hide()
            return
        self._loupe.hide()
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1.0 / 1.15
        self._zoom_level = max(0.05, min(20.0, self._zoom_level * factor))
        self.scale(factor, factor)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F:
            if self._pixmap_item:
                self.fitInView(self._pixmap_item, QtCore.Qt.KeepAspectRatio)
        super().keyPressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reposition_unload_btn()

    # ── Drag & drop: replace image in-place ───────────────────────────────

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            paths = [u.toLocalFile() for u in event.mimeData().urls()]
            if any(os.path.splitext(p)[1].lower() in _IMAGE_EXTS for p in paths):
                event.acceptProposedAction()
                return
        event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        paths = [u.toLocalFile() for u in event.mimeData().urls()]
        imgs  = [p for p in paths if os.path.splitext(p)[1].lower() in _IMAGE_EXTS]
        if imgs:
            self.imageDropped.emit(imgs[0])
            event.acceptProposedAction()
        else:
            event.ignore()

    # ── Perspective floor grid ────────────────────────────────────────────

    def set_grid_visible(self, visible):
        self._grid_visible = visible
        for item in self._grid_lines:
            item.setVisible(visible)

    def clear_grid(self):
        for item in self._grid_lines:
            self._scene.removeItem(item)
        self._grid_lines.clear()

    def update_grid(self, vp_x, vp_z, img_w, img_h, origin=None):
        """Draw a perspective grid: VP-fan lines + cross-dividers for square cell appearance."""
        self.clear_grid()
        if not self._grid_visible or img_w <= 0 or img_h <= 0:
            return

        horizon_y = (vp_x[1] + vp_z[1]) / 2.0
        N = 10  # fan lines per VP axis

        def mk_pen(hex_color, alpha, width=1.3, style=QtCore.Qt.SolidLine):
            c = QtGui.QColor(hex_color)
            c.setAlphaF(alpha)
            p = QtGui.QPen(c, width, style)
            p.setCosmetic(True)
            return p

        pen_x   = mk_pen(_C.AX_X,      0.55, 1.3)
        pen_z   = mk_pen(_C.AX_Z,      0.55, 1.3)
        pen_h   = mk_pen(_C.REF_COLOR, 0.90, 1.5, QtCore.Qt.DashLine)
        pen_div = mk_pen('#aaaaaa',     0.30, 0.7)   # cross-divider lines

        def _add(x1, y1, x2, y2, pen, z=11):
            item = self._scene.addLine(x1, y1, x2, y2, pen)
            item.setZValue(z)
            item.setVisible(True)
            self._grid_lines.append(item)

        # Horizon
        if -img_h < horizon_y < img_h * 2:
            _add(0, horizon_y, img_w, horizon_y, pen_h, z=13)

        below_h = max(horizon_y + 1.0, 0.0)

        def angle_anchors(vp, n, origin=None):
            if origin is not None:
                dx_c = origin[0] - vp[0]; dy_c = origin[1] - vp[1]
                if abs(dx_c) > 0.5 or abs(dy_c) > 0.5:
                    a_center = math.atan2(dy_c, dx_c)
                    half = math.radians(28)
                    pts = []
                    for k in range(n):
                        t = (k / max(n-1, 1)) * 2 - 1   # -1..+1
                        a = a_center + t * half
                        far = max(img_w, img_h) * 4
                        pts.append((vp[0] + far * math.cos(a), vp[1] + far * math.sin(a)))
                    return pts
            # default: equally spaced in angle across the bottom edge
            dy = img_h - vp[1]
            a_left  = math.atan2(dy, 0      - vp[0])
            a_right = math.atan2(dy, img_w  - vp[0])
            pts = []
            for k in range(n):
                a = a_left + k * (a_right - a_left) / max(n-1, 1)
                if abs(math.sin(a)) < 1e-8: continue
                t = dy / math.sin(a)
                if t <= 0: continue
                pts.append((vp[0] + t * math.cos(a), img_h))
            return pts

        def build_rays(vp, anchors, pen):
            rays = []
            for pt in anchors:
                dx = pt[0] - vp[0]; dy = pt[1] - vp[1]
                if abs(dx) < 0.1 and abs(dy) < 0.1:
                    continue
                seg = _clip_ray_to_rect(vp[0], vp[1], dx, dy, img_w, img_h)
                if seg and len(seg) == 2:
                    _add(seg[0][0], seg[0][1], seg[1][0], seg[1][1], pen)
                    rays.append((vp, (dx, dy)))
            return rays

        rays_x = build_rays(vp_x, angle_anchors(vp_x, N, origin), pen_x)
        rays_z = build_rays(vp_z, angle_anchors(vp_z, N, origin), pen_z)

        # Cross-dividers: for each interior Z-ray, find its intersections with all X-rays
        # and draw a segment connecting them (closes the grid cells laterally).
        def intersect(p1, d1, p2, d2):
            c = d1[0]*d2[1] - d1[1]*d2[0]
            if abs(c) < 1e-9:
                return None
            t = ((p2[0]-p1[0])*d2[1] - (p2[1]-p1[1])*d2[0]) / c
            return (p1[0]+t*d1[0], p1[1]+t*d1[1])

        for pz, dz in rays_z[1:-1]:
            hits = []
            for px, dx in rays_x:
                pt = intersect(pz, dz, px, dx)
                if pt and 0 <= pt[0] <= img_w and below_h <= pt[1] <= img_h:
                    hits.append(pt)
            if len(hits) >= 2:
                hits.sort(key=lambda p: p[0])
                _add(hits[0][0], hits[0][1], hits[-1][0], hits[-1][1], pen_div)

        for px, dx in rays_x[1:-1]:
            hits = []
            for pz, dz in rays_z:
                pt = intersect(px, dx, pz, dz)
                if pt and 0 <= pt[0] <= img_w and below_h <= pt[1] <= img_h:
                    hits.append(pt)
            if len(hits) >= 2:
                hits.sort(key=lambda p: p[0])
                _add(hits[0][0], hits[0][1], hits[-1][0], hits[-1][1], pen_div)


# ---------------------------------------------------------------------------
# _ImageLoadZone — QFrame drop target wrapping the canvas
# Follows the same pattern as _RefCard in TurnTable Comp Setup (Nuke).
# QFrame-level drops work reliably; QGraphicsView viewport routing does not.
# ---------------------------------------------------------------------------

class _ImageLoadZone(QtWidgets.QFrame):

    imageDropped = QtCore.Signal(str)

    _BG_EMPTY   = "#141414"
    _BG_LOADED  = "#1a1a1a"
    _BDR_EMPTY  = "#3a3a3a"
    _BDR_LOADED = "#2b2b2b"
    _BDR_DRAG   = "#80cc80"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._has_image = False

        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.canvas = MatchCanvas()
        lay.addWidget(self.canvas)

        # Placeholder overlay — visible when no image is loaded
        self._overlay = QtWidgets.QLabel(self)
        self._overlay.setAlignment(QtCore.Qt.AlignCenter)
        self._overlay.setText(
            '<span style="font-size:22px;color:#2e2e2e;font-weight:bold;">⊕</span><br>'
            '<span style="font-size:12px;color:#3a3a3a;">drop image here</span><br>'
            '<span style="font-size:10px;color:#2e2e2e;">or click to browse</span>'
        )
        self._overlay.setTextFormat(QtCore.Qt.RichText)
        self._overlay.setCursor(QtCore.Qt.PointingHandCursor)
        self._overlay.mousePressEvent = self._overlay_clicked
        self._refresh_style()

    def set_has_image(self, has_image):
        self._has_image = has_image
        self._overlay.setVisible(not has_image)
        if not has_image:
            self._overlay.raise_()
        self._refresh_style()

    def _refresh_style(self):
        bg  = self._BG_LOADED  if self._has_image else self._BG_EMPTY
        bdr = self._BDR_LOADED if self._has_image else self._BDR_EMPTY
        self.setStyleSheet(
            f"QFrame {{ background: {bg}; border: 1px solid {bdr}; border-radius: 2px; }}"
        )

    def _overlay_clicked(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Load Reference Image", "", _IMAGE_EXTENSIONS
            )
            if path:
                self.imageDropped.emit(path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            paths = [u.toLocalFile() for u in event.mimeData().urls()]
            if any(os.path.splitext(p)[1].lower() in _IMAGE_EXTS for p in paths):
                event.acceptProposedAction()
                self.setStyleSheet(
                    f"QFrame {{ background: #1e2b1e; border: 2px solid {self._BDR_DRAG}; "
                    "border-radius: 2px; }}"
                )
                return
        event.ignore()

    def dragLeaveEvent(self, event):
        self._refresh_style()
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        self._refresh_style()
        paths = [u.toLocalFile() for u in event.mimeData().urls()]
        imgs  = [p for p in paths if os.path.splitext(p)[1].lower() in _IMAGE_EXTS]
        if imgs:
            self.imageDropped.emit(imgs[0])
        event.acceptProposedAction()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._overlay.setGeometry(0, 0, self.width(), self.height())
        if not self._has_image:
            self._overlay.raise_()


# ---------------------------------------------------------------------------
# Main dialog
# ---------------------------------------------------------------------------

class CameraMatchmaker(QtWidgets.QDialog):

    def __init__(self, parent=None):
        maya_main = self._get_maya_main_window()
        super().__init__(maya_main)
        self.setObjectName(WINDOW_OBJECT_NAME)
        self.setWindowTitle(f"Camera Matchmaker  {VERSION}")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window)
        self.setMinimumSize(660, 600)

        self._solve_result    = None
        self._last_grid_params = None   # (vp_x, vp_z, focal, cx, cy, w, h)
        self._scene_unit = self._read_maya_unit()

        self._build_ui()
        self.setStyleSheet(MAIN_QSS)
        self._populate_cameras()
        self.adjustSize()

        # Debounced auto-save — fires 500 ms after the last change
        self._autosave_timer = QtCore.QTimer(self)
        self._autosave_timer.setSingleShot(True)
        self._autosave_timer.setInterval(500)
        self._autosave_timer.timeout.connect(self._autosave)
        self._wire_autosave()

    @staticmethod
    def _read_maya_unit():
        """Return Maya's current linear unit string (e.g. 'cm', 'm', 'mm', 'ft', 'in')."""
        try:
            return cmds.currentUnit(query=True, linear=True)
        except Exception:
            return "cm"

    @staticmethod
    def _default_height_for_unit(unit):
        """Return a sensible eye-height default in the given Maya unit."""
        defaults = {
            "mm": 1700.0, "cm": 170.0, "m": 1.7,
            "km": 0.0017, "in": 67.0, "ft": 5.6, "yd": 1.9, "mi": 0.001,
        }
        return defaults.get(unit, 170.0)

    @staticmethod
    def _get_maya_main_window():
        try:
            from maya import OpenMayaUI as omui
            from shiboken6 import wrapInstance
            ptr = omui.MQtUtil.mainWindow()
            return wrapInstance(int(ptr), QtWidgets.QWidget)
        except Exception:
            return None

    # ── UI build ──────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_header())

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(10, 10, 10, 10)
        vbox.setSpacing(6)

        # Instructions (collapsible, closed by default — same as all other tools)
        guide_sec = CollapsibleSection("Instructions", start_collapsed=True)
        guide_sec.add_widget(self._make_step_guide())
        vbox.addWidget(guide_sec.widget)

        # Toolbar
        vbox.addWidget(self._make_toolbar())

        # Axis legend
        vbox.addWidget(self._make_axis_legend())

        # Canvas wrapped in drop zone
        self._drop_zone = _ImageLoadZone()
        self._canvas = self._drop_zone.canvas
        self._canvas.solveChanged.connect(self._on_solve_changed)
        self._canvas.refLineChanged.connect(self._on_ref_line_changed)
        self._canvas.originChanged.connect(self._on_origin_changed)
        self._drop_zone.imageDropped.connect(self._on_image_dropped)
        self._canvas.imageDropped.connect(self._on_image_dropped)
        self._canvas.unloadRequested.connect(self._reset_canvas_state)
        vbox.addWidget(self._drop_zone)

        # Solve readout
        vbox.addWidget(self._make_solve_readout())

        # Scene data: camera height, lens override, measurement ref (all optional)
        data_sec = CollapsibleSection("Scene Data", start_collapsed=True)
        data_sec.add_widget(self._make_scene_data_section())
        vbox.addWidget(data_sec.widget)

        # Output section (collapsed by default so canvas is visible on open)
        out_sec = CollapsibleSection("Output", start_collapsed=True)
        out_sec.add_widget(self._make_output_section())
        vbox.addWidget(out_sec.widget)

        # Status
        self._status_lbl = QtWidgets.QLabel("Load an image to begin.")
        self._status_lbl.setObjectName("statusIdle")
        self._status_lbl.setWordWrap(True)
        vbox.addWidget(self._status_lbl)

        root.addLayout(vbox)
        root.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)

    def _make_header(self):
        icon_dir = cmds.internalVar(userPrefDir=True) + "icons/"
        hdr = QtWidgets.QWidget()
        hdr.setFixedHeight(106)
        hdr.setStyleSheet(f"background-color: {_C.BG_HEADER};")

        hbox = QtWidgets.QHBoxLayout(hdr)
        hbox.setContentsMargins(10, 5, 10, 5)
        hbox.setSpacing(0)

        # Left: tool icon 96×96
        left_lbl = QtWidgets.QLabel()
        left_lbl.setFixedSize(96, 96)
        left_lbl.setAlignment(QtCore.Qt.AlignCenter)
        tool_icon = icon_dir + "icon_camera_matchmaker.png"
        if os.path.isfile(tool_icon):
            pm = QtGui.QPixmap(tool_icon).scaled(96, 96, QtCore.Qt.KeepAspectRatio,
                                                  QtCore.Qt.SmoothTransformation)
            left_lbl.setPixmap(pm)
        else:
            left_lbl.setText("[Icon]")
            left_lbl.setStyleSheet("background: #333333; color: white;")
        hbox.addWidget(left_lbl)

        # Center: logo + tool name + version
        center = QtWidgets.QVBoxLayout()
        center.setContentsMargins(0, 0, 0, 0)
        center.setSpacing(2)
        center.setAlignment(QtCore.Qt.AlignVCenter)

        logo_lbl = QtWidgets.QLabel()
        logo_lbl.setFixedSize(262, 48)
        logo_lbl.setAlignment(QtCore.Qt.AlignCenter)
        logo_path = icon_dir + "PXLtools_logo.png"
        if os.path.isfile(logo_path):
            lpm = QtGui.QPixmap(logo_path).scaled(262, 48, QtCore.Qt.KeepAspectRatio,
                                                    QtCore.Qt.SmoothTransformation)
            logo_lbl.setPixmap(lpm)
        else:
            logo_lbl.setText("PXLtools")
            logo_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")

        logo_row = QtWidgets.QHBoxLayout()
        logo_row.setContentsMargins(0, 0, 0, 0)
        logo_row.addStretch()
        logo_row.addWidget(logo_lbl)
        logo_row.addStretch()
        center.addLayout(logo_row)

        name_lbl = QtWidgets.QLabel("Camera Matchmaker")
        name_lbl.setAlignment(QtCore.Qt.AlignCenter)
        name_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")
        center.addWidget(name_lbl)

        ver_lbl = QtWidgets.QLabel(f"v{VERSION}")
        ver_lbl.setAlignment(QtCore.Qt.AlignCenter)
        ver_lbl.setStyleSheet("color: #aaaaaa; font-size: 9px;")
        center.addWidget(ver_lbl)

        hbox.addLayout(center, 1)

        # Right: balancing spacer
        right_sp = QtWidgets.QLabel()
        right_sp.setFixedSize(96, 96)
        hbox.addWidget(right_sp)

        return hdr

    def _make_step_guide(self):
        frame = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(frame)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        steps = QtWidgets.QLabel(
            "<span style='color:#aaaaaa'>&#9312;</span> "
            "<span style='color:#888888'>Load a photo — or <b>drag &amp; drop</b> an image onto the canvas.</span><br>"
            "<span style='color:#aaaaaa'>&#9313;</span> "
            f"<span style='color:#888888'>Select </span>"
            f"<b><span style='color:{_C.AX_X}'>X Axis</span></b>"
            "<span style='color:#888888'> and draw 2+ lines along horizontal parallel edges "
            "(floor, ceiling, window sills going sideways).</span><br>"
            "<span style='color:#aaaaaa'>&#9314;</span> "
            f"<span style='color:#888888'>Select </span>"
            f"<b><span style='color:{_C.AX_Z}'>Z Axis</span></b>"
            "<span style='color:#888888'> and draw 2+ lines along depth-parallel edges "
            "(edges going away from you into the scene).</span><br>"
            "<span style='color:#aaaaaa'>&#9315;</span> "
            f"<span style='color:#888888'>Optional: select </span>"
            f"<b><span style='color:{_C.AX_Y}'>Y Axis</span></b>"
            "<span style='color:#888888'> for vertical reference lines (columns, door frames).</span><br>"
            "<span style='color:#aaaaaa'>&#9316;</span> "
            f"<span style='color:#888888'>Optional: draw a </span>"
            f"<b><span style='color:{_C.REF_COLOR}'>Ref</span></b>"
            "<span style='color:#888888'> line across a known object to set real-world scene scale.</span><br>"
            "<span style='color:#aaaaaa'>&#9317;</span> "
            "<span style='color:#888888'>Click <b>APPLY TO CAMERA</b> or <b>CREATE NEW CAMERA</b>.</span>"
        )
        steps.setTextFormat(QtCore.Qt.RichText)
        steps.setWordWrap(True)
        steps.setStyleSheet("background: transparent; font-size: 11px; line-height: 160%;")
        vbox.addWidget(steps)
        return frame

    def _make_toolbar(self):
        bar = QtWidgets.QWidget()
        bar.setStyleSheet("background: #3a3a3a; border-radius: 2px;")
        hbox = QtWidgets.QHBoxLayout(bar)
        hbox.setContentsMargins(8, 6, 8, 6)
        hbox.setSpacing(6)


        self._btn_save_setup = QtWidgets.QPushButton("Save Setup")
        self._btn_save_setup.setObjectName("btnSmall")
        self._btn_save_setup.setMinimumWidth(84)
        self._btn_save_setup.setToolTip(
            "Save line setup, origin, and settings to a .matchmaker.json\n"
            "file next to the current image. Auto-restored on next load."
        )
        self._btn_save_setup.clicked.connect(self._save_setup)
        hbox.addWidget(self._btn_save_setup)

        self._btn_load_setup = QtWidgets.QPushButton("Load Setup")
        self._btn_load_setup.setObjectName("btnSmall")
        self._btn_load_setup.setMinimumWidth(84)
        self._btn_load_setup.setToolTip("Load a saved .matchmaker.json setup file manually.")
        self._btn_load_setup.clicked.connect(self._load_setup)
        hbox.addWidget(self._btn_load_setup)

        div = QtWidgets.QFrame()
        div.setFrameShape(QtWidgets.QFrame.VLine)
        div.setStyleSheet("color: #555555;")
        hbox.addWidget(div)

        axis_lbl = QtWidgets.QLabel("Axis:")
        axis_lbl.setStyleSheet("color: #888888; font-size: 11px; background: transparent;")
        hbox.addWidget(axis_lbl)

        self._btn_axis_x = QtWidgets.QPushButton("X")
        self._btn_axis_x.setObjectName("btnAxisX")
        self._btn_axis_x.setCheckable(True)
        self._btn_axis_x.setChecked(True)
        self._btn_axis_x.setMinimumWidth(36)
        self._btn_axis_x.setToolTip("X Axis — horizontal parallel edges")
        self._btn_axis_x.clicked.connect(lambda: self._set_active_axis("X"))
        hbox.addWidget(self._btn_axis_x)

        self._btn_axis_y = QtWidgets.QPushButton("Y")
        self._btn_axis_y.setObjectName("btnAxisY")
        self._btn_axis_y.setCheckable(True)
        self._btn_axis_y.setChecked(False)
        self._btn_axis_y.setMinimumWidth(36)
        self._btn_axis_y.setToolTip("Y Axis — vertical reference lines (optional)")
        self._btn_axis_y.clicked.connect(lambda: self._set_active_axis("Y"))
        hbox.addWidget(self._btn_axis_y)

        self._btn_axis_z = QtWidgets.QPushButton("Z")
        self._btn_axis_z.setObjectName("btnAxisZ")
        self._btn_axis_z.setCheckable(True)
        self._btn_axis_z.setChecked(False)
        self._btn_axis_z.setMinimumWidth(36)
        self._btn_axis_z.setToolTip("Z Axis — depth-parallel edges")
        self._btn_axis_z.clicked.connect(lambda: self._set_active_axis("Z"))
        hbox.addWidget(self._btn_axis_z)

        self._btn_axis_ref = QtWidgets.QPushButton("Ref")
        self._btn_axis_ref.setObjectName("btnAxisRef")
        self._btn_axis_ref.setCheckable(True)
        self._btn_axis_ref.setChecked(False)
        self._btn_axis_ref.setMinimumWidth(40)
        self._btn_axis_ref.setToolTip("Scale Reference — draw across a known real-world object")
        self._btn_axis_ref.clicked.connect(lambda: self._set_active_axis("REF"))
        hbox.addWidget(self._btn_axis_ref)

        div_orig = QtWidgets.QFrame()
        div_orig.setFrameShape(QtWidgets.QFrame.VLine)
        div_orig.setStyleSheet("color: #555555;")
        hbox.addWidget(div_orig)

        self._btn_set_origin = QtWidgets.QPushButton("Set Origin")
        self._btn_set_origin.setObjectName("btnOrigin")
        self._btn_set_origin.setCheckable(True)
        self._btn_set_origin.setChecked(False)
        self._btn_set_origin.setMinimumWidth(76)
        self._btn_set_origin.setToolTip(
            "Click to place the scene origin (0,0,0) marker on the image.\n"
            "Used to compute camera horizontal offset during position estimation."
        )
        self._btn_set_origin.clicked.connect(self._on_set_origin_clicked)
        hbox.addWidget(self._btn_set_origin)

        div2 = QtWidgets.QFrame()
        div2.setFrameShape(QtWidgets.QFrame.VLine)
        div2.setStyleSheet("color: #555555;")
        hbox.addWidget(div2)

        self._btn_add = QtWidgets.QPushButton("+ Add Line")
        self._btn_add.setObjectName("btnSmall")
        self._btn_add.setMinimumWidth(80)
        self._btn_add.setEnabled(False)
        self._btn_add.clicked.connect(lambda: self._canvas.start_add_line())
        hbox.addWidget(self._btn_add)

        self._btn_remove = QtWidgets.QPushButton("− Remove")
        self._btn_remove.setObjectName("btnSmall")
        self._btn_remove.setMinimumWidth(76)
        self._btn_remove.setEnabled(False)
        self._btn_remove.clicked.connect(lambda: self._canvas.remove_last_line())
        hbox.addWidget(self._btn_remove)

        div_grid = QtWidgets.QFrame()
        div_grid.setFrameShape(QtWidgets.QFrame.VLine)
        div_grid.setStyleSheet("color: #555555;")
        hbox.addWidget(div_grid)

        self._btn_grid = QtWidgets.QPushButton("Grid")
        self._btn_grid.setObjectName("btnSmall")
        self._btn_grid.setCheckable(True)
        self._btn_grid.setChecked(False)
        self._btn_grid.setMinimumWidth(52)
        self._btn_grid.setToolTip(
            "Toggle perspective floor grid overlay.\n"
            "Grid shows the solved camera's ground plane — red = X axis rows,\n"
            "blue = Z axis depth columns, gold = horizon line."
        )
        self._btn_grid.toggled.connect(self._on_grid_toggled)
        hbox.addWidget(self._btn_grid)

        div_clear = QtWidgets.QFrame()
        div_clear.setFrameShape(QtWidgets.QFrame.VLine)
        div_clear.setStyleSheet("color: #555555;")
        hbox.addWidget(div_clear)

        self._btn_clear = QtWidgets.QPushButton("Clear All")
        self._btn_clear.setObjectName("btnSmall")
        self._btn_clear.setMinimumWidth(68)
        self._btn_clear.setEnabled(False)
        self._btn_clear.setToolTip(
            "Remove all axis lines, ref line, and origin marker.\n"
            "Image stays loaded — draw new lines from scratch."
        )
        self._btn_clear.clicked.connect(self._clear_canvas)
        hbox.addWidget(self._btn_clear)

        hbox.addStretch()
        return bar

    def _make_axis_legend(self):
        frame = QtWidgets.QFrame()
        frame.setStyleSheet(
            "QFrame { background: #383838; border: 1px solid #2b2b2b; border-radius: 2px; }"
        )
        hbox = QtWidgets.QHBoxLayout(frame)
        hbox.setContentsMargins(10, 6, 10, 6)
        hbox.setSpacing(16)

        def _dot_label(color, text):
            w = QtWidgets.QWidget()
            w.setStyleSheet("background: transparent;")
            row = QtWidgets.QHBoxLayout(w)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(5)
            dot = QtWidgets.QLabel("■")
            dot.setStyleSheet(f"color: {color}; font-size: 12px; background: transparent;")
            row.addWidget(dot)
            lbl = QtWidgets.QLabel(text)
            lbl.setStyleSheet("color: #909090; font-size: 11px; background: transparent;")
            row.addWidget(lbl)
            return w

        hbox.addWidget(_dot_label(_C.AX_X,     "X  Horizontal edges"))
        hbox.addWidget(_dot_label(_C.AX_Z,     "Z  Depth edges"))
        hbox.addWidget(_dot_label(_C.AX_Y,     "Y  Vertical (optional)"))
        hbox.addWidget(_dot_label(_C.REF_COLOR, "Ref  Real-world scale"))

        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.VLine)
        sep.setStyleSheet("color: #4a4a4a;")
        hbox.addWidget(sep)

        ctrl = QtWidgets.QLabel("Scroll = zoom  |  Middle mouse = pan  |  F = fit  |  Drag handles to adjust")
        ctrl.setStyleSheet("color: #606060; font-size: 10px; background: transparent;")
        hbox.addWidget(ctrl)
        hbox.addStretch()
        return frame

    def _make_solve_readout(self):
        frame = QtWidgets.QFrame()
        frame.setStyleSheet("background: #383838; border-radius: 2px;")
        grid = QtWidgets.QGridLayout(frame)
        grid.setContentsMargins(12, 8, 12, 8)
        grid.setSpacing(4)
        grid.setHorizontalSpacing(20)

        def _kv(key):
            k = QtWidgets.QLabel(key)
            k.setObjectName("solveKey")
            v = QtWidgets.QLabel("—")
            v.setObjectName("solveVal")
            return k, v

        k1, self._lbl_fov  = _kv("Horiz. FOV")
        k2, self._lbl_pan  = _kv("Pan (Ry)")
        k3, self._lbl_tilt = _kv("Tilt (Rx)")
        k4, self._lbl_roll = _kv("Roll (Rz)")

        for col, (k, v) in enumerate([(k1, self._lbl_fov), (k2, self._lbl_pan),
                                       (k3, self._lbl_tilt), (k4, self._lbl_roll)]):
            grid.addWidget(k, 0, col)
            grid.addWidget(v, 1, col)

        return frame

    def _make_scene_data_section(self):
        """Optional ground-truth constraints — all off by default."""
        w = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(w)
        vbox.setContentsMargins(0, 4, 0, 0)
        vbox.setSpacing(10)

        def _row(checkbox, spin):
            row = QtWidgets.QHBoxLayout()
            row.addWidget(checkbox)
            row.addWidget(spin)
            row.addStretch()
            return row

        # ── Camera Height ──────────────────────────────────────────────────
        self._chk_height = QtWidgets.QCheckBox("Camera Height")
        self._chk_height.setChecked(True)
        self._chk_height.setToolTip(
            "Real-world height of the camera lens above the ground plane.\n"
            "Required for position solve. Uncheck if unknown."
        )
        self._height_spin = QtWidgets.QDoubleSpinBox()
        self._height_spin.setRange(0.001, 1_000_000.0)
        self._height_spin.setValue(self._default_height_for_unit(self._scene_unit))
        self._height_spin.setSuffix(f"  {self._scene_unit}")
        self._height_spin.setMinimumWidth(130)
        self._height_spin.setEnabled(True)
        vbox.addLayout(_row(self._chk_height, self._height_spin))

        # ── Camera Lens ────────────────────────────────────────────────────
        self._chk_lens = QtWidgets.QCheckBox("Camera Lens")
        self._chk_lens.setChecked(False)
        self._chk_lens.setToolTip(
            "Override the computed focal length with a known lens value.\n"
            "Assumes 36mm full-frame sensor. Leave off to derive from vanishing points."
        )
        self._focal_mm_spin = QtWidgets.QDoubleSpinBox()
        self._focal_mm_spin.setRange(1.0, 2000.0)
        self._focal_mm_spin.setValue(35.0)
        self._focal_mm_spin.setSuffix("  mm")
        self._focal_mm_spin.setMinimumWidth(130)
        self._focal_mm_spin.setEnabled(False)
        vbox.addLayout(_row(self._chk_lens, self._focal_mm_spin))

        # ── Measurement Ref ────────────────────────────────────────────────
        self._chk_use_ref = QtWidgets.QCheckBox("Measurement Ref")
        self._chk_use_ref.setChecked(False)
        self._chk_use_ref.setToolTip(
            f"Draw a Ref line on an object of known size to scale the position solve.\n"
            f"Scene unit: {self._scene_unit}"
        )
        ref_hdr = QtWidgets.QHBoxLayout()
        ref_hdr.addWidget(self._chk_use_ref)
        ref_hdr.addStretch()
        vbox.addLayout(ref_hdr)

        self._ref_sub = QtWidgets.QWidget()
        ref_sub_vbox = QtWidgets.QVBoxLayout(self._ref_sub)
        ref_sub_vbox.setContentsMargins(20, 0, 0, 0)
        ref_sub_vbox.setSpacing(3)

        self._ref_rows_container = QtWidgets.QWidget()
        self._ref_rows_layout = QtWidgets.QVBoxLayout(self._ref_rows_container)
        self._ref_rows_layout.setContentsMargins(0, 0, 0, 0)
        self._ref_rows_layout.setSpacing(3)
        ref_sub_vbox.addWidget(self._ref_rows_container)

        self._ref_scale_lbl = QtWidgets.QLabel("—")
        self._ref_scale_lbl.setObjectName("hint")
        ref_sub_vbox.addWidget(self._ref_scale_lbl)

        self._ref_sub.setVisible(False)
        vbox.addWidget(self._ref_sub)

        self._ref_value_spins = []

        # Wire signals
        self._chk_height.toggled.connect(self._height_spin.setEnabled)
        self._chk_lens.toggled.connect(self._on_lens_toggled)
        self._focal_mm_spin.valueChanged.connect(self._on_focal_mm_changed)
        self._chk_use_ref.toggled.connect(self._on_ref_line_changed)

        return w

    def _make_output_section(self):
        w = QtWidgets.QWidget()
        root = QtWidgets.QVBoxLayout(w)
        root.setContentsMargins(0, 4, 0, 0)
        root.setSpacing(0)

        tabs = QtWidgets.QTabWidget()
        tabs.setDocumentMode(True)
        root.addWidget(tabs)

        # ── Tab 1: Apply ──────────────────────────────────────────────────
        apply_tab = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(apply_tab)
        vbox.setContentsMargins(8, 10, 8, 8)
        vbox.setSpacing(8)

        exist_lbl = QtWidgets.QLabel("APPLY TO EXISTING CAMERA")
        exist_lbl.setStyleSheet(
            "color: #707070; font-size: 9px; font-weight: bold; letter-spacing: 1.5px;"
        )
        vbox.addWidget(exist_lbl)

        cam_row = QtWidgets.QHBoxLayout()
        lbl = QtWidgets.QLabel("Target camera:")
        lbl.setObjectName("ctrlLabel")
        cam_row.addWidget(lbl)
        self._cam_combo = QtWidgets.QComboBox()
        self._cam_combo.setMinimumWidth(160)
        cam_row.addWidget(self._cam_combo)
        btn_refresh = QtWidgets.QPushButton("Refresh")
        btn_refresh.setObjectName("btnSmall")
        btn_refresh.setMinimumWidth(70)
        btn_refresh.clicked.connect(self._populate_cameras)
        cam_row.addWidget(btn_refresh)
        cam_row.addStretch()
        vbox.addLayout(cam_row)

        chk_row = QtWidgets.QHBoxLayout()
        self._chk_fov = QtWidgets.QCheckBox("Set FOV")
        self._chk_rot = QtWidgets.QCheckBox("Set Rotation")
        self._chk_pos = QtWidgets.QCheckBox("Estimate Position")
        for c in (self._chk_fov, self._chk_rot, self._chk_pos):
            c.setChecked(True)
            chk_row.addWidget(c)
        chk_row.addStretch()
        vbox.addLayout(chk_row)

        # ── Action buttons row: CREATE | APPLY | ADD IMAGE PLANE ─────────────
        action_row = QtWidgets.QHBoxLayout()
        action_row.setSpacing(6)
        self._btn_create_cam = QtWidgets.QPushButton("CREATE NEW CAMERA")
        self._btn_create_cam.setObjectName("btnPrimary")
        self._btn_create_cam.setEnabled(False)
        self._btn_create_cam.clicked.connect(self._create_camera)
        action_row.addWidget(self._btn_create_cam)
        self._btn_apply = QtWidgets.QPushButton("APPLY TO CAMERA")
        self._btn_apply.setObjectName("btnPrimary")
        self._btn_apply.setEnabled(False)
        self._btn_apply.clicked.connect(self._apply_to_camera)
        action_row.addWidget(self._btn_apply)
        self._btn_imgplane = QtWidgets.QPushButton("ADD IMAGE PLANE")
        self._btn_imgplane.setObjectName("btnPrimary")
        self._btn_imgplane.setEnabled(False)
        self._btn_imgplane.clicked.connect(self._add_image_plane)
        action_row.addWidget(self._btn_imgplane)
        action_row.addStretch()
        vbox.addLayout(action_row)

        # ── Create options row: camera name + Add image plane checkbox ────────
        create_opts = QtWidgets.QHBoxLayout()
        name_lbl = QtWidgets.QLabel("New cam name:")
        name_lbl.setObjectName("ctrlLabel")
        create_opts.addWidget(name_lbl)
        self._new_cam_name = QtWidgets.QLineEdit("MatchCam_01")
        self._new_cam_name.setMinimumWidth(130)
        self._new_cam_name.setMaximumWidth(160)
        create_opts.addWidget(self._new_cam_name)
        self._chk_create_imgplane = QtWidgets.QCheckBox("Add image plane")
        self._chk_create_imgplane.setChecked(True)
        self._chk_create_imgplane.setToolTip(
            "Automatically attach the loaded reference image as an image plane\n"
            "to the new camera after creation."
        )
        create_opts.addWidget(self._chk_create_imgplane)
        create_opts.addStretch()
        vbox.addLayout(create_opts)

        vbox.addStretch()
        tabs.addTab(apply_tab, "Apply")

        # ── Tab 2: Verify ─────────────────────────────────────────────────
        verify_tab = QtWidgets.QWidget()
        vbox2 = QtWidgets.QVBoxLayout(verify_tab)
        vbox2.setContentsMargins(8, 10, 8, 8)
        vbox2.setSpacing(8)

        test_lbl = QtWidgets.QLabel("VERIFY CAMERA MATCH")
        test_lbl.setStyleSheet(
            "color: #707070; font-size: 9px; font-weight: bold; letter-spacing: 1.5px;"
        )
        vbox2.addWidget(test_lbl)

        test_info = QtWidgets.QLabel(
            "Place a reference cube at the scene origin. Look through the solve camera "
            "and compare against the reference photo to verify the match before committing."
        )
        test_info.setObjectName("hint")
        test_info.setWordWrap(True)
        vbox2.addWidget(test_info)

        btn_test = QtWidgets.QPushButton("Place Test Object at Origin")
        btn_test.setObjectName("btnSmall")
        btn_test.setMinimumWidth(200)
        btn_test.setToolTip(
            "Creates MatchOrigin_grp (locator + cube) at (0,0,0).\n"
            "Look through the solved camera to check alignment."
        )
        btn_test.clicked.connect(self._place_test_object)
        vbox2.addWidget(btn_test)

        btn_grid = QtWidgets.QPushButton("Create 3D Ground Grid")
        btn_grid.setObjectName("btnSmall")
        btn_grid.setMinimumWidth(200)
        btn_grid.setToolTip(
            "Creates a real Maya curve grid at Y=0, centered at world (0,0,0).\n"
            "Red lines = X axis  |  Blue lines = Z axis\n"
            "Look through the camera — this grid should align with the canvas overlay."
        )
        btn_grid.clicked.connect(self._create_maya_grid)
        vbox2.addWidget(btn_grid)

        vbox2.addStretch()
        tabs.addTab(verify_tab, "Verify")

        return w

    # ── Actions ───────────────────────────────────────────────────────────

    def _set_active_axis(self, axis):
        self._canvas.set_active_axis(axis)
        for btn, ax in (
            (self._btn_axis_x, "X"),
            (self._btn_axis_y, "Y"),
            (self._btn_axis_z, "Z"),
            (self._btn_axis_ref, "REF"),
        ):
            btn.setChecked(ax == axis)

    def _on_set_origin_clicked(self):
        if self._btn_set_origin.isChecked():
            self._canvas.start_set_origin()
        else:
            self._canvas.clear_origin()

    def _on_origin_changed(self):
        # Uncheck the button once origin is placed (single-shot mode)
        self._btn_set_origin.setChecked(self._canvas.get_origin_scene_pos() is not None)

    def _load_image(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Load Reference Image", "", _IMAGE_EXTENSIONS
        )
        if path:
            self._load_image_path(path)

    def _on_image_dropped(self, path):
        """Centralised drop handler: if an image is already loaded, wipe state before
        loading the new one (so lines/origin/ref from the old image don't carry over)."""
        if self._canvas.image_path:
            self._reset_canvas_state()
        self._load_image_path(path)

    def _reset_canvas_state(self):
        """Discard all canvas state (image + lines + origin + ref + solve).
        Used by the X overlay button and by drop-replacing-existing-image."""
        self._canvas.clear_all_lines()
        self._canvas.unload_image()
        self._solve_result = None
        self._last_grid_params = None
        self._drop_zone.set_has_image(False)
        self._btn_add.setEnabled(False)
        self._btn_remove.setEnabled(False)
        self._btn_imgplane.setEnabled(False)
        self._btn_clear.setEnabled(False)
        self._btn_apply.setEnabled(False)
        self._btn_create_cam.setEnabled(False)
        for lbl in (self._lbl_fov, self._lbl_pan, self._lbl_tilt, self._lbl_roll):
            lbl.setText("—")
        self._rebuild_ref_list()
        self._set_status("idle", "Image unloaded — drop a new photo onto the canvas or drop zone.")

    def _load_image_path(self, path):
        if not self._canvas.load_image(path):
            self._set_status("err", f"Could not load image: {os.path.basename(path)}")
            return
        self._drop_zone.set_has_image(True)
        self._btn_add.setEnabled(True)
        self._btn_remove.setEnabled(True)
        self._btn_imgplane.setEnabled(True)
        self._btn_clear.setEnabled(True)
        w, h = self._canvas.image_size
        # Auto-restore sidecar if it exists, otherwise place default lines
        sidecar = self._sidecar_path(path)
        if os.path.isfile(sidecar):
            try:
                self._load_setup_from(sidecar)
                self._set_status("ok",
                    f"Image loaded: {os.path.basename(path)}  ({w}×{h})  — setup restored")
                return
            except Exception as e:
                logger.warning(f"Could not restore setup from sidecar: {e}")
        self._canvas.add_default_lines()
        self._set_status("idle", f"Image loaded: {os.path.basename(path)}  ({w}×{h})")

    # ── Solve ─────────────────────────────────────────────────────────────

    def _on_solve_changed(self):
        segs_x, _segs_y, segs_z = self._canvas.get_axis_lines()
        vp_x = _compute_vp(segs_x)
        vp_z = _compute_vp(segs_z)

        if vp_x is None or vp_z is None:
            self._solve_result = None
            for lbl in (self._lbl_fov, self._lbl_pan, self._lbl_tilt, self._lbl_roll):
                lbl.setText("—")
            self._btn_apply.setEnabled(False)
            self._btn_create_cam.setEnabled(False)
            return

        w, h = self._canvas.image_size
        # fSpy-exact: convert VPs to normalised Image Plane coords, solve in that frame.
        Fu = _pixel_to_image_plane(vp_x[0], vp_x[1], w, h)
        Fv = _pixel_to_image_plane(vp_z[0], vp_z[1], w, h)

        f_rel = _compute_focal_relative(Fu, Fv)
        # Optional manual lens override (mm on 36mm sensor) converted to image-plane units.
        if self._chk_lens.isChecked():
            focal_mm = self._focal_mm_spin.value()
            if focal_mm > 0:
                # f_px = focal_mm * w / 36 ; f_rel = f_px / (w/2)  →  f_rel = focal_mm * 2 / 36
                f_rel = focal_mm * 2.0 / 36.0
        if f_rel is None:
            self._solve_result = None
            for lbl in (self._lbl_fov, self._lbl_pan, self._lbl_tilt, self._lbl_roll):
                lbl.setText("?")
            self._set_status("err",
                "Cannot solve: X and Z vanishing points must be on opposite sides of the image center.")
            self._btn_apply.setEnabled(False)
            self._btn_create_cam.setEnabled(False)
            return

        R_ctw = _compute_camera_rotation(Fu, Fv, f_rel)
        if R_ctw is None:
            self._solve_result = None
            for lbl in (self._lbl_fov, self._lbl_pan, self._lbl_tilt, self._lbl_roll):
                lbl.setText("?")
            self._set_status("err", "Cannot solve: degenerate VPs (cross product collapsed).")
            self._btn_apply.setEnabled(False)
            self._btn_create_cam.setEnabled(False)
            return

        fov = _compute_fov_deg_from_frel(f_rel, w, h)
        rx, ry, rz = _maya_xyz_euler_from_rctw(R_ctw)
        # Label convention: pan=ry, tilt=rx, roll=rz
        pan, tilt, roll = ry, rx, rz
        self._solve_result = (fov, pan, tilt, roll, R_ctw, f_rel, vp_x, vp_z)
        self._last_grid_params = (vp_x, vp_z, f_rel, w/2.0, h/2.0, w, h)

        # ── Fit quality: how well do the drawn lines converge to the computed VPs? ──
        err_x = _vp_fit_error_deg(segs_x, vp_x)
        err_z = _vp_fit_error_deg(segs_z, vp_z)
        warnings = []
        if err_x is not None and err_x > 2.0:
            warnings.append(f"X-lines don't converge well (avg {err_x:.2f}° off)")
        if err_z is not None and err_z > 2.0:
            warnings.append(f"Z-lines don't converge well (avg {err_z:.2f}° off)")
        if fov > 110.0:
            warnings.append(f"very wide FOV ({fov:.0f}°) — check Z-line placement")
        elif fov < 20.0:
            warnings.append(f"very narrow FOV ({fov:.0f}°) — check X-line placement")

        self._lbl_fov.setText(f"{fov:.1f}°")
        self._lbl_pan.setText(f"{pan:.1f}°")
        self._lbl_tilt.setText(f"{tilt:.1f}°")
        self._lbl_roll.setText(f"{roll:.1f}°")
        self._btn_apply.setEnabled(True)
        self._btn_create_cam.setEnabled(True)

        ex = f"{err_x:.2f}°" if err_x is not None else "—"
        ez = f"{err_z:.2f}°" if err_z is not None else "—"
        base_msg = (f"Solved  |  FOV {fov:.1f}°  Pan {pan:.1f}°  Tilt {tilt:.1f}°  "
                    f"Roll {roll:.1f}°  |  fit X {ex}  Z {ez}")
        if warnings:
            self._set_status("warn", base_msg + "  ⚠ " + " · ".join(warnings))
        else:
            self._set_status("ok", base_msg)
        self._refresh_grid()

    def _refresh_grid(self):
        if not self._last_grid_params:
            return
        vp_x, vp_z, focal, cx, cy, w, h = self._last_grid_params
        origin = self._canvas.get_origin_scene_pos()
        self._canvas.update_grid(vp_x, vp_z, w, h, origin=origin)

    def _on_grid_toggled(self, checked):
        self._canvas.set_grid_visible(checked)
        if checked:
            self._refresh_grid()

    def _clear_canvas(self):
        self._canvas.clear_all_lines()
        self._canvas.clear_grid()
        self._last_grid_params = None
        self._solve_result = None
        self._btn_apply.setEnabled(False)
        self._btn_create_cam.setEnabled(False)
        for lbl in (self._lbl_fov, self._lbl_pan, self._lbl_tilt, self._lbl_roll):
            lbl.setText("—")
        self._rebuild_ref_list()
        self._set_status("idle", "Canvas cleared — draw new X and Z lines to solve.")

    def _rebuild_ref_list(self):
        """Sync the dynamic ref-line rows with canvas._ref_lines."""
        # Clear old rows
        while self._ref_rows_layout.count():
            item = self._ref_rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        px_lengths = self._canvas.get_ref_lines_px()
        old_vals = [s.value() for s in self._ref_value_spins]
        self._ref_value_spins = []

        for i, px_len in enumerate(px_lengths):
            row_w = QtWidgets.QWidget()
            row = QtWidgets.QHBoxLayout(row_w)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(6)

            swatch = QtWidgets.QLabel("■")
            swatch.setStyleSheet(f"color: {_C.REF_COLOR}; font-size: 13px;")
            row.addWidget(swatch)

            px_lbl = QtWidgets.QLabel(f"Ref {i+1}:  {px_len:.0f} px  →")
            px_lbl.setObjectName("ctrlLabel")
            row.addWidget(px_lbl)

            spin = QtWidgets.QDoubleSpinBox()
            spin.setRange(0.001, 1_000_000.0)
            spin.setValue(old_vals[i] if i < len(old_vals) else 200.0)
            spin.setSuffix(f"  {self._scene_unit}")
            spin.setMinimumWidth(130)
            spin.valueChanged.connect(self._on_ref_value_changed)
            row.addWidget(spin)
            self._ref_value_spins.append(spin)

            del_btn = QtWidgets.QPushButton("✕")
            del_btn.setObjectName("btnSmall")
            del_btn.setFixedWidth(26)
            del_btn.clicked.connect(lambda _checked, idx=i: self._delete_ref_line(idx))
            row.addWidget(del_btn)
            row.addStretch()
            self._ref_rows_layout.addWidget(row_w)

        if not px_lengths:
            hint = QtWidgets.QLabel("Click Ref in toolbar then draw a line on the canvas.")
            hint.setObjectName("hint")
            self._ref_rows_layout.addWidget(hint)

        self._update_ref_scale_readout()
        self._sync_ref_labels()

    def _delete_ref_line(self, index):
        self._canvas.remove_ref_line(index)
        # refLineChanged will trigger _rebuild_ref_list

    def _on_ref_value_changed(self):
        self._update_ref_scale_readout()
        self._sync_ref_labels()
        self._autosave_timer.start()

    def _sync_ref_labels(self):
        texts = [f"{s.value():.1f} {self._scene_unit}" for s in self._ref_value_spins]
        self._canvas.update_ref_labels(texts)

    def _update_ref_scale_readout(self):
        px_lengths = self._canvas.get_ref_lines_px()
        scales = []
        for i, px_len in enumerate(px_lengths):
            if i < len(self._ref_value_spins) and px_len and px_len > 0:
                real = self._ref_value_spins[i].value()
                if real > 0:
                    scales.append(real / px_len)
        if scales:
            avg = sum(scales) / len(scales)
            n = len(scales)
            self._ref_scale_lbl.setText(
                f"Scale: 1 px = {avg:.4f} {self._scene_unit}  ({n} ref line{'s' if n > 1 else ''})"
            )
        else:
            self._ref_scale_lbl.setText("—")

    def _on_ref_line_changed(self):
        self._ref_sub.setVisible(self._chk_use_ref.isChecked())
        self._rebuild_ref_list()

    def _on_lens_toggled(self, on):
        self._focal_mm_spin.setEnabled(on)
        self._on_solve_changed()

    def _on_focal_mm_changed(self):
        if self._chk_lens.isChecked():
            self._on_solve_changed()

    def _populate_cameras(self):
        self._cam_combo.clear()
        try:
            cams = cmds.listCameras(perspective=True) or []
            for c in cams:
                self._cam_combo.addItem(c)
            if not cams:
                self._cam_combo.addItem("persp")
        except Exception as e:
            logger.warning(f"Could not list cameras: {e}")
            self._cam_combo.addItem("persp")

    def _get_camera(self):
        cam_name = self._cam_combo.currentText().strip()
        if not cam_name or not cmds.objExists(cam_name):
            return None, None
        if cmds.nodeType(cam_name) == "camera":
            shape = cam_name
            parents = cmds.listRelatives(cam_name, parent=True, fullPath=True) or []
            transform = parents[0].split("|")[-1] if parents else cam_name
        else:
            transform = cam_name
            shapes = cmds.listRelatives(cam_name, shapes=True, type="camera", fullPath=True) or []
            shape = shapes[0] if shapes else None
        return transform, shape

    def _apply_solve_to(self, cam_transform, cam_shape):
        fov, pan, tilt, roll, R_ctw, f_rel, vp_x, vp_z = self._solve_result
        applied = []
        if self._chk_fov.isChecked():
            cmds.camera(cam_shape, edit=True, horizontalFieldOfView=fov)
            w_img, h_img = self._canvas.image_size
            H_AP = 36.0 / 25.4
            cmds.setAttr(f"{cam_shape}.horizontalFilmAperture", H_AP)
            cmds.setAttr(f"{cam_shape}.verticalFilmAperture", H_AP * h_img / w_img)
            applied.append(f"FOV {fov:.1f}°")
        if self._chk_rot.isChecked():
            cmds.setAttr(f"{cam_transform}.rotateX", tilt)
            cmds.setAttr(f"{cam_transform}.rotateY", pan)
            cmds.setAttr(f"{cam_transform}.rotateZ", roll)
            applied.append(f"Rot ({tilt:.1f}, {pan:.1f}, {roll:.1f})")
        if self._chk_pos.isChecked():
            pos_ok = self._estimate_position(cam_transform, R_ctw, f_rel)
            if pos_ok:
                applied.append("Position estimated")
            else:
                applied.append("Position skipped — enable Camera Height in Scene Data")
        return applied

    def _apply_to_camera(self):
        if not self._solve_result:
            self._set_status("err", "No valid solve — adjust axis lines first.")
            return
        transform, shape = self._get_camera()
        if not shape:
            self._set_status("err", f"Camera not found: {self._cam_combo.currentText()}")
            return
        try:
            applied = self._apply_solve_to(transform, shape)
            self._set_status("ok",
                f"Applied to {self._cam_combo.currentText()}: " + "  |  ".join(applied))
        except Exception as e:
            self._set_status("err", f"Apply failed: {e}")
            logger.exception("Apply to camera error")

    def _create_camera(self):
        if not self._solve_result:
            self._set_status("err", "No valid solve — adjust axis lines first.")
            return
        base = self._new_cam_name.text().strip() or "MatchCam"
        name = base
        i = 1
        while cmds.objExists(name):
            name = f"{base}_{i:02d}"
            i += 1
        try:
            result = cmds.camera()
            orig_transform = result[0]
            orig_shape     = result[1]
            fov, pan, tilt, roll, R_ctw, f_rel, vp_x, vp_z = self._solve_result
            cmds.camera(orig_shape, edit=True, horizontalFieldOfView=fov)
            w_img, h_img = self._canvas.image_size
            H_AP = 36.0 / 25.4
            cmds.setAttr(f"{orig_shape}.horizontalFilmAperture", H_AP)
            cmds.setAttr(f"{orig_shape}.verticalFilmAperture", H_AP * h_img / w_img)
            cmds.setAttr(f"{orig_transform}.rotateX", tilt)
            cmds.setAttr(f"{orig_transform}.rotateY", pan)
            cmds.setAttr(f"{orig_transform}.rotateZ", roll)
            if self._chk_pos.isChecked():
                self._estimate_position(orig_transform, R_ctw, f_rel)
            cam_transform = cmds.rename(orig_transform, name)

            # Build ground grid in world space, group it with the camera
            rig_name = f"{name}_rig"
            if cmds.objExists(rig_name):
                cmds.delete(rig_name)
            grid_curves = self._build_ground_grid_curves(name)
            if grid_curves:
                grid_grp = cmds.group(grid_curves, name=f"{name}_grid")
                cmds.group(cam_transform, grid_grp, name=rig_name)
            else:
                cmds.group(cam_transform, name=rig_name)

            self._populate_cameras()
            idx = self._cam_combo.findText(cam_transform)
            if idx >= 0:
                self._cam_combo.setCurrentIndex(idx)
            if self._chk_create_imgplane.isChecked():
                shapes = cmds.listRelatives(cam_transform, shapes=True, fullPath=True) or []
                renamed_shape = shapes[0] if shapes else None
                if renamed_shape and self._canvas.image_path:
                    existing = cmds.listConnections(f"{renamed_shape}.imagePlane") or []
                    if not existing:
                        _, ip_shape = cmds.imagePlane(camera=renamed_shape)
                        cmds.setAttr(f"{ip_shape}.imageName",
                                     self._canvas.image_path.replace("\\", "/"),
                                     type="string")
                        cmds.setAttr(f"{ip_shape}.displayMode", 2)
                        cmds.setAttr(f"{ip_shape}.fit", 2)
                        cmds.setAttr(f"{ip_shape}.alphaGain", 0.5)
            # Look through the newly created camera in the active 3D viewport
            self._look_through_camera(cam_transform)
            self._set_status("ok",
                f"Created: {rig_name}  |  FOV {fov:.1f}°  Pan {pan:.1f}°  Tilt {tilt:.1f}°")
        except Exception as e:
            self._set_status("err", f"Camera creation failed: {e}")
            logger.exception("Create camera error")

    def _look_through_camera(self, cam_transform):
        """Switch the active (or first available) modelPanel viewport to look through
        the given camera. Safe no-op if no model panel is open."""
        try:
            model_panels = cmds.getPanel(type="modelPanel") or []
            if not model_panels:
                return
            focused = cmds.getPanel(withFocus=True)
            target = focused if focused in model_panels else model_panels[0]
            cmds.lookThru(target, cam_transform)
        except Exception:
            logger.exception("lookThru failed")

    def _estimate_position(self, cam_transform, R_ctw, f_rel):
        """CP022 — use the solver's own R_ctw (no Euler reconstruction) and f_rel in
        Image Plane units. Forward-projects world origin (0,0,0) at the end and prints
        how far it lands from the origin marker — any rotation/focal error becomes
        visible as a numeric pixel delta, removing guesswork from verification.
        """
        w, h_img = self._canvas.image_size
        cx, cy = w / 2.0, h_img / 2.0

        def _world_ray(px, py):
            """Unit world-space direction of the ray from the camera origin through pixel (px, py)."""
            x_ip, y_ip = _pixel_to_image_plane(px, py, w, h_img)
            d_cam = (x_ip, y_ip, -f_rel)
            dw = [R_ctw[i][0]*d_cam[0] + R_ctw[i][1]*d_cam[1] + R_ctw[i][2]*d_cam[2]
                  for i in range(3)]
            mag = math.sqrt(dw[0]*dw[0] + dw[1]*dw[1] + dw[2]*dw[2])
            return [v / mag for v in dw] if mag > 1e-9 else None

        height = None
        height_source = "none"

        # ── Priority 1: derive height from Measurement Ref lines on ground ──
        if self._chk_use_ref.isChecked() and self._canvas._ref_lines and self._ref_value_spins:
            h_estimates = []
            for i, rl in enumerate(self._canvas._ref_lines):
                if i >= len(self._ref_value_spins):
                    break
                real_len = self._ref_value_spins[i].value()
                if real_len <= 0:
                    continue
                (x1, y1), (x2, y2) = rl.endpoints()
                d1 = _world_ray(x1, y1)
                d2 = _world_ray(x2, y2)
                if d1 is None or d2 is None:
                    continue
                if abs(d1[1]) < 1e-6 or abs(d2[1]) < 1e-6:
                    continue
                # hit_i = cam + (h / (-d_i.y)) * d_i  →  hit1-hit2 = h*(d1/(-d1.y) - d2/(-d2.y))
                dx = d1[0]/d1[1] - d2[0]/d2[1]
                dz = d1[2]/d1[1] - d2[2]/d2[1]
                span = math.sqrt(dx*dx + dz*dz)
                if span > 1e-9:
                    h_estimates.append(real_len / span)
            if h_estimates:
                height = sum(h_estimates) / len(h_estimates)
                height_source = "ref-lines"

        # ── Priority 2: explicit Camera Height override ──
        if height is None and self._chk_height.isChecked():
            h_val = self._height_spin.value()
            if h_val > 0:
                height = h_val
                height_source = "spin"

        # ── Priority 3: normalised fallback (no real-world info) ──
        if height is None:
            D = self._default_height_for_unit(self._scene_unit) * 10.0
            vx, vy, vz = -R_ctw[0][2], -R_ctw[1][2], -R_ctw[2][2]   # camera forward in world = R_ctw @ (0,0,-1)
            mag = math.sqrt(vx*vx + vy*vy + vz*vz)
            if mag < 1e-6:
                return False
            vx, vy, vz = vx/mag, vy/mag, vz/mag
            cam_pos = (-vx * D, max(-vy * D, D * 0.05), -vz * D)
            cmds.setAttr(f"{cam_transform}.translateX", cam_pos[0])
            cmds.setAttr(f"{cam_transform}.translateY", cam_pos[1])
            cmds.setAttr(f"{cam_transform}.translateZ", cam_pos[2])
            print(f"[CamMatchmaker] Position solved  [normalised fallback]  "
                  f"cam=({cam_pos[0]:.2f}, {cam_pos[1]:.2f}, {cam_pos[2]:.2f})")
            return True

        # ── Height-constrained ray-cast to Y=0 ground ──
        origin = self._canvas.get_origin_scene_pos()
        ox, oy = origin if origin is not None else (cx, cy)
        origin_label = f"({ox:.1f},{oy:.1f})" if origin else f"center({cx:.1f},{cy:.1f})"

        dw = _world_ray(ox, oy)
        if dw is None or abs(dw[1]) < 1e-6:
            print(f"[CamMatchmaker] Position failed — ray parallel to ground. "
                  f"dw={dw}, origin={origin_label}")
            return False
        cam_x = height * dw[0] / dw[1]
        cam_z = height * dw[2] / dw[1]
        cam_pos = (cam_x, height, cam_z)
        cmds.setAttr(f"{cam_transform}.translateX", cam_pos[0])
        cmds.setAttr(f"{cam_transform}.translateY", cam_pos[1])
        cmds.setAttr(f"{cam_transform}.translateZ", cam_pos[2])

        # ── FORWARD-PROJECTION VERIFICATION ──
        proj = _project_world_point((0.0, 0.0, 0.0), cam_pos, R_ctw, f_rel, w, h_img)
        if proj is None:
            print(f"[CamMatchmaker] Position solved  [BEHIND-CAMERA — rotation wrong]\n"
                  f"    origin_marker_px = {origin_label}\n"
                  f"    cam_pos = ({cam_x:.2f}, {height:.2f}, {cam_z:.2f})\n"
                  f"    height_source = {height_source}")
        else:
            err_px = math.sqrt((proj[0]-ox)**2 + (proj[1]-oy)**2)
            verdict = "OK" if err_px < 1.0 else f"MISMATCH {err_px:.2f}px"
            print(f"[CamMatchmaker] Position solved  [{verdict}]\n"
                  f"    origin_marker_px = {origin_label}\n"
                  f"    world(0,0,0) projects to ({proj[0]:.1f}, {proj[1]:.1f})\n"
                  f"    cam_pos = ({cam_x:.2f}, {height:.2f}, {cam_z:.2f})\n"
                  f"    height_source = {height_source}  f_rel = {f_rel:.4f}")
        return True

    def _add_image_plane(self):
        img_path = self._canvas.image_path
        if not img_path:
            self._set_status("err", "No image loaded.")
            return
        transform, shape = self._get_camera()
        if not shape:
            self._set_status("err", f"Camera not found: {self._cam_combo.currentText()}")
            return
        try:
            w_img, h_img = self._canvas.image_size
            if w_img and h_img:
                H_AP = 36.0 / 25.4
                cmds.setAttr(f"{shape}.horizontalFilmAperture", H_AP)
                cmds.setAttr(f"{shape}.verticalFilmAperture", H_AP * h_img / w_img)
            existing = cmds.listConnections(f"{shape}.imagePlane") or []
            if existing:
                ip_shapes = cmds.listRelatives(existing[0], shapes=True, fullPath=True) or []
                ip_shape = ip_shapes[0] if ip_shapes else None
                if not ip_shape:
                    _, ip_shape = cmds.imagePlane(camera=shape)
            else:
                _, ip_shape = cmds.imagePlane(camera=shape)
            cmds.setAttr(f"{ip_shape}.imageName", img_path.replace("\\", "/"), type="string")
            cmds.setAttr(f"{ip_shape}.displayMode", 2)
            cmds.setAttr(f"{ip_shape}.fit", 1)
            cmds.setAttr(f"{ip_shape}.alphaGain", 0.5)
            self._set_status("ok", f"Image plane set on {self._cam_combo.currentText()}")
        except Exception as e:
            self._set_status("err", f"Image plane failed: {e}")
            logger.exception("Image plane error")

    # ── Setup persistence ─────────────────────────────────────────────────

    @staticmethod
    def _sidecar_path(image_path):
        base = os.path.splitext(image_path)[0]
        return base + ".matchmaker.json"

    def _wire_autosave(self):
        """Connect every user-editable signal to the debounced autosave timer."""
        trigger = self._autosave_timer.start
        self._canvas.solveChanged.connect(trigger)
        self._canvas.refLineChanged.connect(trigger)
        self._canvas.originChanged.connect(trigger)
        self._canvas.originChanged.connect(lambda: self._refresh_grid())
        self._chk_height.toggled.connect(trigger)
        self._height_spin.valueChanged.connect(trigger)
        self._chk_lens.toggled.connect(trigger)
        self._focal_mm_spin.valueChanged.connect(trigger)
        self._chk_use_ref.toggled.connect(trigger)
        self._chk_fov.toggled.connect(trigger)
        self._chk_rot.toggled.connect(trigger)
        self._chk_pos.toggled.connect(trigger)
        self._chk_create_imgplane.toggled.connect(trigger)
        self._new_cam_name.textChanged.connect(trigger)

    def _autosave(self):
        """Silently write the sidecar — called by the debounced timer."""
        img_path = self._canvas.image_path
        if not img_path:
            return
        segs_x, segs_y, segs_z = self._canvas.get_axis_lines()
        origin = self._canvas.get_origin_scene_pos()
        data = {
            "version": "1",
            "image_path": img_path.replace("\\", "/"),
            "image_size": list(self._canvas.image_size),
            "axes": {
                "X": [[list(p[0]), list(p[1])] for p in segs_x],
                "Y": [[list(p[0]), list(p[1])] for p in segs_y],
                "Z": [[list(p[0]), list(p[1])] for p in segs_z],
            },
            "ref_lines": [
                {"ep": [[ep[0][0], ep[0][1]], [ep[1][0], ep[1][1]]],
                 "real_length": self._ref_value_spins[i].value() if i < len(self._ref_value_spins) else 200.0}
                for i, rl in enumerate(self._canvas._ref_lines)
                for ep in [rl.endpoints()]
            ],
            "origin": list(origin) if origin else None,
            "scale_ref": {
                "enabled": self._chk_use_ref.isChecked(),
            },
            "output": {
                "camera_height_enabled": self._chk_height.isChecked(),
                "camera_height": self._height_spin.value(),
                "camera_lens_enabled": self._chk_lens.isChecked(),
                "camera_lens_mm": self._focal_mm_spin.value(),
                "use_fov": self._chk_fov.isChecked(),
                "use_rotation": self._chk_rot.isChecked(),
                "use_position": self._chk_pos.isChecked(),
                "camera_name": self._new_cam_name.text(),
                "create_imgplane": self._chk_create_imgplane.isChecked(),
            },
        }
        sidecar = self._sidecar_path(img_path)
        try:
            with open(sidecar, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Autosave failed: {e}")

    def _save_setup(self):
        img_path = self._canvas.image_path
        if not img_path:
            self._set_status("err", "Load an image first.")
            return
        segs_x, segs_y, segs_z = self._canvas.get_axis_lines()
        origin = self._canvas.get_origin_scene_pos()
        data = {
            "version": "1",
            "image_path": img_path.replace("\\", "/"),
            "image_size": list(self._canvas.image_size),
            "axes": {
                "X": [[list(p[0]), list(p[1])] for p in segs_x],
                "Y": [[list(p[0]), list(p[1])] for p in segs_y],
                "Z": [[list(p[0]), list(p[1])] for p in segs_z],
            },
            "ref_lines": [
                {"ep": [[ep[0][0], ep[0][1]], [ep[1][0], ep[1][1]]],
                 "real_length": self._ref_value_spins[i].value() if i < len(self._ref_value_spins) else 200.0}
                for i, rl in enumerate(self._canvas._ref_lines)
                for ep in [rl.endpoints()]
            ],
            "origin": list(origin) if origin else None,
            "scale_ref": {
                "enabled": self._chk_use_ref.isChecked(),
            },
            "output": {
                "camera_height_enabled": self._chk_height.isChecked(),
                "camera_height": self._height_spin.value(),
                "camera_lens_enabled": self._chk_lens.isChecked(),
                "camera_lens_mm": self._focal_mm_spin.value(),
                "use_fov": self._chk_fov.isChecked(),
                "use_rotation": self._chk_rot.isChecked(),
                "use_position": self._chk_pos.isChecked(),
                "camera_name": self._new_cam_name.text(),
                "create_imgplane": self._chk_create_imgplane.isChecked(),
            },
        }
        sidecar = self._sidecar_path(img_path)
        try:
            with open(sidecar, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self._set_status("ok", f"Setup saved: {os.path.basename(sidecar)}")
        except Exception as e:
            self._set_status("err", f"Save failed: {e}")
            logger.exception("Save setup error")

    def _load_setup(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Load Setup", "", "Matchmaker Setup (*.matchmaker.json)"
        )
        if not path:
            return
        try:
            self._load_setup_from(path)
            self._set_status("ok", f"Setup loaded: {os.path.basename(path)}")
        except Exception as e:
            self._set_status("err", f"Load failed: {e}")
            logger.exception("Load setup error")

    def _load_setup_from(self, sidecar_path):
        with open(sidecar_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._canvas.clear_all_lines()
        axes = data.get("axes", {})
        for ep in axes.get("X", []):
            self._canvas.add_axis_line("X", ep[0][0], ep[0][1], ep[1][0], ep[1][1])
        for ep in axes.get("Y", []):
            self._canvas.add_axis_line("Y", ep[0][0], ep[0][1], ep[1][0], ep[1][1])
        for ep in axes.get("Z", []):
            self._canvas.add_axis_line("Z", ep[0][0], ep[0][1], ep[1][0], ep[1][1])
        # Support new multi-line format
        ref_lines = data.get("ref_lines", [])
        if not ref_lines:
            # backward-compat: single ref_line
            old = data.get("ref_line")
            if old:
                ref_lines = [{"ep": old, "real_length": data.get("scale_ref", {}).get("real_length", 200.0)}]
        for entry in ref_lines:
            ep = entry.get("ep", [])
            if len(ep) == 2:
                self._canvas.add_ref_line_endpoints(ep[0][0], ep[0][1], ep[1][0], ep[1][1])
        # Restore spinbox values after rebuilding the list
        self._rebuild_ref_list()
        for i, entry in enumerate(ref_lines):
            if i < len(self._ref_value_spins):
                self._ref_value_spins[i].setValue(entry.get("real_length", 200.0))
        origin = data.get("origin")
        if origin:
            self._canvas.set_origin(origin[0], origin[1])
            self._btn_set_origin.setChecked(True)
        else:
            self._btn_set_origin.setChecked(False)
        scale = data.get("scale_ref", {})
        self._chk_use_ref.setChecked(scale.get("enabled", False))
        out = data.get("output", {})
        default_h = self._default_height_for_unit(self._scene_unit)
        self._chk_height.setChecked(out.get("camera_height_enabled", False))
        self._height_spin.setValue(out.get("camera_height", default_h))
        self._chk_lens.setChecked(out.get("camera_lens_enabled", False))
        self._focal_mm_spin.setValue(out.get("camera_lens_mm", 35.0))
        self._chk_fov.setChecked(out.get("use_fov", True))
        self._chk_rot.setChecked(out.get("use_rotation", True))
        self._chk_pos.setChecked(out.get("use_position", True))
        if "camera_name" in out:
            self._new_cam_name.setText(out["camera_name"])
        if "create_imgplane" in out:
            self._chk_create_imgplane.setChecked(out["create_imgplane"])

    def _place_test_object(self):
        try:
            # Locator
            if cmds.objExists("MatchOrigin_loc"):
                cmds.delete("MatchOrigin_loc")
            loc = cmds.spaceLocator(name="MatchOrigin_loc")[0]
            cmds.setAttr(f"{loc}.localScaleX", 20)
            cmds.setAttr(f"{loc}.localScaleY", 20)
            cmds.setAttr(f"{loc}.localScaleZ", 20)

            # Reference cube (1×2×1 m default)
            if cmds.objExists("MatchOrigin_cube"):
                cmds.delete("MatchOrigin_cube")
            cube = cmds.polyCube(w=10, h=10, d=10, name="MatchOrigin_cube")[0]
            cmds.setAttr(f"{cube}.translateY", 5)  # sit on ground plane

            # Orange material
            mat_name = "MatchOrigin_mat"
            sg_name  = "MatchOrigin_matSG"
            if not cmds.objExists(mat_name):
                mat_name = cmds.shadingNode("lambert", asShader=True, name=mat_name)
                sg_name  = cmds.sets(
                    renderable=True, noSurfaceShader=True, empty=True, name=sg_name
                )
                cmds.connectAttr(f"{mat_name}.outColor", f"{sg_name}.surfaceShader", force=True)
            cmds.setAttr(f"{mat_name}.color", 0.91, 0.51, 0.05, type="double3")
            cmds.sets(cube, edit=True, forceElement=sg_name)

            # Group
            if cmds.objExists("MatchOrigin_grp"):
                cmds.delete("MatchOrigin_grp")
            grp = cmds.group(loc, cube, name="MatchOrigin_grp")

            cmds.select(grp)
            self._set_status(
                "ok",
                "MatchOrigin_grp created at (0,0,0). "
                "Look through the solved camera and check alignment against the reference photo."
            )
        except Exception as e:
            self._set_status("err", f"Test object failed: {e}")
            logger.exception("Place test object error")

    def _build_ground_grid_curves(self, cam_name="MatchCam"):
        """
        Build world-space ground grid curves at Y=0, centered at (0,0,0).
        Lines go in world X (red) and world Z (blue), matching the canvas overlay.
        Returns list of curve/locator names (ungrouped).
        """
        height = self._height_spin.value() if self._chk_height.isChecked() else 100.0
        step = height
        divisions = 8
        extent = step * divisions

        def _line(p1, p2, color):
            c = cmds.curve(d=1, p=[p1, p2], k=[0, 1])
            cmds.setAttr(f"{c}.overrideEnabled", 1)
            cmds.setAttr(f"{c}.overrideColor", color)
            return c

        curves = []

        # Lines running along world X (parallel to X axis, spaced along Z) — red
        for i in range(-divisions, divisions + 1):
            z = i * step
            color = 17 if i == 0 else 13  # yellow main axis, red parallels
            curves.append(_line((-extent, 0, z), (extent, 0, z), color))

        # Lines running along world Z (parallel to Z axis, spaced along X) — blue
        for i in range(-divisions, divisions + 1):
            x = i * step
            color = 17 if i == 0 else 6   # yellow main axis, blue parallels
            curves.append(_line((x, 0, -extent), (x, 0, extent), color))

        # Origin locator at (0,0,0)
        loc_name = f"{cam_name}_origin_loc"
        loc = cmds.spaceLocator(name=loc_name)[0]
        s = step * 0.5
        for ax in ("X", "Y", "Z"):
            cmds.setAttr(f"{loc}.localScale{ax}", s)
        cmds.setAttr(f"{loc}.overrideEnabled", 1)
        cmds.setAttr(f"{loc}.overrideColor", 17)
        curves.append(loc)

        return curves

    def _create_maya_grid(self):
        """Standalone grid creation from the Verify tab button."""
        try:
            if cmds.objExists("CamMatch_Grid"):
                cmds.delete("CamMatch_Grid")
            curves = self._build_ground_grid_curves("CamMatch")
            grp = cmds.group(curves, name="CamMatch_Grid")
            cmds.select(grp)
            height = self._height_spin.value() if self._chk_height.isChecked() else 100.0
            self._set_status("ok",
                f"CamMatch_Grid created at Y=0, origin at (0,0,0). "
                f"Step={height:.1f} {self._scene_unit}. "
                f"Red=X parallels  Blue=Z parallels  Yellow=axes & origin.")
        except Exception as e:
            self._set_status("err", f"Grid creation failed: {e}")
            logger.exception("Create maya grid error")

    def _set_status(self, state, msg):
        self._status_lbl.setText(msg)
        name = {"ok": "statusOk", "err": "statusErr", "warn": "statusWarn"}.get(state, "statusIdle")
        self._status_lbl.setObjectName(name)
        self._status_lbl.setStyle(self._status_lbl.style())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    # Close any existing instance (including stale versions) before opening fresh
    _old_names = {WINDOW_OBJECT_NAME,
                  "PXLmentorCameraMatchmaker_v010",
                  "PXLmentorCameraMatchmaker_v020"}
    for w in app.topLevelWidgets():
        try:
            if w.objectName() in _old_names:
                w.close()
                w.deleteLater()
        except RuntimeError:
            pass
    win = CameraMatchmaker()
    win.show()
    win.raise_()
    return win


run()
