# Maya Toolbox — VFX Tools
# Sub-context for J:\ClaudeCode\projects\PXLtools\maya\
# Parent project context: J:\ClaudeCode\projects\PXLtools\CLAUDE.md (identity, versioning, engineering standards)

---

## 04 · Maya Toolbox

**DCC:** Autodesk Maya 2025 | Python 3 | PySide6 | Arnold | ACES 1.2

| Tool                        | Status | Notes                              |
|-----------------------------|--------|------------------------------------|
| Advanced Batch Renamer      | STABLE |                                    |
| OBJ Batch Exporter          | STABLE |                                    |
| Arnold PBR Material Creator | STABLE | v1.0.5 — STANDARD v1.1.0 compliance (no-right-spacer header), auto-detect identifiers, TurnTable UI parity |
| Legacy Render Layer Manager | STABLE |                                    |
| GLB Manager                 | ALPHA  | v0.1.7-alpha CP008 — STANDARD v1.1.0 compliance, import + export unified  |
| Claude for Maya (mAIa)      | STABLE |                                    |
| Animatic Builder            | STABLE |                                    |
| TurnTable Builder           | BETA   | v1.0.40-beta CP074 — STANDARD v1.1.0 compliance (no-right-spacer header) |
| Camera Matchmaker           | ALPHA  | v0.1.0-alpha CP001 — fSpy-inspired interactive VP camera solve |
| MU Bridge                   | ALPHA  | v0.1.2-alpha CP003 — Maya → Unreal shader-preserving export (FBX + .pxlbridge.json sidecar) — first tool built against PXLMENTOR_TOOL_STANDARD (v1.1.0, no-right-spacer header) |

### Maya Deployment Paths
| Content | Location |
|---------|----------|
| Scripts | `C:\Users\Evil Knight\Documents\maya\2025\scripts\` |
| Icons   | `C:\Users\Evil Knight\Documents\maya\2025\prefs\icons\` |

> **Deployment rule:** After a Maya tool is approved, copy the script to the `scripts\` folder above. Icons are placed in `prefs\icons\` by the user. The icon path in code (`cmds.internalVar(userPrefDir=True) + "icons/"`) resolves to this location automatically — never hardcode it.

### Maya Key Technical Rules
- `resizeToFitChildren` is **unreliable** — NEVER use for dynamic panels
- Use explicit `base_height + instructions_height` for all collapsible sections
- ACES colorspace: **dynamically read from environment**, never hardcode
- Arnold materials: support Substance Painter naming conventions and UDIM workflows
- Shared `place2dTexture` option for unified UV control

### GLB Manager — Alpha Known Issues (v0.1.0-alpha)
- Export ORM packing requires Pillow (optional — checkbox disabled by default)
- Camera export: perspective only, no animation, no orthographic cameras
- Multi-material GLB import uses first material only (v0.9.1 behaviour preserved)
- Scene hierarchy panel: refresh required after scene changes

---

## Maya — Known Bugs

| Issue                    | Resolution                                               |
|--------------------------|----------------------------------------------------------|
| `resizeToFitChildren`    | Unreliable — use explicit height calculations instead    |
| Logo stretching on resize| Known Maya UI limitation — accepted, not fought          |
| ACES colorspace list     | Read dynamically from environment — never hardcode       |
| `borderStyle='etchedIn'` | Obsolete in Maya 2025 — NEVER use on `frameLayout`       |
| `if __name__ == "__main__"` | Scripts imported in Maya never have `__name__ == "__main__"` — always call `run()` at module level |

---

## Maya — Environment

| Component | Details |
|-----------|---------|
| Maya      | Autodesk Maya 2025 — Python 3, PySide6 |
| Rendering | Arnold + ACES 1.2 (official Academy OCIO config) |
| Maya Prefs | Maya user preferences directory (`cmds.internalVar(userPrefDir=True)`) |

> Cross-DCC UI/UX engineering patterns (status feedback, signal blocking, path normalization, re-scan buttons) apply here — see `PXLtools/CLAUDE.md § 08b`.

---

## Maya Tool Catalog

### Advanced Batch Renamer
- **File:** `maya/scripts/PXLmentor_Advanced_Batch_Renamer_v1_0_4.py`
- **Status:** STABLE (v1.0.4)
- **Description:** Comprehensive renaming utility — search/replace with namespace support, prefix/suffix/base name rename, sequential numbering with custom padding, automatic invalid character handling.

### OBJ Batch Exporter
- **File:** `maya/scripts/PXLmentor_OBJ_Batch_Exporter_v1_0_2.py`
- **Status:** STABLE (v1.0.2)
- **Description:** Batch export all children of a selected group to individual OBJ files. Configurable export options (groups, ptgroups, materials, smoothing, normals), progress bar with ETA.

### Arnold PBR Material Creator
- **File:** `maya/scripts/PXLmentor_Arnold_PBR_Material_Creator_v1_0_5.py`
- **Status:** STABLE (v1.0.4)
- **Description:** Create Arnold aiStandardSurface PBR materials from Substance Painter texture sets. Supports UDIM, ACES 1.2, auto-detected texture identifiers (BaseColor/Diff/Diffuse/Albedo, Roughness/Rough/Rgh, Metalness/Metallic/Met/Mtl, Normal/Norm/Nrm — case-insensitive), shared place2dTexture, and bump-from-diffuse fallback. Full PySide6 QDialog UI with auto-resize on section collapse, TurnTable-parity QSS.

### Legacy Render Layer Creator
- **File:** `maya/scripts/PXLmentor_Legacy_Render_Layer_Creator_v1_2_2.py`
- **Status:** STABLE (v1.2.2)
- **Description:** Create legacy Maya render layers with per-object, per-light separation. Full naming options (prefix, suffix, object/camera/light compositing). Camera renderability overrides per layer.

### GLB Manager
- **File:** `maya/scripts/PXLmentor_GLB_Manager_v0_1_7_alpha.py`
- **Status:** ALPHA (v0.1.3-alpha) — CP004
- **Description:** Unified GLB import/export manager. Tab-based UI (IMPORT | EXPORT).
  IMPORT: Parses GLB/GLTF binary, builds mesh via OpenMaya2, splits ORM textures (Pillow), creates Arnold PBR materials with ACES pipeline, places on ground, optional 1m ref cube.
  EXPORT: Exports selected Maya meshes (world-space triangulated, normals, UVs) and perspective cameras to binary GLB. Traverses Arnold/lambert shading networks to embed textures; optional ORM channel packing (Pillow). Writes valid glTF 2.0 binary (JSON + BIN chunks).
  SCENE PANEL: Indented DAG hierarchy browser — refresh, select/hide/show in Maya, multi-select for export. Groups auto-expanded to mesh/camera descendants on export.
- **Previous:** `maya/scripts/_OLD/PXLmentor_GLB_Importer_v0_9_1_beta.py`

### Claude for Maya (mAIa)
- **File:** `maya/scripts/PXLmentor_AI_Assistant_v1_4_1.py`
- **Status:** STABLE (v1.4.1)
- **Description:** Claude AI assistant embedded in Maya. Text + image input (up to 6 per message), live streaming responses, code review before execution, session logs (last 5 sessions, rotating), Log Viewer for past sessions.
- **Config:** `~/Documents/maya/claude_for_maya/config.json` (API key)
- **Usage:** Paste full script into Maya Script Editor (Python), Ctrl+Enter

### Animatic Builder
- **File:** `maya/scripts/PXLmentor_Animatic_Builder_v1_6_5.py`
- **Status:** STABLE (v1.6.5)
- **Description:** Create animatics from JSON/CSV shot list files. Generates cameras, timing, Camera Sequencer integration, object placeholders, orbital camera animation, organized groups for export.

### Camera Matchmaker
- **File:** `maya/scripts/PXLmentor_Camera_Matchmaker_v0_1_0_alpha.py`
- **Status:** ALPHA (v0.1.0-alpha) — CP001
- **Description:** fSpy-inspired interactive camera matching for Maya. Load a reference photo into
  a QGraphicsView canvas. Draw VP1 (red) lines for horizontal parallels and VP2 (blue) lines for
  depth parallels. Vanishing points and focal length are solved live from pairwise line intersections.
  Outputs: horizontal FOV, camera rotation (pan/tilt/roll as Maya XYZ Euler), image plane on the
  camera, and simplified position estimate from user-supplied camera height above ground.
  Supports 2-point perspective. Canvas: scroll-wheel zoom, middle-mouse pan, F to fit.

### MU Bridge
- **File:** `maya/scripts/PXLmentor_MU_Bridge_v0_1_1_alpha.py`
- **Logic:** `maya/scripts/pxl_mu_bridge/` (package — 6 modules)
- **Shared schema:** `J:\ClaudeCode\projects\PXLtools\shared\pxl_mu_bridge_schema\`
- **Status:** ALPHA (v0.1.2-alpha) — CP003 — first tool built against `PXLMENTOR_TOOL_STANDARD.md` v1.1.0 (no-right-spacer header)
- **Description:** Maya 2025 → Unreal Engine 5.6 shader-preserving asset bridge.
  Walks selected aiStandardSurface networks and exports an FBX plus a
  `.pxlbridge.json` sidecar manifest. Texture color spaces are tagged for the
  ACEScg pipeline (sRGB / Linear / ACEScg / Raw); normal maps flagged for UE
  DirectX Y-flip on import. Intermediate nodes (aiNormalMap, bump2d,
  aiColorCorrect) are walked through with warnings logged in the export report.
  UDIM tokens normalised to `<UDIM>` for path portability. Unmapped Arnold
  attributes (subsurface, coat, transmission, sheen, thinWalled) are listed
  in the report rather than silently dropped.
- **Direction (V0.1):** Maya → Unreal only. Reverse direction and utility-node
  translation (aiColorCorrect, aiMultiply, hsvToRgb → HueSaturation, Multiply,
  custom MaterialFunctions) deferred to V0.2+.
- **Unreal side:** to be built under `J:\ClaudeCode\projects\PXLtools\unreal\python\`
  after the master Material `M_PXL_PBR_Master.uasset` is authored manually in
  UE 5.6 and committed to `J:\ClaudeCode\projects\PXLtools\unreal\content\PXLbridge\`.

### TurnTable Builder
- **File:** `maya/scripts/PXLmentor_TurnTable_Builder_v1_0_40_beta.py`
- **Status:** BETA (v0.9.1-beta) — CP035
- **Description:** Automates turntable scene setup. References the PXLmentor turntable .ma scene, attaches model under `_TO_RENDER_grp`, auto-centers and grounds. 8-slot HDRI grid (6 preset + 2 custom) drives `aiSwitchHDRI`; custom HDRIs set colorspace to `Utility - Linear - sRGB`. Auto-switches viewport to `main_CAM` on load; enables resolution gate and gate mask on the camera. Frame range retiming uses `cutKey`/`setKeyframe` on `asset_ROT` and `lights_ROT` directly (reliable reference-file compatibility). Clear Scene removes reference, rescues model from fosterParent nodes, re-parents to world. EXR thumbnails via OpenCV Drago tonemapper + p2/p98 percentile stretch. Session persistence on reopen. OpenCV in-process install with Maya.env EXR flag.
- **Config:** `~/Documents/maya/PXLmentor/turntable_builder_config.json` (root folder, frame_start, frame_end)
- **Scene:** `{root}/scenes/PXLmentor_TB3DTT_ACES_2025_v001.ma`
- **HDRI previews:** `{root}/sourceimages/HDRIs/preview/`
