"""
Tool Name   : PXLmentor GLB Manager
Version     : 0.1.8-alpha
Stage       : Alpha
Checkpoint  : CP9
Author      : PXLmentor AI Pipeline TD
Description : Unified GLB import / export manager for Maya.
              IMPORT — Parse GLB/GLTF binary, build mesh geometry via OpenMaya2,
              extract & split ORM textures, create Arnold PBR materials with ACES
              pipeline, place asset on ground plane, optional 1m reference cube.
              EXPORT — Export selected Maya meshes and cameras to GLB binary.
              Reads Arnold/lambert shading networks, embeds textures, packs ORM
              channels (Pillow), writes valid glTF 2.0 binary.
              SCENE PANEL — Indented scene hierarchy browser; select, hide/show
              assets in the Maya scene directly from the tool.

Changelog:
    0.1.8-alpha - PXLtools branding pass: in-tool header logo swapped
                 from PixelMentor_Logo_Long.png to PXLtools_logo.png.
                 Fallback text label changed to "PXLtools".
    0.1.7-alpha - CP008: Conform to PXLMENTOR_TOOL_STANDARD v1.1.0 - removed
                  the 96x96 right-spacer from _build_header so the PXLmentor
                  logo centers in the visible content area (right of the tool
                  icon) rather than on the dialog geometric midline. The
                  previous symmetric layout looked off-balance because the
                  spacer carried no visual weight. Also formalizes the
                  filename/header version mismatch — the in-file VERSION
                  constant already declared 0.1.7-alpha; this pass renames
                  the file from v0_1_6_alpha to v0_1_7_alpha to match.
    0.1.6-alpha - CP007: Full PySide6 QDialog migration — same dark theme as
                  TurnTable Builder v1.0.5. Replaced cmds.window + all cmds
                  widgets with QDialog + QTabWidget + Qt equivalents. Singleton
                  pattern added. QScrollArea wraps tab contents. MAIN_QSS applied
                  globally.
    0.1.5-alpha - CP006: Opacity support — import and export.
                  EXPORT:
                  - build_glb_data() now writes alphaMode on the glTF material:
                      "BLEND" when alpha < 0.999 (semi-transparent mesh),
                      "OPAQUE" otherwise.
                    Without alphaMode="BLEND", glTF spec defaults to OPAQUE and
                    all renderers (including ComfyUI) ignore baseColorFactor alpha.
                    Fixes: transparency invisible in ComfyUI GLB viewer.
                  IMPORT:
                  - extract_textures() now reads baseColorFactor [r,g,b,a] and
                    alphaMode from glTF materials. Stored as BASE_COLOR and
                    ALPHA_MODE keys in the tex_map dict.
                  - create_material() now applies BASE_COLOR on import:
                      * RGB → shader colour (aiStandardSurface.baseColor or
                        lambert.color) when no DIFF texture is present.
                      * Alpha → aiStandardSurface.opacity or lambert.transparency
                        (inverted), always applied regardless of DIFF texture.
    0.1.4-alpha - CP005: Texture embed robustness fix.
                  - _file_path_from_attr() now wraps cmds.listConnections in try/except
                    to handle shader attributes that don't exist on the shader type
                    (e.g. lambert.baseColor, lambert.metalness) without silently
                    dropping the entire mesh from the export.
                  - build_glb_data() texture-embedding block wrapped in per-mesh
                    try/except: an _embed_image() failure now logs a warning and falls
                    back to flat baseColorFactor instead of aborting the whole loop.
                    Fixes: "only cameras in GLB when Embed Texture Files is ON".
                  - Removed stale dead-code line (tex_map key, superseded by mat_data).
    0.1.3-alpha - CP004: Material colour export + texture checkbox clarification.
                  - collect_textures_from_shader() replaced by collect_material_data().
                    Now always reads flat base colour (lambert/blinn/phong/phongE/
                    aiStandardSurface) so every mesh gets a distinguishable material
                    even without file textures. Supports transparency / opacity.
                  - build_glb_data() always writes a glTF material per mesh with
                    baseColorFactor — never leaves a mesh without a material.
                    File textures (DIFF/MTL/RGH/NRM) layered on top when present.
                  - export_glb() collects material data unconditionally; embed_textures
                    flag now only controls whether texture file bytes enter the BIN chunk.
                  - UI checkbox relabelled: "Embed Texture Files (DIFF/MTL/RGH/NRM —
                    base colour always exported)" to remove ambiguity.
    0.1.2-alpha - CP003: selectAll flag fix.
                  - textScrollList 'selectAll' flag not available in Maya 2025.
                    Replaced with _select_all_hier() helper that iterates items.
    0.1.1-alpha - CP002: Duplicate-name robustness pass.
                  - _get_node_type_tag() now always receives full DAG path —
                    eliminates ValueError "More than one object matches name".
                  - refresh_hierarchy() detects duplicate short names, marks
                    them [!DUP] in the list, and emits a Maya warning with a
                    rename suggestion (Advanced Batch Renamer).
                  - do_export() catches ValueError separately; duplicate-name
                    errors surface a friendly status message with rename
                    instructions instead of a raw traceback.
    0.1.0-alpha - CP001: Initial unified GLB Manager.
                  Combined GLB Importer v0.9.1-beta with new GLB Exporter.
                  Tab-based UI: IMPORT | EXPORT.
                  EXPORT: mesh triangulation via OpenMaya2 (world space),
                          camera export (perspective FOV + world matrix),
                          Arnold/lambert texture network traversal,
                          ORM channel packing (Pillow optional),
                          binary GLB writer (JSON chunk + BIN chunk).
                  SCENE PANEL: indented DAG hierarchy in textScrollList,
                               refresh, select-all/none/invert,
                               Select in Maya, Hide, Show buttons.
                  All import functionality preserved from v0.9.1-beta.
"""

import maya.cmds as cmds
import maya.api.OpenMaya as om2
import math
import struct
import json
import os
import base64
import logging


# =============================================================================
# LOGGER
# =============================================================================

_log = logging.getLogger("PXLmentor.GLBManager")
_log.setLevel(logging.DEBUG)
if not _log.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(
        logging.Formatter("[PXLmentor GLB Manager] %(levelname)s: %(message)s")
    )
    _log.addHandler(_h)


# =============================================================================
# COLOUR TOKENS
# =============================================================================

class _C:
    BG_DARK        = "#333333"
    BG_WINDOW      = "#464646"
    BG_SECTION_HDR = "#393939"
    BG_SECTION_BOD = "#4a4a4a"
    BG_INPUT       = "#3a3a3a"
    BG_HEADER      = "#0D1F24"
    BORDER         = "#2b2b2b"
    ORANGE         = "#E8820C"
    TEXT_PRIMARY   = "#dcdcdc"
    TEXT_MUTED     = "#b0b0b0"
    STATUS_OK_BG   = "#2a402a"
    STATUS_OK_TEXT = "#7acc7a"
    STATUS_ERR_BG  = "#4a3030"
    STATUS_ERR_TEXT = "#e07070"
    BTN_ACTION_BG  = "#2a3850"
    BTN_ACTION_TEXT = "#8ab0d0"
    HEADER_BG      = (0.051, 0.122, 0.141)
    BTN_PRIMARY    = (0.910, 0.510, 0.047)
    BTN_RESET      = (0.320, 0.320, 0.320)
    BTN_ACTION     = (0.200, 0.380, 0.540)
    STATUS_OK      = (0.220, 0.420, 0.220)
    STATUS_ERR     = (0.500, 0.220, 0.220)
    STATUS_IDLE    = (0.220, 0.220, 0.220)


MAIN_QSS = """
QDialog, QWidget {
    background: #464646;
    color: #dcdcdc;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
}
QTabWidget::pane { border: none; background: #464646; }
QTabBar { background: #393939; border-bottom: 1px solid #2b2b2b; }
QTabBar::tab {
    background: #393939; color: #888888;
    padding: 10px 24px; font-size: 12px; font-weight: bold;
    letter-spacing: 1px; border-bottom: 2px solid transparent;
    margin-bottom: -1px;
}
QTabBar::tab:selected { color: #dcdcdc; border-bottom: 2px solid #E8820C; }
QTabBar::tab:hover:!selected { color: #b0b0b0; }
QScrollArea { border: none; background: #464646; }
QScrollBar:vertical { background: #3a3a3a; width: 8px; }
QScrollBar::handle:vertical { background: #606060; border-radius: 4px; }
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
QPushButton#btnAction {
    background: #2a3850; color: #8ab0d0; border: 1px solid #3a5a7a;
}
QPushButton#btnAction:hover { background: #3a4860; color: #a0c8e8; }
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
QLineEdit {
    background: #3a3a3a; color: #dcdcdc;
    border: 1px solid #2b2b2b; border-radius: 2px;
    padding: 4px 8px; font-size: 12px;
}
QListWidget {
    background: #3a3a3a; color: #dcdcdc;
    border: 1px solid #2b2b2b; border-radius: 2px;
    font-size: 12px;
}
QListWidget::item:selected { background: #E8820C; color: white; }
QCheckBox { color: #dcdcdc; font-size: 12px; spacing: 8px; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border-radius: 2px; background: #3a3a3a; border: 1px solid #2b2b2b;
}
QCheckBox::indicator:checked { background: #E8820C; border: 1px solid #c06000; }
QCheckBox:disabled { color: #686868; }
QFrame#divider {
    background: #2b2b2b; border: none; max-height: 1px; min-height: 1px;
}
"""


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
            "generator": "PXLmentor GLB Manager v{}".format(VERSION),
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

VERSION            = "0.1.8-alpha"
WINDOW_OBJECT_NAME = "PXLmentorGLBManager_v018"

_IMP_STEPS = 8    # import progress steps
_EXP_STEPS = 6    # export progress steps

# Module-level scene hierarchy map: display_string → full_dag_path
_HIER_MAP = {}

# Singleton reference
_INSTANCE = None


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


# ── Helper: CollapsibleSection ────────────────────────────────────────────────

class CollapsibleSection(object):
    """Collapsible section — header bar + body frame."""

    def __init__(self, title, number=None, parent=None):
        from PySide6 import QtWidgets, QtCore, QtGui

        self._collapsed = False
        self._container = QtWidgets.QWidget(parent)
        outer = QtWidgets.QVBoxLayout(self._container)
        outer.setContentsMargins(0, 0, 0, 2)
        outer.setSpacing(0)

        self._header = QtWidgets.QFrame()
        self._header.setFixedHeight(38)
        self._header.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self._header.setStyleSheet(
            "QFrame { background: #393939; border: 1px solid #2b2b2b; "
            "border-bottom: none; border-radius: 3px 3px 0 0; }"
        )
        hbox = QtWidgets.QHBoxLayout(self._header)
        hbox.setContentsMargins(10, 0, 10, 0)
        hbox.setSpacing(6)

        self._arrow = QtWidgets.QLabel("▾")
        self._arrow.setStyleSheet("color: #E8820C; font-size: 16px; background: transparent;")
        hbox.addWidget(self._arrow)

        if number:
            num_lbl = QtWidgets.QLabel(number)
            num_lbl.setStyleSheet(
                "color: #aaaaaa; font-size: 12px; font-family: 'Courier New'; background: transparent;"
            )
            hbox.addWidget(num_lbl)

        title_lbl = QtWidgets.QLabel(title.upper())
        title_lbl.setStyleSheet(
            "color: #dcdcdc; font-weight: bold; font-size: 12px; "
            "letter-spacing: 1px; background: transparent;"
        )
        hbox.addWidget(title_lbl)
        hbox.addStretch()
        outer.addWidget(self._header)

        self._body = QtWidgets.QFrame()
        self._body.setStyleSheet(
            "QFrame { background: #4a4a4a; border: 1px solid #2b2b2b; "
            "border-top: 1px solid #3a3a3a; border-radius: 0 0 3px 3px; }"
        )
        self._body_layout = QtWidgets.QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(10, 10, 10, 12)
        self._body_layout.setSpacing(6)
        outer.addWidget(self._body)

        self._header.mousePressEvent = lambda _e: self.set_collapsed(not self._collapsed)

    @property
    def widget(self):
        return self._container

    @property
    def body_layout(self):
        return self._body_layout

    def add_widget(self, w):
        self._body_layout.addWidget(w)

    def set_collapsed(self, collapsed):
        self._collapsed = collapsed
        self._body.setVisible(not collapsed)
        self._arrow.setText("▸" if collapsed else "▾")
        if collapsed:
            self._header.setStyleSheet(
                "QFrame { background: #3a3a3a; border: 1px solid #2b2b2b; border-radius: 3px; }"
            )
            self._arrow.setStyleSheet("color: #888888; font-size: 16px; background: transparent;")
        else:
            self._header.setStyleSheet(
                "QFrame { background: #393939; border: 1px solid #2b2b2b; "
                "border-bottom: none; border-radius: 3px 3px 0 0; }"
            )
            self._arrow.setStyleSheet("color: #E8820C; font-size: 16px; background: transparent;")
        self._container.updateGeometry()


# =============================================================================
# ── MAIN DIALOG ───────────────────────────────────────────────────────────────
# =============================================================================

class GLBManager(object):
    """
    PySide6 QDialog singleton for the PXLmentor GLB Manager.
    Mirrors the full TurnTable Builder v1.0.5 dark-theme QDialog pattern.
    """

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

        # ── Parent to Maya main window ────────────────────────────────────────
        main_ptr = omui.MQtUtil.mainWindow()
        maya_win = shiboken6.wrapInstance(int(main_ptr), QtWidgets.QWidget)

        self._dialog = QtWidgets.QDialog(maya_win)
        self._dialog.setObjectName(WINDOW_OBJECT_NAME)
        self._dialog.setWindowTitle(
            "PXLmentor  —  GLB Manager  v{}".format(VERSION)
        )
        self._dialog.setMinimumWidth(580)
        self._dialog.resize(600, 760)
        self._dialog.setStyleSheet(MAIN_QSS)
        self._dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

        root_vbox = QtWidgets.QVBoxLayout(self._dialog)
        root_vbox.setContentsMargins(0, 0, 0, 0)
        root_vbox.setSpacing(0)

        # ── Branded header ────────────────────────────────────────────────────
        root_vbox.addWidget(self._build_header(QtCore, QtGui, QtWidgets))

        # ── Instructions (collapsible, collapsed by default) ──────────────────
        root_vbox.addWidget(self._build_instructions())

        # ── Divider ───────────────────────────────────────────────────────────
        div = QtWidgets.QFrame()
        div.setObjectName("divider")
        div.setFrameShape(QtWidgets.QFrame.HLine)
        root_vbox.addWidget(div)

        # ── Tab widget ────────────────────────────────────────────────────────
        self._tabs = QtWidgets.QTabWidget()
        self._tabs.addTab(self._build_import_tab(QtWidgets, QtCore), "  IMPORT  ")
        self._tabs.addTab(self._build_export_tab(QtWidgets, QtCore), "  EXPORT  ")
        self._tabs.addTab(self._build_scene_tab(QtWidgets, QtCore),  "  SCENE   ")
        root_vbox.addWidget(self._tabs, 1)

        self._dialog.show()

        # Auto-populate hierarchy on open
        self._refresh_hierarchy()

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self, QtCore, QtGui, QtWidgets):
        icon_path = cmds.internalVar(userPrefDir=True) + "icons/"
        bg_int    = tuple(int(round(v * 255)) for v in _C.HEADER_BG)

        header_widget = QtWidgets.QWidget()
        header_widget.setFixedHeight(106)
        header_widget.setStyleSheet(
            "background-color: rgb({},{},{});".format(*bg_int)
        )

        root_hbox = QtWidgets.QHBoxLayout(header_widget)
        root_hbox.setContentsMargins(10, 5, 10, 5)
        root_hbox.setSpacing(0)

        left_label = QtWidgets.QLabel()
        left_label.setFixedSize(96, 96)
        left_label.setAlignment(QtCore.Qt.AlignCenter)
        tool_icon = icon_path + "icon_glb_manager.png"
        if os.path.exists(tool_icon):
            pix = QtGui.QPixmap(tool_icon).scaled(
                96, 96, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            )
            left_label.setPixmap(pix)
        else:
            fallback = icon_path + "icon_glb_importer.png"
            if os.path.exists(fallback):
                pix = QtGui.QPixmap(fallback).scaled(
                    96, 96, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
                )
                left_label.setPixmap(pix)
            else:
                left_label.setText("[Icon]")
                left_label.setStyleSheet("background-color: rgb(51,51,51); color: white;")
        root_hbox.addWidget(left_label)

        center_vbox = QtWidgets.QVBoxLayout()
        center_vbox.setContentsMargins(0, 0, 0, 0)
        center_vbox.setSpacing(2)
        center_vbox.setAlignment(QtCore.Qt.AlignVCenter)

        logo_label = QtWidgets.QLabel()
        logo_label.setFixedSize(262, 48)
        logo_label.setAlignment(QtCore.Qt.AlignCenter)
        logo_path = icon_path + "PXLtools_logo.png"
        if os.path.exists(logo_path):
            logo_pix = QtGui.QPixmap(logo_path).scaled(
                262, 48, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            )
            logo_label.setPixmap(logo_pix)
        else:
            logo_label.setText("PXLmentor")
            logo_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")

        logo_hbox = QtWidgets.QHBoxLayout()
        logo_hbox.setContentsMargins(0, 0, 0, 0)
        logo_hbox.addStretch()
        logo_hbox.addWidget(logo_label)
        logo_hbox.addStretch()

        name_lbl = QtWidgets.QLabel("GLB Manager")
        name_lbl.setAlignment(QtCore.Qt.AlignCenter)
        name_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")

        ver_lbl = QtWidgets.QLabel("v{}".format(VERSION))
        ver_lbl.setAlignment(QtCore.Qt.AlignCenter)
        ver_lbl.setStyleSheet("color: #aaaaaa; font-size: 9px;")

        center_vbox.addLayout(logo_hbox)
        center_vbox.addWidget(name_lbl)
        center_vbox.addWidget(ver_lbl)
        root_hbox.addLayout(center_vbox, 1)

        # NO right spacer per PXLMENTOR_TOOL_STANDARD v1.1.0 - the center_vbox
        # stretches all the way to the right margin so the logo centers in the
        # visible content area (visually balanced against the left icon).

        return header_widget

    # ── Instructions panel ────────────────────────────────────────────────────

    def _build_instructions(self):
        from PySide6 import QtWidgets
        instr = CollapsibleSection("Instructions")
        instr.set_collapsed(True)
        for line in [
            "IMPORT: Browse a .glb/.gltf file, configure options, click Import.",
            "EXPORT: Use the Scene panel to select objects, set output path, click Export GLB.",
            "SCENE:  Refresh updates the list. Select/Hide/Show act on the Maya scene.",
            "         Multi-select supported. Groups are auto-expanded on export.",
        ]:
            lbl = QtWidgets.QLabel(line)
            lbl.setStyleSheet("color: #b0b0b0; font-size: 11px;")
            instr.add_widget(lbl)
        return instr.widget

    # ── IMPORT TAB ────────────────────────────────────────────────────────────

    def _build_import_tab(self, QtWidgets, QtCore):
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        inner = QtWidgets.QWidget()
        vbox  = QtWidgets.QVBoxLayout(inner)
        vbox.setContentsMargins(14, 12, 14, 14)
        vbox.setSpacing(6)

        # GLB File ────────────────────────────────────────────────────────────
        lbl = QtWidgets.QLabel("GLB File:")
        lbl.setStyleSheet("font-weight: bold; color: #dcdcdc;")
        vbox.addWidget(lbl)

        file_row = QtWidgets.QHBoxLayout()
        self._imp_path_fld = QtWidgets.QLineEdit()
        self._imp_path_fld.setReadOnly(True)
        self._imp_path_fld.setPlaceholderText("No file selected…")
        browse_btn = QtWidgets.QPushButton("Browse…")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self._browse_glb)
        file_row.addWidget(self._imp_path_fld, 1)
        file_row.addWidget(browse_btn)
        vbox.addLayout(file_row)

        vbox.addSpacing(6)

        # Asset Name ──────────────────────────────────────────────────────────
        lbl2 = QtWidgets.QLabel("Asset Name:")
        lbl2.setStyleSheet("font-weight: bold; color: #dcdcdc;")
        vbox.addWidget(lbl2)
        self._imp_name_fld = QtWidgets.QLineEdit()
        self._imp_name_fld.setPlaceholderText("Auto from filename…")
        vbox.addWidget(self._imp_name_fld)

        # Divider
        d = QtWidgets.QFrame(); d.setObjectName("divider")
        d.setFrameShape(QtWidgets.QFrame.HLine); vbox.addWidget(d)

        # Options ─────────────────────────────────────────────────────────────
        lbl3 = QtWidgets.QLabel("OPTIONS:")
        lbl3.setStyleSheet("font-weight: bold; color: #dcdcdc;")
        vbox.addWidget(lbl3)

        self._imp_uv_chk = QtWidgets.QCheckBox("Import UVs")
        self._imp_uv_chk.setChecked(True)
        vbox.addWidget(self._imp_uv_chk)

        self._imp_tex_chk = QtWidgets.QCheckBox(
            "Extract Textures  (_DIFF  _MTL  _RGH  _NRM)"
        )
        self._imp_tex_chk.setChecked(True)
        vbox.addWidget(self._imp_tex_chk)

        # Texture folder row
        self._imp_tex_row = QtWidgets.QWidget()
        tex_row_hbox = QtWidgets.QHBoxLayout(self._imp_tex_row)
        tex_row_hbox.setContentsMargins(0, 0, 0, 0)
        tex_row_hbox.setSpacing(4)
        self._imp_tex_fld = QtWidgets.QLineEdit()
        self._imp_tex_fld.setPlaceholderText("Texture output folder…")
        tex_browse_btn = QtWidgets.QPushButton("Browse…")
        tex_browse_btn.setFixedWidth(100)
        tex_browse_btn.clicked.connect(self._browse_tex_folder)
        tex_row_hbox.addWidget(self._imp_tex_fld, 1)
        tex_row_hbox.addWidget(tex_browse_btn)
        vbox.addWidget(self._imp_tex_row)

        self._imp_tex_chk.toggled.connect(self._imp_tex_row.setEnabled)

        vbox.addSpacing(4)

        self._imp_mat_chk = QtWidgets.QCheckBox("Create Material")
        self._imp_mat_chk.setChecked(True)
        vbox.addWidget(self._imp_mat_chk)

        # Shader / ColorSpace row
        self._imp_mat_row = QtWidgets.QWidget()
        mat_row_hbox = QtWidgets.QHBoxLayout(self._imp_mat_row)
        mat_row_hbox.setContentsMargins(0, 0, 0, 0)
        mat_row_hbox.setSpacing(8)

        shader_lbl = QtWidgets.QLabel("Shader:")
        shader_lbl.setStyleSheet("font-weight: bold;")
        mat_row_hbox.addWidget(shader_lbl)

        self._imp_shader_menu = QtWidgets.QComboBox()
        self._imp_shader_menu.addItems(["aiStandardSurface", "lambert"])
        self._imp_shader_menu.setFixedWidth(150)
        self._imp_shader_menu.setStyleSheet(
            "QComboBox { background: #3a3a3a; color: #dcdcdc; "
            "border: 1px solid #2b2b2b; border-radius: 2px; padding: 3px 6px; }"
            "QComboBox::drop-down { border: none; }"
            "QComboBox QAbstractItemView { background: #3a3a3a; color: #dcdcdc; "
            "selection-background-color: #E8820C; }"
        )
        mat_row_hbox.addWidget(self._imp_shader_menu)

        cs_lbl = QtWidgets.QLabel("Color Space:")
        cs_lbl.setStyleSheet("font-weight: bold;")
        mat_row_hbox.addWidget(cs_lbl)

        self._imp_aces_menu = QtWidgets.QComboBox()
        self._imp_aces_menu.addItems(["ACES 1.2", "Standard"])
        self._imp_aces_menu.setFixedWidth(110)
        self._imp_aces_menu.setStyleSheet(self._imp_shader_menu.styleSheet())
        mat_row_hbox.addWidget(self._imp_aces_menu)
        mat_row_hbox.addStretch()

        vbox.addWidget(self._imp_mat_row)
        self._imp_mat_chk.toggled.connect(self._imp_mat_row.setEnabled)

        vbox.addSpacing(4)

        self._imp_ref_chk = QtWidgets.QCheckBox(
            "Create 1m Reference Cube on ground"
        )
        self._imp_ref_chk.setChecked(False)
        vbox.addWidget(self._imp_ref_chk)

        # Divider
        d2 = QtWidgets.QFrame(); d2.setObjectName("divider")
        d2.setFrameShape(QtWidgets.QFrame.HLine); vbox.addWidget(d2)

        # Progress bar
        self._imp_prog = QtWidgets.QProgressBar()
        self._imp_prog.setMaximum(_IMP_STEPS)
        self._imp_prog.setValue(0)
        self._imp_prog.setFixedHeight(14)
        self._imp_prog.setVisible(False)
        self._imp_prog.setStyleSheet(
            "QProgressBar { background: #3a3a3a; border: 1px solid #2b2b2b; "
            "border-radius: 2px; } "
            "QProgressBar::chunk { background: #E8820C; border-radius: 2px; }"
        )
        vbox.addWidget(self._imp_prog)

        self._imp_prog_lbl = QtWidgets.QLabel("")
        self._imp_prog_lbl.setVisible(False)
        self._imp_prog_lbl.setStyleSheet("color: #b0b0b0; font-size: 11px;")
        vbox.addWidget(self._imp_prog_lbl)

        # Status bar
        self._import_status = QtWidgets.QLabel(
            "\u2014  Select a GLB file to begin."
        )
        self._import_status.setObjectName("statusIdle")
        self._import_status.setWordWrap(True)
        vbox.addWidget(self._import_status)

        vbox.addSpacing(4)

        # Import button
        import_btn = QtWidgets.QPushButton("Import")
        import_btn.setObjectName("btnPrimary")
        import_btn.clicked.connect(self._do_import)
        vbox.addWidget(import_btn)

        vbox.addStretch()
        scroll.setWidget(inner)
        return scroll

    # ── EXPORT TAB ────────────────────────────────────────────────────────────

    def _build_export_tab(self, QtWidgets, QtCore):
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        inner = QtWidgets.QWidget()
        vbox  = QtWidgets.QVBoxLayout(inner)
        vbox.setContentsMargins(14, 12, 14, 14)
        vbox.setSpacing(6)

        # Output path ─────────────────────────────────────────────────────────
        lbl = QtWidgets.QLabel("OUTPUT:")
        lbl.setStyleSheet("font-weight: bold; color: #dcdcdc;")
        vbox.addWidget(lbl)

        exp_lbl2 = QtWidgets.QLabel("Export File:")
        vbox.addWidget(exp_lbl2)

        out_row = QtWidgets.QHBoxLayout()
        self._exp_path_fld = QtWidgets.QLineEdit()
        self._exp_path_fld.setPlaceholderText("output.glb path…")
        out_browse_btn = QtWidgets.QPushButton("Browse…")
        out_browse_btn.setFixedWidth(100)
        out_browse_btn.clicked.connect(self._browse_glb_save)
        out_row.addWidget(self._exp_path_fld, 1)
        out_row.addWidget(out_browse_btn)
        vbox.addLayout(out_row)

        # Divider
        d = QtWidgets.QFrame(); d.setObjectName("divider")
        d.setFrameShape(QtWidgets.QFrame.HLine); vbox.addWidget(d)

        # Options ─────────────────────────────────────────────────────────────
        lbl3 = QtWidgets.QLabel("OPTIONS:")
        lbl3.setStyleSheet("font-weight: bold; color: #dcdcdc;")
        vbox.addWidget(lbl3)

        self._exp_norm_chk = QtWidgets.QCheckBox("Export Normals")
        self._exp_norm_chk.setChecked(True)
        vbox.addWidget(self._exp_norm_chk)

        self._exp_uv_chk = QtWidgets.QCheckBox("Export UVs")
        self._exp_uv_chk.setChecked(True)
        vbox.addWidget(self._exp_uv_chk)

        self._exp_tex_chk = QtWidgets.QCheckBox(
            "Embed Texture Files  (DIFF / MTL / RGH / NRM — base colour always exported)"
        )
        self._exp_tex_chk.setChecked(True)
        vbox.addWidget(self._exp_tex_chk)

        self._exp_cam_chk = QtWidgets.QCheckBox(
            "Export Cameras (perspective, no animation)"
        )
        self._exp_cam_chk.setChecked(True)
        vbox.addWidget(self._exp_cam_chk)

        self._exp_orm_chk = QtWidgets.QCheckBox(
            "Pack ORM Channels  (requires Pillow)"
        )
        self._exp_orm_chk.setChecked(False)
        vbox.addWidget(self._exp_orm_chk)

        # Divider
        d2 = QtWidgets.QFrame(); d2.setObjectName("divider")
        d2.setFrameShape(QtWidgets.QFrame.HLine); vbox.addWidget(d2)

        # Progress
        self._exp_prog = QtWidgets.QProgressBar()
        self._exp_prog.setMaximum(_EXP_STEPS)
        self._exp_prog.setValue(0)
        self._exp_prog.setFixedHeight(14)
        self._exp_prog.setVisible(False)
        self._exp_prog.setStyleSheet(
            "QProgressBar { background: #3a3a3a; border: 1px solid #2b2b2b; "
            "border-radius: 2px; } "
            "QProgressBar::chunk { background: #E8820C; border-radius: 2px; }"
        )
        vbox.addWidget(self._exp_prog)

        self._exp_prog_lbl = QtWidgets.QLabel("")
        self._exp_prog_lbl.setVisible(False)
        self._exp_prog_lbl.setStyleSheet("color: #b0b0b0; font-size: 11px;")
        vbox.addWidget(self._exp_prog_lbl)

        # Status
        self._export_status = QtWidgets.QLabel(
            "\u2014  Select objects and set output path."
        )
        self._export_status.setObjectName("statusIdle")
        self._export_status.setWordWrap(True)
        vbox.addWidget(self._export_status)

        vbox.addSpacing(4)

        # Export button
        export_btn = QtWidgets.QPushButton("Export GLB")
        export_btn.setObjectName("btnPrimary")
        export_btn.clicked.connect(self._do_export)
        vbox.addWidget(export_btn)

        vbox.addStretch()
        scroll.setWidget(inner)
        return scroll

    # ── SCENE TAB ────────────────────────────────────────────────────────────

    def _build_scene_tab(self, QtWidgets, QtCore):
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        inner = QtWidgets.QWidget()
        vbox  = QtWidgets.QVBoxLayout(inner)
        vbox.setContentsMargins(14, 12, 14, 14)
        vbox.setSpacing(6)

        lbl = QtWidgets.QLabel("SCENE OBJECTS:")
        lbl.setStyleSheet("font-weight: bold; color: #dcdcdc;")
        vbox.addWidget(lbl)

        self._hier_list = QtWidgets.QListWidget()
        self._hier_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self._hier_list.setFixedHeight(200)
        self._hier_list.setFont(
            __import__('PySide6').QtGui.QFont("Courier New", 10)
        )
        vbox.addWidget(self._hier_list)

        # Hierarchy action buttons — row 1
        row1 = QtWidgets.QHBoxLayout()
        row1.setSpacing(4)
        for label, slot in [
            ("Refresh",     self._refresh_hierarchy),
            ("Select All",  self._select_all_hier),
            ("Select None", self._select_none_hier),
            ("Invert Sel",  self._invert_hier_selection),
        ]:
            btn = QtWidgets.QPushButton(label)
            btn.clicked.connect(slot)
            row1.addWidget(btn)
        vbox.addLayout(row1)

        # Hierarchy action buttons — row 2
        row2 = QtWidgets.QHBoxLayout()
        row2.setSpacing(4)
        for label, slot in [
            ("Select in Maya", self._select_in_maya),
            ("Hide",           lambda: self._set_visibility_from_hier(False)),
            ("Show",           lambda: self._set_visibility_from_hier(True)),
        ]:
            btn = QtWidgets.QPushButton(label)
            btn.setObjectName("btnAction")
            btn.clicked.connect(slot)
            row2.addWidget(btn)
        vbox.addLayout(row2)

        # Note about hierarchy
        note = QtWidgets.QLabel(
            "Tip: Select objects here, then switch to the EXPORT tab to export them."
        )
        note.setStyleSheet("color: #888888; font-size: 11px;")
        note.setWordWrap(True)
        vbox.addWidget(note)

        vbox.addStretch()
        scroll.setWidget(inner)
        return scroll

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
        if not self._imp_name_fld.text().strip():
            auto = (os.path.splitext(os.path.basename(path))[0]
                    .replace("-", "_").replace(" ", "_").replace(".", "_"))
            self._imp_name_fld.setText(auto)

    def _browse_tex_folder(self):
        res = cmds.fileDialog2(fileMode=3, caption="Select Folder")
        if res:
            self._imp_tex_fld.setText(res[0])

    def _do_import(self):
        from PySide6 import QtWidgets as QW
        path = self._imp_path_fld.text().strip()
        if not path:
            self._set_import_status("\u2715  No file selected.", "err")
            return
        if not os.path.isfile(path):
            self._set_import_status(
                "\u2715  File not found: {}".format(path), "err"
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
        self._set_import_status("\u2014  Importing…", "idle")

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
                "\u2713  " + "   ".join(parts), "ok"
            )

            self._imp_prog.setVisible(False)
            self._imp_prog_lbl.setVisible(False)
            # Refresh scene hierarchy
            self._refresh_hierarchy()

        except Exception as exc:
            _log.exception("Import failed: %s", exc)
            self._imp_prog.setVisible(False)
            self._imp_prog_lbl.setVisible(False)
            self._set_import_status(
                "\u2715  ERROR: {}".format(exc), "err"
            )
            cmds.warning("PXLmentor GLB Manager: Import failed — {}".format(exc))

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

    def _do_export(self):
        from PySide6 import QtWidgets as QW

        sel_items = [
            self._hier_list.item(i).text()
            for i in range(self._hier_list.count())
            if self._hier_list.item(i).isSelected()
        ]
        if not sel_items:
            self._set_export_status(
                "\u2715  Select at least one object in the Scene tab.", "err"
            )
            return

        out_path = self._exp_path_fld.text().strip()
        if not out_path:
            self._set_export_status(
                "\u2715  No output file path specified.", "err"
            )
            return
        if not out_path.lower().endswith('.glb'):
            out_path += '.glb'

        # Resolve DAG paths from display strings
        node_names = []
        for item in sel_items:
            dag = _HIER_MAP.get(item, "")
            if dag and cmds.objExists(dag):
                node_names.append(dag)
        if not node_names:
            self._set_export_status(
                "\u2715  Selected objects no longer exist — Refresh the Scene tab.", "err"
            )
            return

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
        self._set_export_status("\u2014  Exporting…", "idle")

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
                "\u2713  Exported {} item(s) \u2192 {} ({:.1f} KB)".format(
                    n, os.path.basename(out_path), size_kb
                ), "ok"
            )

            self._exp_prog.setVisible(False)
            self._exp_prog_lbl.setVisible(False)

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
                self._set_export_status("\u2715  " + friendly, "err")
                cmds.warning("PXLmentor GLB Manager: " + friendly)
            else:
                _log.exception("Export failed: %s", exc)
                self._set_export_status("\u2715  ERROR: {}".format(exc), "err")
                cmds.warning(
                    "PXLmentor GLB Manager: Export failed — {}".format(exc)
                )
        except Exception as exc:
            _log.exception("Export failed: %s", exc)
            self._exp_prog.setVisible(False)
            self._exp_prog_lbl.setVisible(False)
            self._set_export_status("\u2715  ERROR: {}".format(exc), "err")
            cmds.warning(
                "PXLmentor GLB Manager: Export failed — {}".format(exc)
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
                "PXLmentor GLB Manager — Duplicate names detected: [{}]. "
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

def show():
    GLBManager()

show()
