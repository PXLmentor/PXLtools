"""
GLB Manager v0.3.0-alpha

Purpose:    Unified GLB / glTF import & export manager for Maya — parse/build
            geometry, ORM texture extraction, Arnold PBR materials, glTF 2.0
            binary writing, and a live scene-hierarchy panel.
Author:     Cristian Spagnuolo
Date:       2026-06-15
Stack:      Maya 2025
Python:     3.11
Depends:    PySide6, shiboken6, maya.cmds, maya.api.OpenMaya, mtoa (optional),
            PIL/Pillow (optional, ORM split/pack), pxl_ui (shared kit)

Description:
    IMPORT — Parse GLB/GLTF binary, build mesh geometry via OpenMaya2, extract &
    split ORM textures, create Arnold PBR materials with the ACES pipeline, place
    asset on the ground plane, optional 1m reference cube.
    EXPORT — Export selected Maya meshes and cameras to GLB binary. Reads
    Arnold/lambert shading networks, embeds textures, packs ORM channels
    (Pillow), writes valid glTF 2.0 binary.
    SCENE PANEL — Indented scene hierarchy browser; select, hide/show assets in
    the Maya scene directly from the tool.

    Migrated to the shared PXLtools pxl_ui UI/UX standard (one shared stylesheet +
    AppHeader + shared collapsible/section look); 100% of the import/export/
    binary/material logic is unchanged from v0.1.8-alpha — only the UI chrome was
    migrated. The dual-tab IMPORT | EXPORT | SCENE QTabWidget structure is kept;
    the tab bar is now styled by tool_qss.

    v0.3.0-alpha is a full STANDARD-compliance rework of the UI chrome and the
    guided flow ONLY — every byte of the import/export/binary/material/scene CORE
    LOGIC is preserved verbatim from v0.2.0-alpha.

Changelog:
    0.3.0-alpha - STANDARD.md compliance rework (§1 colours, §2 structure,
            §3 step-gating). UI-chrome + guided-flow ONLY; import/export/scene
            core logic byte-for-byte unchanged:
              - Deleted the bespoke fallback header block (hard-coded #333333 /
                rgb(51,51,51) / white / #aaaaaa inline colours). The header is
                now ONLY pxlw.AppHeader(tool_name, version, icon_path) — exactly
                like TurnTable. Tool icon resolved to the deployed
                icon_glb_manager.png (fallback icon_glb_importer.png).
              - Removed EVERY remaining inline/hard-coded colour setStyleSheet:
                the two QProgressBar stylesheets are gone (bars rely on tool_qss);
                shader/color-space field labels are now objectName "ctrlLabel"
                (no inline font/colour QSS). Combos rely on tool_qss only.
              - Guided, numbered, gated step-gating added to BOTH the IMPORT and
                EXPORT tabs, replicating the TurnTable mechanism exactly: shared
                helpers _repolish / _mk_step_badge / _mk_step_confirm /
                _mk_step_header / _set_badge / _set_step_btn / _set_confirm /
                _btn_obj, objectNames btnStepActive/btnStepDone/btnStepLocked and
                badges stepReady/stepDone/stepLocked/stepTitle/stepConfirmDone/
                stepConfirmEmpty, plus per-tab state machines
                _update_import_steps() / _update_export_steps() called at every
                real success point and on reset (state derived from REALITY;
                future steps setEnabled(False)).
                IMPORT  : 1 Browse GLB file -> 2 Confirm options -> 3 Import.
                EXPORT  : 1 Select objects  -> 2 Confirm output  -> 3 Export.
              - _make_section_frame now returns a small _SectionFrame object with
                set_state('idle'|'active'|'done') so each section reflects
                progress, matching CollapsibleSection.set_state in TurnTable.
              - A per-tab instruction line: "Follow the numbers — the orange step
                is what to do next; it turns green when done."
            File renamed PXLtools_GLB_Manager_v0_2_0_alpha.py ->
            PXLtools_GLB_Manager_v0_3_0_alpha.py.
    0.2.0-alpha - Migrated the UI to the shared PXLtools pxl_ui kit, EXACTLY
            mirroring the gold-standard PXLtools TurnTable Builder and the
            just-migrated PBR Material sibling:
              - imports pxl_ui (theme/widgets/icons + pxl_update) with the same
                bootstrap + reload + _PXLUI availability flag pattern;
              - removed the bespoke `class _C` colour-token class and the inline
                MAIN_QSS; MAIN_QSS is now pxlt.tool_qss() with the icon tokens
                (__CHECK__, __SPINUP__, __SPINDOWN__, __SPINUPH__, __SPINDOWNH__,
                __SLH__, __SLHH__) substituted with generated PNG paths via the
                shared _resolved_qss() helper (space-free temp dir);
              - bespoke CollapsibleSection replaced with the shared
                pxlw.CollapsibleSection (grey header bar, accent, chevron) +
                _make_section_frame thin always-open wrapper using the same look;
              - bespoke _build_header replaced with pxlw.AppHeader(...), graceful
                fallback when pxl_ui is unavailable;
              - the IMPORT | EXPORT | SCENE QTabWidget is kept verbatim — the tab
                bar is now styled by tool_qss (folder-style tabs, single source);
              - the scene-hierarchy QListWidget panel logic is unchanged; only its
                styling is now via tool_qss objectNames (no bespoke colours);
              - shader / colour-space combos rely on tool_qss ONLY (single native
                arrow) — removed the per-widget QComboBox stylesheets that would
                have caused the double-arrow bug;
              - inline browse/action buttons and their paired line-edits share one
                height (32px) and are vertically centred;
              - _FlatTextStyle proxy applied on the dialog (kills host etch);
              - auto-update wired on launch via pxl_update.check (deferred, once/day).
            File renamed PXLmentor_GLB_Manager_v0_1_8_alpha.py ->
            PXLtools_GLB_Manager_v0_2_0_alpha.py; window title -> "GLB Manager".
            All import/export/binary/material/scene logic preserved verbatim.
    0.1.8-alpha - PXLtools branding pass: in-tool header logo swapped
                 from PixelMentor_Logo_Long.png to PXLtools_logo.png.
                 Fallback text label changed to "PXLtools".
    0.1.7-alpha - CP008: Conform to PXLMENTOR_TOOL_STANDARD v1.1.0 - removed
                  the 96x96 right-spacer from _build_header so the PXLmentor
                  logo centers in the visible content area.
    0.1.6-alpha - CP007: Full PySide6 QDialog migration — same dark theme as
                  TurnTable Builder v1.0.5. Replaced cmds.window + all cmds
                  widgets with QDialog + QTabWidget + Qt equivalents.
    0.1.5-alpha - CP006: Opacity support — import and export (alphaMode BLEND,
                  baseColorFactor alpha → opacity/transparency).
    0.1.4-alpha - CP005: Texture embed robustness fix (per-attr / per-mesh
                  try/except so a single failure can't abort the export loop).
    0.1.3-alpha - CP004: Material colour export + texture checkbox clarification.
    0.1.2-alpha - CP003: selectAll flag fix (textScrollList Maya 2025).
    0.1.1-alpha - CP002: Duplicate-name robustness pass.
    0.1.0-alpha - CP001: Initial unified GLB Manager (IMPORT | EXPORT tabs +
                  Scene panel), combined GLB Importer v0.9.1-beta with new
                  GLB Exporter.

Usage:
    Paste this script into the Maya Script Editor (Python tab) and press Ctrl+Enter,
    or launch it from the PXLtools shelf.
"""

import maya.cmds as cmds
import maya.api.OpenMaya as om2
import math
import struct
import json
import os
import sys
import base64
import logging


# =============================================================================
# LOGGER
# =============================================================================

_log = logging.getLogger("PXLtools.GLBManager")
_log.setLevel(logging.DEBUG)
if not _log.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(
        logging.Formatter("[PXLtools GLB Manager] %(levelname)s: %(message)s")
    )
    _log.addHandler(_h)


# =============================================================================
# TOOL IDENTITY
# =============================================================================

TOOL_NAME          = "GLB Manager"
VERSION            = "0.4.0-alpha"
WINDOW_OBJECT_NAME = "PXLtoolsGLBManager_v040"
ICON_NAME          = "icon_glb_manager.png"
ICON_FALLBACK      = "icon_glb_importer.png"


# =============================================================================
# pxl_ui shared kit bootstrap (Maya 2025 PySide6 / Nuke 15 PySide2 compatible)
# =============================================================================
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


# =============================================================================
# COLOR SPACE TABLES
# =============================================================================

CS_ACES = {
    "DIFF": "Utility - sRGB - Texture",
    "MTL":  "Utility - Raw",
    "RGH":  "Utility - Raw",
    "NRM":  "Utility - Raw",
}
CS_STANDARD = {
    "DIFF": "sRGB",
    "MTL":  "Raw",
    "RGH":  "Raw",
    "NRM":  "Raw",
}

P2D_CONNECTIONS = [
    ('coverage',        'coverage'),
    ('translateFrame',  'translateFrame'),
    ('rotateFrame',     'rotateFrame'),
    ('mirrorU',         'mirrorU'),
    ('mirrorV',         'mirrorV'),
    ('stagger',         'stagger'),
    ('wrapU',           'wrapU'),
    ('wrapV',           'wrapV'),
    ('repeatUV',        'repeatUV'),
    ('offset',          'offset'),
    ('rotateUV',        'rotateUV'),
    ('noiseUV',         'noiseUV'),
    ('vertexUvOne',     'vertexUvOne'),
    ('vertexUvTwo',     'vertexUvTwo'),
    ('vertexUvThree',   'vertexUvThree'),
    ('vertexCameraOne', 'vertexCameraOne'),
    ('outUV',           'uv'),
    ('outUvFilterSize', 'uvFilterSize'),
]


# =============================================================================
# ──────────────────────────── IMPORT CORE ────────────────────────────────────
# =============================================================================

def parse_glb(path):
    """Parse a GLB binary container and return (gltf_dict, blob_bytes)."""
    with open(path, "rb") as f:
        data = f.read()
    if struct.unpack_from("<I", data, 0)[0] != 0x46546C67:
        raise RuntimeError("Not a valid GLB file.")
    gltf, blob = {}, b""
    offset = 12
    while offset < len(data) - 8:
        clen, ctype = struct.unpack_from("<II", data, offset)
        offset += 8
        chunk = data[offset: offset + clen]
        offset += clen
        if   ctype == 0x4E4F534A:
            gltf = json.loads(chunk.decode("utf-8"))
        elif ctype == 0x004E4942:
            blob = chunk
    return gltf, blob


def read_accessor(gltf, blob, idx):
    """Read a glTF accessor and return a flat list of component values."""
    TC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
    CF = {5120: "b", 5121: "B", 5122: "h", 5123: "H", 5125: "I", 5126: "f"}
    a      = gltf["accessors"][idx]
    bv     = gltf["bufferViews"][a["bufferView"]]
    nc     = TC[a["type"]]
    fmt    = CF[a["componentType"]]
    isize  = struct.calcsize(fmt) * nc
    bv_off = bv.get("byteOffset", 0)
    a_off  = a.get("byteOffset", 0)
    stride = bv.get("byteStride", isize)
    vals   = []
    for i in range(a["count"]):
        p = bv_off + a_off + i * stride
        vals.extend(struct.unpack_from("<" + fmt * nc, blob[p: p + isize]))
    return vals


# ── Texture extraction ────────────────────────────────────────────────────────

def get_image_bytes(gltf, blob, img_idx):
    """Return (raw_bytes, mime_type) for an image embedded in a GLB."""
    img = gltf["images"][img_idx]
    if "bufferView" in img:
        bv = gltf["bufferViews"][img["bufferView"]]
        s  = bv.get("byteOffset", 0)
        return blob[s: s + bv["byteLength"]], img.get("mimeType", "image/png")
    if "uri" in img:
        uri = img["uri"]
        if uri.startswith("data:"):
            hdr, b64 = uri.split(",", 1)
            return base64.b64decode(b64), hdr.split(";")[0].replace("data:", "")
    return None, None


def extract_textures(gltf, blob, asset_name, out_dir):
    """
    Extract PBR textures from the first GLB material into out_dir.

    Splits ORM (metallicRoughness) into MTL/RGH channels when Pillow is
    available; saves the packed ORM file otherwise.
    Returns a dict mapping slot keys to file paths.
    """
    try:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
    except Exception as exc:
        _log.error("Could not create texture output directory '%s': %s", out_dir, exc)
        return {}

    result    = {}
    materials = gltf.get("materials", [])
    if not materials:
        _log.warning("No materials found in GLB.")
        return result

    mat = materials[0]
    pbr = mat.get("pbrMetallicRoughness", {})

    # Base colour factor + alpha mode ─────────────────────────────────────────
    bcf = pbr.get("baseColorFactor", [1.0, 1.0, 1.0, 1.0])
    # Normalise to list of 4 floats regardless of source format
    while len(bcf) < 4:
        bcf.append(1.0)
    result["BASE_COLOR"] = [float(v) for v in bcf[:4]]
    result["ALPHA_MODE"] = mat.get("alphaMode", "OPAQUE")

    # DIFF ────────────────────────────────────────────────────────────────────
    bc_tex = pbr.get("baseColorTexture", {})
    if "index" in bc_tex:
        img_idx = gltf["textures"][bc_tex["index"]]["source"]
        raw, mime = get_image_bytes(gltf, blob, img_idx)
        if raw:
            ext  = ".jpg" if (mime and "jpeg" in mime) else ".png"
            path = os.path.join(out_dir, asset_name + "_DIFF" + ext)
            try:
                with open(path, "wb") as f:
                    f.write(raw)
                result["DIFF"] = path
                _log.info("DIFF -> %s", os.path.basename(path))
            except Exception as exc:
                _log.error("Failed to write DIFF texture: %s", exc)

    # MTL + RGH (ORM packed) ──────────────────────────────────────────────────
    mr_tex = pbr.get("metallicRoughnessTexture", {})
    if "index" in mr_tex:
        img_idx = gltf["textures"][mr_tex["index"]]["source"]
        raw, mime = get_image_bytes(gltf, blob, img_idx)
        if raw:
            try:
                import io
                from PIL import Image as PI
                with PI.open(io.BytesIO(raw)) as im:
                    _r, g, b_ch = im.convert("RGB").split()
                    mtl_path = os.path.join(out_dir, asset_name + "_MTL.png")
                    rgh_path = os.path.join(out_dir, asset_name + "_RGH.png")
                    b_ch.save(mtl_path)
                    g.save(rgh_path)
                    result["MTL"] = mtl_path
                    result["RGH"] = rgh_path
                    _log.info("MTL -> %s", os.path.basename(mtl_path))
                    _log.info("RGH -> %s", os.path.basename(rgh_path))
            except ImportError:
                ext      = ".jpg" if (mime and "jpeg" in mime) else ".png"
                orm_path = os.path.join(out_dir, asset_name + "_ORM" + ext)
                try:
                    with open(orm_path, "wb") as f:
                        f.write(raw)
                    result["ORM"] = orm_path
                    _log.warning(
                        "ORM saved unsplit (Pillow not available): %s",
                        os.path.basename(orm_path)
                    )
                except Exception as exc:
                    _log.error("Failed to write ORM texture: %s", exc)
            except Exception as exc:
                _log.error("ORM split failed: %s", exc)

    # NRM ─────────────────────────────────────────────────────────────────────
    nrm_tex = mat.get("normalTexture", {})
    if "index" in nrm_tex:
        img_idx = gltf["textures"][nrm_tex["index"]]["source"]
        raw, mime = get_image_bytes(gltf, blob, img_idx)
        if raw:
            ext  = ".jpg" if (mime and "jpeg" in mime) else ".png"
            path = os.path.join(out_dir, asset_name + "_NRM" + ext)
            try:
                with open(path, "wb") as f:
                    f.write(raw)
                result["NRM"] = path
                _log.info("NRM -> %s", os.path.basename(path))
            except Exception as exc:
                _log.error("Failed to write NRM texture: %s", exc)

    return result


# ── Material builder ──────────────────────────────────────────────────────────

def _make_file_node(node_name, tex_path, color_space):
    """Create a Maya file node wired to a new place2dTexture."""
    file_node = cmds.shadingNode('file', asTexture=True, name=node_name)
    cmds.setAttr("{}.fileTextureName".format(file_node), tex_path, type="string")
    cmds.setAttr("{}.colorSpace".format(file_node), color_space, type="string")
    place2d = cmds.shadingNode('place2dTexture', asUtility=True,
                               name=node_name + "_p2d")
    for src, dst in P2D_CONNECTIONS:
        cmds.connectAttr(
            "{}.{}".format(place2d, src),
            "{}.{}".format(file_node, dst),
            force=True
        )
    return file_node


def create_material(asset_name, tex_map, shader_type="aiStandardSurface",
                    use_aces=True):
    """
    Build an Arnold (or lambert fallback) PBR material from a texture map dict.
    Returns (shader_node, shading_group).
    """
    cs = CS_ACES if use_aces else CS_STANDARD

    if shader_type == "aiStandardSurface":
        if not cmds.pluginInfo('mtoa', query=True, loaded=True):
            try:
                cmds.loadPlugin('mtoa')
            except Exception:
                _log.warning("Arnold not available — falling back to lambert.")
                shader_type = "lambert"

    mat_name  = asset_name + "_MAT"
    is_arnold = (shader_type == "aiStandardSurface")

    shader = cmds.shadingNode(shader_type, asShader=True, name=mat_name)
    sg     = cmds.sets(renderable=True, noSurfaceShader=True,
                       empty=True, name=mat_name + "_SG")
    cmds.connectAttr("{}.outColor".format(shader),
                     "{}.surfaceShader".format(sg), force=True)

    # Flat base colour + opacity from baseColorFactor ─────────────────────────
    if "BASE_COLOR" in tex_map:
        r, g, b, a = tex_map["BASE_COLOR"]
        # Apply RGB only when no DIFF texture (texture overrides colour)
        if "DIFF" not in tex_map:
            if is_arnold:
                cmds.setAttr("{}.baseColor".format(shader), r, g, b, type="double3")
            else:
                cmds.setAttr("{}.color".format(shader), r, g, b, type="double3")
        # Apply opacity regardless — alpha multiplies the final result in glTF
        alpha_mode = tex_map.get("ALPHA_MODE", "OPAQUE")
        if alpha_mode in ("BLEND", "MASK") or a < 0.999:
            if is_arnold:
                cmds.setAttr("{}.opacity".format(shader), a, a, a, type="double3")
            else:
                t = 1.0 - a
                cmds.setAttr("{}.transparency".format(shader), t, t, t, type="double3")

    if "DIFF" in tex_map:
        fn  = _make_file_node(mat_name + "_DIFF_file", tex_map["DIFF"], cs["DIFF"])
        tgt = ("{}.baseColor".format(shader) if is_arnold
               else "{}.color".format(shader))
        cmds.connectAttr("{}.outColor".format(fn), tgt, force=True)

    if is_arnold and "MTL" in tex_map:
        fn = _make_file_node(mat_name + "_MTL_file", tex_map["MTL"], cs["MTL"])
        cmds.connectAttr("{}.outColorR".format(fn),
                         "{}.metalness".format(shader), force=True)

    if is_arnold and "RGH" in tex_map:
        fn = _make_file_node(mat_name + "_RGH_file", tex_map["RGH"], cs["RGH"])
        cmds.connectAttr("{}.outColorR".format(fn),
                         "{}.specularRoughness".format(shader), force=True)

    if is_arnold and "ORM" in tex_map and "MTL" not in tex_map:
        fn = _make_file_node(mat_name + "_ORM_file", tex_map["ORM"], cs["MTL"])
        cmds.connectAttr("{}.outColorB".format(fn),
                         "{}.metalness".format(shader), force=True)
        cmds.connectAttr("{}.outColorG".format(fn),
                         "{}.specularRoughness".format(shader), force=True)

    if "NRM" in tex_map:
        fn = _make_file_node(mat_name + "_NRM_file", tex_map["NRM"], cs["NRM"])
        if is_arnold:
            nm = cmds.shadingNode('aiNormalMap', asUtility=True,
                                  name=mat_name + "_aiNormalMap")
            cmds.connectAttr("{}.outColor".format(fn),
                             "{}.input".format(nm), force=True)
            cmds.connectAttr("{}.outValue".format(nm),
                             "{}.normalCamera".format(shader), force=True)
        else:
            bump = cmds.shadingNode('bump2d', asUtility=True,
                                    name=mat_name + "_bump2d")
            cmds.setAttr("{}.bumpDepth".format(bump), 1.0)
            cmds.connectAttr("{}.outAlpha".format(fn),
                             "{}.bumpValue".format(bump), force=True)
            cmds.connectAttr("{}.outNormal".format(bump),
                             "{}.normalCamera".format(shader), force=True)

    _log.info("Material created: %s  (type=%s, aces=%s)", mat_name, shader_type, use_aces)
    return shader, sg


# ── Mesh builder ──────────────────────────────────────────────────────────────

def build_mesh(name, positions, uvs, indices):
    """
    Build a Maya mesh from raw position/UV/index data via OpenMaya2.
    Returns (transform_name, shape_name).
    """
    nv  = len(positions) // 3
    nt  = len(indices)   // 3
    huv = len(uvs) >= nv * 2

    verts = om2.MFloatPointArray()
    for i in range(nv):
        verts.append(om2.MFloatPoint(
            positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2]
        ))

    fn   = om2.MFnMesh()
    mobj = fn.create(verts,
                     om2.MIntArray([3] * nt),
                     om2.MIntArray(indices))

    dag   = om2.MDagPath.getAPathTo(mobj)
    xform = cmds.rename(om2.MFnDagNode(dag.transform()).name(), name)
    shapes = cmds.listRelatives(xform, shapes=True, type="mesh") or []
    shape  = cmds.rename(shapes[0], name + "Shape") if shapes else xform

    if huv:
        u_arr = om2.MFloatArray([uvs[i * 2]           for i in range(nv)])
        v_arr = om2.MFloatArray([1.0 - uvs[i * 2 + 1] for i in range(nv)])
        sel   = om2.MSelectionList()
        sel.add(shape)
        fn2 = om2.MFnMesh(sel.getDagPath(0))
        fn2.setUVs(u_arr, v_arr)
        fn2.assignUVs(om2.MIntArray([3] * nt), om2.MIntArray(indices))

    return xform, shape


# ── Placement ─────────────────────────────────────────────────────────────────

def place_on_ground(root):
    """Move pivot to base centre and translate so pivot sits at world origin."""
    bb = cmds.exactWorldBoundingBox(root)
    xmin, ymin, zmin, xmax, ymax, zmax = bb
    cx     = (xmin + xmax) * 0.5
    cz     = (zmin + zmax) * 0.5
    base_y = ymin
    cmds.xform(root, worldSpace=True, pivots=[cx, base_y, cz])
    cmds.move(-cx, -base_y, -cz, root, worldSpace=True, absolute=True)
    _log.info("Placed: bbox base=(%.3f, %.3f, %.3f) -> world origin", cx, base_y, cz)


def create_reference_cube(asset_name):
    """Create a 1m x 1m x 1m reference cube sitting on Y=0."""
    UNIT_TO_METRE = {
        "mm": 0.001, "millimeter": 0.001,
        "cm": 0.01,  "centimeter": 0.01,
        "m":  1.0,   "meter":      1.0,
        "km": 1000.0,"kilometer":  1000.0,
        "in": 0.0254,"inch":       0.0254,
        "ft": 0.3048,"foot":       0.3048,
        "yd": 0.9144,"yard":       0.9144,
    }
    unit      = cmds.currentUnit(query=True, linear=True)
    factor    = UNIT_TO_METRE.get(unit, 1.0)
    size_maya = 1.0 / factor
    cube, _   = cmds.polyCube(w=size_maya, h=size_maya, d=size_maya,
                               name="Cube_REF_1mt")
    cmds.move(size_maya, size_maya * 0.5, 0, cube, worldSpace=True, absolute=True)
    cmds.makeIdentity(cube, apply=True, translate=True)
    _log.info("Reference cube: %s  (1m = %.4f %s)", cube, size_maya, unit)
    return cube


# ── Import pipeline ───────────────────────────────────────────────────────────

def import_glb(path, asset_name,
               import_uvs, extract_tex, tex_dir,
               create_mat, shader_type, use_aces,
               ref_cube,
               prog_cb=None):
    """
    Full GLB import pipeline.
    Returns (root_group_name, texture_result_dict).
    """
    def step(msg):
        _log.debug("STEP: %s", msg)
        if prog_cb:
            prog_cb(msg)

    _log.info("=== GLB Manager — Import  v%s ===", VERSION)
    _log.info("File : %s", path)
    _log.info("Name : %s", asset_name)

    step("Parsing GLB…")
    gltf, blob = parse_glb(path)
    nodes  = gltf.get("nodes",  [])
    meshes = gltf.get("meshes", [])

    step("Building mesh geometry…")
    root = cmds.group(empty=True, name=asset_name + "_GRP")
    used = set()
    ok   = 0

    for node in nodes:
        if "mesh" not in node:
            continue
        mesh = meshes[node["mesh"]]
        for pi, prim in enumerate(mesh.get("primitives", [])):
            attrs = prim.get("attributes", {})
            if "POSITION" not in attrs or "indices" not in prim:
                continue

            positions = read_accessor(gltf, blob, attrs["POSITION"])
            indices   = read_accessor(gltf, blob, prim["indices"])
            uvs       = (
                read_accessor(gltf, blob, attrs["TEXCOORD_0"])
                if (import_uvs and "TEXCOORD_0" in attrs) else []
            )

            name   = asset_name if ok == 0 else "{}_{}".format(asset_name, ok)
            suffix = ok
            while name in used:
                suffix += 1
                name = "{}_{}".format(asset_name, suffix)
            used.add(name)

            step("Importing mesh '{}' ({} verts, {} tris)…".format(
                name, len(positions) // 3, len(indices) // 3))

            try:
                xform, _ = build_mesh(name, positions, uvs, indices)
                cmds.parent(xform, root)
                ok += 1
            except Exception as exc:
                _log.exception("Mesh build failed for '%s': %s", name, exc)

    step("Setting pivot and placing on ground…")
    place_on_ground(root)

    tex_result = {}
    if extract_tex and tex_dir:
        step("Extracting textures…")
        try:
            tex_result = extract_textures(gltf, blob, asset_name, tex_dir)
        except Exception as exc:
            _log.exception("Texture extraction failed: %s", exc)

    sg = None
    if create_mat:
        step("Creating material ({})…".format(shader_type))
        try:
            _, sg = create_material(asset_name, tex_result, shader_type, use_aces)
        except Exception as exc:
            _log.exception("Material creation failed: %s", exc)

    if sg:
        step("Assigning material…")
        all_transforms = cmds.listRelatives(
            root, allDescendents=True, type="transform", fullPath=True
        ) or []
        all_transforms.append(root)
        mesh_shapes = []
        for xf in all_transforms:
            mesh_shapes.extend(
                cmds.listRelatives(xf, shapes=True, type="mesh", fullPath=True) or []
            )
        for sh in mesh_shapes:
            cmds.sets(sh, edit=True, forceElement=sg)
        _log.info("Material assigned to %d shape(s).", len(mesh_shapes))

    if ref_cube:
        step("Creating 1m reference cube…")
        create_reference_cube(asset_name)

    step("Done!")
    cmds.select(root)
    _log.info("Root: %s  Meshes: %d", root, ok)
    _log.info("=== Import complete ===")
    return root, tex_result


# =============================================================================
# ──────────────────────────── EXPORT CORE ────────────────────────────────────
# =============================================================================

def get_mesh_triangles(transform_name, export_normals=True, export_uvs=True):
    """
    Extract triangulated mesh data from a Maya transform via OpenMaya2.

    Returns (positions, normals, uvs, indices) — all expanded to
    per-face-vertex (no vertex sharing).  World space.
    positions : flat float list [x,y,z, ...]
    normals   : flat float list [x,y,z, ...] or []
    uvs       : flat float list [u,v, ...]   or []
    indices   : sequential int list [0,1,2, ...]
    """
    sel = om2.MSelectionList()
    try:
        sel.add(transform_name)
    except Exception:
        _log.error("get_mesh_triangles: node not found: %s", transform_name)
        return [], [], [], []

    dag = sel.getDagPath(0)
    try:
        dag.extendToShape()
    except Exception:
        _log.error("get_mesh_triangles: no shape on %s", transform_name)
        return [], [], [], []

    if dag.apiType() != om2.MFn.kMesh:
        _log.error("get_mesh_triangles: shape is not a mesh: %s", transform_name)
        return [], [], [], []

    fn = om2.MFnMesh(dag)

    all_pts      = fn.getPoints(om2.MSpace.kWorld)
    tri_counts, tri_verts = fn.getTriangles()

    has_uvs = export_uvs and fn.numUVs() > 0
    u_arr, v_arr = (fn.getUVs() if has_uvs else ([], []))

    positions = []
    normals   = []
    uvs       = []
    indices   = []
    vert_idx  = 0
    tri_offset = 0

    for poly_idx in range(fn.numPolygons):
        n_tris     = tri_counts[poly_idx]
        poly_verts = fn.getPolygonVertices(poly_idx)

        for t in range(n_tris):
            for corner in range(3):
                mesh_vert = tri_verts[tri_offset + t * 3 + corner]

                pt = all_pts[mesh_vert]
                positions.extend([pt.x, pt.y, pt.z])

                if export_normals:
                    try:
                        nrm = fn.getFaceVertexNormal(
                            poly_idx, mesh_vert, om2.MSpace.kWorld
                        )
                        normals.extend([nrm.x, nrm.y, nrm.z])
                    except Exception:
                        normals.extend([0.0, 1.0, 0.0])

                if has_uvs:
                    fv_idx = next(
                        (i for i, v in enumerate(poly_verts) if v == mesh_vert),
                        None
                    )
                    if fv_idx is not None:
                        try:
                            uv_id = fn.getPolygonUVid(poly_idx, fv_idx)
                            if 0 <= uv_id < len(u_arr):
                                uvs.extend([u_arr[uv_id], 1.0 - v_arr[uv_id]])
                            else:
                                uvs.extend([0.0, 0.0])
                        except Exception:
                            uvs.extend([0.0, 0.0])
                    else:
                        uvs.extend([0.0, 0.0])

                indices.append(vert_idx)
                vert_idx += 1

        tri_offset += n_tris * 3

    return positions, normals if export_normals else [], uvs, indices


def get_camera_data(transform_name):
    """
    Read perspective camera data from a Maya camera transform.

    Returns a dict or None if the transform has no camera shape.
    Keys: name, yfov (radians), aspect_ratio, znear, zfar, matrix (16 floats).

    Matrix note: Maya xform ws matrix flat layout (row-major) is numerically
    identical to glTF column-major layout for the same transformation, so no
    transposition is needed.
    """
    shapes = cmds.listRelatives(transform_name, shapes=True, type='camera') or []
    if not shapes:
        return None
    cam = shapes[0]

    try:
        vfov_deg = cmds.camera(cam, query=True, verticalFieldOfView=True)
    except Exception:
        fl    = cmds.getAttr(cam + '.focalLength')
        haperture = cmds.getAttr(cam + '.horizontalFilmAperture') * 25.4
        vaperture = cmds.getAttr(cam + '.verticalFilmAperture')   * 25.4
        vfov_deg  = math.degrees(2.0 * math.atan(vaperture * 0.5 / fl))

    yfov = math.radians(vfov_deg)

    try:
        width  = cmds.getAttr('defaultResolution.width')
        height = cmds.getAttr('defaultResolution.height')
        aspect = float(width) / float(height) if height else (16.0 / 9.0)
    except Exception:
        aspect = 16.0 / 9.0

    znear  = cmds.getAttr(cam + '.nearClipPlane')
    zfar   = cmds.getAttr(cam + '.farClipPlane')
    matrix = cmds.xform(transform_name, query=True, worldSpace=True, matrix=True)

    return {
        'name':         transform_name,
        'yfov':         yfov,
        'aspect_ratio': aspect,
        'znear':        znear,
        'zfar':         zfar,
        'matrix':       matrix,
    }


def collect_material_data(transform_name):
    """
    Read the shading network from a mesh transform.

    Always returns base_color (flat RGBA from the shader) so every mesh gets
    a distinguishable material even without file textures.
    File texture paths (DIFF / MTL / RGH / NRM) are added when connected
    file nodes are found on disk.

    Supported shader types: lambert, blinn, phong, phongE, aiStandardSurface.
    Falls back to neutral grey for unknown shader types.

    Returns dict:
        shader_name : str  — Maya shader node name
        base_color  : [r, g, b, a]  — flat colour, 0-1 linear
        DIFF / MTL / RGH / NRM : file paths (optional, only when found)
    """
    result = {
        'shader_name': transform_name + '_MAT',
        'base_color':  [0.5, 0.5, 0.5, 1.0],
    }

    shapes = cmds.listRelatives(transform_name, shapes=True,
                                type='mesh', fullPath=True) or []
    if not shapes:
        return result

    sgs = cmds.listConnections(shapes[0], type='shadingEngine') or []
    if not sgs:
        return result

    shaders = cmds.listConnections(
        sgs[0] + '.surfaceShader', source=True, destination=False
    ) or []
    if not shaders:
        return result

    shader      = shaders[0]
    shader_type = cmds.nodeType(shader)
    result['shader_name'] = shader

    # ── Read flat base colour ─────────────────────────────────────────────────

    def _read_rgb(attr):
        """Return [r, g, b] from a colour attribute, or None on failure."""
        try:
            raw = cmds.getAttr('{}.{}'.format(shader, attr))
            return [float(raw[0][0]), float(raw[0][1]), float(raw[0][2])]
        except Exception:
            return None

    def _read_scalar(attr):
        """Return a single float attribute value, or None on failure."""
        try:
            return float(cmds.getAttr('{}.{}'.format(shader, attr)))
        except Exception:
            return None

    if shader_type == 'aiStandardSurface':
        rgb = _read_rgb('baseColor')
        if rgb:
            # opacity: RGB, 1.0 = fully opaque (not inverted like transparency)
            op_raw = _read_rgb('opacity')
            alpha  = op_raw[0] if op_raw else 1.0
            result['base_color'] = rgb + [alpha]

    elif shader_type in ('lambert', 'blinn', 'phong', 'phongE', 'anisotropic'):
        rgb = _read_rgb('color')
        if rgb:
            # transparency: 0 = opaque, 1 = fully transparent → invert
            t_raw  = _read_rgb('transparency')
            alpha  = 1.0 - t_raw[0] if t_raw else 1.0
            result['base_color'] = rgb + [alpha]

    else:
        # Generic fallback — attempt 'color' attribute
        rgb = _read_rgb('color')
        if rgb:
            result['base_color'] = rgb + [1.0]

    # ── Walk for connected file textures ──────────────────────────────────────

    def _file_path_from_attr(node, attr):
        """Trace a shader attribute one or two hops to a file node."""
        try:
            conns = cmds.listConnections(
                '{}.{}'.format(node, attr),
                source=True, destination=False, plugs=False
            ) or []
        except Exception:
            return None
        for c in conns:
            if cmds.nodeType(c) == 'file':
                p = cmds.getAttr(c + '.fileTextureName')
                return p if (p and os.path.isfile(p)) else None
            # One hop upstream (e.g., aiNormalMap → file)
            upstream = cmds.listConnections(
                c, source=True, destination=False, plugs=False
            ) or []
            for u in upstream:
                if cmds.nodeType(u) == 'file':
                    p = cmds.getAttr(u + '.fileTextureName')
                    return p if (p and os.path.isfile(p)) else None
        return None

    for attr in ('baseColor', 'color'):
        p = _file_path_from_attr(shader, attr)
        if p:
            result['DIFF'] = p
            break

    p = _file_path_from_attr(shader, 'metalness')
    if p:
        result['MTL'] = p

    p = _file_path_from_attr(shader, 'specularRoughness')
    if p:
        result['RGH'] = p

    p = _file_path_from_attr(shader, 'normalCamera')
    if p:
        result['NRM'] = p

    return result


# ── GLB binary builder ────────────────────────────────────────────────────────

def build_glb_data(export_items, embed_textures=True, pack_orm=False):
    """
    Build glTF JSON + BIN blob from a list of export item dicts.

    Each item must have:
        type    : 'mesh' | 'camera'
        name    : str
      mesh keys : positions, normals, uvs, indices, tex_map
      cam keys  : yfov, aspect_ratio, znear, zfar, matrix

    Returns (gltf_dict, bin_bytes).
    """
    bin_parts    = []
    accessors    = []
    buffer_views = []
    materials    = []
    tex_list     = []
    img_list     = []
    nodes        = []
    meshes_out   = []
    cameras_out  = []
    scene_nodes  = []
    tex_cache    = {}   # file_path → image index

    # ── BIN helpers ───────────────────────────────────────────────────────────

    def _align4():
        total = sum(len(p) for p in bin_parts)
        pad   = (4 - total % 4) % 4
        if pad:
            bin_parts.append(b'\x00' * pad)

    def _add_bv(data, target=None):
        _align4()
        byte_offset = sum(len(p) for p in bin_parts)
        bin_parts.append(bytes(data))
        bv = {"buffer": 0, "byteOffset": byte_offset, "byteLength": len(data)}
        if target is not None:
            bv["target"] = target
        buffer_views.append(bv)
        return len(buffer_views) - 1

    def _acc_vec3(data_list, need_minmax=False):
        packed = struct.pack('<{}f'.format(len(data_list)), *data_list)
        bv_idx = _add_bv(packed, target=34962)
        n   = len(data_list) // 3
        acc = {"bufferView": bv_idx, "componentType": 5126,
               "count": n, "type": "VEC3"}
        if need_minmax and n:
            xs, ys, zs = data_list[0::3], data_list[1::3], data_list[2::3]
            acc["min"] = [min(xs), min(ys), min(zs)]
            acc["max"] = [max(xs), max(ys), max(zs)]
        accessors.append(acc)
        return len(accessors) - 1

    def _acc_vec2(data_list):
        packed = struct.pack('<{}f'.format(len(data_list)), *data_list)
        bv_idx = _add_bv(packed, target=34962)
        acc = {"bufferView": bv_idx, "componentType": 5126,
               "count": len(data_list) // 2, "type": "VEC2"}
        accessors.append(acc)
        return len(accessors) - 1

    def _acc_indices(data_list):
        packed = struct.pack('<{}I'.format(len(data_list)), *data_list)
        bv_idx = _add_bv(packed, target=34963)
        acc = {"bufferView": bv_idx, "componentType": 5125,
               "count": len(data_list), "type": "SCALAR"}
        accessors.append(acc)
        return len(accessors) - 1

    def _embed_image(path):
        if path in tex_cache:
            return tex_cache[path]
        with open(path, 'rb') as fh:
            raw = fh.read()
        ext  = os.path.splitext(path)[1].lower()
        mime = 'image/jpeg' if ext in ('.jpg', '.jpeg') else 'image/png'
        bv_idx = _add_bv(raw)
        img_list.append({"bufferView": bv_idx, "mimeType": mime})
        idx = len(img_list) - 1
        tex_cache[path] = idx
        return idx

    def _pack_orm(mtl_path, rgh_path):
        """Pack MTL→B, RGH→G into an ORM PNG. Returns bytes or None."""
        try:
            import io as _io
            from PIL import Image as PI
            mtl = PI.open(mtl_path).convert('L')
            rgh = PI.open(rgh_path).convert('L').resize(mtl.size, PI.LANCZOS)
            occ = PI.new('L', mtl.size, 255)
            orm = PI.merge('RGB', (occ, rgh, mtl))
            buf = _io.BytesIO()
            orm.save(buf, format='PNG')
            return buf.getvalue()
        except Exception as exc:
            _log.warning("ORM pack failed: %s", exc)
            return None

    # ── Process items ─────────────────────────────────────────────────────────

    for item in export_items:

        if item['type'] == 'mesh':
            positions = item.get('positions', [])
            normals   = item.get('normals',   [])
            uvs_data  = item.get('uvs',       [])
            indices   = item.get('indices',   [])
            name      = item['name']

            if not positions or not indices:
                _log.warning("Skipping empty mesh: %s", name)
                continue

            attrs    = {"POSITION": _acc_vec3(positions, need_minmax=True)}
            if normals:
                attrs["NORMAL"]      = _acc_vec3(normals)
            if uvs_data:
                attrs["TEXCOORD_0"]  = _acc_vec2(uvs_data)
            idx_acc  = _acc_indices(indices)

            # Material ─────────────────────────────────────────────────────────
            # mat_data always contains base_color; tex paths present only when
            # connected file nodes were found AND embed_textures=True.
            mat_data     = item.get('mat_data', {})
            base_color   = mat_data.get('base_color', [0.5, 0.5, 0.5, 1.0])
            shader_name  = mat_data.get('shader_name', name + '_MAT')

            # Always write a material so meshes are visually distinguishable.
            pbr = {'baseColorFactor': [round(v, 4) for v in base_color]}

            nrm_ti = None
            if embed_textures:
                try:
                    if 'DIFF' in mat_data and os.path.isfile(mat_data['DIFF']):
                        ii = _embed_image(mat_data['DIFF'])
                        ti = len(tex_list)
                        tex_list.append({"source": ii})
                        pbr['baseColorTexture'] = {'index': ti}

                    has_mtl = 'MTL' in mat_data and os.path.isfile(mat_data['MTL'])
                    has_rgh = 'RGH' in mat_data and os.path.isfile(mat_data['RGH'])

                    if pack_orm and has_mtl and has_rgh:
                        orm_bytes = _pack_orm(mat_data['MTL'], mat_data['RGH'])
                        if orm_bytes:
                            bv_idx = _add_bv(orm_bytes)
                            img_list.append({"bufferView": bv_idx, "mimeType": "image/png"})
                            ii = len(img_list) - 1
                            ti = len(tex_list)
                            tex_list.append({"source": ii})
                            pbr['metallicRoughnessTexture'] = {'index': ti}
                    elif has_mtl and not pack_orm:
                        ii = _embed_image(mat_data['MTL'])
                        ti = len(tex_list)
                        tex_list.append({"source": ii})
                        pbr['metallicRoughnessTexture'] = {'index': ti}

                    if 'NRM' in mat_data and os.path.isfile(mat_data['NRM']):
                        ii = _embed_image(mat_data['NRM'])
                        nrm_ti = len(tex_list)
                        tex_list.append({"source": ii})

                except Exception as tex_exc:
                    _log.warning(
                        "Texture embed failed for mesh '%s': %s — "
                        "exporting with flat colour only.", name, tex_exc
                    )

            mat_entry = {"name": shader_name, "pbrMetallicRoughness": pbr}
            if base_color[3] < 0.999:
                mat_entry['alphaMode'] = 'BLEND'
            if nrm_ti is not None:
                mat_entry['normalTexture'] = {'index': nrm_ti}
            materials.append(mat_entry)
            mat_idx = len(materials) - 1

            prim = {"attributes": attrs, "indices": idx_acc}
            if mat_idx is not None:
                prim['material'] = mat_idx

            meshes_out.append({"name": name, "primitives": [prim]})
            node_entry = {"name": name, "mesh": len(meshes_out) - 1}
            nodes.append(node_entry)
            scene_nodes.append(len(nodes) - 1)

        elif item['type'] == 'camera':
            cam_entry = {
                "name": item['name'],
                "type": "perspective",
                "perspective": {
                    "yfov":        item['yfov'],
                    "aspectRatio": item['aspect_ratio'],
                    "znear":       item['znear'],
                    "zfar":        item['zfar'],
                },
            }
            cameras_out.append(cam_entry)
            node_entry = {
                "name":   item['name'],
                "camera": len(cameras_out) - 1,
                "matrix": [float(v) for v in item['matrix']],
            }
            nodes.append(node_entry)
            scene_nodes.append(len(nodes) - 1)

    # ── Assemble glTF dict ────────────────────────────────────────────────────

    bin_bytes  = b''.join(bin_parts)
    total_bin  = len(bin_bytes)

    gltf = {
        "asset": {
            "version":   "2.0",
            "generator": "PXLtools GLB Manager v{}".format(VERSION),
        },
        "scene":  0,
        "scenes": [{"name": "Scene", "nodes": scene_nodes}],
        "nodes":  nodes,
    }
    if meshes_out:    gltf["meshes"]      = meshes_out
    if cameras_out:   gltf["cameras"]     = cameras_out
    if materials:     gltf["materials"]   = materials
    if tex_list:      gltf["textures"]    = tex_list
    if img_list:      gltf["images"]      = img_list
    if accessors:     gltf["accessors"]   = accessors
    if buffer_views:  gltf["bufferViews"] = buffer_views
    if bin_bytes:     gltf["buffers"]     = [{"byteLength": total_bin}]

    return gltf, bin_bytes


def write_glb(path, gltf_dict, bin_data):
    """Write a valid binary GLB file (glTF 2.0 spec)."""
    json_bytes  = json.dumps(gltf_dict, separators=(',', ':')).encode('utf-8')
    json_pad    = (4 - len(json_bytes) % 4) % 4
    json_padded = json_bytes + b' ' * json_pad

    json_chunk = struct.pack('<II', len(json_padded), 0x4E4F534A) + json_padded

    bin_pad    = (4 - len(bin_data) % 4) % 4 if bin_data else 0
    bin_padded = bin_data + b'\x00' * bin_pad
    bin_chunk  = (struct.pack('<II', len(bin_padded), 0x004E4942) + bin_padded
                  if bin_padded else b'')

    total_len = 12 + len(json_chunk) + len(bin_chunk)
    header    = struct.pack('<III', 0x46546C67, 2, total_len)

    with open(path, 'wb') as fh:
        fh.write(header + json_chunk + bin_chunk)

    _log.info("GLB written: %s  (%.1f KB)", os.path.basename(path),
              total_len / 1024.0)


def _expand_to_meshes_and_cameras(node_names, export_cameras):
    """
    Recursively expand node_names to lists of mesh transforms and camera
    transforms found as descendants (inclusive).
    """
    meshes  = []
    cameras = []
    visited = set()

    def _walk(node):
        if node in visited:
            return
        visited.add(node)
        shapes      = cmds.listRelatives(node, shapes=True, fullPath=True) or []
        shape_types = {cmds.nodeType(s) for s in shapes}
        if 'mesh' in shape_types and node not in meshes:
            meshes.append(node)
        if export_cameras and 'camera' in shape_types and node not in cameras:
            cameras.append(node)
        for child in (cmds.listRelatives(node, children=True,
                                         type='transform', fullPath=True) or []):
            _walk(child)

    for n in node_names:
        _walk(n)

    return meshes, cameras


def export_glb(node_names, out_path,
               export_normals=True, export_uvs=True,
               embed_textures=True, export_cameras=True, pack_orm=False,
               prog_cb=None):
    """
    Full GLB export pipeline.

    node_names  : list of Maya transform names to export (groups auto-expanded)
    out_path    : destination .glb file path
    Returns     : number of items exported
    """
    def step(msg):
        _log.debug("STEP: %s", msg)
        if prog_cb:
            prog_cb(msg)

    _log.info("=== GLB Manager — Export  v%s ===", VERSION)
    _log.info("Output : %s", out_path)

    step("Collecting scene objects…")
    mesh_nodes, cam_nodes = _expand_to_meshes_and_cameras(node_names, export_cameras)
    _log.info("Meshes: %d  Cameras: %d", len(mesh_nodes), len(cam_nodes))

    if not mesh_nodes and not cam_nodes:
        raise RuntimeError("No exportable meshes or cameras found in selection.")

    export_items = []

    for mn in mesh_nodes:
        short = mn.split('|')[-1]
        step("Reading mesh '{}'…".format(short))
        try:
            pos, nrm, uvs, idx = get_mesh_triangles(mn, export_normals, export_uvs)
            if not pos:
                _log.warning("Empty mesh, skipping: %s", mn)
                continue

            # Always collect material data (flat colour + texture paths).
            # embed_textures only controls whether file bytes go into the BIN chunk.
            mat_data = collect_material_data(mn)
            export_items.append({
                'type':      'mesh',
                'name':      short,
                'positions': pos,
                'normals':   nrm,
                'uvs':       uvs,
                'indices':   idx,
                'mat_data':  mat_data,
            })
            tex_keys = [k for k in ('DIFF', 'MTL', 'RGH', 'NRM') if k in mat_data]
            _log.info("  %s — %d verts, %d tris, colour=%s, textures=%s",
                      short, len(pos) // 3, len(idx) // 3,
                      mat_data.get('base_color', []), tex_keys)
        except Exception as exc:
            _log.exception("Mesh export failed for '%s': %s", mn, exc)

    for cn in cam_nodes:
        short = cn.split('|')[-1]
        step("Reading camera '{}'…".format(short))
        try:
            cam_data = get_camera_data(cn)
            if cam_data:
                cam_data['type'] = 'camera'
                export_items.append(cam_data)
                _log.info("  Camera: %s  yfov=%.3f°  znear=%.3f  zfar=%.1f",
                          short, math.degrees(cam_data['yfov']),
                          cam_data['znear'], cam_data['zfar'])
        except Exception as exc:
            _log.exception("Camera export failed for '%s': %s", cn, exc)

    step("Building GLB binary…")
    gltf, bin_data = build_glb_data(export_items, embed_textures, pack_orm)

    step("Writing file…")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    write_glb(out_path, gltf, bin_data)

    step("Done!")
    _log.info("=== Export complete — %d items ===", len(export_items))
    return len(export_items)


# =============================================================================
# ──────────────────────────────── UI ─────────────────────────────────────────
# =============================================================================

_IMP_STEPS = 8    # import progress steps
_EXP_STEPS = 6    # export progress steps

# Module-level scene hierarchy map: display_string → full_dag_path
_HIER_MAP = {}

# Singleton reference
_INSTANCE = None


# =============================================================================
# Global QSS — shared single-source stylesheet (icon tokens substituted at build)
# =============================================================================

MAIN_QSS = pxlt.tool_qss() if _PXLUI else ""


# =============================================================================
# Flat-text proxy style — kills the host's etched/drop-shadow disabled-text
# =============================================================================

try:
    from PySide6 import QtWidgets as _QtW, QtGui as _QtG
except ImportError:
    from PySide2 import QtWidgets as _QtW, QtGui as _QtG


class _FlatTextStyle(_QtW.QProxyStyle):
    """Kills any text drop-shadow / etch the host style draws (matches the
    reference tool)."""
    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint in (_QtW.QStyle.SH_EtchDisabledText,
                    _QtW.QStyle.SH_DitherDisabledText):
            return 0
        return super().styleHint(hint, option, widget, returnData)

    def drawItemText(self, painter, rect, flags, pal, enabled, text,
                     textRole=_QtG.QPalette.NoRole):
        if not text:
            return
        painter.save()
        if textRole != _QtG.QPalette.NoRole:
            painter.setPen(pal.color(textRole))
        painter.drawText(rect, int(flags), text)
        painter.restore()


# =============================================================================
# QSS icon-token substitution (mirrors the reference tools exactly)
# =============================================================================

def _resolved_qss():
    """Return MAIN_QSS with the icon tokens substituted by generated PNG paths
    (check / spin arrows / slider handle), written to a space-free temp dir.
    Identical helper to the TurnTable / PBR Material reference."""
    try:
        from PySide6 import QtCore, QtGui
    except ImportError:
        from PySide2 import QtCore, QtGui

    _qss = MAIN_QSS
    try:
        if _PXLUI:
            _icd = cmds.internalVar(userPrefDir=True) + "icons/"
            _ic = _icd + "_pxlui_check.png"
            pxli.save_png("check", 11, pxlt.c("on_accent"), _ic)
            _qss = _qss.replace("__CHECK__", _ic.replace("\\", "/"))
            # Spin-box / combo arrows — real PNG chevrons (PySide6 does NOT
            # render CSS border-triangles). Grey default + white on hover.
            _up  = _icd + "_pxlui_arrow_up.png"
            _dn  = _icd + "_pxlui_arrow_down.png"
            _uph = _icd + "_pxlui_arrow_up_h.png"
            _dnh = _icd + "_pxlui_arrow_down_h.png"
            pxli.save_png("chevron-up",   9, "#B8B8B8", _up)
            pxli.save_png("chevron-down", 9, "#B8B8B8", _dn)
            pxli.save_png("chevron-up",   9, "#ffffff", _uph)
            pxli.save_png("chevron-down", 9, "#ffffff", _dnh)
            _qss = (_qss.replace("__SPINUP__",   _up.replace("\\", "/"))
                        .replace("__SPINDOWN__", _dn.replace("\\", "/"))
                        .replace("__SPINUPH__",  _uph.replace("\\", "/"))
                        .replace("__SPINDOWNH__", _dnh.replace("\\", "/")))
            # Slider handle: white dot (normal) + white dot with an orange
            # RING on hover — drawn to PNG so it stays perfectly round.
            def _mk_handle(out_path, ring):
                _D = 20
                _pm = QtGui.QPixmap(_D, _D); _pm.fill(QtCore.Qt.transparent)
                _pn = QtGui.QPainter(_pm)
                _pn.setRenderHint(QtGui.QPainter.Antialiasing, True)
                _cc = _D / 2.0
                _pn.setPen(QtCore.Qt.NoPen)
                _pn.setBrush(QtGui.QColor("#ffffff"))
                _pn.drawEllipse(QtCore.QPointF(_cc, _cc), 6.5, 6.5)
                if ring:
                    _pen = QtGui.QPen(QtGui.QColor("#E8820C")); _pen.setWidthF(2.0)
                    _pn.setPen(_pen); _pn.setBrush(QtCore.Qt.NoBrush)
                    _pn.drawEllipse(QtCore.QPointF(_cc, _cc), 8.0, 8.0)
                _pn.end(); _pm.save(out_path, "PNG")
            _slh  = _icd + "_pxlui_slh.png"
            _slhh = _icd + "_pxlui_slh_h.png"
            _mk_handle(_slh, False)
            _mk_handle(_slhh, True)
            _qss = (_qss.replace("__SLH__",  _slh.replace("\\", "/"))
                        .replace("__SLHH__", _slhh.replace("\\", "/")))
        else:
            for _ph in ("__CHECK__", "__SPINUP__", "__SPINDOWN__",
                        "__SPINUPH__", "__SPINDOWNH__", "__SLH__", "__SLHH__"):
                _qss = _qss.replace(_ph, "")
    except Exception:
        for _ph in ("__CHECK__", "__SPINUP__", "__SPINDOWN__",
                    "__SPINUPH__", "__SPINDOWNH__", "__SLH__", "__SLHH__"):
            _qss = _qss.replace(_ph, "")
    return _qss


# =============================================================================
# Section-frame helper — non-collapsible section using the shared look.
# Mirrors the shared CollapsibleSection header (3px accent bar + icon + title)
# but stays always-open. Body uses objectName "sectionFrame" so tool_qss styles
# it. Returns (section, body_layout, header_hbox) so callers can add a
# right-aligned action button into the header bar.
#
# The returned `section` is a QWidget with a bound set_state('idle'|'active'|
# 'done') method that recolours the accent bar (orange active / green done) and
# tints the header + shows a header ✓ when done — exactly like the reference
# tool's CollapsibleSection.set_state, so each section reflects step progress.
# =============================================================================

def _make_section_frame(title, icon_name=None, accent=None, parent=None):
    try:
        from PySide6 import QtWidgets, QtCore, QtGui
    except ImportError:
        from PySide2 import QtWidgets, QtCore, QtGui

    base_accent = accent or (pxlt.c("accent") if _PXLUI else "#E8820C")
    radius = (pxlt.m("r_section") if _PXLUI else 6)

    container = QtWidgets.QWidget(parent)
    outer = QtWidgets.QVBoxLayout(container)
    outer.setContentsMargins(0, 0, 0, 0)
    outer.setSpacing(0)

    header = QtWidgets.QFrame()
    header.setObjectName("PxlSectionHeader")
    header.setFixedHeight(pxlt.m("section_h") if _PXLUI else 30)

    hbox = QtWidgets.QHBoxLayout(header)
    hbox.setContentsMargins(0, 0, 8, 0)
    hbox.setSpacing(8)

    bar = QtWidgets.QFrame()
    bar.setFixedWidth(3)
    bar.setStyleSheet("background: {}; border: none;".format(base_accent))
    hbox.addWidget(bar)

    if icon_name and _PXLUI:
        try:
            icl = QtWidgets.QLabel()
            icl.setFixedWidth(pxlt.m("icon"))
            icl.setStyleSheet("background: transparent;")
            icl.setPixmap(pxli.pixmap(icon_name, pxlt.m("icon"), base_accent))
            hbox.addWidget(icl)
        except Exception:
            pass

    # Title: font only (no inline colour) — inherits `text` from tool_qss.
    title_lbl = QtWidgets.QLabel(title)
    _tf = title_lbl.font()
    _tf.setBold(True)
    _tf.setPointSize(max(_tf.pointSize(), 9))
    title_lbl.setFont(_tf)
    title_lbl.setStyleSheet("background: transparent;")
    hbox.addWidget(title_lbl)
    hbox.addStretch(1)

    # Section-level done check (pale-green ✓ when complete) — same as TurnTable.
    state_chk = QtWidgets.QLabel("")
    state_chk.setStyleSheet(
        "color: {}; font-weight: bold; font-size: 13px; "
        "background: transparent;".format(pxlt.c("ok") if _PXLUI else "#5BBF6A")
    )
    hbox.addWidget(state_chk)

    outer.addWidget(header)

    body = QtWidgets.QFrame()
    body.setObjectName("sectionFrame")
    body_layout = QtWidgets.QVBoxLayout(body)
    body_layout.setContentsMargins(11, 8, 8, 8)
    body_layout.setSpacing(6)
    outer.addWidget(body)

    # ── set_state — mirrors CollapsibleSection.set_state in the reference tool ──
    def _apply_header_bg(state):
        if state == "done":
            bg = "#33402d"
        elif state == "active":
            bg = "#46413a"
        else:
            bg = (pxlt.c("section_head") if _PXLUI else "#454545")
        header.setStyleSheet(
            "QFrame#PxlSectionHeader {{ background: {}; border: none; "
            "border-top-left-radius: {r}px; "
            "border-top-right-radius: {r}px; }}".format(bg, r=radius)
        )

    def set_state(state):
        """Visual progress state: 'idle' | 'active' (orange) | 'done' (green)."""
        if state == "done":
            bar.setStyleSheet(
                "background: {}; border: none;".format(
                    pxlt.c("ok") if _PXLUI else "#5BBF6A"))
        elif state == "active":
            bar.setStyleSheet(
                "background: {}; border: none;".format(
                    pxlt.c("accent") if _PXLUI else "#E8820C"))
        else:
            bar.setStyleSheet("background: {}; border: none;".format(base_accent))
        state_chk.setText("✓" if state == "done" else "")
        _apply_header_bg(state)

    _apply_header_bg("idle")
    container.set_state = set_state
    # collapse support — hide the body, keep the header. Used to auto-close a
    # completed section (e.g. SOURCE FILE once the asset name is applied).
    container.set_collapsed = lambda c, _b=body: _b.setVisible(not c)

    return container, body_layout, hbox


# =============================================================================
# ── SCENE / HIERARCHY HELPERS (pure Maya logic, no Qt) ───────────────────────
# =============================================================================

def _get_node_type_tag(full_dag_path):
    """
    Return a 4-char type tag for a transform node.
    Always requires the full DAG path to avoid ambiguous-name errors.
    """
    try:
        shapes = cmds.listRelatives(full_dag_path, shapes=True, fullPath=True) or []
        types  = {cmds.nodeType(s) for s in shapes}
    except ValueError:
        return 'OTH '
    if 'mesh'   in types: return 'MESH'
    if 'camera' in types: return 'CAM '
    if not types:         return 'GRP '
    return 'OTH '


# =============================================================================
# ── MAIN DIALOG ───────────────────────────────────────────────────────────────
# =============================================================================

class GLBManager(object):
    """
    PySide6 QDialog singleton for the PXLtools GLB Manager (pxl_ui).
    Keeps the dual-tab IMPORT | EXPORT | SCENE QTabWidget structure; all chrome
    comes from the shared pxl_ui kit (tool_qss + AppHeader + shared sections).
    """

    TOOL_NAME          = TOOL_NAME
    VERSION            = VERSION
    WINDOW_OBJECT_NAME = WINDOW_OBJECT_NAME
    ICON_NAME          = ICON_NAME

    def __init__(self):
        from PySide6 import QtWidgets, QtGui, QtCore
        import shiboken6
        from maya import OpenMayaUI as omui

        global _INSTANCE
        # ── Singleton: close any existing window ──────────────────────────────
        if _INSTANCE is not None:
            try:
                _INSTANCE._dialog.close()
                _INSTANCE._dialog.deleteLater()
            except Exception:
                pass
        _INSTANCE = self

        # ── Guided-flow state (derived from reality; reset recomputes) ────────
        # IMPORT : step1 file chosen, step2 options confirmed, step3 imported.
        # EXPORT : step1 objects chosen, step2 output confirmed, step3 exported.
        self._imp_name_confirmed = False
        self._imp_opts_confirmed = False
        self._imp_done           = False
        self._exp_sel_count      = 0
        self._exp_node_names     = []
        self._exp_opts_confirmed = False
        self._exp_done           = False
        # Step-widget handles (created in the build methods).
        self._imp_step1_badge = self._imp_step1_confirm = None
        self._imp_step2_badge = self._imp_step2_confirm = None
        self._imp_step3_badge = self._imp_step3_confirm = None
        self._exp_step1_badge = self._exp_step1_confirm = None
        self._exp_step2_badge = self._exp_step2_confirm = None
        self._exp_step3_badge = self._exp_step3_confirm = None
        self._imp_src_frame = self._imp_opt_frame = self._imp_run_frame = None
        self._exp_sel_frame = self._exp_out_frame = self._exp_run_frame = None

        # ── Parent to Maya main window ────────────────────────────────────────
        main_ptr = omui.MQtUtil.mainWindow()
        maya_win = shiboken6.wrapInstance(int(main_ptr), QtWidgets.QWidget)

        self._dialog = QtWidgets.QDialog(maya_win)
        self._dialog.setObjectName(self.WINDOW_OBJECT_NAME)
        self._dialog.setWindowTitle(
            "{}  v{}".format(self.TOOL_NAME, self.VERSION)
        )
        self._dialog.setProperty("pxlGLBVersion", self.VERSION)
        self._dialog.setMinimumWidth(580)
        self._dialog.resize(600, 780)
        self._dialog.setStyleSheet(_resolved_qss())
        self._dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        # Remove Qt's etched disabled-text emboss (matches the reference tool).
        try:
            self._dialog.setStyle(_FlatTextStyle(self._dialog.style()))
        except Exception:
            pass

        root_vbox = QtWidgets.QVBoxLayout(self._dialog)
        root_vbox.setContentsMargins(0, 0, 0, 0)
        root_vbox.setSpacing(0)

        # ── Branded header (shared AppHeader) ─────────────────────────────────
        self._build_header(root_vbox)

        # ── Instructions (collapsible, collapsed by default) ──────────────────
        instr_wrap = QtWidgets.QWidget()
        instr_lay  = QtWidgets.QVBoxLayout(instr_wrap)
        instr_lay.setContentsMargins(14, 10, 14, 4)
        instr_lay.setSpacing(0)
        instr_lay.addWidget(self._build_instructions())
        root_vbox.addWidget(instr_wrap)

        # ── Tab widget (IMPORT | EXPORT | SCENE — styled by tool_qss) ─────────
        self._tabs = QtWidgets.QTabWidget()
        self._tabs.addTab(self._build_import_tab(QtWidgets, QtCore), "  IMPORT  ")
        self._tabs.addTab(self._build_export_tab(QtWidgets, QtCore), "  EXPORT  ")
        self._tabs.addTab(self._build_scene_tab(QtWidgets, QtCore),  "  SCENE   ")
        root_vbox.addWidget(self._tabs, 1)

        self._dialog.show()

        # Auto-populate hierarchy on open
        self._refresh_hierarchy()

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self, layout):
        """Branded header — ALWAYS the shared pxlw.AppHeader (no bespoke header).

        Resolves the deployed tool icon (icon_glb_manager.png, falling back to
        icon_glb_importer.png) in the Maya prefs icons dir, exactly like the
        TurnTable Builder resolves its icon. There is NO hand-built fallback
        header with hard-coded colours — all chrome comes from the kit."""
        icon_dir = cmds.internalVar(userPrefDir=True) + "icons/"
        _ip = icon_dir + self.ICON_NAME
        if not os.path.isfile(_ip):
            _ip = icon_dir + ICON_FALLBACK
        layout.addWidget(pxlw.AppHeader(
            self.TOOL_NAME, "v" + self.VERSION, icon_path=_ip))

    # ── Instructions panel ────────────────────────────────────────────────────

    def _build_instructions(self):
        from PySide6 import QtWidgets
        instr = pxlw.CollapsibleSection(
            "INSTRUCTIONS", icon_name="info", accent="#46C2D6",
            collapsed=True,
        )
        for line in [
            "Follow the numbers — the orange step is what to do next; it turns "
            "green when done.",
            "IMPORT: 1 Browse a .glb/.gltf file → 2 Confirm options → 3 Import.",
            "EXPORT: 1 Select objects (Scene tab) → 2 Confirm output → 3 Export.",
            "SCENE:  Refresh updates the list. Select/Hide/Show act on the Maya scene.",
            "        Multi-select supported. Groups are auto-expanded on export.",
        ]:
            lbl = QtWidgets.QLabel(line)
            lbl.setObjectName("hint")
            lbl.setWordWrap(True)
            instr.add_widget(lbl)
        return instr

    # ── IMPORT TAB ────────────────────────────────────────────────────────────

    def _build_import_tab(self, QtWidgets, QtCore):
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        inner = QtWidgets.QWidget()
        vbox  = QtWidgets.QVBoxLayout(inner)
        vbox.setContentsMargins(14, 12, 14, 14)
        vbox.setSpacing(10)

        intro = QtWidgets.QLabel(
            "Follow the numbers — the orange step is what to do next; "
            "it turns green when done."
        )
        intro.setObjectName("hint")
        intro.setWordWrap(True)
        vbox.addWidget(intro)

        # ── STEP 1 — BROWSE GLB FILE (SOURCE FILE section) ──────────────────
        self._imp_src_frame, src_lay, _src_hbox = _make_section_frame(
            "SOURCE FILE", icon_name="folder", accent="#E8820C", parent=inner,
        )

        row1, self._imp_step1_badge, self._imp_step1_confirm = \
            self._mk_step_header("1", "BROWSE GLB FILE")
        src_lay.addLayout(row1)

        s1_hint = QtWidgets.QLabel("Pick the .glb / .gltf file to import.")
        s1_hint.setObjectName("hint")
        s1_hint.setWordWrap(True)
        src_lay.addWidget(s1_hint)

        lbl = QtWidgets.QLabel("GLB File:")
        lbl.setObjectName("ctrlLabel")
        src_lay.addWidget(lbl)

        file_row = QtWidgets.QHBoxLayout()
        file_row.setSpacing(6)
        self._imp_path_fld = QtWidgets.QLineEdit()
        self._imp_path_fld.setReadOnly(True)
        self._imp_path_fld.setPlaceholderText("No file selected…")
        self._imp_path_fld.setMinimumHeight(32)
        self._imp_browse_btn = QtWidgets.QPushButton("Browse…")
        self._imp_browse_btn.setObjectName("btnStepActive")
        self._imp_browse_btn.setMinimumHeight(32)
        self._imp_browse_btn.setMinimumWidth(110)
        self._imp_browse_btn.clicked.connect(self._browse_glb)
        file_row.addWidget(self._imp_path_fld, 1)
        file_row.addWidget(self._imp_browse_btn)
        src_lay.addLayout(file_row)

        # ── STEP 2 — ASSET NAME (Apply collapses SOURCE FILE, opens OPTIONS) ──
        row2, self._imp_step2_badge, self._imp_step2_confirm = \
            self._mk_step_header("2", "ASSET NAME")
        src_lay.addLayout(row2)

        s2n_hint = QtWidgets.QLabel(
            "Confirm the name (auto-filled from the file) or type your own, "
            "then press Apply."
        )
        s2n_hint.setObjectName("hint")
        s2n_hint.setWordWrap(True)
        src_lay.addWidget(s2n_hint)

        lbl2 = QtWidgets.QLabel("Asset Name:")
        lbl2.setObjectName("ctrlLabel")
        src_lay.addWidget(lbl2)
        self._imp_name_fld = QtWidgets.QLineEdit()
        self._imp_name_fld.setPlaceholderText("Auto from filename…")
        self._imp_name_fld.setMinimumHeight(32)
        self._imp_name_fld.textEdited.connect(self._on_import_name_changed)
        src_lay.addWidget(self._imp_name_fld)

        name_row = QtWidgets.QHBoxLayout()
        name_row.addStretch(1)
        self._imp_name_apply_btn = QtWidgets.QPushButton("Apply")
        self._imp_name_apply_btn.setObjectName("btnStepLocked")
        self._imp_name_apply_btn.setMinimumHeight(32)
        self._imp_name_apply_btn.setMinimumWidth(120)
        self._imp_name_apply_btn.clicked.connect(self._confirm_import_name)
        name_row.addWidget(self._imp_name_apply_btn)
        src_lay.addLayout(name_row)

        vbox.addWidget(self._imp_src_frame)

        # ── STEP 2 — CONFIGURE OPTIONS (OPTIONS section) ────────────────────
        self._imp_opt_frame, opt_lay, _opt_hbox = _make_section_frame(
            "OPTIONS", icon_name="utilities", accent="#34B3A0", parent=inner,
        )

        row3, self._imp_step3_badge, self._imp_step3_confirm = \
            self._mk_step_header("3", "OUTPUT FOLDER & OPTIONS")
        opt_lay.addLayout(row3)

        s3_hint = QtWidgets.QLabel(
            "Choose where extracted textures are saved, set the import options, "
            "then press Use These Settings to continue."
        )
        s3_hint.setObjectName("hint")
        s3_hint.setWordWrap(True)
        opt_lay.addWidget(s3_hint)

        # Output folder — on top of the options.
        of_lbl = QtWidgets.QLabel("Output Folder:")
        of_lbl.setObjectName("ctrlLabel")
        opt_lay.addWidget(of_lbl)
        self._imp_tex_row = QtWidgets.QWidget()
        _of_hbox = QtWidgets.QHBoxLayout(self._imp_tex_row)
        _of_hbox.setContentsMargins(0, 0, 0, 0)
        _of_hbox.setSpacing(6)
        self._imp_tex_fld = QtWidgets.QLineEdit()
        self._imp_tex_fld.setPlaceholderText("Folder for extracted textures…")
        self._imp_tex_fld.setMinimumHeight(32)
        _of_browse = QtWidgets.QPushButton("Browse…")
        _of_browse.setObjectName("btnApply")
        _of_browse.setMinimumHeight(32)
        _of_browse.setMinimumWidth(110)
        _of_browse.clicked.connect(self._browse_tex_folder)
        _of_hbox.addWidget(self._imp_tex_fld, 1)
        _of_hbox.addWidget(_of_browse)
        opt_lay.addWidget(self._imp_tex_row)

        self._imp_uv_chk = QtWidgets.QCheckBox("Import UVs")
        self._imp_uv_chk.setChecked(True)
        opt_lay.addWidget(self._imp_uv_chk)

        self._imp_tex_chk = QtWidgets.QCheckBox(
            "Extract Textures  (_DIFF  _MTL  _RGH  _NRM)"
        )
        self._imp_tex_chk.setChecked(True)
        opt_lay.addWidget(self._imp_tex_chk)

        # Output-folder row is created at the TOP of this section; its enable
        # state follows the Extract Textures toggle.
        self._imp_tex_chk.toggled.connect(self._imp_tex_row.setEnabled)

        self._imp_mat_chk = QtWidgets.QCheckBox("Create Material")
        self._imp_mat_chk.setChecked(True)
        opt_lay.addWidget(self._imp_mat_chk)

        # Shader / ColorSpace row — combos rely on tool_qss only (single arrow)
        self._imp_mat_row = QtWidgets.QWidget()
        mat_row_hbox = QtWidgets.QHBoxLayout(self._imp_mat_row)
        mat_row_hbox.setContentsMargins(0, 0, 0, 0)
        mat_row_hbox.setSpacing(8)

        shader_lbl = QtWidgets.QLabel("Shader:")
        shader_lbl.setObjectName("ctrlLabel")
        mat_row_hbox.addWidget(shader_lbl)

        self._imp_shader_menu = QtWidgets.QComboBox()
        self._imp_shader_menu.addItems(["aiStandardSurface", "lambert"])
        self._imp_shader_menu.setFixedWidth(160)
        mat_row_hbox.addWidget(self._imp_shader_menu)

        cs_lbl = QtWidgets.QLabel("Color Space:")
        cs_lbl.setObjectName("ctrlLabel")
        mat_row_hbox.addWidget(cs_lbl)

        self._imp_aces_menu = QtWidgets.QComboBox()
        self._imp_aces_menu.addItems(["ACES 1.2", "Standard"])
        self._imp_aces_menu.setFixedWidth(120)
        mat_row_hbox.addWidget(self._imp_aces_menu)
        mat_row_hbox.addStretch()

        opt_lay.addWidget(self._imp_mat_row)
        self._imp_mat_chk.toggled.connect(self._imp_mat_row.setEnabled)

        self._imp_ref_chk = QtWidgets.QCheckBox(
            "Create 1m Reference Cube on ground"
        )
        self._imp_ref_chk.setChecked(False)
        opt_lay.addWidget(self._imp_ref_chk)

        # Confirm-options step button (turns step 2 DONE, unlocks step 3).
        # Editing any option after confirming re-opens step 2 (and re-locks 3).
        for _w in (self._imp_uv_chk, self._imp_tex_chk, self._imp_mat_chk,
                   self._imp_ref_chk):
            _w.toggled.connect(self._on_import_option_changed)
        self._imp_shader_menu.currentIndexChanged.connect(
            self._on_import_option_changed)
        self._imp_aces_menu.currentIndexChanged.connect(
            self._on_import_option_changed)

        confirm_row = QtWidgets.QHBoxLayout()
        confirm_row.addStretch(1)
        self._imp_confirm_btn = QtWidgets.QPushButton("Use These Settings")
        self._imp_confirm_btn.setObjectName("btnStepLocked")
        self._imp_confirm_btn.setMinimumHeight(32)
        self._imp_confirm_btn.setMinimumWidth(160)
        self._imp_confirm_btn.clicked.connect(self._confirm_import_options)
        confirm_row.addWidget(self._imp_confirm_btn)
        opt_lay.addLayout(confirm_row)

        vbox.addWidget(self._imp_opt_frame)

        # ── STEP 3 — IMPORT (RUN section) ───────────────────────────────────
        self._imp_run_frame, run_lay, _run_hbox = _make_section_frame(
            "IMPORT", icon_name="download", accent="#E8820C", parent=inner,
        )

        row4, self._imp_step4_badge, self._imp_step4_confirm = \
            self._mk_step_header("4", "IMPORT")
        run_lay.addLayout(row4)

        s3_hint = QtWidgets.QLabel(
            "Build the asset in Maya from the chosen file and options."
        )
        s3_hint.setObjectName("hint")
        s3_hint.setWordWrap(True)
        run_lay.addWidget(s3_hint)

        # Progress bar (no inline colour — styled by tool_qss).
        self._imp_prog = QtWidgets.QProgressBar()
        self._imp_prog.setMaximum(_IMP_STEPS)
        self._imp_prog.setValue(0)
        self._imp_prog.setFixedHeight(14)
        self._imp_prog.setTextVisible(False)
        self._imp_prog.setVisible(False)
        run_lay.addWidget(self._imp_prog)

        self._imp_prog_lbl = QtWidgets.QLabel("")
        self._imp_prog_lbl.setObjectName("hint")
        self._imp_prog_lbl.setVisible(False)
        run_lay.addWidget(self._imp_prog_lbl)

        # Status bar
        self._import_status = QtWidgets.QLabel(
            "—  Select a GLB file to begin."
        )
        self._import_status.setObjectName("statusIdle")
        self._import_status.setWordWrap(True)
        run_lay.addWidget(self._import_status)

        # Import button — the step-3 action button.
        self._imp_import_btn = QtWidgets.QPushButton("Import")
        self._imp_import_btn.setObjectName("btnStepLocked")
        self._imp_import_btn.setMinimumHeight(42)
        self._imp_import_btn.clicked.connect(self._do_import)
        run_lay.addWidget(self._imp_import_btn)

        vbox.addWidget(self._imp_run_frame)

        vbox.addStretch()
        scroll.setWidget(inner)

        self._update_import_steps()
        return scroll

    # ── EXPORT TAB ────────────────────────────────────────────────────────────

    def _build_export_tab(self, QtWidgets, QtCore):
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        inner = QtWidgets.QWidget()
        vbox  = QtWidgets.QVBoxLayout(inner)
        vbox.setContentsMargins(14, 12, 14, 14)
        vbox.setSpacing(10)

        intro = QtWidgets.QLabel(
            "Follow the numbers — the orange step is what to do next; "
            "it turns green when done."
        )
        intro.setObjectName("hint")
        intro.setWordWrap(True)
        vbox.addWidget(intro)

        # ── STEP 1 — SELECT OBJECTS TO EXPORT (SELECTION section) ───────────
        self._exp_sel_frame, sel_lay, _sel_hbox = _make_section_frame(
            "SELECTION", icon_name="scene", accent="#4F9DE0", parent=inner,
        )

        row1, self._exp_step1_badge, self._exp_step1_confirm = \
            self._mk_step_header("1", "SELECT OBJECTS TO EXPORT")
        sel_lay.addLayout(row1)

        s1_hint = QtWidgets.QLabel(
            "In the SCENE tab, select the objects you want, then press "
            "Use Scene Selection. Groups are auto-expanded on export."
        )
        s1_hint.setObjectName("hint")
        s1_hint.setWordWrap(True)
        sel_lay.addWidget(s1_hint)

        self._exp_sel_label = QtWidgets.QLabel("No objects selected yet.")
        self._exp_sel_label.setObjectName("selLabel")
        self._exp_sel_label.setWordWrap(True)
        sel_lay.addWidget(self._exp_sel_label)

        sel_btn_row = QtWidgets.QHBoxLayout()
        sel_btn_row.addStretch(1)
        self._exp_sel_btn = QtWidgets.QPushButton("Use Scene Selection")
        self._exp_sel_btn.setObjectName("btnStepActive")
        self._exp_sel_btn.setMinimumHeight(32)
        self._exp_sel_btn.setMinimumWidth(170)
        self._exp_sel_btn.clicked.connect(self._capture_export_selection)
        sel_btn_row.addWidget(self._exp_sel_btn)
        sel_lay.addLayout(sel_btn_row)

        vbox.addWidget(self._exp_sel_frame)

        # ── STEP 2 — OUTPUT OPTIONS (OUTPUT section) ────────────────────────
        self._exp_out_frame, out_lay, _out_hbox = _make_section_frame(
            "OUTPUT OPTIONS", icon_name="folder", accent="#E8820C", parent=inner,
        )

        row2, self._exp_step2_badge, self._exp_step2_confirm = \
            self._mk_step_header("2", "OUTPUT OPTIONS")
        out_lay.addLayout(row2)

        s2_hint = QtWidgets.QLabel(
            "Set the output .glb path and export options, then press "
            "Use These Settings to continue."
        )
        s2_hint.setObjectName("hint")
        s2_hint.setWordWrap(True)
        out_lay.addWidget(s2_hint)

        exp_lbl2 = QtWidgets.QLabel("Export File:")
        exp_lbl2.setObjectName("ctrlLabel")
        out_lay.addWidget(exp_lbl2)

        out_row = QtWidgets.QHBoxLayout()
        out_row.setSpacing(6)
        self._exp_path_fld = QtWidgets.QLineEdit()
        self._exp_path_fld.setPlaceholderText("output.glb path…")
        self._exp_path_fld.setMinimumHeight(32)
        out_browse_btn = QtWidgets.QPushButton("Browse…")
        out_browse_btn.setObjectName("btnApply")
        out_browse_btn.setMinimumHeight(32)
        out_browse_btn.setMinimumWidth(110)
        out_browse_btn.clicked.connect(self._browse_glb_save)
        out_row.addWidget(self._exp_path_fld, 1)
        out_row.addWidget(out_browse_btn)
        out_lay.addLayout(out_row)

        self._exp_norm_chk = QtWidgets.QCheckBox("Export Normals")
        self._exp_norm_chk.setChecked(True)
        out_lay.addWidget(self._exp_norm_chk)

        self._exp_uv_chk = QtWidgets.QCheckBox("Export UVs")
        self._exp_uv_chk.setChecked(True)
        out_lay.addWidget(self._exp_uv_chk)

        self._exp_tex_chk = QtWidgets.QCheckBox(
            "Embed Texture Files  (DIFF / MTL / RGH / NRM — base colour always exported)"
        )
        self._exp_tex_chk.setChecked(True)
        out_lay.addWidget(self._exp_tex_chk)

        self._exp_cam_chk = QtWidgets.QCheckBox(
            "Export Cameras (perspective, no animation)"
        )
        self._exp_cam_chk.setChecked(True)
        out_lay.addWidget(self._exp_cam_chk)

        self._exp_orm_chk = QtWidgets.QCheckBox(
            "Pack ORM Channels  (requires Pillow)"
        )
        self._exp_orm_chk.setChecked(False)
        out_lay.addWidget(self._exp_orm_chk)

        # Editing path or any option after confirming re-opens step 2.
        self._exp_path_fld.textEdited.connect(self._on_export_option_changed)
        for _w in (self._exp_norm_chk, self._exp_uv_chk, self._exp_tex_chk,
                   self._exp_cam_chk, self._exp_orm_chk):
            _w.toggled.connect(self._on_export_option_changed)

        confirm_row = QtWidgets.QHBoxLayout()
        confirm_row.addStretch(1)
        self._exp_confirm_btn = QtWidgets.QPushButton("Use These Settings")
        self._exp_confirm_btn.setObjectName("btnStepLocked")
        self._exp_confirm_btn.setMinimumHeight(32)
        self._exp_confirm_btn.setMinimumWidth(160)
        self._exp_confirm_btn.clicked.connect(self._confirm_export_options)
        confirm_row.addWidget(self._exp_confirm_btn)
        out_lay.addLayout(confirm_row)

        vbox.addWidget(self._exp_out_frame)

        # ── STEP 3 — EXPORT (RUN section) ───────────────────────────────────
        self._exp_run_frame, run_lay, _run_hbox = _make_section_frame(
            "EXPORT", icon_name="utilities", accent="#E8820C", parent=inner,
        )

        row3, self._exp_step3_badge, self._exp_step3_confirm = \
            self._mk_step_header("3", "EXPORT")
        run_lay.addLayout(row3)

        s3_hint = QtWidgets.QLabel(
            "Write the selected objects to the output .glb file."
        )
        s3_hint.setObjectName("hint")
        s3_hint.setWordWrap(True)
        run_lay.addWidget(s3_hint)

        # Progress bar (no inline colour — styled by tool_qss).
        self._exp_prog = QtWidgets.QProgressBar()
        self._exp_prog.setMaximum(_EXP_STEPS)
        self._exp_prog.setValue(0)
        self._exp_prog.setFixedHeight(14)
        self._exp_prog.setTextVisible(False)
        self._exp_prog.setVisible(False)
        run_lay.addWidget(self._exp_prog)

        self._exp_prog_lbl = QtWidgets.QLabel("")
        self._exp_prog_lbl.setObjectName("hint")
        self._exp_prog_lbl.setVisible(False)
        run_lay.addWidget(self._exp_prog_lbl)

        # Status
        self._export_status = QtWidgets.QLabel(
            "—  Select objects and set output path."
        )
        self._export_status.setObjectName("statusIdle")
        self._export_status.setWordWrap(True)
        run_lay.addWidget(self._export_status)

        # Export button — the step-3 action button.
        self._exp_export_btn = QtWidgets.QPushButton("Export GLB")
        self._exp_export_btn.setObjectName("btnStepLocked")
        self._exp_export_btn.setMinimumHeight(42)
        self._exp_export_btn.clicked.connect(self._do_export)
        run_lay.addWidget(self._exp_export_btn)

        vbox.addWidget(self._exp_run_frame)

        vbox.addStretch()
        scroll.setWidget(inner)

        self._update_export_steps()
        return scroll

    # ── SCENE TAB ────────────────────────────────────────────────────────────

    def _build_scene_tab(self, QtWidgets, QtCore):
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        inner = QtWidgets.QWidget()
        vbox  = QtWidgets.QVBoxLayout(inner)
        vbox.setContentsMargins(14, 12, 14, 14)
        vbox.setSpacing(10)

        # ── SCENE OBJECTS section ───────────────────────────────────────────
        scn_frame, scn_lay, _scn_hbox = _make_section_frame(
            "SCENE OBJECTS", icon_name="scene", accent="#4F9DE0", parent=inner,
        )

        self._hier_list = QtWidgets.QListWidget()
        self._hier_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self._hier_list.setFixedHeight(220)
        self._hier_list.setFont(
            __import__('PySide6').QtGui.QFont("Courier New", 10)
        )
        scn_lay.addWidget(self._hier_list)

        # Hierarchy action buttons — row 1 (neutral)
        row1 = QtWidgets.QHBoxLayout()
        row1.setSpacing(6)
        for label, slot in [
            ("Refresh",     self._refresh_hierarchy),
            ("Select All",  self._select_all_hier),
            ("Select None", self._select_none_hier),
            ("Invert Sel",  self._invert_hier_selection),
        ]:
            btn = QtWidgets.QPushButton(label)
            btn.setObjectName("btnApply")
            btn.clicked.connect(slot)
            row1.addWidget(btn)
        scn_lay.addLayout(row1)

        # Hierarchy action buttons — row 2 (action)
        row2 = QtWidgets.QHBoxLayout()
        row2.setSpacing(6)
        for label, slot in [
            ("Select in Maya", self._select_in_maya),
            ("Hide",           lambda: self._set_visibility_from_hier(False)),
            ("Show",           lambda: self._set_visibility_from_hier(True)),
        ]:
            btn = QtWidgets.QPushButton(label)
            btn.setObjectName("btnAction")
            btn.clicked.connect(slot)
            row2.addWidget(btn)
        scn_lay.addLayout(row2)

        # Note about hierarchy
        note = QtWidgets.QLabel(
            "Tip: Select objects here, then switch to the EXPORT tab to export them."
        )
        note.setObjectName("hint")
        note.setWordWrap(True)
        scn_lay.addWidget(note)

        vbox.addWidget(scn_frame)
        vbox.addStretch()
        scroll.setWidget(inner)
        return scroll

    # ── Guided-flow helpers (replicated from the TurnTable reference) ──────────

    @staticmethod
    def _repolish(w):
        if w is not None:
            w.style().unpolish(w)
            w.style().polish(w)

    def _mk_step_badge(self, text):
        """Small numbered badge: grey (locked) / orange (active) / green (done)."""
        try:
            from PySide6 import QtWidgets, QtCore
        except ImportError:
            from PySide2 import QtWidgets, QtCore
        b = QtWidgets.QLabel(str(text))
        b.setFixedSize(22, 22)
        b.setAlignment(QtCore.Qt.AlignCenter)
        b.setObjectName("stepLocked")
        return b

    def _mk_step_confirm(self):
        """Right-side 'done' badge — the single confirmation per step."""
        try:
            from PySide6 import QtWidgets, QtCore
        except ImportError:
            from PySide2 import QtWidgets, QtCore
        c = QtWidgets.QLabel("")
        c.setObjectName("stepConfirmEmpty")
        c.setFixedWidth(58)
        c.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        return c

    def _set_badge(self, badge, state):
        if badge is None:
            return
        badge.setObjectName(
            {"locked": "stepLocked", "active": "stepReady", "done": "stepDone"}[state]
        )
        self._repolish(badge)

    def _set_step_btn(self, btn, state, gate_enable=True):
        if btn is None:
            return
        btn.setObjectName(
            {"locked": "btnStepLocked", "active": "btnStepActive",
             "done": "btnStepDone"}[state]
        )
        if gate_enable:
            btn.setEnabled(state != "locked")
        self._repolish(btn)

    def _btn_obj(self, btn, name):
        if btn is None:
            return
        btn.setObjectName(name)
        self._repolish(btn)

    def _set_confirm(self, confirm, done):
        if confirm is None:
            return
        confirm.setText("✓ done" if done else "")
        confirm.setObjectName("stepConfirmDone" if done else "stepConfirmEmpty")
        self._repolish(confirm)

    def _mk_step_header(self, num, title):
        """Numbered step header row: [badge] TITLE ............ [✓ done].
        Returns (hbox, badge, confirm)."""
        try:
            from PySide6 import QtWidgets
        except ImportError:
            from PySide2 import QtWidgets
        badge   = self._mk_step_badge(num)
        confirm = self._mk_step_confirm()
        lbl = QtWidgets.QLabel(title)
        lbl.setObjectName("stepTitle")
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(8)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(badge)
        row.addWidget(lbl, 1)
        row.addWidget(confirm)
        return row, badge, confirm

    # ── IMPORT step gating ─────────────────────────────────────────────────────

    def _imp_file_ok(self):
        """Step 1 reality: a real .glb/.gltf path is in the file field."""
        p = self._imp_path_fld.text().strip() if self._imp_path_fld else ""
        return bool(p) and p.lower().endswith((".glb", ".gltf")) and os.path.isfile(p)

    def _on_import_name_changed(self, *_):
        """Editing the asset name after applying re-opens step 2 (re-locks 3-4)."""
        if self._imp_name_confirmed:
            self._imp_name_confirmed = False
            self._imp_opts_confirmed = False
            self._imp_done = False
            self._update_import_steps()

    def _confirm_import_name(self):
        """Step 2 action: lock in the asset name -> collapse SOURCE FILE, open OPTIONS."""
        if not self._imp_file_ok():
            return
        if not self._imp_name_fld.text().strip():
            return
        self._imp_name_confirmed = True
        self._update_import_steps()

    def _on_import_option_changed(self, *_):
        """Changing any option after confirming re-opens step 3 and re-locks 4."""
        if self._imp_opts_confirmed:
            self._imp_opts_confirmed = False
            self._imp_done = False
            self._update_import_steps()

    def _confirm_import_options(self):
        """Step 3 action: lock in the chosen options, unlock step 4 (Import)."""
        if not (self._imp_file_ok() and self._imp_name_confirmed):
            return
        self._imp_opts_confirmed = True
        self._update_import_steps()

    def _update_import_steps(self):
        """State machine: 1 Browse -> 2 Name(Apply) -> 3 Options -> 4 Import.
        Every state is derived from reality; future steps are disabled, and a
        completed section auto-collapses so the active one is the focus."""
        if self._imp_step1_badge is None:
            return
        file_ok = self._imp_file_ok()
        name_ok = file_ok and self._imp_name_confirmed
        opts_ok = name_ok and self._imp_opts_confirmed
        done    = opts_ok and self._imp_done

        # Step 1 — Browse GLB file
        if file_ok:
            self._set_badge(self._imp_step1_badge, "done")
            self._set_confirm(self._imp_step1_confirm, True)
            self._btn_obj(self._imp_browse_btn, "btnApply")
        else:
            self._set_badge(self._imp_step1_badge, "active")
            self._set_confirm(self._imp_step1_confirm, False)
            self._btn_obj(self._imp_browse_btn, "btnStepActive")

        # Step 2 — Asset name (locked until step 1 done)
        self._imp_name_fld.setEnabled(file_ok)
        if name_ok:
            self._set_badge(self._imp_step2_badge, "done")
            self._set_confirm(self._imp_step2_confirm, True)
            self._set_step_btn(self._imp_name_apply_btn, "done")
        else:
            st = "active" if file_ok else "locked"
            self._set_badge(self._imp_step2_badge, st)
            self._set_confirm(self._imp_step2_confirm, False)
            self._set_step_btn(self._imp_name_apply_btn, st)

        # Step 3 — Output folder & options (locked until step 2 done)
        self._imp_opt_frame.setEnabled(name_ok)
        if opts_ok:
            self._set_badge(self._imp_step3_badge, "done")
            self._set_confirm(self._imp_step3_confirm, True)
            self._set_step_btn(self._imp_confirm_btn, "done")
        else:
            st = "active" if name_ok else "locked"
            self._set_badge(self._imp_step3_badge, st)
            self._set_confirm(self._imp_step3_confirm, False)
            self._set_step_btn(self._imp_confirm_btn, st)

        # Step 4 — Import (locked until step 3 done)
        self._imp_run_frame.setEnabled(opts_ok)
        if done:
            self._set_badge(self._imp_step4_badge, "done")
            self._set_confirm(self._imp_step4_confirm, True)
            self._set_step_btn(self._imp_import_btn, "done")
        else:
            st = "active" if opts_ok else "locked"
            self._set_badge(self._imp_step4_badge, st)
            self._set_confirm(self._imp_step4_confirm, False)
            self._set_step_btn(self._imp_import_btn, st)

        # Section progress + auto-collapse: close SOURCE FILE once the name is
        # applied and open OPTIONS; open IMPORT once the options are applied.
        if self._imp_src_frame:
            self._imp_src_frame.set_state("done" if name_ok else "active")
            self._imp_src_frame.set_collapsed(name_ok)
        if self._imp_opt_frame:
            self._imp_opt_frame.set_state(
                "done" if opts_ok else ("active" if name_ok else "idle"))
            self._imp_opt_frame.set_collapsed(not name_ok)
        if self._imp_run_frame:
            self._imp_run_frame.set_state(
                "done" if done else ("active" if opts_ok else "idle"))
            self._imp_run_frame.set_collapsed(not opts_ok)

    # ── EXPORT step gating ─────────────────────────────────────────────────────

    def _capture_export_selection(self):
        """Step 1 action: capture the SCENE-tab selection (resolved to DAG
        paths) as the export source. DONE when ≥1 valid object is captured."""
        sel_items = [
            self._hier_list.item(i).text()
            for i in range(self._hier_list.count())
            if self._hier_list.item(i).isSelected()
        ]
        node_names = []
        for item in sel_items:
            dag = _HIER_MAP.get(item, "")
            if dag and cmds.objExists(dag):
                node_names.append(dag)
        self._exp_node_names = node_names
        self._exp_sel_count  = len(node_names)
        # Re-capturing the source invalidates downstream confirmation + export.
        self._exp_opts_confirmed = False
        self._exp_done           = False
        if self._exp_sel_count:
            shorts = ", ".join(n.split('|')[-1] for n in node_names[:6])
            if self._exp_sel_count > 6:
                shorts += ", …"
            self._exp_sel_label.setText(
                "{} object(s) selected:  {}".format(self._exp_sel_count, shorts))
        else:
            self._exp_sel_label.setText(
                "No objects selected — pick them in the SCENE tab first.")
        self._update_export_steps()

    def _on_export_option_changed(self, *_):
        """Changing the path or any option after confirming re-opens step 2."""
        if self._exp_opts_confirmed:
            self._exp_opts_confirmed = False
            self._exp_done = False
            self._update_export_steps()

    def _exp_path_ok(self):
        return bool(self._exp_path_fld and self._exp_path_fld.text().strip())

    def _confirm_export_options(self):
        """Step 2 action: lock in the output path + options, unlock step 3."""
        if not (self._exp_sel_count and self._exp_path_ok()):
            return
        self._exp_opts_confirmed = True
        self._update_export_steps()

    def _update_export_steps(self):
        """State machine: 1 Select objects -> 2 Output options -> 3 Export.
        Every state is derived from reality; future steps are disabled."""
        if self._exp_step1_badge is None:
            return
        sel_ok  = self._exp_sel_count > 0
        opts_ok = sel_ok and self._exp_opts_confirmed and self._exp_path_ok()
        done    = opts_ok and self._exp_done

        # Step 1 — Select objects
        if sel_ok:
            self._set_badge(self._exp_step1_badge, "done")
            self._set_confirm(self._exp_step1_confirm, True)
            self._btn_obj(self._exp_sel_btn, "btnApply")
        else:
            self._set_badge(self._exp_step1_badge, "active")
            self._set_confirm(self._exp_step1_confirm, False)
            self._btn_obj(self._exp_sel_btn, "btnStepActive")

        # Step 2 — Output options (locked until step 1 done)
        self._exp_out_frame.setEnabled(sel_ok)
        if opts_ok:
            self._set_badge(self._exp_step2_badge, "done")
            self._set_confirm(self._exp_step2_confirm, True)
            self._set_step_btn(self._exp_confirm_btn, "done")
        else:
            st = "active" if sel_ok else "locked"
            self._set_badge(self._exp_step2_badge, st)
            self._set_confirm(self._exp_step2_confirm, False)
            self._set_step_btn(self._exp_confirm_btn, st)

        # Step 3 — Export (locked until step 2 done)
        if done:
            self._set_badge(self._exp_step3_badge, "done")
            self._set_confirm(self._exp_step3_confirm, True)
            self._set_step_btn(self._exp_export_btn, "done")
        else:
            st = "active" if opts_ok else "locked"
            self._set_badge(self._exp_step3_badge, st)
            self._set_confirm(self._exp_step3_confirm, False)
            self._set_step_btn(self._exp_export_btn, st)

        # Section progress states
        if self._exp_sel_frame:
            self._exp_sel_frame.set_state("done" if sel_ok else "active")
        if self._exp_out_frame:
            self._exp_out_frame.set_state(
                "done" if opts_ok else ("active" if sel_ok else "idle"))
        if self._exp_run_frame:
            self._exp_run_frame.set_state(
                "done" if done else ("active" if opts_ok else "idle"))

    # ── Status helpers ────────────────────────────────────────────────────────

    def _set_import_status(self, msg, state="idle"):
        name = {"ok": "statusOk", "err": "statusErr", "idle": "statusIdle"}.get(
            state, "statusIdle"
        )
        self._import_status.setObjectName(name)
        self._import_status.setText(msg)
        self._import_status.setStyle(self._import_status.style())

    def _set_export_status(self, msg, state="idle"):
        name = {"ok": "statusOk", "err": "statusErr", "idle": "statusIdle"}.get(
            state, "statusIdle"
        )
        self._export_status.setObjectName(name)
        self._export_status.setText(msg)
        self._export_status.setStyle(self._export_status.style())

    # ── Import callbacks ──────────────────────────────────────────────────────

    def _browse_glb(self):
        res = cmds.fileDialog2(fileMode=1, caption="Select GLB File",
                               fileFilter="GLB Files (*.glb *.gltf)")
        if not res:
            return
        path = res[0]
        self._imp_path_fld.setText(path)
        # Auto-fill the asset name from the file (user confirms/edits in step 2).
        auto = (os.path.splitext(os.path.basename(path))[0]
                .replace("-", "_").replace(" ", "_").replace(".", "_"))
        self._imp_name_fld.setText(auto)
        # A new file invalidates downstream confirmation + the completed import.
        self._imp_name_confirmed = False
        self._imp_opts_confirmed = False
        self._imp_done           = False
        self._update_import_steps()

    def _browse_tex_folder(self):
        res = cmds.fileDialog2(fileMode=3, caption="Select Folder")
        if res:
            self._imp_tex_fld.setText(res[0])

    def _do_import(self):
        from PySide6 import QtWidgets as QW
        # Step-gate guard (defense in depth — the button is also disabled).
        if not (self._imp_file_ok() and self._imp_name_confirmed
                and self._imp_opts_confirmed):
            return
        path = self._imp_path_fld.text().strip()
        if not path:
            self._set_import_status("✕  No file selected.", "err")
            return
        if not os.path.isfile(path):
            self._set_import_status(
                "✕  File not found: {}".format(path), "err"
            )
            return

        asset_name = self._imp_name_fld.text().strip()
        if not asset_name:
            asset_name = (os.path.splitext(os.path.basename(path))[0]
                          .replace("-", "_").replace(" ", "_").replace(".", "_"))

        import_uvs  = self._imp_uv_chk.isChecked()
        extract_tex = self._imp_tex_chk.isChecked()
        create_mat  = self._imp_mat_chk.isChecked()
        ref_cube    = self._imp_ref_chk.isChecked()

        tex_dir = self._imp_tex_fld.text().strip()
        if extract_tex and not tex_dir:
            tex_dir = os.path.join(os.path.dirname(path), asset_name + "_textures")
            self._imp_tex_fld.setText(tex_dir)

        shader_type = self._imp_shader_menu.currentText()
        use_aces    = self._imp_aces_menu.currentText() == "ACES 1.2"

        _prog_state = [0]

        def prog_cb(msg):
            _prog_state[0] += 1
            step = min(_prog_state[0], _IMP_STEPS)
            self._imp_prog.setValue(step)
            self._imp_prog.setVisible(True)
            self._imp_prog_lbl.setText("  {}".format(msg))
            self._imp_prog_lbl.setVisible(True)
            QW.QApplication.processEvents()

        self._imp_prog.setValue(0)
        self._imp_prog.setVisible(True)
        self._imp_prog_lbl.setText("  Starting…")
        self._imp_prog_lbl.setVisible(True)
        QW.QApplication.processEvents()
        self._set_import_status("—  Importing…", "idle")

        try:
            root, tex_result = import_glb(
                path, asset_name,
                import_uvs, extract_tex, tex_dir,
                create_mat, shader_type, use_aces,
                ref_cube,
                prog_cb=prog_cb,
            )
            self._imp_prog.setValue(_IMP_STEPS)
            QW.QApplication.processEvents()

            parts = ["Done!  {}".format(root)]
            if tex_result:
                parts.append(" ".join(["_" + k for k in sorted(tex_result.keys())]))
            if create_mat:
                parts.append("Mat: {}_MAT".format(asset_name))
            self._set_import_status(
                "✓  " + "   ".join(parts), "ok"
            )

            self._imp_prog.setVisible(False)
            self._imp_prog_lbl.setVisible(False)
            # Step 3 done only on a clean import success.
            self._imp_done = True
            self._update_import_steps()
            # Refresh scene hierarchy
            self._refresh_hierarchy()

        except Exception as exc:
            _log.exception("Import failed: %s", exc)
            self._imp_prog.setVisible(False)
            self._imp_prog_lbl.setVisible(False)
            self._set_import_status(
                "✕  ERROR: {}".format(exc), "err"
            )
            cmds.warning("PXLtools GLB Manager: Import failed — {}".format(exc))

    # ── Export callbacks ──────────────────────────────────────────────────────

    def _browse_glb_save(self):
        res = cmds.fileDialog2(fileMode=0, caption="Save GLB As…",
                               fileFilter="GLB File (*.glb)",
                               dialogStyle=2)
        if res:
            path = res[0]
            if not path.lower().endswith('.glb'):
                path += '.glb'
            self._exp_path_fld.setText(path)
            # setText() does not emit textEdited — invalidate + re-gate by hand.
            self._exp_opts_confirmed = False
            self._exp_done           = False
            self._update_export_steps()

    def _do_export(self):
        from PySide6 import QtWidgets as QW

        # Step-gate guard (defense in depth — the button is also disabled).
        if not (self._exp_sel_count > 0 and self._exp_opts_confirmed
                and self._exp_path_ok()):
            return

        # Selection captured at step 1 (Use Scene Selection). Fall back to the
        # live Scene-tab selection if nothing was captured — same resolution
        # logic as before (DAG path lookup + objExists), only sourced earlier.
        node_names = list(getattr(self, "_exp_node_names", []) or [])
        if not node_names:
            sel_items = [
                self._hier_list.item(i).text()
                for i in range(self._hier_list.count())
                if self._hier_list.item(i).isSelected()
            ]
            if not sel_items:
                self._set_export_status(
                    "✕  Select at least one object in the Scene tab.", "err"
                )
                return
            for item in sel_items:
                dag = _HIER_MAP.get(item, "")
                if dag and cmds.objExists(dag):
                    node_names.append(dag)

        # Drop any captured nodes that no longer exist.
        node_names = [n for n in node_names if cmds.objExists(n)]
        if not node_names:
            self._set_export_status(
                "✕  Selected objects no longer exist — Refresh the Scene tab.", "err"
            )
            return

        out_path = self._exp_path_fld.text().strip()
        if not out_path:
            self._set_export_status(
                "✕  No output file path specified.", "err"
            )
            return
        if not out_path.lower().endswith('.glb'):
            out_path += '.glb'

        export_normals = self._exp_norm_chk.isChecked()
        export_uvs     = self._exp_uv_chk.isChecked()
        embed_textures = self._exp_tex_chk.isChecked()
        export_cameras = self._exp_cam_chk.isChecked()
        pack_orm       = self._exp_orm_chk.isChecked()

        _prog_state = [0]

        def prog_cb(msg):
            _prog_state[0] += 1
            step = min(_prog_state[0], _EXP_STEPS)
            self._exp_prog.setValue(step)
            self._exp_prog.setVisible(True)
            self._exp_prog_lbl.setText("  {}".format(msg))
            self._exp_prog_lbl.setVisible(True)
            QW.QApplication.processEvents()

        self._exp_prog.setValue(0)
        self._exp_prog.setVisible(True)
        self._exp_prog_lbl.setText("  Starting export…")
        self._exp_prog_lbl.setVisible(True)
        QW.QApplication.processEvents()
        self._set_export_status("—  Exporting…", "idle")

        try:
            n = export_glb(
                node_names, out_path,
                export_normals, export_uvs,
                embed_textures, export_cameras, pack_orm,
                prog_cb=prog_cb,
            )
            self._exp_prog.setValue(_EXP_STEPS)
            QW.QApplication.processEvents()

            size_kb = os.path.getsize(out_path) / 1024.0
            self._set_export_status(
                "✓  Exported {} item(s) → {} ({:.1f} KB)".format(
                    n, os.path.basename(out_path), size_kb
                ), "ok"
            )

            self._exp_prog.setVisible(False)
            self._exp_prog_lbl.setVisible(False)
            # Step 3 done only on a clean export success.
            self._exp_done = True
            self._update_export_steps()

        except ValueError as exc:
            msg = str(exc)
            self._exp_prog.setVisible(False)
            self._exp_prog_lbl.setVisible(False)
            if "More than one object matches name" in msg:
                dup = msg.split(":")[-1].strip() if ":" in msg else msg
                friendly = (
                    "Duplicate name '{}' — objects must have unique names. "
                    "Fix: select the duplicates and rename them using the "
                    "Advanced Batch Renamer, then Refresh the Scene tab.".format(dup)
                )
                self._set_export_status("✕  " + friendly, "err")
                cmds.warning("PXLtools GLB Manager: " + friendly)
            else:
                _log.exception("Export failed: %s", exc)
                self._set_export_status("✕  ERROR: {}".format(exc), "err")
                cmds.warning(
                    "PXLtools GLB Manager: Export failed — {}".format(exc)
                )
        except Exception as exc:
            _log.exception("Export failed: %s", exc)
            self._exp_prog.setVisible(False)
            self._exp_prog_lbl.setVisible(False)
            self._set_export_status("✕  ERROR: {}".format(exc), "err")
            cmds.warning(
                "PXLtools GLB Manager: Export failed — {}".format(exc)
            )

    # ── Scene / hierarchy callbacks ───────────────────────────────────────────

    def _refresh_hierarchy(self):
        global _HIER_MAP
        _HIER_MAP = {}
        self._hier_list.clear()

        all_dag = cmds.ls(type='transform', long=True) or []
        top_level = []
        for t in all_dag:
            parents = cmds.listRelatives(t, parent=True, fullPath=True) or []
            if not parents:
                top_level.append(t)

        duplicate_names = []

        def _add(node_path, depth):
            try:
                tag = _get_node_type_tag(node_path)
            except Exception:
                return
            if tag == 'OTH ':
                return
            short   = node_path.split('|')[-1]
            indent  = '  ' * min(depth, 8)
            display = "[{}] {}{}".format(tag, indent, short)

            if display in _HIER_MAP:
                duplicate_names.append(short)
                display = "[{}] {}{}  [!DUP]".format(tag, indent, short)

            _HIER_MAP[display] = node_path
            self._hier_list.addItem(display)

            children = (
                cmds.listRelatives(
                    node_path, children=True, type='transform', fullPath=True
                ) or []
            )
            for child in sorted(children):
                _add(child, depth + 1)

        for node in sorted(top_level):
            _add(node, 0)

        count = len(_HIER_MAP)
        _log.info("Hierarchy refreshed — %d objects.", count)

        if duplicate_names:
            dupes = ", ".join(sorted(set(duplicate_names)))
            _log.warning("Duplicate node names detected: %s", dupes)
            cmds.warning(
                "PXLtools GLB Manager — Duplicate names detected: [{}]. "
                "Maya cannot resolve these by short name. "
                "Rename the objects to unique names using the Advanced Batch Renamer "
                "or Outliner > right-click > Rename before exporting.".format(dupes)
            )

    def _select_all_hier(self):
        for i in range(self._hier_list.count()):
            self._hier_list.item(i).setSelected(True)

    def _select_none_hier(self):
        self._hier_list.clearSelection()

    def _invert_hier_selection(self):
        for i in range(self._hier_list.count()):
            item = self._hier_list.item(i)
            item.setSelected(not item.isSelected())

    def _select_in_maya(self):
        sel_items = [
            self._hier_list.item(i).text()
            for i in range(self._hier_list.count())
            if self._hier_list.item(i).isSelected()
        ]
        nodes = [
            _HIER_MAP[i] for i in sel_items
            if i in _HIER_MAP and cmds.objExists(_HIER_MAP[i])
        ]
        if nodes:
            cmds.select(nodes, replace=True)
            _log.info("Selected in Maya: %s", nodes)
        else:
            cmds.select(clear=True)

    def _set_visibility_from_hier(self, visible):
        sel_items = [
            self._hier_list.item(i).text()
            for i in range(self._hier_list.count())
            if self._hier_list.item(i).isSelected()
        ]
        nodes = [
            _HIER_MAP[i] for i in sel_items
            if i in _HIER_MAP and cmds.objExists(_HIER_MAP[i])
        ]
        if not nodes:
            return
        for node in nodes:
            try:
                cmds.setAttr(node + '.visibility', 1 if visible else 0)
            except Exception as exc:
                _log.warning(
                    "Could not set visibility on %s: %s", node, exc
                )
        action = "Shown" if visible else "Hidden"
        _log.info("%s: %s", action, nodes)


# =============================================================================
# ENTRY POINT
# =============================================================================

def run():
    """Launch the PXLtools GLB Manager."""
    GLBManager()
    # Auto-update: check GitHub for a newer STABLE release (throttled once/day),
    # deferred so it never slows the tool open and can't break launch.
    try:
        from pxl_ui import pxl_update
        cmds.evalDeferred(lambda: pxl_update.check(channel="stable", dcc="maya"),
                          lowestPriority=True)
    except Exception:
        pass


def show():
    run()


run()
