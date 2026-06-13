"""
Tool Name   : PXLtools TurnTable Builder
Version     : 1.0.26
Stage       : Release
Checkpoint  : CP112
Author      : PXLsuite / BlackMamba3D
Description : Load the PXL turntable scene as a Maya reference, attach a
              selected model or use the built-in shader ball, and auto-center for
              rendering. Two-tab interface: PREP (material testing) and TURNTABLE
              (render layer pipeline — legacy render layers, Nuke-ready, master layer
              disabled on creation, layers named RL_hdri_XX / RL_charts_XX by HDRI slot,
              Arnold mergeAOVs enabled on layer creation). Full PySide6 UI — zero external
              installs — Maya 2025.

Changelog:
    1.0.26      - CP112: Camera switch + frame FIXED (root-caused via research,
                 sourced to Autodesk docs + maya-capture). TWO real bugs: (1) the
                 panel was getPanel("modelPanel")[0] = CREATION order, so it switched
                 a HIDDEN panel while the user stayed on top; now resolves the VISIBLE
                 panel + modelEditor(activeView=True). (2) viewFit's first positional
                 arg is a CAMERA, not a panel — old code passed the panel and silently
                 mis-fit; now passes the camera. New _resolve_visible_model_panel();
                 scene-load switch fixed the same way. lookThru + viewFit(cam, 0.8).
    1.0.25      - CP111: Attach->main_CAM frame: switched from lookThru/
                 playblast (which silently did nothing) to the PROVEN
                 cmds.modelEditor(panel, edit=True, camera=cam) used by scene-load,
                 run synchronously, with a visible inViewMessage on success and a
                 cmds.warning on every skip/failure so it is obvious if it ran.
    1.0.24      - CP110: Fixes from in-DCC testing:
                 - Attach -> main_CAM framing FINALLY works: removed the
                   _is_turntable_loaded() gate (it matched TT_SCENE_FILENAME, which
                   the PXLtools rebrand changed, so it silently returned and skipped
                   the whole routine). Now gated only on main_CAM + targets; uses the
                   ACTIVE model editor (playblast activeEditor) + lookThru; viewFit
                   runs DEFERRED so the new rig/bbox is valid (~10% margins, fit 0.8).
                 - HDRI card no longer cramped: cells 118x116 -> 124x128, preview
                   84 -> 96; grid spacing 8/10; grid widget keeps full height.
                 - Default HDRI = Studio: detected by name on build, orange-selected
                   by default, and applied to the scene on load (the starting HDRI).
    1.0.23      - CP109: Lighting (03) layout refinements:
                 - Visibility + Size References moved INTO the collapsible, which is
                   renamed UTILITIES/"REF BALL & CHARTS" -> "CUSTOM SETTINGS" (one
                   place for all fine-tuning: visibility, size refs, ref ball, charts).
                 - HDRI section reflow: short description ("Click the HDRI you want
                   to use") at top; image grid stays first; rotation moved BELOW the
                   images under a "HDRI STARTING POSITION" header + note ("rotate to
                   set the starting position / main light direction"); a divider then
                   separates it from the Backdrop | Arnold Render card (was cramped).
                 - Attach framing (from v1.0.22): main_CAM lookThru + bbox viewFit
                   ~10% breathing room retained.
                 File renamed v1_0_22 -> v1_0_23.
    1.0.22      - CP108: In-DCC polish batch (TurnTable_FIXLIST items 1-5):
                 (1) Instructions auto-collapse + Scene Setup opens when the root is
                 already set, so a configured user lands straight on Scene Setup;
                 (2) clearer Model empty-state copy ("No model captured — select the
                 model you want to capture"); (3) Attach now switches the active
                 viewport to main_CAM (lookThru) and frames the asset bbox with ~10%
                 breathing room (fit 0.75 -> 0.8); (4) "save your scene first"
                 reminder above Render Turntable (render names derive from the scene
                 file name, with example); (5) Lighting (03) reordered — HDRI first
                 (with a Backdrop | Arnold "decide & render" card), then Display
                 (Visibility | Size Refs), then "REF BALL & CHARTS" (was UTILITIES).
                 File renamed v1_0_21 -> v1_0_22 per the PXLtools naming convention.
                 FIX: the window singleton check was version-blind — an open window
                 (same objectName across versions) made a relaunch just re-raise the
                 stale window, so the shelf "Update" never swapped in new code. Now
                 version-aware: same version raises, a different/older build is closed
                 and rebuilt. Window tagged via setProperty("pxlTTVersion", VERSION).
    1.0.21      - CP107: Rebrand/rename — file is now PXLtools_TurnTable_Builder_v1_0_21.py
                 (PXLtools prefix + real version in filename, under the PXLsuite
                 umbrella); config + OpenCV cache paths moved maya/PXLmentor ->
                 maya/PXLtools; header tool-name -> "PXLtools TurnTable Builder".
                 (drawItemText flat-paint + min-width floor from earlier this version.)
    1.0.21      - CP106: Drop-shadow on text killed for good: _FlatTextStyle now
                 reimplements drawItemText() to paint flat text (no host-style
                 shadow/etch on any font); min-width:84 floor added so no button
                 renders narrower than its siblings.
    1.0.20      - CP105: Expandable-section triangle is now a same-size chevron
                 ICON (identical closed/open, no glyph size jump, matches Nuke);
                 etched disabled-text emboss ('drop shadow') removed via
                 _FlatTextStyle proxy.
    1.0.19      - CP104: Cross-tool consistency: expandable-section triangle now
                 the full glyph at one size (▼/▶ 11px, same closed/open, matches
                 Nuke); Scene Setup section uses the same import icon as the Nuke
                 Import Template; combo down-arrow pinned right (no centre arrow).
    1.0.18      - CP103: Combo dropdown double-arrow fixed — drop-down was a
                 floating 'center right' box leaving the native arrow visible;
                 now a full-height 'top right' button (single arrow) + combo
                 right-padding so text never runs under it.
    1.0.17      - CP102: Slider bar now lightens on hover (Qt only repaints the
                 handle on hover, not the bar -> force a full repaint via a
                 'hov' property toggle keyed in the theme). Slider given a fixed
                 height so the orange handle ring is no longer cropped by the row.
    1.0.16      - CP101: Slider hover, done right. Handle is now a real PNG so it
                 stays a perfect CIRCLE: same white dot normally, white dot with
                 an ORANGE RING on hover (no shape/size change). Both halves of
                 the bar brighten on hover (orange #E8820C->#FFA838, track
                 #0a0a0a->#2c2c2c) so it reads as draggable.
    1.0.15      - CP100: SETUP spin-boxes (slider editable fields) now reuse the
                 themed up/down buttons+arrows+hover (dropped the inline
                 override) so they match RENDER exactly. Slider handle: the
                 orange border rendered as a SQUARE in PySide — replaced with a
                 round handle that turns orange and grows on hover; bar lightens.
                 HDRI cells: taller (Replace no longer cropped), preview corners
                 ROUNDED (card + masked pixmap), and the Replace button is now
                 the themed button (same font/size/hover as the others).
    1.0.14      - CP099: Universal hover feedback (REUSE the themed styles).
                 RENDER tab spin-boxes + resolution combo now use the themed
                 style (dropped bespoke inline) so the up/down + dropdown
                 BUTTON area lightens (#404040->#5a5a5a) and the arrow goes
                 white on hover. Sliders: handle gains an orange ring (slightly
                 larger) and the bar lightens on hover. Collapsible section
                 headers (Lighting/Model/Utilities/etc.) lighten on hover.
                 Shared theme -> Nuke inherits it.
    1.0.13      - CP098: Tabs renamed to just "1 · SETUP" and "2 · RENDER".
                 RENDER tab: HDRI slot checkboxes now use the themed size/font
                 (match the Lighting checkboxes) and sit in TWO columns (Slot
                 1-4 | 5-8) to save height; Include Charts themed too; dark
                 separators kept. Instructions rewritten — current names, more
                 descriptive (what/how to select), Your Model default noted, and
                 a "File ▸ Set Project" reminder so exports land in the shot folder.
    1.0.12      - CP097: FIX regression — spin/combo arrows rendered as squares
                 in Maya (PySide6 does not draw CSS border-triangles). Reverted
                 to real PNG chevrons; hover now swaps grey->white chevron PNG.
                 Folder tabs retained.
    1.0.11      - CP096: Hover feedback on ALL number/combo arrows — switched the
                 spin-box + combo arrows from fixed PNG chevrons to border-
                 triangles that lighten to white on mouse-over (matches the
                 buttons; same arrows now in Nuke). Tabs restyled as two raised
                 FOLDER tabs (rounded top corners, selected tab raised + orange
                 top accent) so "Setup & Light" / "Render & Export" read as two
                 folders. Shared theme change — Nuke inherits the arrow look.
    1.0.10      - CP095: New tool icon — "Orbit" (iso asset cube inside a 270°
                 open orange rotation ring, arrowhead, dark app tile). Replaces
                 the old icon. SVG master + 256px PNG deployed to Maya prefs,
                 project icons, and the Nuke toolbox (shared face for both tools).
    1.0.9       - CP094: Denoiser note "requires NVIDIA GPU" moved onto the same
                 line as the checkbox (smaller, muted) — no longer two lines.
    1.0.8       - CP093: Lighting > ARNOLD RENDER now has a "Denoiser (OptiX)"
                 checkbox (off by default) that toggles the scene's
                 aiImagerDenoiserOptix imager, with a "Requires an NVIDIA GPU."
                 note. Denoiser is forced off on scene load to match.
    1.0.7       - CP092: Render Turntable "By Frame" now defaults to 10 (render
                 every 10th frame) instead of 1.
    1.0.6       - CP091: Clear Scene now has an "Also remove the TT render
                 layers (full clean)" checkbox, ON by default. When checked,
                 clearing the scene also deletes RL_hdri_* / RL_charts_* so
                 nothing is left behind; render Step 2 button re-locks.
    1.0.5       - CP090: UI clarity pass. (1) Tabs renamed/numbered for a clear
                 1->2 flow: "1 · SETUP & LIGHT" and "2 · RENDER & EXPORT" (was
                 PREP / TURNTABLE). (2) RENDER LAYERS SETUP is now a collapsible
                 section; after Create Render Layers it auto-collapses and the
                 RENDER TURNTABLE section opens below. (3) Restored the spin-box
                 up/down arrows and combo drop-down arrow globally (themed chevron
                 PNGs via new chevron-up.svg + __SPINUP__/__SPINDOWN__ QSS hooks).
                 (4) Utilities "Scale" sub-label bumped from an 8px/#4a4a4a near-
                 invisible line to the standard themed hint size.
    1.0.4       - CP089: Shader ball geometry now follows the mode — HIDDEN on
                 scene load (Your Model is default) and shown only when the user
                 switches to Shader Ball mode (visibility + checkboxes track the
                 mode symmetrically). Plus: on Attach, main_CAM auto-frames the
                 asset's bounding box (centred, fitFactor 0.75 for breathing room
                 top/bottom) via new _frame_main_cam_to_asset() — no manual
                 camera work.
    1.0.3       - CP088: Model 02 default is now YOUR MODEL — it is the left
                 toggle button and the active mode on open (Shader Ball moved to
                 the right, shown only when chosen). Clearer default path for new
                 users; no need to look at Shader Ball.
    1.0.2       - CP087: Guided-flow language extended across the WHOLE tool —
                 idiot-proof, numbered, labelled. Every confirmable action is now
                 a numbered step that turns ORANGE (do this now) -> PALE GREEN +
                 right-side "✓ done" when complete; the parent CollapsibleSection
                 also shows an active/done state (accent bar + header ✓).
                 Applied to: Preliminary Steps (1 Set Root Folder via Browse->Set,
                 2 ACES auto-check, 3 OpenCV auto-check), Scene Setup 01 (1 Load
                 Scene -> 2 Apply Frame Range), Model 02 (unchanged 1-2-3, left
                 badge keeps the NUMBER — duplicate left tick removed, only the
                 right "done" badge remains), and the TURNTABLE tab (1 Create
                 Render Layers -> 2 Render Turntable). New CollapsibleSection
                 .set_state() + shared `_mk_step_header/_set_badge/_set_step_btn/
                 _set_confirm` helpers and per-area `_update_*` state machines,
                 all wired at the real success points (set-root / load / apply /
                 create / render) and reset on Clear Scene / Delete Layers.
                 Fixed the orange active-border getting cropped (step buttons use
                 min-height, not a too-short fixed height). Unified all info/hint
                 typography to the themed `#hint` (dropped the ad-hoc 8px/#1e1e1e
                 boxes). Instructions panel rewritten to match the numbered path.
    1.0.1       - CP086: Your Model step sequence now reads as a clear gated
                 1->2->3 progression. Plain numerals (1/2/3) replace the circled
                 glyphs; three high-contrast states via shared pxl_ui QSS —
                 LOCKED (muted grey, unclickable), ACTIVE (orange badge + orange-
                 border button), DONE (green badge + check, button goes dark via
                 new #btnStepDone). FIX: _update_step_ui() now restyles the
                 just-completed button (previously it never changed, so a done
                 step looked active). FIX: removed the inline setStyleSheet poison
                 in both reset paths (capture / clear scene) that overrode the
                 themed QSS and stopped the next step from lighting up — reset now
                 clears inline styles and lets objectName + repolish drive.
                 Render Layers Setup panel (TURNTABLE tab) switched from a dark
                 #2b2b2b outlier to the shared #3a3a3a "sectionFrame" so it matches
                 every PREP-tab section; inner separators/buttons/checkboxes
                 re-tuned for contrast on the lighter panel.
    1.0.0       - CP085: First public release (dropped alpha/beta). pxl_ui
                 force-reload so kit/icon changes apply on relaunch; Scene
                 Setup uses the clapperboard icon (shared with Nuke).
    1.2.5-beta  - CP084: Scrollable + resizable (height), collapsed sections
                 sit tight (section height capped + trailing stretch),
                 uniform header text/icon size, distinct Scene icon
                 (clapperboard), slider unfilled line now black.
    1.2.4-beta  - CP083: Slider track fully TRANSPARENT (orange fill line +
                 white circle only, nothing on the unfilled side). Header
                 logo+name centre in the space between the tool icon and the
                 right edge (right spacer removed).
    1.2.3-beta  - CP082: Slider = transparent track (thin orange/dark line)
                 + plain white circle handle. Header: PXLtools logo ~50%
                 larger and width-scaled so it centres cleanly with the
                 tool name directly beneath it. Window widened to 620.
    1.2.2-beta  - CP081: UI polish — borderless clean section headers
                 (no card/line artefacts), uniform 32px collapsed bars,
                 refined sliders (deeper groove, bordered white handle),
                 lighter Utilities labels, flat header/tab background.
    1.2.1-beta  - CP080: Full body restyle to the approved pxl_ui preview.
                 MAIN_QSS rebuilt on the theme palette (darker greys,
                 rounded panels/inputs, orange primary w/ dark text, tick
                 checkboxes, themed sliders/combos). Inline restyle methods
                 now drive QSS via objectName + repolish (no hard-coded
                 colours). compat with all existing wiring.
    1.2.0-beta  - CP079: New shared pxl_ui UI kit (Maya PySide6 / Nuke
                 PySide2). AppHeader logo header and colour-coded icon
                 section headers; same kit drives the Nuke comp tool.
    1.1.1-beta  - CP078: In-tool header logo swap. _build_header() now loads
                 PXLtools_logo.png (the PXLtools wordmark) into the 262x48
                 logo slot instead of PixelMentor_Logo_Long.png. Fallback
                 text label changed from "PXLsuite" to "PXLtools" to match.
                 The 96x96 tool icon (icon_turntable_builder.png) stays as is.
                 The tool name "TurnTable Builder" displayed under the logo
                 is unchanged.
    1.1.0-beta  - CP077: Rebrand pass — tool belongs to PXLtools (under PXLsuite,
                 BlackMamba3D umbrella), not PXLmentor. Renamed file to
                 PXL_TurnTable_Builder_v1_1_0_beta.py. Internal TOOL_NAME,
                 WINDOW_OBJECT_NAME, logger names, dialog warnings, UI logo
                 label, and header metadata swept from "PXLmentor TurnTable
                 Builder" to "PXL TurnTable Builder" / "PXLsuite". Internal
                 cache paths (~/Documents/maya/PXLmentor/, python_libs cache,
                 TT_SCENE_FILENAME on disk) preserved to keep existing user
                 state intact — only user-visible surfaces rebranded.
    1.0.42-beta - CP076: Scope the texture path remap to the turntable
                 reference only. v1.0.41 walked every file/aiImage node in
                 the entire Maya scene, which clobbered the user's own assets
                 whose textures legitimately live elsewhere on disk. Now
                 _remap_textures_to_root() filters by the active turntable
                 namespace (self._get_active_namespace() or self.TT_NAMESPACE)
                 — nodes outside that namespace are never touched. If no
                 turntable namespace is resolvable, the remap is a no-op.
    1.0.41-beta - CP075: Texture path remap on scene load. After
                 load_turntable_scene() references the turntable .ma, the new
                 helper _remap_textures_to_root() walks every `file` and
                 `aiImage` node, detects a structural anchor in the saved path
                 (sourceimages/HDRIs, sourceimages/shaders, etc.) and rewrites
                 the path so it sits under the user's currently-set
                 root_folder. Fixes "broken textures after fresh install" — the
                 scene's baked-in absolute paths are no longer trusted; the
                 user's root drives resolution. Anchor-based remap, not dirmap,
                 so no need to know the previous root. Idempotent and UDIM-safe.
    1.0.40-beta - CP074: Conform to PXLMENTOR_TOOL_STANDARD v1.1.0 - removed
                 the 96x96 right-spacer from _build_header so the PXLmentor
                 logo centers in the visible content area (right of the tool
                 icon) rather than on the dialog geometric midline. The previous
                 symmetric layout looked off-balance because the spacer carried
                 no visual weight.
    1.0.39-beta - Fix: removed Python per-layer loop from render_tt_layers(). renderSequence()
                 reads renderSequenceAllLayers=1 and renderSequenceAllCameras=1 optionVars
                 and iterates internally — our Python loop was compounding with Maya's
                 internal iteration causing an infinite render cycle. renderSequence() is
                 now called once; Maya handles all layer and camera iteration. Both optionVars
                 set at layer creation time.
    1.0.38-beta - Fix: removed defaultRenderGlobals.renderAll=1 from create_tt_render_layers().
                 Setting renderAll=1 caused renderSequence() to iterate over all
                 renderable cameras on every call in the Python layer loop, compounding
                 into an infinite render cycle. renderSequenceAllCameras optionVar alone
                 is sufficient — the per-layer camera renderable override handles
                 which camera fires.
    1.0.37-beta - Fix: "All Render-Enabled Cameras" is controlled by the optionVar
                 "renderSequenceAllCameras", NOT defaultRenderGlobals.renderAll.
                 cmds.optionVar(intValue=("renderSequenceAllCameras", 1)) now set at
                 layer creation time. defaultRenderGlobals.renderAll also kept for
                 completeness.
    1.0.36-beta - defaultRenderGlobals.renderAll=1 set once in create_tt_render_layers()
                 after all layers are built — not touched at render time. Removed
                 per-layer editRenderLayerAdjustment for renderAll (unnecessary) and
                 removed renderAll setAttr from render_tt_layers() entirely.
    1.0.35-beta - (superseded) Per-layer renderAll override via editRenderLayerAdjustment.
    1.0.32-beta - Resolution selector added to RENDER TURNTABLE section: HD 720
                 (1280x720), HD 1080 (1920x1080, default), 4K (3840x2160). Selection
                 sets defaultResolution.width/height/deviceAspectRatio before rendering.
    1.0.31-beta - "Maintain Offset" checkbox now defaults to unchecked (OFF). Objects
                 are centered to XZ origin on Attach by default.
    1.0.30-beta - create_tt_render_layers() now enables "Merge AOVs" in Arnold render
                 settings (defaultArnoldDriver.mergeAOVs = 1) so all AOV channels are
                 merged into a single multi-layer EXR per frame, ready for Nuke.
    1.0.29-beta - Render layer naming changed: RL_model_XX → RL_hdri_XX, where XX is
                 the HDRI switch node index + 1 (padded to 2 digits). So slot 0 →
                 RL_hdri_01, slot 2 → RL_hdri_03. RL_charts_XX follows the same
                 numbering. All RL_model_* references updated to RL_hdri_* in
                 _tt_layers_exist(), render_tt_layers(), and delete_tt_render_layers().
    1.0.28-beta - create_tt_render_layers() now disables the master layer
                 (defaultRenderLayer.renderable=0) and explicitly enables each
                 created RL_model_XX / RL_charts_XX layer (renderable=1) so that
                 only the TT render layers are active for the render sequence.
    1.0.27-beta - render_tt_layers() now sets defaultRenderGlobals.renderAll=1 before
                 calling renderSequence(). This activates "All Render-Enabled Cameras"
                 so each layer renders through its designated camera (set via per-layer
                 .renderable override) without needing an explicit camera argument.
    1.0.26-beta - File name prefix set on layer creation: <RenderLayer>/<Scene>_<RenderLayer>.
                 Animation format set: name.####.ext (putFrameBeforeExt, periodInExt, padding=4).
                 New "RENDER TURNTABLE" CollapsibleSection in TURNTABLE tab:
                   - Start/End frame spinboxes defaulting to tool frame range.
                   - "By Frame" spinbox (default 1 = every frame).
                   - "RENDER TURNTABLE" button — disabled until TT layers exist.
                     Iterates all RL_hdri_*/RL_charts_* layers, sets globals, calls
                     renderSequence() per layer via MEL.
                 Render button also enabled on session restore if TT layers exist.
    1.0.25-beta - Fix: correct default collapse behaviour for all sections.
                 First run: Instructions open, all sections (01/02/03) collapsed.
                 Session restore: Instructions collapsed, only Section 01 (Scene
                 Setup) open, sections 02 and 03 collapsed.
                 Added self._instructions_frame reference so restore can collapse
                 the outer Instructions panel.
                 load_turntable_scene() now calls _advance_to_section(1) to open
                 Section 01 on first load (since it is now collapsed by default).
    1.0.24-beta - RL_model_XX layers now include _TT_setup_grp/ENV_grp with a
                 visibility=1 override (ENV_grp is hidden by default in the scene).
                 _create_tt_layer() gains extra_vis_grp parameter for this purpose.
    1.0.23-beta - Fix: cmds.listRelatives flag corrected from allDescendants to ad=True
                 (Maya uses allDescendents/ad — invalid flag caused all render layers
                 to fail with "Invalid flag 'allDescendants'" error).
    1.0.22-beta - Feature: TURNTABLE tab fully implemented — legacy render layer pipeline.
                 Creates RL_model_XX layers (mainModel_grp + aiSkyDome_HDRI + main_CAM)
                 and optional RL_charts_XX layers (TT_setup charts_grp + chart_CAM).
                 Per-layer overrides: aiSwitchHDRI.index (HDRI slot), camera renderable,
                 charts_grp visibility (hidden by default, overridden to 1 per layer).
                 "Delete TT Render Layers" cleans up RL_hdri_* / RL_charts_* layers.
                 HDRI slot checkboxes sync their labels from the HDRI grid on rebuild.
    1.0.21-beta - Fix: re-added orientConstraint(asset_ROT, locator, maintainOffset=True,
                 skip=["x","z"]) in attach_to_turntable(). Each locator is Y-constrained
                 to asset_ROT so objects spin correctly on their own pivots.
                 Fix: Instructions/Preliminary section now auto-collapses when
                 _advance_to_section(3) is called (i.e. after first full setup or
                 on session restore).
    1.0.20-beta - Locators (and their child objects) now parented under mainModel_grp
                 instead of a separate TT_userRigs_grp. Rotation is inherited from
                 the asset_ROT → mainModel_grp hierarchy naturally — no orient
                 constraint required. Simplifies render layer setup.
    1.0.19-beta - Fix: locators now created at Capture time (not Attach time), placed at
                 the base-center (cx, ymin, cz) of each object's bounding box. Objects
                 are immediately parented under their locator at capture.
                 Fix: Align to Ground moves each locator to Y=0 — since objects are
                 already parented under their locators, they ground correctly with no
                 pivot or offset issues.
                 Simplify: Attach to Turntable now only adds the orientConstraint (Y
                 only) to existing locators — no object reparenting needed.
                 Re-capture: clicking Capture again cleans up old locators and resets
                 steps 2 and 3 to locked before starting fresh.
                 Feature: HDRI rotation slider (-180 to +180) added under HDRI
                 ENVIRONMENT, before the image grid. Controls aiSkyDomeLight rotateY.
                 Feature: Section 3 lighting reorganized — CHARTS PLACEMENT and HDRI
                 ENVIRONMENT wrapped in compact CollapsibleSection submenus to reduce
                 UI clutter. Default: both expanded.
    1.0.18-beta - Multi-object locator rig: each captured object/group gets a world-space
                 locator at its base center, orient-constrained (Y rotation only) to
                 asset_ROT. Objects spin on their own pivots in sync with the turntable.
                 Step workflow order changed: Capture → Align to Ground → Attach.
                 "Center to Ground" renamed "Align to Ground" (Y only, no XZ centering).
                 New "Maintain Offset" checkbox: ON = objects keep world positions;
                 OFF = objects centered to XZ origin before attaching.
                 clear_scene() tears down locator rigs cleanly.
                 _restore_session_state() detects new TT_userRigs_grp structure with
                 legacy mainModel_grp fallback for backward compatibility.
    1.0.17-beta - Preliminary Steps moved inside the Instructions tab.\n                 Instructions now defaults to expanded.\n    1.0.16-beta - Compact mode for Instructions and Preliminary Steps:\n                 CollapsibleSection gains compact=False param: 26px header,\n                 9px title, 11px arrow, tighter body margins/spacing.\n                 Preliminary content: smaller ctrlLabel fonts, halved\n                 spacings, reduced button heights.\n    1.0.15-beta - Fix: _sb_main_ck (Sec 2 Shader Ball checkbox) starts False and\n                 was never synced on scene load; only _lighting_shaderball_ck (Sec 3)\n                 was updated. Both checkboxes now synced on load and session restore.\n                 Fix: _sync_ui_from_scene aiSwitchMeasures mapping was inverted\n                 ("cm if idx==1" should be "mt if idx==1"). Default is now 1mt.\n    1.0.14-beta - Fix: Shaderball checkbox still unchecked — CollapsibleSection._body\n                 used setStyleSheet() which is the real cascade breaker (all sections\n                 affected). Fix: setObjectName("collapsibleBody") + MAIN_QSS rule.\n                 Button height uniformity: toggle buttons 26->28px, QSS enforced.\n                 HDRI cell: hover feedback via enterEvent/leaveEvent. Ring visible:\n                 CELL_W/H +4px, (2,2,2,2) layout margins, no fixed child widths.\n    1.0.13-beta - Fix: ShaderBall checkbox indicator broken — section frames used
                 setStyleSheet() which breaks Qt child-widget stylesheet cascade.
                 Replaced with setObjectName("sectionFrame") + MAIN_QSS rule. Added
                 hover/pressed states to checkboxes, toggle buttons, slider handle.
                 Arnold buttons use new btnAction (neutral off style). aiSwitchMeasures
                 .index=1 (1mt) set on scene load to match UI default.
    1.0.12-beta - Section 3 (Lighting) redesigned as 2x2 grid: Visibility (top-left),
                 Size References (top-right), Backdrop (bottom-left), Arnold (bottom-right).
                 Backdrop is now HDRI/LIMBO toggle pair. Floor Grid checkbox in Size
                 References controls aiSwitchBackdrop.index (0=white, 1=grid). Default:
                 LIMBO + Floor Grid ON = measurements mode. aiSwitchMeasures: 0=CM, 1=MT.
    1.0.11-beta - Backdrop/Floor redesign: "Measurements Floor" split into two controls.
                 "Floor" checkbox toggles _TT_setup_grp/ENV_grp vs utilities_grp/ENV_grp.
                 New indented "Measurements" sub-option controls aiSwitchBackdrop.index
                 (0=white limbo, 1=grid texture via aiSwitchMeasures). Size Ref Unit
                 buttons now also drive aiSwitchMeasures.index (0=1mt, 1=10cm). Removed
                 dead expression2 references from set_grid_unit / _sync_ui_from_scene.
    1.0.10-beta - Fix: Scale slider full-width regression. Added Expanding size
                 policy to Scale slider widget and _compact_col containers so
                 the VBoxLayout correctly stretches the Scale row to full width
                 alongside the two-column Ref Ball / Macbeth chart block.
    1.0.5-beta  - CP051: Macbeth Y and Ref Ball Y sliders added (position control on both axes).
                 - _sync_ui_from_scene() added — called after scene load and session restore.
                   Reads expression2.in[0] for grid unit (1=mt, 0=cm), reads macbeth_grp/
                   refBall_grp translateX/Y to sync sliders to actual scene state.
                   Eliminates mismatch between UI defaults and live scene values.
    1.0.4-beta  - CP050: toggle_size_ref_cubes fixed — enabling now enforces per-unit
                   cube visibility (cube_1mt_REF on, cube_10cm_REF off when 1mt active
                   and vice versa) instead of showing both cubes simultaneously.
                 - SliderRow redesigned: label is now a clickable QPushButton that resets
                   to default on click (turns orange on hover). Value readout replaced
                   with QDoubleSpinBox — unbounded range allows manual override beyond
                   the slider limits. Slider and spinbox stay in sync via _syncing flag.
    1.0.3-beta  - CP049: Custom HDRI loading fixed — wrapped browse_custom_hdri in
                   cmds.evalDeferred so cmds.fileDialog2 runs after Qt's mousePressEvent
                   finishes. Direct call from Qt's event loop caused the dialog to return
                   empty silently (Qt/MEL event loop conflict).
                 - HDRI cell size reduced: CELL_W 124→114, CELL_H 108→96, PREV_H 86→74.
                   Cells now fit the 550px window without overflow.
                 - Render button fixed: render_with_arnold now calls
                   renderWindowRender renderSequence renderView instead of
                   RenderIntoNewWindow — renders all frames through RenderView (play
                   behavior) rather than single-frame render.
    1.0.2-beta  - CP048: Interface resize definitively fixed — SetFixedSize constraint on root
                   layout replaces all manual resize machinery. Removes addStretch() from
                   prep_layout, removes stretch=1 from tab_widget, removes resize_callback
                   from CollapsibleSection. Qt now auto-resizes window when sections toggle.
                 - Lighting section redesigned: two-column layout (Visibility | Size Ref Unit
                   + Arnold Render). Floor Grid Unit renamed to Size Ref Unit. Button order
                   corrected: 10 cm before 1 mt. Arnold RenderView and Render buttons added.
    1.0.1-beta  - CP046: Interface resize finally fixed — root cause was Qt's chained
                   LayoutRequest events requiring processEvents(ExcludeUserInputEvents)
                   to flush the full propagation chain before measuring minimumSizeHint.
                   QTimer.singleShot(0) only skipped ONE tick; Qt needs N ticks (one
                   per hierarchy level) to propagate setVisible through the tree.
                 - CP045: Ref cubes hidden on load (sizeRef_grp visibility=False).
                 - Shader Ball checkbox default corrected to True (matches scene state).
                 - Added "Size Ref Cubes" checkbox to toggle sizeRef_grp visibility.
    1.0.0-beta  - CP044: Section collapse now shrinks window (QTimer.singleShot deferred adjustSize).
                 - Measurements Floor: toggles utilities_grp/ENV_grp ↔ _TT_setup_grp/ENV_grp via full path.
                 - Grid unit (mt/cm) also shows/hides matching sizeRef cube (cube_1mt_REF / cube_10cm_REF).
    0.9.9-beta  - CP043: Scene updated to v003 — removed old MainCAM, shaderBall cam → main_CAM.
                 - On load: shaderBall_grp shown, viewport looks through main_CAM, framed on shaderBall.
                 - Lighting: "Measurements Floor" checkbox (scaleSM_geo visibility toggle).
                 - Lighting: mt / cm toggle buttons (switches expression2.in[0] → aiSwitchBackdrop).
    0.9.8-beta  - CP042: Re-open after close fixed — show() hidden window instead of just raise().
                 - Section collapse now shrinks dialog — use minimumSizeHint() not adjustSize().
    0.9.7-beta  - CP041: Section arrows larger (16px), section numbers more visible (#aaaaaa).
    0.9.6-beta  - CP040: Singleton fixed — uses topLevelWidgets() search, survives module reloads.
                 - Added show() module-level entry point.
    0.9.5-beta  - CP039: Singleton window (re-run raises existing instead of spawning new).
                 - Removed QScrollArea — dialog height adapts as sections expand/collapse.
                 - Colour palette shifted to Maya native grays for readability.
                 - CollapsibleSection triggers adjustSize() on parent dialog on toggle.
    0.9.4-beta  - CP038: Full PySide6 UI rewrite — all cmds widgets replaced with Qt.
                 - UI now matches the approved HTML design preview exactly.
                 - CollapsibleSection, SliderRow, HdriCell helper classes.
                 - QDialog parented to Maya main window — no cmds.window required.
                 - Consistent dark theme: #272727 bg, #E8820C accent, readable contrast.
                 - Step flow: circle badges (done/ready/locked), sequential lock/unlock.
                 - HDRI grid: HdriCell with image preview, orange border on active slot.
                 - install_opencv progress uses QProgressDialog instead of cmds.progressWindow.
    0.9.3-beta  - CP037: UI redesign — toggle buttons, guided step flow, extended lighting.
    0.9.2-beta  - CP036: v002 scene support + two-tab interface + new utilities controls.
    0.9.1-beta  - CP035: UI standardisation + code cleanup pass.
    0.9.0-beta  - CP034: Beta promotion. All alpha features complete and validated.

Usage:
    Paste this script into the Maya Script Editor (Python tab) and press Ctrl+Enter.
    On first run, expand the root folder section and select your extracted archive root.
    The path and frame range are saved and restored automatically on subsequent runs.
"""

import maya.cmds as cmds
import os
import sys
import json
import logging

# ---------------------------------------------------------------------------
# pxl_ui shared kit bootstrap (Maya 2025 PySide6 / Nuke 15 PySide2 compatible)
# ---------------------------------------------------------------------------
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

# ── OpenCV library path ──────────────────────────────────────────────────────
_OPENCV_LIBS = os.path.join(
    os.path.expanduser("~"), "Documents", "maya", "PXLtools", "python_libs"
).replace("\\", "/")
if os.path.isdir(_OPENCV_LIBS) and _OPENCV_LIBS not in sys.path:
    sys.path.insert(0, _OPENCV_LIBS)

os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

# ── Logger ───────────────────────────────────────────────────────────────────
_log = logging.getLogger("PXL.TurnTableBuilder")
_log.setLevel(logging.DEBUG)
if not _log.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(
        logging.Formatter("[PXL TurnTable] %(levelname)s: %(message)s")
    )
    _log.addHandler(_h)


# ── PySide compatibility (Maya 2024 = PySide2 / Maya 2025 = PySide6) ──────
try:
    import PySide6 as _ps
    _PYSIDE_VER = 6
    from PySide6 import QtWidgets, QtCore, QtGui   # module-level for top-level classes
except ImportError:
    _PYSIDE_VER = 2
    from PySide2 import QtWidgets, QtCore, QtGui   # module-level for top-level classes

ACES_SETUP_URL = "https://youtu.be/kX3CQC7HzN8?t=222"

# ── Colour tokens ────────────────────────────────────────────────────────────

class _C:
    # Maya 2025 native palette — readable, matches host app
    BG_DARK        = "#333333"
    BG_WINDOW      = "#464646"   # Maya panel background
    BG_SECTION_HDR = "#393939"   # Section header (slightly darker)
    BG_SECTION_BOD = "#4a4a4a"   # Section body (slightly lighter)
    BG_INPUT       = "#3a3a3a"   # Input fields
    BG_HEADER      = "#0D1F24"   # Keep dark teal for brand header
    BORDER         = "#2b2b2b"
    BORDER_FAINT   = "#3a3a3a"
    ORANGE         = "#E8820C"
    TEXT_PRIMARY   = "#dcdcdc"   # Maya standard text
    TEXT_MUTED     = "#b0b0b0"
    TEXT_FAINT     = "#888888"
    STATUS_OK_BG   = "#2a402a"
    STATUS_OK_TEXT = "#7acc7a"
    STATUS_OK_BDR  = "#3a5a3a"
    STATUS_IDL_BG  = "#404040"
    DESTRUCT_BG    = "#4a3030"
    DESTRUCT_TEXT  = "#e07070"
    DESTRUCT_BDR   = "#6a3a3a"
    STEP_DONE_BG   = "#2a402a"
    STEP_DONE_TEXT = "#7acc7a"
    STEP_DONE_BDR  = "#3a5a3a"
    WARN_BG        = "#4a3a00"
    WARN_TEXT      = "#f0a820"
    FRAME_WARN_BG  = "#3a2c00"
    FRAME_WARN_TXT = "#c8850a"
    # Tuples kept for the few remaining cmds calls
    HEADER_BG      = (0.051, 0.122, 0.141)
    BTN_PRIMARY    = (0.910, 0.510, 0.047)
    BTN_RESET      = (0.320, 0.320, 0.320)


# ── Global QSS ───────────────────────────────────────────────────────────────

MAIN_QSS = pxlt.tool_qss() if _PXLUI else ""


# ── Helper widgets ────────────────────────────────────────────────────────────

class _FlatTextStyle(QtWidgets.QProxyStyle):
    """Kills any text drop-shadow / etch the host style draws.

    styleHint() disables the etched/dithered DISABLED-text effect; drawItemText()
    re-implements text drawing FLAT so even ENABLED text never gets a shadow."""
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


class CollapsibleSection(object):
    """
    Collapsible section built from two QFrame objects (header + body).
    Works in both Maya 2024 (PySide2) and Maya 2025 (PySide6).
    """
    try:
        from PySide6 import QtWidgets as _Qw, QtCore as _Qc, QtGui as _Qg
    except ImportError:
        from PySide2 import QtWidgets as _Qw, QtCore as _Qc, QtGui as _Qg

    def __init__(self, title, number=None, parent=None, compact=False,
                 icon_name=None, accent=None):
        try:
            from PySide6 import QtWidgets, QtCore, QtGui
        except ImportError:
            from PySide2 import QtWidgets, QtCore, QtGui

        self._collapsed = False
        self._compact = compact
        self._accent = accent or "#E8820C"
        self._icon_name = icon_name
        self._state = "idle"   # "idle" | "active" | "done"

        self._container = QtWidgets.QWidget(parent)
        self._container.setObjectName("collapsibleContainer")
        self._container.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        outer = QtWidgets.QVBoxLayout(self._container)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Header ──────────────────────────────────────────────────────────
        self._header = QtWidgets.QFrame()
        self._header.setFixedHeight(32)
        self._header.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        hbox = QtWidgets.QHBoxLayout(self._header)
        hbox.setContentsMargins(0, 0, 10, 0)
        hbox.setSpacing(7)

        self._bar = QtWidgets.QFrame()
        self._bar.setFixedWidth(3)
        self._bar.setStyleSheet("background: {}; border: none;".format(self._accent))
        hbox.addWidget(self._bar)

        if icon_name:
            try:
                from pxl_ui import icons as _pi
                _icl = QtWidgets.QLabel()
                _icl.setFixedWidth(18)
                _icl.setStyleSheet("background: transparent;")
                _icl.setPixmap(_pi.pixmap(icon_name, 18, self._accent))
                hbox.addWidget(_icl)
            except Exception:
                pass

        # Chevron icon (NOT a text glyph) so closed/open are exactly the same size.
        self._arrow = QtWidgets.QLabel()
        self._arrow.setFixedSize(14, 14)
        self._arrow.setAlignment(QtCore.Qt.AlignCenter)
        self._arrow.setStyleSheet("background: transparent;")
        self._update_arrow_icon()

        if number:
            num_lbl = QtWidgets.QLabel(number)
            num_lbl.setStyleSheet(
                "color: #aaaaaa; font-size: 12px; font-family: 'Courier New'; background: transparent;"
            )
            hbox.addWidget(num_lbl)

        title_lbl = QtWidgets.QLabel(title.upper())
        _tsiz = "12px"
        title_lbl.setStyleSheet(
            "color: #dcdcdc; font-weight: bold; font-size: {}; "
            "letter-spacing: 1px; background: transparent;".format(_tsiz)
        )
        hbox.addWidget(title_lbl)
        hbox.addStretch()

        # Section-level done check (pale green ✓ when complete)
        self._state_chk = QtWidgets.QLabel("")
        self._state_chk.setStyleSheet(
            "color: #5BBF6A; font-weight: bold; font-size: 12px; background: transparent;"
        )
        hbox.addWidget(self._state_chk)

        hbox.addWidget(self._arrow)

        outer.addWidget(self._header)
        self._apply_header_style()

        # ── Body ─────────────────────────────────────────────────────────────
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

        # Click handler
        self._header.mousePressEvent = lambda _e: self.set_collapsed(
            not self._collapsed
        )

    # ── Public API ────────────────────────────────────────────────────────────

    @property
    def widget(self):
        return self._container

    @property
    def body_layout(self):
        return self._body_layout

    def add_widget(self, w):
        self._body_layout.addWidget(w)

    def add_layout(self, lay):
        self._body_layout.addLayout(lay)

    def add_spacing(self, n):
        self._body_layout.addSpacing(n)

    def _update_arrow_icon(self):
        """Same-size chevron icon (chevron-right collapsed / chevron-down open)."""
        try:
            from pxl_ui import icons as _pi
        except Exception:
            return
        name = "collapsed" if self._collapsed else "expanded"   # chevron-right / chevron-down
        col  = "#888888" if self._collapsed else self._accent
        self._arrow.setPixmap(_pi.pixmap(name, 12, col))

    def set_collapsed(self, collapsed):
        self._collapsed = collapsed
        self._body.setVisible(not collapsed)
        self._apply_header_style()
        self._container.updateGeometry()

    def _apply_header_style(self):
        """Header background reflects progress state; radius reflects collapse."""
        radius = "5px" if self._collapsed else "5px 5px 0 0"
        if self._state == "done":
            bg = "#33402d"; hov = "#3d4a37"   # pale-green tint — section complete
        elif self._state == "active":
            bg = "#46413a"; hov = "#524d44"   # warm tint — this is the current step
        else:
            bg = "#3f3f3f"; hov = "#4a4a4a"
        # header is clickable (toggles) -> lighten on hover for clear feedback
        self._header.setStyleSheet(
            "QFrame {{ background: {}; border: none; border-radius: {}; }}"
            "QFrame:hover {{ background: {}; }}".format(bg, radius, hov)
        )
        self._update_arrow_icon()

    def set_state(self, state):
        """Visual progress state: 'idle' | 'active' (orange) | 'done' (pale green)."""
        self._state = state
        if state == "done":
            bar = "#5BBF6A"
        elif state == "active":
            bar = "#E8820C"
        else:
            bar = self._accent
        if getattr(self, "_bar", None):
            self._bar.setStyleSheet("background: {}; border: none;".format(bar))
        if getattr(self, "_state_chk", None):
            self._state_chk.setText("✓" if state == "done" else "")
        self._apply_header_style()


class SliderRow(object):
    """Label (click to reset) + QSlider + editable spinbox for manual override."""

    def __init__(self, label, min_val, max_val, default, step=0.01,
                 on_change=None, parent=None):
        try:
            from PySide6 import QtWidgets, QtCore, QtGui
        except ImportError:
            from PySide2 import QtWidgets, QtCore, QtGui

        self._min       = float(min_val)
        self._max       = float(max_val)
        self._step      = float(step)
        self._default   = float(default)
        self._on_change = on_change
        self._steps     = int(round((max_val - min_val) / step))
        self._syncing   = False

        self._widget = QtWidgets.QWidget(parent)
        # widget-level bg on the container keeps the slider groove truly
        # transparent (Fusion leaks a grey native groove otherwise)
        self._widget.setStyleSheet("background: transparent;")
        hbox = QtWidgets.QHBoxLayout(self._widget)
        hbox.setContentsMargins(0, 2, 0, 2)
        hbox.setSpacing(8)

        # Label — clickable, resets to default on click
        fmt = "{:.0f}" if step >= 1.0 else "{:.2f}"
        lbl = QtWidgets.QPushButton(label)
        lbl.setFixedWidth(110)
        lbl.setFlat(True)
        lbl.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        lbl.setToolTip("Click to reset to default ({})".format(fmt.format(default)))
        lbl.setStyleSheet(
            "QPushButton { color: #A8A8A8; font-size: 12px; background: transparent; "
            "border: none; text-align: right; padding-right: 4px; }"
            "QPushButton:hover { color: #E8820C; }"
        )
        lbl.clicked.connect(self._reset)
        hbox.addWidget(lbl)

        # Slider
        self._slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._slider.setRange(0, self._steps)
        self._slider.setValue(int(round((default - min_val) / step)))
        self._slider.setFixedHeight(24)   # room for the 20px handle/ring (no crop)
        # Qt only repaints the handle on hover, not the bar — force a full
        # repaint via a property toggle so the bar lightens on hover too.
        def _sl_enter(_e):
            self._slider.setProperty("hov", True)
            self._slider.style().unpolish(self._slider)
            self._slider.style().polish(self._slider)
        def _sl_leave(_e):
            self._slider.setProperty("hov", False)
            self._slider.style().unpolish(self._slider)
            self._slider.style().polish(self._slider)
        self._slider.enterEvent = _sl_enter
        self._slider.leaveEvent = _sl_leave
        hbox.addWidget(self._slider, 1)

        # Editable spinbox — unbounded so the user can type any override value
        decimals = 0 if step >= 1.0 else 2
        self._spinbox = QtWidgets.QDoubleSpinBox()
        self._spinbox.setDecimals(decimals)
        self._spinbox.setSingleStep(step)
        self._spinbox.setRange(-999999, 999999)
        self._spinbox.setValue(default)
        self._spinbox.setFixedSize(80, 28)
        # Base look only — let the shared theme drive the up/down BUTTONS, arrows
        # and hover so these match the RENDER-tab spin-boxes exactly.
        self._spinbox.setStyleSheet(
            "QDoubleSpinBox { background: #2c2c2c; border: 1px solid #262626; "
            "border-radius: 4px; color: #E6E6E6; font-size: 12px; "
            "font-family: 'Courier New'; padding: 0 2px; }"
            "QDoubleSpinBox:focus { border: 1px solid #E8820C; }"
        )
        hbox.addWidget(self._spinbox)

        self._slider.valueChanged.connect(self._on_slider_changed)
        self._spinbox.valueChanged.connect(self._on_spinbox_changed)

    def _on_slider_changed(self):
        if self._syncing:
            return
        v = self._min + self._slider.value() * self._step
        self._syncing = True
        self._spinbox.setValue(v)
        self._syncing = False
        if self._on_change:
            self._on_change(v)

    def _on_spinbox_changed(self, v):
        if self._syncing:
            return
        # Sync slider — clamp position to valid range, but pass raw value to Maya
        slider_pos = int(round((v - self._min) / self._step))
        slider_pos = max(0, min(self._steps, slider_pos))
        self._syncing = True
        self._slider.setValue(slider_pos)
        self._syncing = False
        if self._on_change:
            self._on_change(v)

    def _reset(self):
        self._syncing = True
        self._spinbox.setValue(self._default)
        self._slider.setValue(int(round((self._default - self._min) / self._step)))
        self._syncing = False
        if self._on_change:
            self._on_change(self._default)

    @property
    def widget(self):
        return self._widget

    def value(self):
        return self._spinbox.value()

    def set_value(self, v):
        """Set value without triggering on_change callback."""
        self._syncing = True
        self._spinbox.setValue(v)
        slider_pos = int(round((v - self._min) / self._step))
        slider_pos = max(0, min(self._steps, slider_pos))
        self._slider.setValue(slider_pos)
        self._syncing = False

    def set_enabled(self, state):
        self._slider.setEnabled(state)
        self._spinbox.setEnabled(state)


class HdriCell(object):
    """Single HDRI slot — preview image + name label, orange border when active."""

    CELL_W  = 124
    CELL_H  = 128   # taller — more breathing room for the preview + Replace button
    PREV_H  = 96    # preview image area height (larger so HDRIs read clearly)
    NAME_H  = 24    # name label height

    def __init__(self, slot_index, name="", is_custom=False, on_click=None):
        try:
            from PySide6 import QtWidgets, QtCore, QtGui
        except ImportError:
            from PySide2 import QtWidgets, QtCore, QtGui

        self._index     = slot_index
        self._is_custom = is_custom
        self._on_click  = on_click
        self._active    = False
        self._hover     = False

        self._frame = QtWidgets.QFrame()
        self._frame.setObjectName("hdriCellInactive")
        self._frame.setFixedSize(self.CELL_W, self.CELL_H)
        self._frame.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        vbox = QtWidgets.QVBoxLayout(self._frame)
        vbox.setContentsMargins(2, 2, 2, 2)
        vbox.setSpacing(0)

        # Preview
        self._preview = QtWidgets.QLabel()
        self._preview.setFixedHeight(self.PREV_H)
        self._preview.setAlignment(QtCore.Qt.AlignCenter)
        if is_custom:
            self._preview.setText("+")
            self._preview.setStyleSheet(
                "background: #2b2b2b; color: #888888; font-size: 22px; border-radius: 6px;"
            )
        else:
            self._preview.setStyleSheet("background: #2b2b2b; border-radius: 6px;")
        vbox.addWidget(self._preview)

        # Name
        self._name_lbl = QtWidgets.QLabel(name)
        self._name_lbl.setFixedHeight(self.NAME_H)
        self._name_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self._name_lbl.setStyleSheet(
            "background: #2b2b2b; color: #aaaaaa; font-size: 10px; padding: 2px 3px;"
        )
        vbox.addWidget(self._name_lbl)

        self._frame.mousePressEvent = lambda _e: self._clicked()
        self._frame.enterEvent = lambda _e: self._set_hover(True)
        self._frame.leaveEvent = lambda _e: self._set_hover(False)

    def _clicked(self):
        if self._on_click:
            self._on_click(self._index)

    @property
    def widget(self):
        return self._frame

    def set_active(self, active):
        self._active = active
        self._refresh_frame_style()
        self._name_lbl.setStyleSheet(
            "background: #2b2b2b; color: {}; font-size: 10px; padding: 2px 3px;".format(
                "#E8820C" if active else "#aaaaaa"
            )
        )

    def _set_hover(self, hovered):
        self._hover = hovered
        self._refresh_frame_style()

    def _refresh_frame_style(self):
        if self._active:
            bg  = "#3a3a3a" if self._hover else "#333333"
            bdr = "#f09020" if self._hover else "#E8820C"
        else:
            bg  = "#3d3d3d" if self._hover else "#333333"
            bdr = "#606060" if self._hover else "transparent"
        self._frame.setStyleSheet(
            "QFrame {{ background: {bg}; border: 2px solid {bdr}; "
            "border-radius: 7px; }}".format(bg=bg, bdr=bdr)
        )

    def set_preview(self, image_path):
        try:
            from PySide6 import QtGui, QtCore
        except ImportError:
            from PySide2 import QtGui, QtCore
        if image_path and os.path.isfile(image_path):
            px = QtGui.QPixmap(image_path).scaled(
                self.CELL_W, self.PREV_H,
                QtCore.Qt.KeepAspectRatioByExpanding,
                QtCore.Qt.SmoothTransformation
            )
            # round the image corners to match the rounded card
            rounded = QtGui.QPixmap(px.size())
            rounded.fill(QtCore.Qt.transparent)
            _pnt = QtGui.QPainter(rounded)
            _pnt.setRenderHint(QtGui.QPainter.Antialiasing, True)
            _path = QtGui.QPainterPath()
            _path.addRoundedRect(0, 0, px.width(), px.height(), 6, 6)
            _pnt.setClipPath(_path)
            _pnt.drawPixmap(0, 0, px)
            _pnt.end()
            self._preview.setPixmap(rounded)
            self._preview.setStyleSheet("background: #2b2b2b; border-radius: 6px;")
            self._preview.setText("")

    def set_name(self, name):
        display = name if len(name) <= 18 else name[:16] + "…"
        self._name_lbl.setText(display)

    def reset_to_custom(self, custom_num):
        self._preview.clear()
        self._preview.setText("+")
        self._preview.setStyleSheet(
            "background: #2b2b2b; color: #888888; font-size: 22px; border-radius: 6px;"
        )
        self._name_lbl.setText("Custom {}".format(custom_num))
        self._name_lbl.setStyleSheet(
            "background: #2b2b2b; color: #aaaaaa; font-size: 8px; padding: 2px 3px;"
        )


# ── Main class ────────────────────────────────────────────────────────────────

class TurnTableBuilder(object):
    """
    PXL TurnTable Builder — Maya 2024-2025 / Python 3 / PySide2+PySide6.

    Full PySide6/PySide2 UI embedded in Maya via QDialog parented to Maya main window.
    All Maya scene operations use maya.cmds.
    """

    TOOL_NAME         = "PXL TurnTable Builder"
    VERSION           = "1.0.26"
    WINDOW_OBJECT_NAME = "PXLtools_TurnTableBuilder_v100"
    # Older window ids earlier builds used — matched on relaunch so an Update
    # cleanly closes a stale window instead of leaving a duplicate alongside.
    _LEGACY_WINDOW_NAMES = ("PXLTurnTableBuilder_v100",)
    ICON_NAME         = "icon_turntable_builder.png"
    TT_NAMESPACE      = "TT_SCENE"
    TT_SCENE_FILENAME = "PXLtools_TB3DTT_ACES_2025_v003.ma"
    TT_USER_RIGS_GRP  = "TT_userRigs_grp"   # world-level container for user locator rigs

    HDRI_PRESET_COUNT = 6
    HDRI_CUSTOM_COUNT = 2
    HDRI_SLOT_COUNT   = 8

    CELL_W = 114
    CELL_H = 96

    DEFAULT_FRAME_START = 1001
    DEFAULT_FRAME_END   = 1200

    CONFIG_PATH = os.path.join(
        os.path.expanduser("~"),
        "Documents", "maya", "PXLtools",
        "turntable_builder_config.json"
    )

    def __init__(self):
        # Singleton check via Qt widget registry — survives importlib.reload().
        # topLevelWidgets() is maintained by QApplication, not by module state.
        try:
            from PySide6 import QtWidgets
        except ImportError:
            from PySide2 import QtWidgets
        app = QtWidgets.QApplication.instance()
        if app:
            known_names = (self.WINDOW_OBJECT_NAME,) + self._LEGACY_WINDOW_NAMES
            for w in app.topLevelWidgets():
                if w.objectName() in known_names:
                    # Same name AND same version already open -> just raise it.
                    if (w.objectName() == self.WINDOW_OBJECT_NAME
                            and w.property("pxlTTVersion") == self.VERSION):
                        w.show()
                        w.raise_()
                        w.activateWindow()
                        return
                    # Otherwise an older build (or a legacy-named window) -> close it
                    # and rebuild, so the shelf "Update" swaps in the new code instead
                    # of re-raising the stale window.
                    try:
                        w.close()
                        w.deleteLater()
                    except Exception:
                        pass
                    break
        # Runtime state
        self.root_folder      = None
        self.scene_path       = None
        self.hdri_dir         = None
        self.hdri_preview_dir = None
        self.shaders_dir      = None
        self.utilities_dir    = None
        self.presets_dir      = None

        self.frame_start = self.DEFAULT_FRAME_START
        self.frame_end   = self.DEFAULT_FRAME_END

        self.captured_nodes            = []
        self._user_rig_locators        = []   # locators created by attach_to_turntable
        self._active_hdri_index        = -1
        self._custom_hdri_paths        = {}
        self._hdri_cells               = []   # list of HdriCell (8 slots)

        # Guided-flow progress flags
        self._frames_applied           = False
        self._rendered                 = False
        # Guided-flow widget handles (set in build methods)
        self._prelim_root_badge        = None
        self._prelim_root_confirm      = None
        self._prelim_browse_btn        = None
        self._prelim_set_btn           = None
        self._prelim_aces_badge        = None
        self._prelim_aces_confirm      = None
        self._prelim_cv_badge          = None
        self._prelim_cv_confirm        = None
        self._sc_load_badge            = None
        self._sc_load_confirm          = None
        self._sc_apply_badge           = None
        self._sc_apply_confirm         = None
        self._rl_create_badge          = None
        self._rl_create_confirm        = None
        self._rl_create_btn            = None
        self._rl_render_badge          = None
        self._rl_render_confirm        = None
        self._rt_section_frame         = None   # CollapsibleSection (RENDER TURNTABLE)
        self._rl_section_frame         = None   # CollapsibleSection (RENDER LAYERS SETUP)
        self._clear_layers_ck          = None   # QCheckBox — also delete layers on Clear
        self._denoiser_ck              = None   # QCheckBox — OptiX denoiser toggle

        # ── Qt widget handles ────────────────────────────────────────────────
        self._window                 = None   # QDialog
        self._warning_banner         = None   # QLabel
        self._instructions_frame     = None   # CollapsibleSection — outer Instructions panel
        self._preliminary_frame      = None   # CollapsibleSection
        self._root_field             = None   # QLineEdit
        self._root_status_label      = None   # QLabel
        self._opencv_status_label    = None   # QLabel
        self._opencv_install_btn     = None   # QPushButton
        self._section1_frame         = None   # CollapsibleSection
        self._scene_status_label     = None   # QLabel
        self._start_frame_field      = None   # QSpinBox
        self._end_frame_field        = None   # QSpinBox
        self._section2_frame         = None   # CollapsibleSection
        self._model_btn_sb           = None   # QPushButton
        self._model_btn_own          = None   # QPushButton
        self._shaderball_section     = None   # QWidget
        self._own_model_section      = None   # QWidget
        self._sb_main_ck             = None   # QCheckBox
        self._sb_cloth_ck            = None   # QCheckBox
        self._sb_liquid_ck           = None   # QCheckBox
        self._selection_label        = None   # QLabel
        self._maintain_offset_ck     = None   # QCheckBox — Maintain Offset
        self._hdri_rotation_slider   = None   # SliderRow — domelight rotateY offset
        self._utilities_subsection   = None   # CollapsibleSection — charts placement
        self._hdri_subsection        = None   # CollapsibleSection — HDRI environment
        # ── Turntable tab ─────────────────────────────────────────────────────
        self._rl_slot_checks         = []     # QCheckBox list — one per HDRI slot
        self._rl_charts_ck           = None   # QCheckBox — include charts layers
        self._rt_start_spin          = None   # QSpinBox — render start frame
        self._rt_end_spin            = None   # QSpinBox — render end frame
        self._rt_step_spin           = None   # QSpinBox — render by frame (step)
        self._rt_res_combo           = None   # QComboBox — render resolution preset
        self._rt_render_btn          = None   # QPushButton — render turntable (gated)
        self._step_done              = [False, False, False]
        self._step_btns              = [None, None, None]    # QPushButton
        self._step_circles           = [None, None, None]    # QLabel (circle badge)
        self._step_confirms          = [None, None, None]    # QLabel (✓ badge)
        self._section3_frame         = None   # CollapsibleSection
        self._lighting_charts_ck     = None   # QCheckBox
        self._lighting_shaderball_ck = None   # QCheckBox
        self._lighting_model_ck      = None   # QCheckBox
        self._backdrop_btn_hdri          = None   # QPushButton toggle — HDRI backdrop
        self._backdrop_btn_limbo         = None   # QPushButton toggle — Limbo backdrop
        self._lighting_floor_grid_ck     = None   # QCheckBox — floor grid (aiSwitchBackdrop)
        self._lighting_size_ref_ck       = None   # QCheckBox — sizeRef_grp
        self._lighting_arnold_rv_btn = None   # QPushButton — Arnold RenderView
        self._lighting_arnold_rn_btn = None   # QPushButton — Arnold Render
        self._grid_btn_mt            = None   # QPushButton — 1mt grid
        self._grid_btn_cm            = None   # QPushButton — 10cm grid
        self._scale_slider           = None   # SliderRow
        self._macbeth_x_slider       = None   # SliderRow
        self._macbeth_y_slider       = None   # SliderRow
        self._refball_x_slider       = None   # SliderRow
        self._refball_y_slider       = None   # SliderRow
        self._hdri_grid_widget       = None   # QWidget container for HDRI grid
        self._gated_buttons          = []     # QPushButton list, enabled when root valid

        self._load_config()
        self._resolve_paths()
        self.create_ui()
        self._restore_session_state()
        if self._is_opencv_available():
            self._write_maya_env_exr_flag()

    # ─────────────────────────────────────────────────────────────────────────
    # Config persistence
    # ─────────────────────────────────────────────────────────────────────────

    def _load_config(self):
        if not os.path.exists(self.CONFIG_PATH):
            return
        try:
            with open(self.CONFIG_PATH, "r") as fh:
                data = json.load(fh)
            if data.get("root_folder"):
                self.root_folder = data["root_folder"]
            self.frame_start = int(data.get("frame_start", self.DEFAULT_FRAME_START))
            self.frame_end   = int(data.get("frame_end",   self.DEFAULT_FRAME_END))
            raw = data.get("custom_hdri_paths", {})
            self._custom_hdri_paths  = {int(k): v for k, v in raw.items()}
            self._active_hdri_index  = int(data.get("active_hdri_index", -1))
        except Exception as exc:
            _log.warning("Config read failed: %s", exc)

    def _save_config(self, root_folder=None, frame_start=None, frame_end=None,
                     custom_hdri_paths=None, active_hdri_index=None):
        try:
            existing = {}
            if os.path.exists(self.CONFIG_PATH):
                try:
                    with open(self.CONFIG_PATH, "r") as fh:
                        existing = json.load(fh)
                except Exception:
                    pass
            if root_folder       is not None: existing["root_folder"]        = root_folder
            if frame_start       is not None: existing["frame_start"]        = frame_start
            if frame_end         is not None: existing["frame_end"]          = frame_end
            if custom_hdri_paths is not None:
                existing["custom_hdri_paths"] = {str(k): v for k, v in custom_hdri_paths.items()}
            if active_hdri_index is not None: existing["active_hdri_index"] = active_hdri_index

            config_dir = os.path.dirname(self.CONFIG_PATH)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            with open(self.CONFIG_PATH, "w") as fh:
                json.dump(existing, fh, indent=4)
        except Exception as exc:
            _log.warning("Config write failed: %s", exc)
            cmds.warning("PXL TurnTable: Config save failed — {}".format(exc))

    def _restore_session_state(self):
        if not self._is_turntable_loaded():
            return
        _log.info("Session restore: turntable reference detected.")

        user_nodes = []
        locators   = []

        to_render_grp = self._get_tt_render_grp()
        if to_render_grp:
            active_ns = self._get_active_namespace() or self.TT_NAMESPACE
            children  = cmds.listRelatives(to_render_grp, children=True, fullPath=False) or []
            for child in children:
                if child.startswith(active_ns + ":"):
                    continue  # skip turntable's own nodes
                if child.startswith("TT_loc_"):
                    # New-style: locator rig — collect its user-object children
                    locators.append(child)
                    for obj in (cmds.listRelatives(child, children=True, fullPath=False) or []):
                        if cmds.nodeType(obj) == "transform":
                            user_nodes.append(obj)
                else:
                    # Legacy-style: object parented directly under mainModel_grp
                    user_nodes.append(child)

        if user_nodes:
            self.captured_nodes       = user_nodes
            self._user_rig_locators   = locators
            if self._selection_label:
                self._selection_label.setText(
                    "  Captured: {}".format(", ".join(user_nodes))
                )
            self._set_model_mode("your_model")
            for i in range(3):
                self._update_step_ui(i, done=True, unlock_next=(i < 2))

        self._set_scene_status(loaded=True)
        self._sync_ui_from_scene()

        for slot_index, hdri_path in self._custom_hdri_paths.items():
            if not os.path.isfile(hdri_path):
                continue
            base       = os.path.splitext(os.path.basename(hdri_path))[0]
            thumb_path = None
            if self.hdri_preview_dir:
                candidate = os.path.join(self.hdri_preview_dir, base + ".jpg").replace("\\", "/")
                if os.path.isfile(candidate):
                    thumb_path = candidate
                else:
                    thumb_path = self._generate_hdri_thumbnail(hdri_path)
            self._update_custom_slot_ui(slot_index, hdri_path, thumb_path)

        if self._active_hdri_index >= 0:
            self._update_hdri_highlight(self._active_hdri_index)

        # On session restore: collapse everything, show only Section 01 (Scene Setup)
        if self._instructions_frame:
            self._instructions_frame.set_collapsed(True)
        if self._preliminary_frame:
            self._preliminary_frame.set_collapsed(True)
        if self._section1_frame:
            self._section1_frame.set_collapsed(False)
        if self._section2_frame:
            self._section2_frame.set_collapsed(True)
        if self._section3_frame:
            self._section3_frame.set_collapsed(True)

        # Enable Render Turntable button if TT layers already exist in the scene
        if self._rt_render_btn and self._tt_layers_exist():
            self._rt_render_btn.setEnabled(True)

        # Guided-flow: a restored turntable scene is already past Scene Setup.
        self._frames_applied = True
        self._update_scene_steps()
        self._update_render_steps()
        self._update_model_section_state()

    def _resolve_paths(self):
        if not self.root_folder:
            self.scene_path = self.hdri_dir = self.hdri_preview_dir = None
            self.shaders_dir = self.utilities_dir = self.presets_dir = None
            return
        root = self.root_folder.replace("\\", "/")
        self.scene_path       = "{}/scenes/{}".format(root, self.TT_SCENE_FILENAME)
        self.hdri_dir         = "{}/sourceimages/HDRIs".format(root)
        self.hdri_preview_dir = "{}/sourceimages/HDRIs/previews".format(root)
        self.shaders_dir      = "{}/sourceimages/shaders".format(root)
        self.utilities_dir    = "{}/sourceimages/utilities".format(root)
        self.presets_dir      = "{}/presets".format(root)

    def _is_root_valid(self):
        return bool(self.root_folder and os.path.isdir(self.root_folder))

    # ─────────────────────────────────────────────────────────────────────────
    # UI construction
    # ─────────────────────────────────────────────────────────────────────────

    def create_ui(self):
        from maya import OpenMayaUI as omui
        try:
            from PySide6 import QtWidgets, QtCore, QtGui
        except ImportError:
            from PySide2 import QtWidgets, QtCore, QtGui
        try:
            import shiboken6 as shiboken
        except ImportError:
            import shiboken2 as shiboken

        maya_ptr  = omui.MQtUtil.mainWindow()
        maya_main = shiboken.wrapInstance(int(maya_ptr), QtWidgets.QWidget)

        self._window = QtWidgets.QDialog(maya_main)
        self._window.setObjectName(self.WINDOW_OBJECT_NAME)
        # Tag the window with its tool version so a later launch can tell a stale
        # build from the current one (drives the version-aware singleton above).
        self._window.setProperty("pxlTTVersion", self.VERSION)
        self._window.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowTitleHint |
            QtCore.Qt.WindowCloseButtonHint
        )
        self._window.setWindowTitle("{} v{}".format(self.TOOL_NAME, self.VERSION))
        self._window.setFixedWidth(620)
        self._window.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
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
                    _c = _D / 2.0
                    _pn.setPen(QtCore.Qt.NoPen)
                    _pn.setBrush(QtGui.QColor("#ffffff"))
                    _pn.drawEllipse(QtCore.QPointF(_c, _c), 6.5, 6.5)
                    if ring:
                        _pen = QtGui.QPen(QtGui.QColor("#E8820C")); _pen.setWidthF(2.0)
                        _pn.setPen(_pen); _pn.setBrush(QtCore.Qt.NoBrush)
                        _pn.drawEllipse(QtCore.QPointF(_c, _c), 8.0, 8.0)
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
        self._window.setStyleSheet(_qss)
        # Remove Qt's etched disabled-text emboss (looks like a text drop-shadow).
        try:
            self._window.setStyle(_FlatTextStyle(self._window.style()))
        except Exception:
            pass

        root_vbox = QtWidgets.QVBoxLayout(self._window)
        root_vbox.setContentsMargins(0, 0, 0, 0)
        root_vbox.setSpacing(0)

        # Header
        self._build_header(root_vbox)

        # Header separator
        hdr_sep = QtWidgets.QFrame()
        hdr_sep.setFixedHeight(1)
        hdr_sep.setStyleSheet("background: #1e2a2d; border: none;")
        root_vbox.addWidget(hdr_sep)

        # Tab widget
        tab_widget = QtWidgets.QTabWidget()
        tab_widget.setDocumentMode(True)
        root_vbox.addWidget(tab_widget, 1)

        def _wrap_scroll(content):
            sa = QtWidgets.QScrollArea()
            sa.setWidgetResizable(True)
            sa.setFrameShape(QtWidgets.QFrame.NoFrame)
            sa.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            sa.setStyleSheet("QScrollArea { background: #333333; border: none; }")
            sa.setWidget(content)
            return sa

        # ── PREP tab ─────────────────────────────────────────────────────────
        prep_content = QtWidgets.QWidget()
        prep_layout  = QtWidgets.QVBoxLayout(prep_content)
        prep_layout.setContentsMargins(12, 10, 12, 14)
        prep_layout.setSpacing(4)
        self._build_prep_content(prep_layout)
        tab_widget.addTab(_wrap_scroll(prep_content), "  1  ·  SETUP  ")

        # ── TURNTABLE tab ─────────────────────────────────────────────────────
        tt_widget = QtWidgets.QWidget()
        tt_layout = QtWidgets.QVBoxLayout(tt_widget)
        tt_layout.setContentsMargins(14, 14, 14, 14)
        tt_layout.setAlignment(QtCore.Qt.AlignTop)
        self._build_turntable_tab(tt_layout)
        tab_widget.addTab(_wrap_scroll(tt_widget), "  2  ·  RENDER  ")

        # Resizable (especially height); content scrolls when long.
        self._window.setMinimumHeight(380)
        self._window.resize(620, 860)
        self._window.show()
        self._refresh_ui_state()

    def _build_header(self, layout):
        try:
            from PySide6 import QtWidgets, QtGui, QtCore
        except ImportError:
            from PySide2 import QtWidgets, QtGui, QtCore

        if _PXLUI:
            try:
                _ip = cmds.internalVar(userPrefDir=True) + "icons/" + self.ICON_NAME
                layout.addWidget(pxlw.AppHeader(
                    "TurnTable Builder", "v" + self.VERSION, icon_path=_ip))
                return
            except Exception:
                pass

        icon_path = cmds.internalVar(userPrefDir=True) + "icons/"

        hw = QtWidgets.QWidget()
        hw.setFixedHeight(106)
        hw.setStyleSheet("background-color: #0D1F24;")

        root_hbox = QtWidgets.QHBoxLayout(hw)
        root_hbox.setContentsMargins(10, 5, 10, 5)
        root_hbox.setSpacing(0)

        # Left: tool icon
        left = QtWidgets.QLabel()
        left.setFixedSize(96, 96)
        left.setAlignment(QtCore.Qt.AlignCenter)
        ti = icon_path + self.ICON_NAME
        if os.path.exists(ti):
            left.setPixmap(
                QtGui.QPixmap(ti).scaled(96, 96, QtCore.Qt.KeepAspectRatio,
                                         QtCore.Qt.SmoothTransformation)
            )
        else:
            left.setText("[Icon]")
            left.setStyleSheet("background:#152a30; color:white; border:1px dashed #2a4a54;")
        root_hbox.addWidget(left)

        # Center: logo + tool name + version
        cv = QtWidgets.QVBoxLayout()
        cv.setContentsMargins(0, 0, 0, 0)
        cv.setSpacing(2)
        cv.setAlignment(QtCore.Qt.AlignVCenter)

        logo_lbl = QtWidgets.QLabel()
        logo_lbl.setFixedSize(262, 48)
        logo_lbl.setAlignment(QtCore.Qt.AlignCenter)
        lp = icon_path + "PXLtools_logo.png"
        if os.path.exists(lp):
            logo_lbl.setPixmap(
                QtGui.QPixmap(lp).scaled(262, 48, QtCore.Qt.KeepAspectRatio,
                                         QtCore.Qt.SmoothTransformation)
            )
        else:
            logo_lbl.setText("PXLtools")
            logo_lbl.setStyleSheet("color:#D7005A; font-weight:bold; font-size:14px;")

        lhbox = QtWidgets.QHBoxLayout()
        lhbox.setContentsMargins(0, 0, 0, 0)
        lhbox.addStretch()
        lhbox.addWidget(logo_lbl)
        lhbox.addStretch()

        div_lbl = QtWidgets.QLabel()
        div_lbl.setFixedSize(200, 1)
        div_lbl.setStyleSheet("background: #1e3a42;")

        name_lbl = QtWidgets.QLabel("TurnTable Builder")
        name_lbl.setAlignment(QtCore.Qt.AlignCenter)
        name_lbl.setStyleSheet("color:white; font-weight:bold; font-size:11px;")

        ver_lbl = QtWidgets.QLabel("v{}".format(self.VERSION))
        ver_lbl.setAlignment(QtCore.Qt.AlignCenter)
        ver_lbl.setStyleSheet("color:#3a5a64; font-size:9px;")

        cv.addLayout(lhbox)
        cv.addWidget(div_lbl, 0, QtCore.Qt.AlignCenter)
        cv.addWidget(name_lbl)
        cv.addWidget(ver_lbl)
        root_hbox.addLayout(cv, 1)

        # NO right spacer per PXLMENTOR_TOOL_STANDARD v1.1.0 - the center
        # vbox stretches all the way to the right margin so the logo centers
        # in the visible content area (visually balanced against the left icon).

        layout.addWidget(hw)

    def _build_prep_content(self, layout):
        try:
            from PySide6 import QtWidgets
        except ImportError:
            from PySide2 import QtWidgets

        # Instructions — open on first run (root not set yet); collapsed once
        # everything is already set up (root valid => the user has read these and
        # configured the prerequisites, so jump straight to Scene Setup below).
        instr = CollapsibleSection("Instructions", compact=True, icon_name="info", accent="#46C2D6")
        instr.set_collapsed(self._is_root_valid())
        self._instructions_frame = instr
        lead = QtWidgets.QLabel(
            "Follow the numbers — the orange step is what to do next, and it turns "
            "green when it is done. There are two tabs: 1 · SETUP builds and lights "
            "the shot; 2 · RENDER writes the Nuke-ready layers.")
        lead.setObjectName("hint")
        lead.setWordWrap(True)
        instr.body_layout.addWidget(lead)
        instr.body_layout.addSpacing(6)

        tip = QtWidgets.QLabel(
            "TIP — In Maya, use File ▸ Set Project and point it at your shot folder "
            "first. That way every render and export is written to the correct "
            "project sub-folder instead of a stray temp location.")
        tip.setObjectName("hint")
        tip.setWordWrap(True)
        tip.setStyleSheet("color:#E8B84B;")   # gentle amber so the reminder stands out
        instr.body_layout.addWidget(tip)
        instr.body_layout.addSpacing(6)

        for line in [
            "Preliminary — Browse and Set the TurnTable Root Folder (required). "
            "ACES 1.2 and OpenCV are checked for you automatically.",
            "01  Scene Setup — Load the turntable scene, then set the Start / End "
            "frames and press Apply to lock the frame range.",
            "02  Model — Your Model is selected by default: select your asset(s) in "
            "the viewport, then run Capture → Align to Ground → Attach. (Switch to "
            "Shader Ball only if you want the built-in test sphere instead.)",
            "03  Lighting — Choose an HDRI, toggle Visibility / Backdrop / Size "
            "References, and use ARNOLD RENDER to preview your look.",
            "2 · RENDER tab — Tick the HDRI slots to render, press Create Render "
            "Layers, then Render Turntable to export the layers for Nuke.",
        ]:
            lbl = QtWidgets.QLabel(line)
            lbl.setObjectName("hint")
            lbl.setWordWrap(True)
            instr.body_layout.addWidget(lbl)

        instr.body_layout.addSpacing(4)

        # Preliminary Steps — nested inside Instructions
        self._preliminary_frame = CollapsibleSection(
            "Preliminary Steps", compact=True, icon_name="folder", accent="#E8820C"
        )
        self._preliminary_frame.set_collapsed(self._is_root_valid())
        self._build_preliminary_content(self._preliminary_frame.body_layout)
        instr.body_layout.addWidget(self._preliminary_frame.widget)

        layout.addWidget(instr.widget)

        layout.addSpacing(4)

        # Warning banner
        self._warning_banner = QtWidgets.QLabel(
            "  ⚠   Set root folder in Preliminary Steps before continuing"
        )
        self._warning_banner.setObjectName("warningBanner")
        self._warning_banner.setVisible(not self._is_root_valid())
        layout.addWidget(self._warning_banner)

        layout.addSpacing(4)

        # Section 01 — Scene Setup. Opened automatically when the prerequisites are
        # already done (root valid) so the user lands straight here; otherwise it
        # stays collapsed until load_turntable_scene opens it.
        self._section1_frame = CollapsibleSection(
            "Scene Setup", number="01", icon_name="install", accent="#4F9DE0"
        )
        self._section1_frame.set_collapsed(not self._is_root_valid())
        self._build_section1_content(self._section1_frame.body_layout)
        layout.addWidget(self._section1_frame.widget)

        layout.addSpacing(4)

        # Section 02 — Model
        self._section2_frame = CollapsibleSection(
            "Model", number="02", icon_name="model", accent="#9B7EDE"
        )
        self._section2_frame.set_collapsed(True)
        self._build_section2_content(self._section2_frame.body_layout)
        layout.addWidget(self._section2_frame.widget)

        layout.addSpacing(4)

        # Section 03 — Lighting
        self._section3_frame = CollapsibleSection(
            "Lighting", number="03", icon_name="lighting", accent="#F2C14E"
        )
        self._section3_frame.set_collapsed(True)
        self._build_section3_content(self._section3_frame.body_layout)
        layout.addWidget(self._section3_frame.widget)

        layout.addStretch(1)
        layout.addSpacing(8)

        # Divider
        div = QtWidgets.QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background: #2b2b2b; border: none;")
        layout.addWidget(div)

        layout.addSpacing(8)

        # Clear Scene
        clear_btn = QtWidgets.QPushButton(
            "  Clear Scene  ·  removes turntable reference, keeps model"
        )
        clear_btn.setObjectName("btnDestruct")
        clear_btn.setFixedHeight(36)
        clear_btn.clicked.connect(self.clear_scene)
        self._gated_buttons.append(clear_btn)
        layout.addWidget(clear_btn)

        # Also remove the TT render layers on Clear (on by default — a full clean).
        self._clear_layers_ck = QtWidgets.QCheckBox(
            "Also remove the TT render layers (full clean)")
        self._clear_layers_ck.setChecked(True)
        layout.addWidget(self._clear_layers_ck)

    def _build_preliminary_content(self, layout):
        try:
            from PySide6 import QtWidgets
        except ImportError:
            from PySide2 import QtWidgets

        intro = QtWidgets.QLabel(
            "One-time setup. Follow the numbers — each turns green when it is done."
        )
        intro.setObjectName("hint")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        layout.addSpacing(5)

        # ── Step 1 — Root Folder (the only required action) ────────────────────
        row1, self._prelim_root_badge, self._prelim_root_confirm = self._mk_step_header(
            "1", "SET TURNTABLE ROOT FOLDER")
        layout.addLayout(row1)

        hint1 = QtWidgets.QLabel("Browse to your TurnTable project folder, then press Set.")
        hint1.setObjectName("hint")
        hint1.setWordWrap(True)
        layout.addWidget(hint1)
        layout.addSpacing(3)

        row = QtWidgets.QHBoxLayout()
        row.setSpacing(4)
        self._root_field = QtWidgets.QLineEdit()
        self._root_field.setPlaceholderText("No folder selected — click Browse…")
        self._root_field.setReadOnly(True)
        self._root_field.setText(self.root_folder or "")
        self._root_field.textChanged.connect(lambda *_: self._update_prelim_ui())
        row.addWidget(self._root_field, 1)

        self._prelim_browse_btn = QtWidgets.QPushButton("Browse…")
        self._prelim_browse_btn.setFixedWidth(92)
        self._prelim_browse_btn.clicked.connect(self.browse_root_folder)
        row.addWidget(self._prelim_browse_btn)
        layout.addLayout(row)
        layout.addSpacing(3)

        self._prelim_set_btn = QtWidgets.QPushButton("Set Root Folder")
        self._prelim_set_btn.clicked.connect(self.set_root_folder)
        layout.addWidget(self._prelim_set_btn)
        layout.addSpacing(2)

        self._root_status_label = QtWidgets.QLabel(self._root_status_text())
        self._root_status_label.setObjectName("hint")
        self._root_status_label.setWordWrap(True)
        layout.addWidget(self._root_status_label)

        # Separator
        sep = QtWidgets.QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #333333; border: none;")
        layout.addSpacing(5)
        layout.addWidget(sep)
        layout.addSpacing(5)

        # \u2500\u2500 Step 2 \u2014 ACES colour management (auto-confirms when present) \u2500\u2500\u2500\u2500\u2500\u2500\u2500
        row2, self._prelim_aces_badge, self._prelim_aces_confirm = self._mk_step_header(
            "2", "ACES 1.2 COLOUR MANAGEMENT")
        layout.addLayout(row2)

        if self._is_aces_configured():
            aces_status = QtWidgets.QLabel("ACES 1.2 active \u2014 colour management ready.")
            aces_status.setObjectName("hint")
            aces_status.setWordWrap(True)
            layout.addWidget(aces_status)
        else:
            aces_status = QtWidgets.QLabel(
                "ACES 1.2 not detected \u2014 renders may not match the expected output. "
                "This tool is built for ACES 1.2; follow the guide to configure Maya.")
            aces_status.setObjectName("hint")
            aces_status.setWordWrap(True)
            layout.addWidget(aces_status)
            layout.addSpacing(3)
            aces_btn = QtWidgets.QPushButton("  Watch Setup Guide (YouTube)")
            aces_btn.setObjectName("btnStepActive")
            aces_btn.clicked.connect(
                lambda: __import__("webbrowser").open(ACES_SETUP_URL))
            layout.addWidget(aces_btn)

        # Separator
        sep2 = QtWidgets.QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet("background: #333333; border: none;")
        layout.addSpacing(5)
        layout.addWidget(sep2)
        layout.addSpacing(5)

        # ── Step 3 — OpenCV (optional; auto-confirms when present) ─────────────
        row3, self._prelim_cv_badge, self._prelim_cv_confirm = self._mk_step_header(
            "3", "OPENCV  (OPTIONAL)")
        layout.addLayout(row3)

        cv_info = QtWidgets.QLabel(
            "Only needed to generate preview thumbnails for custom HDRIs. "
            "Safe one-time install, no admin rights.")
        cv_info.setObjectName("hint")
        cv_info.setWordWrap(True)
        layout.addWidget(cv_info)
        layout.addSpacing(2)

        if self._is_opencv_available():
            self._opencv_status_label = QtWidgets.QLabel(
                "OpenCV installed — custom HDRI previews enabled.")
            self._opencv_status_label.setObjectName("hint")
            self._opencv_status_label.setWordWrap(True)
            layout.addWidget(self._opencv_status_label)
        else:
            cv_row = QtWidgets.QHBoxLayout()
            self._opencv_status_label = QtWidgets.QLabel(
                "Not installed — custom HDRI thumbnails will use a fallback.")
            self._opencv_status_label.setObjectName("hint")
            self._opencv_status_label.setWordWrap(True)
            cv_row.addWidget(self._opencv_status_label, 1)
            self._opencv_install_btn = QtWidgets.QPushButton("Install OpenCV")
            self._opencv_install_btn.setObjectName("btnStepActive")
            self._opencv_install_btn.setFixedWidth(110)
            self._opencv_install_btn.clicked.connect(self.install_opencv)
            cv_row.addWidget(self._opencv_install_btn)
            layout.addLayout(cv_row)

        self._update_prelim_ui()

    def _build_section1_content(self, layout):
        try:
            from PySide6 import QtWidgets
        except ImportError:
            from PySide2 import QtWidgets

        intro = QtWidgets.QLabel("Load the turntable scene, then lock your frame range.")
        intro.setObjectName("hint")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        layout.addSpacing(5)

        # ── Step 1 — Load Scene ────────────────────────────────────────────────
        row1, self._sc_load_badge, self._sc_load_confirm = self._mk_step_header(
            "1", "LOAD TURNTABLE SCENE")
        layout.addLayout(row1)

        self._sc_load_btn = QtWidgets.QPushButton("  Load Turntable Scene")
        self._sc_load_btn.setObjectName("btnStepActive")
        self._sc_load_btn.setFixedHeight(40)
        self._sc_load_btn.clicked.connect(self.load_turntable_scene)
        layout.addWidget(self._sc_load_btn)
        layout.addSpacing(4)

        self._scene_status_label = QtWidgets.QLabel("  —  Scene: Not loaded")
        self._scene_status_label.setObjectName("statusIdle")
        layout.addWidget(self._scene_status_label)

        # Separator
        sep = QtWidgets.QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #333333; border: none;")
        layout.addSpacing(8)
        layout.addWidget(sep)
        layout.addSpacing(8)

        # ── Step 2 — Apply Frame Range ─────────────────────────────────────────
        row2, self._sc_apply_badge, self._sc_apply_confirm = self._mk_step_header(
            "2", "APPLY FRAME RANGE")
        layout.addLayout(row2)

        hint2 = QtWidgets.QLabel(
            "Set start / end frames, then press Apply — without this there is NO animation.")
        hint2.setObjectName("hint")
        hint2.setWordWrap(True)
        layout.addWidget(hint2)
        layout.addSpacing(3)

        fr_row = QtWidgets.QHBoxLayout()
        fr_row.setSpacing(6)

        fr_lbl = QtWidgets.QLabel("Frame Range")
        fr_lbl.setObjectName("stepTitle")
        fr_lbl.setFixedWidth(96)
        fr_row.addWidget(fr_lbl)

        self._start_frame_field = QtWidgets.QSpinBox()
        self._start_frame_field.setRange(0, 999999)
        self._start_frame_field.setValue(self.frame_start)
        fr_row.addWidget(self._start_frame_field)

        sep_lbl = QtWidgets.QLabel("—")
        sep_lbl.setStyleSheet("color: #888888; background: transparent;")
        fr_row.addWidget(sep_lbl)

        self._end_frame_field = QtWidgets.QSpinBox()
        self._end_frame_field.setRange(1, 999999)
        self._end_frame_field.setValue(self.frame_end)
        fr_row.addWidget(self._end_frame_field)

        self._sc_apply_btn = QtWidgets.QPushButton("Apply")
        self._sc_apply_btn.setObjectName("btnStepActive")
        self._sc_apply_btn.setFixedWidth(72)
        self._sc_apply_btn.clicked.connect(self.apply_frame_range)
        fr_row.addWidget(self._sc_apply_btn)
        fr_row.addStretch()
        layout.addLayout(fr_row)

        self._update_scene_steps()

    def _build_section2_content(self, layout):
        try:
            from PySide6 import QtWidgets
        except ImportError:
            from PySide2 import QtWidgets

        # Mode toggle buttons
        toggle_row = QtWidgets.QHBoxLayout()
        toggle_row.setSpacing(4)

        # Your Model is the DEFAULT — left button, active. (Shader Ball is the
        # alternative on the right.)
        self._model_btn_own = QtWidgets.QPushButton("  YOUR MODEL")
        self._model_btn_own.setObjectName("btnToggleActive")
        self._model_btn_own.setFixedHeight(36)
        self._model_btn_own.clicked.connect(lambda: self._set_model_mode("your_model"))

        self._model_btn_sb = QtWidgets.QPushButton("  SHADER BALL")
        self._model_btn_sb.setObjectName("btnToggleInactive")
        self._model_btn_sb.setFixedHeight(36)
        self._model_btn_sb.clicked.connect(lambda: self._set_model_mode("shader_ball"))

        toggle_row.addWidget(self._model_btn_own, 1)
        toggle_row.addWidget(self._model_btn_sb, 1)
        layout.addLayout(toggle_row)

        layout.addSpacing(8)

        # ── Sub-section: Shader Ball (hidden by default — Your Model leads) ────
        self._shaderball_section = QtWidgets.QWidget()
        self._shaderball_section.setVisible(False)
        sb_layout = QtWidgets.QVBoxLayout(self._shaderball_section)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(5)

        sb_title = QtWidgets.QLabel("  SHADER BALL ELEMENTS")
        sb_title.setObjectName("sbExtrasLabel")
        sb_layout.addWidget(sb_title)

        ck_row = QtWidgets.QHBoxLayout()
        ck_row.setSpacing(16)

        self._sb_main_ck = QtWidgets.QCheckBox("Shader Ball")
        self._sb_main_ck.setChecked(False)
        self._sb_main_ck.stateChanged.connect(
            lambda v: self.toggle_shaderball_viz(bool(v))
        )

        self._sb_cloth_ck = QtWidgets.QCheckBox("Cloth")
        self._sb_cloth_ck.setChecked(False)
        self._sb_cloth_ck.stateChanged.connect(
            lambda v: self.toggle_cloth_viz(bool(v))
        )

        self._sb_liquid_ck = QtWidgets.QCheckBox("Liquid")
        self._sb_liquid_ck.setChecked(False)
        self._sb_liquid_ck.stateChanged.connect(
            lambda v: self.toggle_liquid_viz(bool(v))
        )

        ck_row.addWidget(self._sb_main_ck)
        ck_row.addWidget(self._sb_cloth_ck)
        ck_row.addWidget(self._sb_liquid_ck)
        ck_row.addStretch()
        sb_layout.addLayout(ck_row)

        layout.addWidget(self._shaderball_section)

        # ── Sub-section: Your Model ───────────────────────────────────────────
        self._own_model_section = QtWidgets.QWidget()
        self._own_model_section.setVisible(True)   # default mode
        om_layout = QtWidgets.QVBoxLayout(self._own_model_section)
        om_layout.setContentsMargins(0, 0, 0, 0)
        om_layout.setSpacing(6)

        self._selection_label = QtWidgets.QLabel("  No model captured — select the model you want to capture")
        self._selection_label.setObjectName("selLabel")
        om_layout.addWidget(self._selection_label)

        om_layout.addSpacing(4)

        # Steps ① ② ③
        step_defs = [
            ("Capture Selection",   "Select your model(s) or root group(s)",        True),
            ("Align to Ground",     "Grounds base to Y=0",                          False),
            ("Attach to Turntable", "Creates locator rig, constrains to rotation",  False),
        ]
        circle_chars = ["1", "2", "3"]

        for idx, (btn_label, hint_text, enabled) in enumerate(step_defs):
            step_row = QtWidgets.QHBoxLayout()
            step_row.setSpacing(8)

            # Circle badge
            circle = QtWidgets.QLabel(circle_chars[idx])
            circle.setFixedSize(22, 22)
            circle.setAlignment(
                (__import__("PySide6.QtCore" if _PYSIDE_VER == 6 else "PySide2.QtCore", fromlist=["Qt"])).Qt.AlignCenter
            )
            circle.setObjectName("stepReady" if enabled else "stepLocked")
            self._step_circles[idx] = circle
            step_row.addWidget(circle)

            # Button + hint column
            col = QtWidgets.QVBoxLayout()
            col.setSpacing(1)

            btn = QtWidgets.QPushButton(btn_label)
            btn.setMinimumHeight(32)   # room for the orange active border (no crop)
            btn.setObjectName("btnStepActive" if enabled else "btnStepLocked")
            btn.setEnabled(enabled)

            hint = QtWidgets.QLabel(hint_text)
            hint.setObjectName("hint")

            col.addWidget(btn)
            col.addWidget(hint)
            step_row.addLayout(col, 1)

            # Confirm badge
            confirm = QtWidgets.QLabel("")
            confirm.setObjectName("stepConfirmEmpty")
            confirm.setFixedWidth(60)
            self._step_confirms[idx] = confirm
            step_row.addWidget(confirm)

            om_layout.addLayout(step_row)
            self._step_btns[idx] = btn
            if enabled:
                self._gated_buttons.append(btn)
            else:
                self._gated_buttons.append(btn)  # also gated (step logic applies)

        # Wire up step buttons
        self._step_btns[0].clicked.connect(self.capture_selection)
        self._step_btns[1].clicked.connect(self.align_to_ground)
        self._step_btns[2].clicked.connect(self.attach_to_turntable)

        # Maintain Offset checkbox (indented, below Attach button)
        offset_row = QtWidgets.QHBoxLayout()
        offset_row.setContentsMargins(32, 2, 0, 0)
        self._maintain_offset_ck = QtWidgets.QCheckBox("Maintain Offset")
        self._maintain_offset_ck.setChecked(False)
        self._maintain_offset_ck.setToolTip(
            "ON: objects keep their world-space positions and spin on their own pivots.\n"
            "OFF: objects are centered to the XZ origin before attaching."
        )
        offset_row.addWidget(self._maintain_offset_ck)
        offset_row.addStretch()
        om_layout.addLayout(offset_row)

        layout.addWidget(self._own_model_section)

    def _build_section3_content(self, layout):
        try:
            from PySide6 import QtWidgets, QtCore
        except ImportError:
            from PySide2 import QtWidgets, QtCore

        # ── 2x2 grid: Visibility | Size References / Backdrop | Arnold ─────
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(6)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        # ─── Top-left: VISIBILITY ────────────────────────────────────────
        vis_frame = QtWidgets.QFrame()
        vis_frame.setObjectName("sectionFrame")
        vis_frame.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        vis_layout = QtWidgets.QVBoxLayout(vis_frame)
        vis_layout.setContentsMargins(10, 8, 10, 10)
        vis_layout.setSpacing(4)

        vis_title = QtWidgets.QLabel("VISIBILITY")
        vis_title.setStyleSheet("color: #E8820C; font-size: 10px; font-weight: bold; "
            "letter-spacing: 1px; background: transparent; border: none;")
        vis_layout.addWidget(vis_title)

        self._lighting_model_ck = QtWidgets.QCheckBox("Model")
        self._lighting_model_ck.setChecked(True)
        self._lighting_model_ck.stateChanged.connect(
            lambda v: self.toggle_model_viz(bool(v))
        )
        vis_layout.addWidget(self._lighting_model_ck)

        self._lighting_shaderball_ck = QtWidgets.QCheckBox("Shader Ball")
        self._lighting_shaderball_ck.setChecked(True)
        self._lighting_shaderball_ck.stateChanged.connect(
            lambda v: self.toggle_shaderball(bool(v))
        )
        vis_layout.addWidget(self._lighting_shaderball_ck)

        self._lighting_charts_ck = QtWidgets.QCheckBox("Charts")
        self._lighting_charts_ck.setChecked(True)
        self._lighting_charts_ck.stateChanged.connect(
            lambda v: self.toggle_charts(bool(v))
        )
        vis_layout.addWidget(self._lighting_charts_ck)
        vis_layout.addStretch()

        # ─── Top-right: SIZE REFERENCES ──────────────────────────────────
        sizeref_frame = QtWidgets.QFrame()
        sizeref_frame.setObjectName("sectionFrame")
        sizeref_frame.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        sizeref_layout = QtWidgets.QVBoxLayout(sizeref_frame)
        sizeref_layout.setContentsMargins(10, 8, 10, 10)
        sizeref_layout.setSpacing(4)

        sizeref_title = QtWidgets.QLabel("SIZE REFERENCES")
        sizeref_title.setStyleSheet("color: #E8820C; font-size: 10px; font-weight: bold; "
            "letter-spacing: 1px; background: transparent; border: none;")
        sizeref_layout.addWidget(sizeref_title)

        self._lighting_floor_grid_ck = QtWidgets.QCheckBox("Floor Grid")
        self._lighting_floor_grid_ck.setChecked(True)
        self._lighting_floor_grid_ck.setToolTip(
            "Show measurement grid on the limbo backdrop.\n"
            "Grid unit is set by the 10cm / 1mt buttons below."
        )
        self._lighting_floor_grid_ck.stateChanged.connect(
            lambda v: self.toggle_floor_grid(bool(v))
        )
        sizeref_layout.addWidget(self._lighting_floor_grid_ck)

        self._lighting_size_ref_ck = QtWidgets.QCheckBox("Ref Cubes")
        self._lighting_size_ref_ck.setChecked(False)
        self._lighting_size_ref_ck.stateChanged.connect(
            lambda v: self.toggle_size_ref_cubes(bool(v))
        )
        sizeref_layout.addWidget(self._lighting_size_ref_ck)

        unit_btn_row = QtWidgets.QHBoxLayout()
        unit_btn_row.setSpacing(4)
        unit_btn_row.setContentsMargins(0, 4, 0, 0)

        self._grid_btn_cm = QtWidgets.QPushButton("10 cm")
        self._grid_btn_cm.setObjectName("btnToggleInactive")
        self._grid_btn_cm.setFixedHeight(28)
        self._grid_btn_cm.clicked.connect(lambda: self.set_grid_unit("cm"))

        self._grid_btn_mt = QtWidgets.QPushButton("1 mt")
        self._grid_btn_mt.setObjectName("btnToggleActive")
        self._grid_btn_mt.setFixedHeight(28)
        self._grid_btn_mt.clicked.connect(lambda: self.set_grid_unit("mt"))

        unit_btn_row.addWidget(self._grid_btn_cm)
        unit_btn_row.addWidget(self._grid_btn_mt)
        sizeref_layout.addLayout(unit_btn_row)
        self._gated_buttons.extend([self._grid_btn_cm, self._grid_btn_mt])
        sizeref_layout.addStretch()

        # ─── Bottom-left: BACKDROP ───────────────────────────────────────
        backdrop_frame = QtWidgets.QFrame()
        backdrop_frame.setObjectName("sectionFrame")
        backdrop_frame.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        backdrop_layout = QtWidgets.QVBoxLayout(backdrop_frame)
        backdrop_layout.setContentsMargins(10, 8, 10, 10)
        backdrop_layout.setSpacing(6)

        backdrop_title = QtWidgets.QLabel("BACKDROP")
        backdrop_title.setStyleSheet("color: #E8820C; font-size: 10px; font-weight: bold; "
            "letter-spacing: 1px; background: transparent; border: none;")
        backdrop_layout.addWidget(backdrop_title)

        bd_btn_row = QtWidgets.QHBoxLayout()
        bd_btn_row.setSpacing(4)

        self._backdrop_btn_hdri = QtWidgets.QPushButton("HDRI")
        self._backdrop_btn_hdri.setObjectName("btnToggleInactive")
        self._backdrop_btn_hdri.setFixedHeight(28)
        self._backdrop_btn_hdri.setToolTip("Physical floor / HDRI environment geometry.")
        self._backdrop_btn_hdri.clicked.connect(lambda: self.set_backdrop("hdri"))

        self._backdrop_btn_limbo = QtWidgets.QPushButton("LIMBO")
        self._backdrop_btn_limbo.setObjectName("btnToggleActive")
        self._backdrop_btn_limbo.setFixedHeight(28)
        self._backdrop_btn_limbo.setToolTip(
            "Infinite limbo backdrop.\n"
            "Enable Floor Grid (top-right) to overlay the measurement texture."
        )
        self._backdrop_btn_limbo.clicked.connect(lambda: self.set_backdrop("limbo"))

        bd_btn_row.addWidget(self._backdrop_btn_hdri)
        bd_btn_row.addWidget(self._backdrop_btn_limbo)
        backdrop_layout.addLayout(bd_btn_row)
        backdrop_layout.addStretch()

        # ─── Bottom-right: ARNOLD RENDER ─────────────────────────────────
        arnold_frame = QtWidgets.QFrame()
        arnold_frame.setObjectName("sectionFrame")
        arnold_frame.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        arnold_layout = QtWidgets.QVBoxLayout(arnold_frame)
        arnold_layout.setContentsMargins(10, 8, 10, 10)
        arnold_layout.setSpacing(6)

        arnold_title = QtWidgets.QLabel("ARNOLD RENDER")
        arnold_title.setStyleSheet("color: #E8820C; font-size: 10px; font-weight: bold; "
            "letter-spacing: 1px; background: transparent; border: none;")
        arnold_layout.addWidget(arnold_title)

        arnold_btn_row = QtWidgets.QHBoxLayout()
        arnold_btn_row.setSpacing(4)

        self._lighting_arnold_rv_btn = QtWidgets.QPushButton("RenderView")
        self._lighting_arnold_rv_btn.setObjectName("btnAction")
        self._lighting_arnold_rv_btn.setFixedHeight(28)
        self._lighting_arnold_rv_btn.clicked.connect(self.open_arnold_renderview)

        self._lighting_arnold_rn_btn = QtWidgets.QPushButton("Render")
        self._lighting_arnold_rn_btn.setObjectName("btnAction")
        self._lighting_arnold_rn_btn.setFixedHeight(28)
        self._lighting_arnold_rn_btn.clicked.connect(self.render_with_arnold)

        arnold_btn_row.addWidget(self._lighting_arnold_rv_btn)
        arnold_btn_row.addWidget(self._lighting_arnold_rn_btn)
        arnold_layout.addLayout(arnold_btn_row)

        # Denoiser toggle — drives the scene's OptiX denoiser imager. Off by default.
        dn_row = QtWidgets.QHBoxLayout()
        dn_row.setSpacing(6)
        self._denoiser_ck = QtWidgets.QCheckBox("Denoiser (OptiX)")
        self._denoiser_ck.setChecked(False)
        self._denoiser_ck.setToolTip("Enable / disable the scene's OptiX denoiser imager.")
        self._denoiser_ck.stateChanged.connect(lambda v: self.toggle_denoiser(bool(v)))
        dn_row.addWidget(self._denoiser_ck)

        denoise_note = QtWidgets.QLabel("requires NVIDIA GPU")
        denoise_note.setStyleSheet(
            "color: #8a8a8a; font-size: 9px; background: transparent; border: none;")
        dn_row.addWidget(denoise_note)
        dn_row.addStretch()
        arnold_layout.addLayout(dn_row)
        arnold_layout.addStretch()

        # ─── Visibility | Size References ──────────────────────────────────
        # Packed into this grid, which is added INTO the CUSTOM SETTINGS collapsible
        # below (not the main layout). Backdrop + Arnold Render go into the HDRI card.
        grid.addWidget(vis_frame,     0, 0)
        grid.addWidget(sizeref_frame, 0, 1)

        # ── UTILITIES collapsible subsection ─────────────────────────────────
        try:
            from PySide6 import QtWidgets, QtCore
        except ImportError:
            from PySide2 import QtWidgets, QtCore

        utilities_cs = CollapsibleSection("CUSTOM SETTINGS", compact=True, icon_name="utilities", accent="#34B3A0")

        # Visibility | Size References live here now — all the fine-tuning in one place.
        utilities_cs.add_layout(grid)
        utilities_cs.add_spacing(8)
        _cs_div = QtWidgets.QFrame()
        _cs_div.setFrameShape(QtWidgets.QFrame.HLine)
        _cs_div.setFixedHeight(1)
        _cs_div.setStyleSheet("background:#2b2b2b; border:none;")
        utilities_cs.add_widget(_cs_div)
        utilities_cs.add_spacing(8)

        self._scale_slider = SliderRow(
            "Scale",
            min_val=0.5, max_val=1.5, default=1.0, step=0.01,
            on_change=self.set_charts_scale
        )
        self._scale_slider.widget.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        utilities_cs.add_widget(self._scale_slider.widget)

        sub_lbl = QtWidgets.QLabel("Scales the Macbeth chart and reference ball.")
        sub_lbl.setObjectName("hint")
        sub_lbl.setWordWrap(True)
        utilities_cs.add_widget(sub_lbl)
        utilities_cs.add_spacing(4)

        # Two-column layout: Ref Ball (left) | Macbeth (right)
        two_col = QtWidgets.QHBoxLayout()
        two_col.setSpacing(6)
        two_col.setContentsMargins(0, 0, 0, 0)

        def _compact_col(header_text):
            """Returns (QVBoxLayout, container_widget)."""
            col_w = QtWidgets.QWidget()
            col_w.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
            )
            col_l = QtWidgets.QVBoxLayout(col_w)
            col_l.setContentsMargins(0, 0, 0, 0)
            col_l.setSpacing(2)
            hdr = QtWidgets.QLabel(header_text)
            hdr.setObjectName("ctrlLabel")
            col_l.addWidget(hdr)
            return col_l, col_w

        def _slim_label(slider_row):
            """Shrink the SliderRow label button to 28px for compact columns."""
            try:
                from PySide6 import QtWidgets as _QW
            except ImportError:
                from PySide2 import QtWidgets as _QW
            for child in slider_row.widget.children():
                if isinstance(child, _QW.QPushButton) and child.isFlat():
                    child.setFixedWidth(28)
                    break

        # Left column — Ref Ball
        left_l, left_w = _compact_col("  REF BALL")

        self._refball_x_slider = SliderRow(
            "X", min_val=-100.0, max_val=100.0, default=0.0, step=1.0,
            on_change=self.set_refball_x
        )
        _slim_label(self._refball_x_slider)
        left_l.addWidget(self._refball_x_slider.widget)

        self._refball_y_slider = SliderRow(
            "Y", min_val=-100.0, max_val=100.0, default=0.0, step=1.0,
            on_change=self.set_refball_y
        )
        _slim_label(self._refball_y_slider)
        left_l.addWidget(self._refball_y_slider.widget)
        two_col.addWidget(left_w, 1)

        # Vertical divider
        vdiv = QtWidgets.QFrame()
        vdiv.setFrameShape(QtWidgets.QFrame.VLine)
        vdiv.setFixedWidth(1)
        vdiv.setStyleSheet("background: #333333; border: none;")
        two_col.addWidget(vdiv)

        # Right column — Macbeth
        right_l, right_w = _compact_col("  MACBETH")

        self._macbeth_x_slider = SliderRow(
            "X", min_val=-100.0, max_val=100.0, default=0.0, step=1.0,
            on_change=self.set_macbeth_x
        )
        _slim_label(self._macbeth_x_slider)
        right_l.addWidget(self._macbeth_x_slider.widget)

        self._macbeth_y_slider = SliderRow(
            "Y", min_val=-100.0, max_val=100.0, default=0.0, step=1.0,
            on_change=self.set_macbeth_y
        )
        _slim_label(self._macbeth_y_slider)
        right_l.addWidget(self._macbeth_y_slider.widget)
        two_col.addWidget(right_w, 1)

        utilities_cs.add_layout(two_col)
        self._utilities_subsection = utilities_cs
        # (added to `layout` at the end of this method — after HDRI + Display row)

        # ── HDRI collapsible — pick an HDRI, set its start angle, then render ──
        hdri_cs = CollapsibleSection("HDRI", compact=True, icon_name="hdri", accent="#E8694A")

        # Short description at the top.
        hdri_desc = QtWidgets.QLabel("Click the HDRI you want to use.")
        hdri_desc.setObjectName("hint")
        hdri_desc.setWordWrap(True)
        hdri_cs.add_widget(hdri_desc)
        hdri_cs.add_spacing(4)

        # 1) HDRI image grid stays at the top — the main choice.
        self._hdri_grid_widget = QtWidgets.QWidget()
        # Keep its full height (don't let the scroll area compress the rows).
        self._hdri_grid_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum
        )
        hdri_grid_layout = QtWidgets.QGridLayout(self._hdri_grid_widget)
        hdri_grid_layout.setContentsMargins(0, 0, 0, 0)
        hdri_grid_layout.setHorizontalSpacing(8)
        hdri_grid_layout.setVerticalSpacing(10)
        hdri_cs.add_widget(self._hdri_grid_widget)
        hdri_cs.add_spacing(10)

        # 2) Starting position (rotation) UNDER the images, with its own header + note.
        startpos_hdr = QtWidgets.QLabel("HDRI STARTING POSITION")
        startpos_hdr.setStyleSheet("color:#E8820C; font-size:10px; font-weight:bold; "
            "letter-spacing:1px; background:transparent; border:none;")
        hdri_cs.add_widget(startpos_hdr)

        self._hdri_rotation_slider = SliderRow(
            "Angle",
            min_val=-180.0, max_val=180.0, default=0.0, step=1.0,
            on_change=self.set_hdri_rotation
        )
        hdri_cs.add_widget(self._hdri_rotation_slider.widget)

        startpos_desc = QtWidgets.QLabel(
            "Rotate the HDRI to set its starting position — this aims the main "
            "light and reflections where you want them.")
        startpos_desc.setObjectName("hint")
        startpos_desc.setWordWrap(True)
        hdri_cs.add_widget(startpos_desc)
        hdri_cs.add_spacing(10)

        # 3) Separator, then the Backdrop | Arnold Render card.
        hdri_div = QtWidgets.QFrame()
        hdri_div.setFrameShape(QtWidgets.QFrame.HLine)
        hdri_div.setFixedHeight(1)
        hdri_div.setStyleSheet("background:#2b2b2b; border:none;")
        hdri_cs.add_widget(hdri_div)
        hdri_cs.add_spacing(10)

        essentials_row = QtWidgets.QHBoxLayout()
        essentials_row.setSpacing(6)
        essentials_row.addWidget(backdrop_frame, 1)
        essentials_row.addWidget(arnold_frame, 1)
        hdri_cs.add_layout(essentials_row)

        self._hdri_subsection = hdri_cs

        # ── Section order: HDRI (pick + render) → Custom Settings (everything else) ──
        layout.addWidget(hdri_cs.widget)        # 1) HDRI first
        layout.addSpacing(4)
        layout.addWidget(utilities_cs.widget)   # 2) Custom Settings (visibility,
                                                #    size refs, ref ball & charts)

        self._build_hdri_grid()

    def _build_hdri_grid(self):
        try:
            from PySide6 import QtWidgets
        except ImportError:
            from PySide2 import QtWidgets

        self._hdri_cells = []
        self._studio_hdri_index = 0   # updated below when a "Studio" preset is found

        grid_layout = self._hdri_grid_widget.layout()

        # Clear existing
        while grid_layout.count():
            item = grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        previews = self._get_preview_images()

        for i in range(self.HDRI_SLOT_COUNT):
            is_custom = i >= self.HDRI_PRESET_COUNT
            row_idx = i // 4
            col_idx = i % 4

            if is_custom:
                custom_num = i - self.HDRI_PRESET_COUNT + 1
                cell = HdriCell(
                    slot_index=i,
                    name="Custom {}".format(custom_num),
                    is_custom=True,
                    on_click=lambda si=i: cmds.evalDeferred(lambda: self.browse_custom_hdri(si))
                )
            else:
                preview_path = (
                    previews[i].replace("\\", "/") if i < len(previews) else ""
                )
                raw_name  = (
                    os.path.splitext(os.path.basename(preview_path))[0]
                    if preview_path else "HDRI {}".format(i + 1)
                )
                cell = HdriCell(
                    slot_index=i,
                    name=raw_name,
                    is_custom=False,
                    on_click=lambda si=i: self.select_hdri(si)
                )
                if preview_path:
                    cell.set_preview(preview_path)
                if "studio" in raw_name.lower():
                    self._studio_hdri_index = i

            self._hdri_cells.append(cell)
            grid_layout.addWidget(cell.widget, row_idx, col_idx)

        # Restore saved custom slots
        for slot_index, hdri_path in self._custom_hdri_paths.items():
            if os.path.isfile(hdri_path) and slot_index < len(self._hdri_cells):
                base       = os.path.splitext(os.path.basename(hdri_path))[0]
                thumb_path = None
                if self.hdri_preview_dir:
                    cand = os.path.join(self.hdri_preview_dir, base + ".jpg").replace("\\", "/")
                    if os.path.isfile(cand):
                        thumb_path = cand
                if thumb_path:
                    self._hdri_cells[slot_index].set_preview(thumb_path)
                    self._hdri_cells[slot_index].set_name(base)

        # Default selection = Studio (orange-highlighted) when nothing else is set.
        if self._active_hdri_index < 0:
            self._active_hdri_index = self._default_hdri_index()
        self._update_hdri_highlight(self._active_hdri_index)

        # Replace buttons — one below each custom slot (slots 6 and 7)
        try:
            from PySide6 import QtWidgets
        except ImportError:
            from PySide2 import QtWidgets
        for i in range(self.HDRI_PRESET_COUNT, self.HDRI_SLOT_COUNT):
            custom_num = i - self.HDRI_PRESET_COUNT + 1
            col_idx    = i % 4
            replace_btn = QtWidgets.QPushButton("Replace")
            replace_btn.setObjectName("btnAction")   # themed — same font/size/hover as other buttons
            replace_btn.setMinimumHeight(26)
            replace_btn.clicked.connect(
                lambda _checked, si=i: cmds.evalDeferred(
                    lambda si=si: self.browse_custom_hdri(si)
                )
            )
            grid_layout.addWidget(replace_btn, 2, col_idx)

        # Keep TURNTABLE tab slot labels in sync
        self._refresh_rl_slot_names()

    def _rebuild_hdri_grid(self):
        """Tear down and rebuild the HDRI grid after root/scene change."""
        if self._hdri_grid_widget is None:
            return
        self._hdri_cells = []
        self._build_hdri_grid()

    # ─────────────────────────────────────────────────────────────────────────
    # TURNTABLE tab — UI builder
    # ─────────────────────────────────────────────────────────────────────────

    def _build_turntable_tab(self, layout):
        """Build the TURNTABLE tab — render layer pipeline UI."""
        try:
            from PySide6 import QtWidgets, QtCore
        except ImportError:
            from PySide2 import QtWidgets, QtCore

        # ── Section title ─────────────────────────────────────────────────────
        tt_title = QtWidgets.QLabel("TURNTABLE RENDER PIPELINE")
        tt_title.setStyleSheet(
            "color: #c0c0c0; font-weight: bold; font-size: 11px; "
            "letter-spacing: 1px; background: transparent;"
        )
        layout.addWidget(tt_title)
        layout.addSpacing(12)

        # ── Render Layers Setup (collapsible — auto-collapses after Create) ───
        rl_cs = CollapsibleSection(
            "RENDER LAYERS SETUP", compact=True, icon_name="layers", accent="#E8820C")
        rl_cs.set_collapsed(False)
        self._rl_section_frame = rl_cs
        section_vbox = rl_cs.body_layout   # all content below builds into the body

        def _hsep():
            s = QtWidgets.QFrame()
            s.setFrameShape(QtWidgets.QFrame.HLine)
            s.setStyleSheet("border: none; background: #2c2c2c; max-height: 1px;")
            return s

        # ── HDRI slot label ───────────────────────────────────────────────────
        slots_lbl = QtWidgets.QLabel("  SELECT HDRI SLOTS")
        slots_lbl.setStyleSheet(
            "color: #888888; font-size: 9px; letter-spacing: 1px; "
            "background: transparent; border: none;"
        )
        section_vbox.addWidget(slots_lbl)

        # Select All / Deselect All row
        sel_row = QtWidgets.QHBoxLayout()
        sel_row.setSpacing(6)
        sel_all_btn  = QtWidgets.QPushButton("Select All")
        sel_none_btn = QtWidgets.QPushButton("Deselect All")
        for btn in (sel_all_btn, sel_none_btn):
            btn.setFixedHeight(22)
            btn.setStyleSheet(
                "QPushButton { background: #2c2c2c; color: #aaaaaa; font-size: 9px; "
                "border: 1px solid #262626; border-radius: 2px; padding: 0 8px; }"
                "QPushButton:hover { background: #323232; color: #E8820C; border-color: #E8820C; }"
            )
        sel_row.addWidget(sel_all_btn)
        sel_row.addWidget(sel_none_btn)
        sel_row.addStretch()
        section_vbox.addLayout(sel_row)
        section_vbox.addSpacing(4)

        # ── Slot checkboxes — themed (same size/font as the Lighting section),
        #    laid out in two columns: Slot 1-4 | Slot 5-8 to save vertical space.
        slot_grid = QtWidgets.QGridLayout()
        slot_grid.setHorizontalSpacing(18)
        slot_grid.setVerticalSpacing(4)
        slot_grid.setContentsMargins(2, 0, 2, 0)
        self._rl_slot_checks = []
        for i in range(self.HDRI_SLOT_COUNT):
            if i >= self.HDRI_PRESET_COUNT:
                label = "  Slot {:02d}   Custom {}".format(i + 1, i - self.HDRI_PRESET_COUNT + 1)
            else:
                label = "  Slot {:02d}   HDRI {}".format(i + 1, i + 1)
            ck = QtWidgets.QCheckBox(label)
            ck.setChecked(i < self.HDRI_PRESET_COUNT)  # presets checked, custom unchecked
            slot_grid.addWidget(ck, i % 4, i // 4)      # col 0 = 1-4, col 1 = 5-8
            self._rl_slot_checks.append(ck)
        section_vbox.addLayout(slot_grid)

        section_vbox.addSpacing(8)
        section_vbox.addWidget(_hsep())
        section_vbox.addSpacing(6)

        # ── Include Charts checkbox ───────────────────────────────────────────
        self._rl_charts_ck = QtWidgets.QCheckBox("  Include Charts Layers  (RL_charts_XX)")
        self._rl_charts_ck.setChecked(True)
        section_vbox.addWidget(self._rl_charts_ck)
        section_vbox.addSpacing(12)

        # ── Step 1 — Create Render Layers ──────────────────────────────────────
        section_vbox.addSpacing(2)
        crow, self._rl_create_badge, self._rl_create_confirm = self._mk_step_header(
            "1", "CREATE RENDER LAYERS")
        section_vbox.addLayout(crow)

        self._rl_create_btn = QtWidgets.QPushButton("  Create Render Layers")
        self._rl_create_btn.setObjectName("btnStepActive")
        self._rl_create_btn.setMinimumHeight(36)
        self._rl_create_btn.clicked.connect(self.create_tt_render_layers)
        section_vbox.addWidget(self._rl_create_btn)
        section_vbox.addSpacing(4)

        delete_btn = QtWidgets.QPushButton("  DELETE TT RENDER LAYERS")
        delete_btn.setFixedHeight(28)
        delete_btn.setStyleSheet(
            "QPushButton { background: #3a2a2a; color: #cc6666; font-size: 10px; "
            "border: 1px solid #5a3a3a; border-radius: 4px; }"
            "QPushButton:hover { background: #4a2a2a; border-color: #cc6666; }"
            "QPushButton:pressed { background: #2a1a1a; }"
        )
        delete_btn.clicked.connect(self.delete_tt_render_layers)
        section_vbox.addWidget(delete_btn)

        layout.addWidget(rl_cs.widget)
        layout.addSpacing(6)

        # ── Render Turntable section ──────────────────────────────────────────
        self._build_render_turntable_section(layout)

        layout.addStretch()

        # Wire Select All / Deselect All
        sel_all_btn.clicked.connect(
            lambda: [ck.setChecked(True) for ck in self._rl_slot_checks]
        )
        sel_none_btn.clicked.connect(
            lambda: [ck.setChecked(False) for ck in self._rl_slot_checks]
        )

        # Populate slot names from current HDRI grid (grid is built before this tab)
        self._refresh_rl_slot_names()
        self._update_render_steps()

    def _refresh_rl_slot_names(self):
        """Sync HDRI slot checkbox labels with current HDRI cell display names."""
        if not self._rl_slot_checks:
            return
        for i, ck in enumerate(self._rl_slot_checks):
            if i < len(self._hdri_cells):
                name = self._hdri_cells[i]._name_lbl.text()
            elif i >= self.HDRI_PRESET_COUNT:
                name = "Custom {}".format(i - self.HDRI_PRESET_COUNT + 1)
            else:
                name = "HDRI {}".format(i + 1)
            ck.setText("  Slot {:02d}   {}".format(i + 1, name))

    def _build_render_turntable_section(self, layout):
        """Build the RENDER TURNTABLE collapsible section in the TURNTABLE tab."""
        try:
            from PySide6 import QtWidgets, QtCore
        except ImportError:
            from PySide2 import QtWidgets, QtCore

        rt_cs = CollapsibleSection("RENDER TURNTABLE", compact=True, icon_name="render", accent="#E070A8")
        rt_cs.set_collapsed(True)
        self._rt_section_frame = rt_cs

        # ── Step 2 header ──────────────────────────────────────────────────────
        row2, self._rl_render_badge, self._rl_render_confirm = self._mk_step_header(
            "2", "RENDER TURNTABLE")
        rt_cs.add_layout(row2)

        info_lbl = QtWidgets.QLabel(
            "Render all TT layers in sequence using the active renderer.")
        info_lbl.setObjectName("hint")
        info_lbl.setWordWrap(True)
        rt_cs.add_widget(info_lbl)
        rt_cs.add_spacing(6)

        # ── Frame range row ───────────────────────────────────────────────────
        fr_row = QtWidgets.QHBoxLayout()
        fr_row.setSpacing(6)

        def _spin_lbl(text):
            l = QtWidgets.QLabel(text)
            l.setStyleSheet(
                "color: #aaaaaa; font-size: 10px; background: transparent; border: none;"
            )
            return l

        fr_row.addWidget(_spin_lbl("Start"))
        self._rt_start_spin = QtWidgets.QSpinBox()
        self._rt_start_spin.setRange(0, 99999)
        self._rt_start_spin.setValue(self.frame_start)
        self._rt_start_spin.setFixedWidth(70)
        fr_row.addWidget(self._rt_start_spin)

        fr_row.addSpacing(8)
        fr_row.addWidget(_spin_lbl("End"))
        self._rt_end_spin = QtWidgets.QSpinBox()
        self._rt_end_spin.setRange(0, 99999)
        self._rt_end_spin.setValue(self.frame_end)
        self._rt_end_spin.setFixedWidth(70)
        fr_row.addWidget(self._rt_end_spin)

        fr_row.addSpacing(8)
        fr_row.addWidget(_spin_lbl("By Frame"))
        self._rt_step_spin = QtWidgets.QSpinBox()
        self._rt_step_spin.setRange(1, 100)
        self._rt_step_spin.setValue(10)   # default: render every 10th frame
        self._rt_step_spin.setFixedWidth(55)
        fr_row.addWidget(self._rt_step_spin)

        fr_row.addStretch()
        rt_cs.add_layout(fr_row)
        rt_cs.add_spacing(8)

        # ── Resolution row ────────────────────────────────────────────────────
        res_row = QtWidgets.QHBoxLayout()
        res_row.setSpacing(6)

        res_lbl = QtWidgets.QLabel("Resolution")
        res_lbl.setStyleSheet(
            "color: #aaaaaa; font-size: 10px; background: transparent; border: none;"
        )
        res_row.addWidget(res_lbl)

        self._rt_res_combo = QtWidgets.QComboBox()
        self._rt_res_combo.addItems(["HD 720  (1280 x 720)", "HD 1080  (1920 x 1080)", "4K  (3840 x 2160)"])
        self._rt_res_combo.setCurrentIndex(1)   # HD 1080 default
        self._rt_res_combo.setMinimumWidth(170)
        res_row.addWidget(self._rt_res_combo)
        res_row.addStretch()
        rt_cs.add_layout(res_row)
        rt_cs.add_spacing(10)

        # ── Save-first reminder — render names derive from the scene file name ──
        save_note = QtWidgets.QLabel(
            "  Save your scene now — render file names are taken from the Maya scene "
            "file name. Save it with the correct name first and every render follows "
            "your naming convention automatically.\n"
            "   Example:   scene  Scion_TT_v003.ma   →   renders  "
            "Scion_TT_v003_RL_hdri_01.####.exr")
        save_note.setObjectName("frameWarn")
        save_note.setWordWrap(True)
        rt_cs.add_widget(save_note)
        rt_cs.add_spacing(10)

        # ── Render button — locked until TT layers exist ──────────────────────
        self._rt_render_btn = QtWidgets.QPushButton("  Render Turntable")
        self._rt_render_btn.setObjectName("btnStepLocked")
        self._rt_render_btn.setMinimumHeight(36)
        self._rt_render_btn.setEnabled(self._tt_layers_exist())
        self._rt_render_btn.clicked.connect(self.render_tt_layers)
        rt_cs.add_widget(self._rt_render_btn)

        layout.addWidget(rt_cs.widget)

    # ─────────────────────────────────────────────────────────────────────────
    # UI state management
    # ─────────────────────────────────────────────────────────────────────────

    def _root_status_text(self):
        if not self.root_folder:
            return "  Status: [!] Not configured"
        if not os.path.isdir(self.root_folder):
            return "  Status: [X] Folder not found — please re-select"
        return "  Status: [OK] {}".format(self.root_folder)

    def _set_scene_status(self, loaded=False, message=None):
        if not self._scene_status_label:
            return
        if message is not None:
            label = message
        elif loaded:
            grp   = self._get_tt_render_grp()
            label = (
                "  ✓  Scene loaded  |  Attach target: {}".format(grp)
                if grp else "  ✓  Scene loaded"
            )
        else:
            label = "  —  Scene: Not loaded"

        self._scene_status_label.setText(label)
        self._scene_status_label.setObjectName("statusOk" if loaded else "statusIdle")
        self._scene_status_label.style().unpolish(self._scene_status_label)
        self._scene_status_label.style().polish(self._scene_status_label)

    def _refresh_ui_state(self):
        """Sync all Qt controls to current root folder validity."""
        valid = self._is_root_valid()

        if self._warning_banner:
            self._warning_banner.setVisible(not valid)

        if self._root_status_label:
            self._root_status_label.setText(self._root_status_text())

        if self._root_field:
            self._root_field.setText(self.root_folder or "")

        _step_btn_set = set(b for b in self._step_btns if b is not None)

        for btn in self._gated_buttons:
            if btn is None:
                continue
            if btn in _step_btn_set:
                idx = self._step_btns.index(btn)
                if idx == 0:
                    btn.setEnabled(valid)
                else:
                    btn.setEnabled(valid and self._step_done[idx - 1])
            else:
                btn.setEnabled(valid)

        # Guided-flow visuals (badges / orange-border / pale-green) follow the
        # same validity + progress state. Each updater is null-guarded so it is
        # safe to call before those sections have been built.
        self._update_prelim_ui()
        self._update_scene_steps()
        self._update_render_steps()

    # ── Guided-flow helpers (shared by Prelim / Scene / Model / Turntable) ─────
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
            {"locked": "btnStepLocked", "active": "btnStepActive", "done": "btnStepDone"}[state]
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

    def _update_prelim_ui(self):
        """Step 1 Root Folder (Browse -> Set -> done); 2 ACES, 3 OpenCV auto-confirm."""
        if self._preliminary_frame is None:
            return
        root_done = self._is_root_valid()
        has_path  = bool(self._root_field and self._root_field.text().strip())

        self._set_badge(self._prelim_root_badge, "done" if root_done else "active")
        self._set_confirm(self._prelim_root_confirm, root_done)
        if root_done:
            self._btn_obj(self._prelim_browse_btn, "")
            self._set_step_btn(self._prelim_set_btn, "done")
        else:
            # Browse leads first, then Set lights up once a path is in the field
            self._btn_obj(self._prelim_browse_btn, "" if has_path else "btnStepActive")
            self._set_step_btn(self._prelim_set_btn, "active" if has_path else "locked")

        aces_ok = self._is_aces_configured()
        self._set_badge(self._prelim_aces_badge, "done" if aces_ok else "active")
        self._set_confirm(self._prelim_aces_confirm, aces_ok)

        cv_ok = self._is_opencv_available()
        self._set_badge(self._prelim_cv_badge, "done" if cv_ok else "active")
        self._set_confirm(self._prelim_cv_confirm, cv_ok)

        self._preliminary_frame.set_state("done" if root_done else "active")

    def _update_scene_steps(self):
        """Section 01: 1 Load Scene -> 2 Apply Frame Range."""
        if self._sc_load_badge is None:
            return
        root_ok      = self._is_root_valid()
        scene_loaded = self._is_turntable_loaded()

        if scene_loaded:
            self._set_badge(self._sc_load_badge, "done")
            self._set_confirm(self._sc_load_confirm, True)
            self._set_step_btn(self._sc_load_btn, "done")
        else:
            st = "active" if root_ok else "locked"
            self._set_badge(self._sc_load_badge, st)
            self._set_confirm(self._sc_load_confirm, False)
            self._set_step_btn(self._sc_load_btn, st)

        if self._frames_applied:
            self._set_badge(self._sc_apply_badge, "done")
            self._set_confirm(self._sc_apply_confirm, True)
            self._set_step_btn(self._sc_apply_btn, "done")
        else:
            st = "active" if scene_loaded else "locked"
            self._set_badge(self._sc_apply_badge, st)
            self._set_confirm(self._sc_apply_confirm, False)
            self._set_step_btn(self._sc_apply_btn, st)

        if self._section1_frame:
            if scene_loaded and self._frames_applied:
                self._section1_frame.set_state("done")
            elif root_ok:
                self._section1_frame.set_state("active")
            else:
                self._section1_frame.set_state("idle")

    def _update_render_steps(self):
        """TURNTABLE tab: 1 Create Render Layers -> 2 Render Turntable."""
        if self._rl_create_badge is None:
            return
        scene_loaded = self._is_turntable_loaded()
        layers       = self._tt_layers_exist()

        if layers:
            self._set_badge(self._rl_create_badge, "done")
            self._set_confirm(self._rl_create_confirm, True)
            self._set_step_btn(self._rl_create_btn, "done")
        else:
            st = "active" if scene_loaded else "locked"
            self._set_badge(self._rl_create_badge, st)
            self._set_confirm(self._rl_create_confirm, False)
            self._set_step_btn(self._rl_create_btn, st)

        if self._rendered and layers:
            self._set_badge(self._rl_render_badge, "done")
            self._set_confirm(self._rl_render_confirm, True)
            self._set_step_btn(self._rt_render_btn, "done")
        else:
            st = "active" if layers else "locked"
            self._set_badge(self._rl_render_badge, st)
            self._set_confirm(self._rl_render_confirm, False)
            self._set_step_btn(self._rt_render_btn, st)

        if self._rl_section_frame:
            if layers:
                self._rl_section_frame.set_state("done")
            elif scene_loaded:
                self._rl_section_frame.set_state("active")
            else:
                self._rl_section_frame.set_state("idle")

        if self._rt_section_frame:
            if self._rendered and layers:
                self._rt_section_frame.set_state("done")
            elif layers:
                self._rt_section_frame.set_state("active")
            else:
                self._rt_section_frame.set_state("idle")

    def _update_model_section_state(self):
        if not self._section2_frame:
            return
        if all(self._step_done):
            self._section2_frame.set_state("done")
        elif self._is_turntable_loaded():
            self._section2_frame.set_state("active")
        else:
            self._section2_frame.set_state("idle")

    def _set_model_mode(self, mode):
        use_sb = (mode == "shader_ball")

        for _b, _act in ((self._model_btn_sb, use_sb),
                         (self._model_btn_own, not use_sb)):
            if _b:
                _b.setObjectName("btnToggleActive" if _act else "btnToggleInactive")
                _b.style().unpolish(_b)
                _b.style().polish(_b)

        if self._shaderball_section:
            self._shaderball_section.setVisible(use_sb)
        if self._own_model_section:
            self._own_model_section.setVisible(not use_sb)

        # Shader ball geometry follows the mode: visible only in Shader Ball
        # mode, hidden in Your Model mode.
        if self._is_turntable_loaded():
            node = self._get_shaderball_grp()
            if node:
                try:
                    cmds.setAttr("{}.visibility".format(node), use_sb)
                except Exception:
                    pass
            for ck in (self._lighting_shaderball_ck, self._sb_main_ck):
                if ck:
                    ck.blockSignals(True)
                    ck.setChecked(use_sb)
                    ck.blockSignals(False)

        _log.info("Model mode → %s", mode)

    def _update_step_ui(self, step_idx, done=False, unlock_next=False):
        try:
            from PySide6 import QtWidgets
        except ImportError:
            from PySide2 import QtWidgets

        # Confirm badge
        confirm = self._step_confirms[step_idx]
        if confirm:
            confirm.setText("✓ done" if done else "")
            confirm.setObjectName("stepConfirmDone" if done else "stepConfirmEmpty")
            confirm.style().unpolish(confirm)
            confirm.style().polish(confirm)

        # Circle badge
        circle = self._step_circles[step_idx]
        if circle:
            circle.setObjectName("stepDone" if done else "stepReady")
            circle.style().unpolish(circle)
            circle.style().polish(circle)
            circle.setText("✓" if done else str(step_idx + 1))

        # Completed step's own button goes dark/done (Capture stays clickable
        # for re-capture; Align/Attach simply read as finished).
        btn = self._step_btns[step_idx]
        if btn:
            btn.setObjectName("btnStepDone" if done else "btnStepActive")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Unlock next step
        if unlock_next and step_idx + 1 < len(self._step_btns):
            nxt = self._step_btns[step_idx + 1]
            if nxt:
                nxt.setEnabled(True)
                nxt.setObjectName("btnStepActive")
                nxt.style().unpolish(nxt)
                nxt.style().polish(nxt)
            nxt_circle = self._step_circles[step_idx + 1]
            if nxt_circle:
                nxt_circle.setObjectName("stepReady")
                nxt_circle.style().unpolish(nxt_circle)
                nxt_circle.style().polish(nxt_circle)

        self._step_done[step_idx] = done

    def _update_hdri_highlight(self, active_index):
        for i, cell in enumerate(self._hdri_cells):
            cell.set_active(i == active_index)

    def _default_hdri_index(self):
        """Default preset slot = the Studio HDRI (detected by name during
        _build_hdri_grid), falling back to the first preset slot (0)."""
        return getattr(self, "_studio_hdri_index", 0)

    def _update_custom_slot_ui(self, slot_index, hdri_path, thumb_path):
        if slot_index >= len(self._hdri_cells):
            return
        cell = self._hdri_cells[slot_index]
        base = os.path.splitext(os.path.basename(hdri_path))[0]
        if thumb_path and os.path.isfile(thumb_path):
            cell.set_preview(thumb_path)
        cell.set_name(base)
        # After loading, clicking selects (not re-browses)
        cell._on_click = lambda si=slot_index: self.select_hdri(si)

    def _advance_to_section(self, section_num):
        mapping = {
            1: self._section1_frame,
            2: self._section2_frame,
            3: self._section3_frame,
        }
        prev = section_num - 1
        if prev in mapping and mapping[prev]:
            mapping[prev].set_collapsed(True)
        target = mapping.get(section_num)
        if target:
            target.set_collapsed(False)
        # Once the full setup is complete (reaching section 3), collapse instructions
        if section_num >= 3 and self._preliminary_frame:
            self._preliminary_frame.set_collapsed(True)

    def _require_scene(self):
        if self._is_turntable_loaded():
            return True
        cmds.confirmDialog(
            title="Scene Not Loaded",
            message=(
                "The TurnTable scene is not loaded.\n\n"
                "Use 'Load Turntable Scene' in Section 01 first."
            ),
            button=["OK"], defaultButton="OK", icon="warning"
        )
        return False

    # ─────────────────────────────────────────────────────────────────────────
    # Root folder operations
    # ─────────────────────────────────────────────────────────────────────────

    def browse_root_folder(self):
        result = cmds.fileDialog2(
            fileMode=3, caption="Select TurnTable Root Folder", okCaption="Select"
        )
        if result:
            path = result[0].replace("\\", "/")
            if self._root_field:
                self._root_field.setText(path)

    def set_root_folder(self):
        if not self._root_field:
            return
        raw = self._root_field.text().strip()
        if not raw:
            cmds.warning("PXL TurnTable: No path entered.")
            return
        path = raw.replace("\\", "/")
        if not os.path.isdir(path):
            cmds.warning("PXL TurnTable: Folder not found — {}".format(path))
            return
        if not os.path.isdir(os.path.join(path, "scenes")):
            cmds.warning(
                "PXL TurnTable: Missing 'scenes' subfolder — "
                "is this the correct TurnTable root?"
            )
            return

        self.root_folder = path
        self._save_config(root_folder=path)
        self._resolve_paths()
        self._refresh_ui_state()
        self._rebuild_hdri_grid()

        if self._prelim_complete() and self._preliminary_frame:
            self._preliminary_frame.set_collapsed(True)

        _log.info("Root folder set: %s", path)

    # ─────────────────────────────────────────────────────────────────────────
    # Turntable scene
    # ─────────────────────────────────────────────────────────────────────────

    def _is_turntable_loaded(self):
        for ref in (cmds.ls(type="reference") or []):
            try:
                if self.TT_SCENE_FILENAME in cmds.referenceQuery(ref, filename=True):
                    return True
            except Exception:
                continue
        return False

    def _get_tt_render_grp(self):
        primary = "{}:mainModel_grp".format(self.TT_NAMESPACE)
        if cmds.objExists(primary):
            return primary
        candidates = cmds.ls("*:mainModel_grp") or []
        return candidates[0] if candidates else None

    def _get_switch_node(self):
        primary = "{}:aiSwitchHDRI".format(self.TT_NAMESPACE)
        if cmds.objExists(primary):
            return primary
        candidates = cmds.ls("*:aiSwitchHDRI") or []
        return candidates[0] if candidates else None

    def _get_tt_charts_grp(self):
        """charts_grp under _TT_setup_grp — hidden by default, used for turntable chart renders."""
        ns = self._get_active_namespace()
        if not ns:
            return None
        path = "|{ns}:TT_SCENE_grp|{ns}:_TT_setup_grp|{ns}:charts_grp".format(ns=ns)
        return path if cmds.objExists(path) else None

    def _get_tt_sky_dome_transform(self):
        """Transform node for the aiSkyDome_HDRI light."""
        ns = self._get_active_namespace()
        if not ns:
            return None
        path = "|{ns}:TT_SCENE_grp|{ns}:lights_grp|{ns}:aiSkyDome_HDRI".format(ns=ns)
        return path if cmds.objExists(path) else None

    # ─────────────────────────────────────────────────────────────────────────
    # Utilities-group node helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _get_util_charts(self):
        ns = self._get_active_namespace()
        if not ns:
            return None
        path = "|{ns}:TT_SCENE_grp|{ns}:utilities_grp|{ns}:charts_grp".format(ns=ns)
        return path if cmds.objExists(path) else None

    def _get_shaderball_grp(self):
        ns = self._get_active_namespace()
        if not ns:
            return None
        path = "|{ns}:TT_SCENE_grp|{ns}:utilities_grp|{ns}:shaderBall_grp".format(ns=ns)
        return path if cmds.objExists(path) else None

    def _get_scalemove_grp(self):
        ns = self._get_active_namespace()
        if not ns:
            return None
        path = (
            "|{ns}:TT_SCENE_grp|{ns}:utilities_grp"
            "|{ns}:charts_grp|{ns}:scaleMove_GRP"
        ).format(ns=ns)
        return path if cmds.objExists(path) else None

    def _get_util_macbeth(self):
        ns = self._get_active_namespace()
        if not ns:
            return None
        path = (
            "|{ns}:TT_SCENE_grp|{ns}:utilities_grp"
            "|{ns}:charts_grp|{ns}:scaleMove_GRP|{ns}:macbeth_grp"
        ).format(ns=ns)
        return path if cmds.objExists(path) else None

    def _get_util_refball(self):
        ns = self._get_active_namespace()
        if not ns:
            return None
        path = (
            "|{ns}:TT_SCENE_grp|{ns}:utilities_grp"
            "|{ns}:charts_grp|{ns}:scaleMove_GRP|{ns}:refBall_grp"
        ).format(ns=ns)
        return path if cmds.objExists(path) else None

    def _get_cloth_geo(self):
        ns = self._get_active_namespace()
        if not ns:
            return None
        path = (
            "|{ns}:TT_SCENE_grp|{ns}:utilities_grp"
            "|{ns}:shaderBall_grp|{ns}:cloth_geo"
        ).format(ns=ns)
        if cmds.objExists(path):
            return path
        candidates = cmds.ls("*:cloth_geo") or []
        return candidates[0] if candidates else None

    def _get_liquid_geo(self):
        ns = self._get_active_namespace()
        if not ns:
            return None
        path = (
            "|{ns}:TT_SCENE_grp|{ns}:utilities_grp"
            "|{ns}:shaderBall_grp|{ns}:liquid_geo"
        ).format(ns=ns)
        if cmds.objExists(path):
            return path
        candidates = cmds.ls("*:liquid_geo") or []
        return candidates[0] if candidates else None

    # ─────────────────────────────────────────────────────────────────────────
    # Lighting / visibility (Section 3)
    # ─────────────────────────────────────────────────────────────────────────

    def toggle_charts(self, state):
        if not self._require_scene():
            if self._lighting_charts_ck:
                self._lighting_charts_ck.blockSignals(True)
                self._lighting_charts_ck.setChecked(not state)
                self._lighting_charts_ck.blockSignals(False)
            return
        node = self._get_util_charts()
        if not node:
            _log.warning("charts_grp not found.")
            return
        cmds.setAttr("{}.visibility".format(node), bool(state))

    def toggle_shaderball(self, state):
        if not self._require_scene():
            if self._lighting_shaderball_ck:
                self._lighting_shaderball_ck.blockSignals(True)
                self._lighting_shaderball_ck.setChecked(not state)
                self._lighting_shaderball_ck.blockSignals(False)
            return
        node = self._get_shaderball_grp()
        if not node:
            _log.warning("shaderBall_grp not found.")
            return
        cmds.setAttr("{}.visibility".format(node), bool(state))
        if self._sb_main_ck:
            self._sb_main_ck.blockSignals(True)
            self._sb_main_ck.setChecked(bool(state))
            self._sb_main_ck.blockSignals(False)

    def toggle_shaderball_viz(self, state):
        if not self._require_scene():
            if self._sb_main_ck:
                self._sb_main_ck.blockSignals(True)
                self._sb_main_ck.setChecked(not state)
                self._sb_main_ck.blockSignals(False)
            return
        node = self._get_shaderball_grp()
        if not node:
            _log.warning("shaderBall_grp not found.")
            return
        cmds.setAttr("{}.visibility".format(node), bool(state))
        if self._lighting_shaderball_ck:
            self._lighting_shaderball_ck.blockSignals(True)
            self._lighting_shaderball_ck.setChecked(bool(state))
            self._lighting_shaderball_ck.blockSignals(False)

    def toggle_cloth_viz(self, state):
        if not self._require_scene():
            if self._sb_cloth_ck:
                self._sb_cloth_ck.blockSignals(True)
                self._sb_cloth_ck.setChecked(not state)
                self._sb_cloth_ck.blockSignals(False)
            return
        node = self._get_cloth_geo()
        if not node:
            _log.warning("cloth_geo not found.")
            return
        cmds.setAttr("{}.visibility".format(node), bool(state))

    def toggle_liquid_viz(self, state):
        if not self._require_scene():
            if self._sb_liquid_ck:
                self._sb_liquid_ck.blockSignals(True)
                self._sb_liquid_ck.setChecked(not state)
                self._sb_liquid_ck.blockSignals(False)
            return
        node = self._get_liquid_geo()
        if not node:
            _log.warning("liquid_geo not found.")
            return
        cmds.setAttr("{}.visibility".format(node), bool(state))

    def toggle_model_viz(self, state):
        if not self._require_scene():
            if self._lighting_model_ck:
                self._lighting_model_ck.blockSignals(True)
                self._lighting_model_ck.setChecked(not state)
                self._lighting_model_ck.blockSignals(False)
            return
        if not self.captured_nodes:
            return
        for node in self.captured_nodes:
            if cmds.objExists(node):
                try:
                    cmds.setAttr("{}.visibility".format(node), bool(state))
                except Exception as exc:
                    _log.warning("Could not set visibility on %s: %s", node, exc)

    def set_charts_scale(self, value):
        if not self._is_turntable_loaded():
            return
        for get_fn in (self._get_util_macbeth, self._get_util_refball):
            node = get_fn()
            if not node:
                continue
            for ax in ("sx", "sy", "sz"):
                try:
                    cmds.setAttr("{}.{}".format(node, ax), value)
                except Exception as exc:
                    _log.warning("Could not set %s.%s: %s", node, ax, exc)

    def set_macbeth_x(self, value):
        if not self._is_turntable_loaded():
            return
        node = self._get_util_macbeth()
        if not node:
            return
        try:
            cmds.setAttr("{}.translateX".format(node), value)
        except Exception as exc:
            _log.warning("Could not set macbeth translateX: %s", exc)

    def set_refball_x(self, value):
        if not self._is_turntable_loaded():
            return
        node = self._get_util_refball()
        if not node:
            return
        try:
            cmds.setAttr("{}.translateX".format(node), value)
        except Exception as exc:
            _log.warning("Could not set refBall translateX: %s", exc)

    def set_macbeth_y(self, value):
        if not self._is_turntable_loaded():
            return
        node = self._get_util_macbeth()
        if not node:
            return
        try:
            cmds.setAttr("{}.translateY".format(node), value)
        except Exception as exc:
            _log.warning("Could not set macbeth translateY: %s", exc)

    def set_refball_y(self, value):
        if not self._is_turntable_loaded():
            return
        node = self._get_util_refball()
        if not node:
            return
        try:
            cmds.setAttr("{}.translateY".format(node), value)
        except Exception as exc:
            _log.warning("Could not set refBall translateY: %s", exc)

    def _sync_ui_from_scene(self):
        """Read live scene values and update all UI controls to match.
        Called after scene load and after session restore.
        """
        ns = self._get_active_namespace() or self.TT_NAMESPACE

        # Grid unit — read aiSwitchMeasures.index: 0=mt, 1=cm
        sw_meas = "{}:aiSwitchMeasures".format(ns)
        if cmds.objExists(sw_meas):
            try:
                idx = int(cmds.getAttr("{}.index".format(sw_meas)))
                self._update_grid_unit_ui("mt" if idx == 1 else "cm")
            except Exception as exc:
                _log.warning("_sync_ui_from_scene (aiSwitchMeasures): %s", exc)

        # Backdrop mode — read utilities_grp/ENV_grp visibility
        util_env = "|{0}:TT_SCENE_grp|{0}:utilities_grp|{0}:ENV_grp".format(ns)
        if cmds.objExists(util_env):
            try:
                limbo_vis = cmds.getAttr("{}.visibility".format(util_env))
                self._update_backdrop_ui("limbo" if bool(limbo_vis) else "hdri")
            except Exception as exc:
                _log.warning("_sync_ui_from_scene (backdrop): %s", exc)

        # Floor Grid checkbox — read aiSwitchBackdrop.index
        sw_bd2 = "{}:aiSwitchBackdrop".format(ns)
        if cmds.objExists(sw_bd2) and self._lighting_floor_grid_ck:
            try:
                bd_idx = int(cmds.getAttr("{}.index".format(sw_bd2)))
                self._lighting_floor_grid_ck.blockSignals(True)
                self._lighting_floor_grid_ck.setChecked(bd_idx == 1)
                self._lighting_floor_grid_ck.blockSignals(False)
            except Exception as exc:
                _log.warning("_sync_ui_from_scene (floor_grid): %s", exc)

        # ShaderBall visibility — read scene node, sync both checkboxes
        sb_grp_path = self._get_shaderball_grp()
        if sb_grp_path:
            try:
                sb_vis = bool(cmds.getAttr("{}.visibility".format(sb_grp_path)))
                for _ck in (self._lighting_shaderball_ck, self._sb_main_ck):
                    if _ck:
                        _ck.blockSignals(True)
                        _ck.setChecked(sb_vis)
                        _ck.blockSignals(False)
            except Exception as exc:
                _log.warning("_sync_ui_from_scene (shaderball): %s", exc)

        # Macbeth position
        macbeth = self._get_util_macbeth()
        if macbeth:
            try:
                tx = cmds.getAttr("{}.translateX".format(macbeth))
                ty = cmds.getAttr("{}.translateY".format(macbeth))
                if self._macbeth_x_slider:
                    self._macbeth_x_slider.set_value(tx)
                if self._macbeth_y_slider:
                    self._macbeth_y_slider.set_value(ty)
            except Exception as exc:
                _log.warning("_sync_ui_from_scene (macbeth): %s", exc)

        # Ref Ball position
        refball = self._get_util_refball()
        if refball:
            try:
                tx = cmds.getAttr("{}.translateX".format(refball))
                ty = cmds.getAttr("{}.translateY".format(refball))
                if self._refball_x_slider:
                    self._refball_x_slider.set_value(tx)
                if self._refball_y_slider:
                    self._refball_y_slider.set_value(ty)
            except Exception as exc:
                _log.warning("_sync_ui_from_scene (refball): %s", exc)

        # HDRI domelight rotation
        if self._hdri_rotation_slider:
            shapes = cmds.ls(type="aiSkyDomeLight") or []
            if not shapes:
                shapes = cmds.ls("{}:*".format(ns), type="aiSkyDomeLight") or []
            if shapes:
                try:
                    parents = cmds.listRelatives(shapes[0], parent=True, fullPath=True) or []
                    if parents:
                        ry = cmds.getAttr("{}.rotateY".format(parents[0]))
                        self._hdri_rotation_slider.set_value(ry)
                except Exception as exc:
                    _log.warning("_sync_ui_from_scene (hdri_rotation): %s", exc)

    def set_hdri_rotation(self, val):
        """Rotate the aiSkyDomeLight Y axis to reposition the HDRI environment image."""
        if not self._is_turntable_loaded():
            return
        shapes = cmds.ls(type="aiSkyDomeLight") or []
        if not shapes:
            ns = self._get_active_namespace() or self.TT_NAMESPACE
            shapes = cmds.ls("{}:*".format(ns), type="aiSkyDomeLight") or []
        if not shapes:
            _log.warning("set_hdri_rotation: no aiSkyDomeLight found in scene")
            return
        try:
            parents = cmds.listRelatives(shapes[0], parent=True, fullPath=True) or []
            if parents:
                cmds.setAttr("{}.rotateY".format(parents[0]), val)
        except Exception as exc:
            _log.warning("set_hdri_rotation failed: %s", exc)

    def set_backdrop(self, mode):
        """Switch backdrop mode.
        "hdri"  → _TT_setup_grp/ENV_grp visible, utilities_grp/ENV_grp hidden.
        "limbo" → utilities_grp/ENV_grp visible, _TT_setup_grp/ENV_grp hidden.
                  aiSwitchBackdrop.index honoured (0=white, 1=grid per floor_grid toggle).
        """
        if not self._require_scene():
            return
        ns = self._get_active_namespace() or self.TT_NAMESPACE
        util_env  = "|{0}:TT_SCENE_grp|{0}:utilities_grp|{0}:ENV_grp".format(ns)
        setup_env = "|{0}:TT_SCENE_grp|{0}:_TT_setup_grp|{0}:ENV_grp".format(ns)
        is_hdri = (mode == "hdri")
        for node, vis in ((setup_env, is_hdri), (util_env, not is_hdri)):
            if cmds.objExists(node):
                try:
                    cmds.setAttr("{}.visibility".format(node), vis)
                except Exception as exc:
                    _log.warning("set_backdrop %s: %s", node, exc)
            else:
                _log.warning("set_backdrop: node not found — %s", node)
        self._update_backdrop_ui(mode)

    def _update_backdrop_ui(self, active_mode):
        """Refresh HDRI / LIMBO button styles to reflect active mode."""
        for btn, mode in (
            (self._backdrop_btn_hdri, "hdri"),
            (self._backdrop_btn_limbo, "limbo"),
        ):
            if btn is None:
                continue
            name = "btnToggleActive" if mode == active_mode else "btnToggleInactive"
            btn.setObjectName(name)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def toggle_floor_grid(self, state):
        """Floor Grid ON  → aiSwitchBackdrop.index = 1 (measurement grid on limbo).
        Floor Grid OFF → aiSwitchBackdrop.index = 0 (white/grey limbo).
        Only has a visible effect when LIMBO backdrop is active.
        """
        if not self._require_scene():
            if self._lighting_floor_grid_ck:
                self._lighting_floor_grid_ck.blockSignals(True)
                self._lighting_floor_grid_ck.setChecked(not state)
                self._lighting_floor_grid_ck.blockSignals(False)
            return
        ns = self._get_active_namespace() or self.TT_NAMESPACE
        sw_node = "{}:aiSwitchBackdrop".format(ns)
        if cmds.objExists(sw_node):
            try:
                cmds.setAttr("{}.index".format(sw_node), 1 if state else 0)
            except Exception as exc:
                _log.warning("toggle_floor_grid: %s", exc)
        else:
            _log.warning("toggle_floor_grid: aiSwitchBackdrop not found in ns %s", ns)

    def open_arnold_renderview(self):
        """Open the Arnold RenderView panel."""
        import maya.mel as mel
        try:
            mel.eval('arnoldRenderView')
        except Exception as exc:
            cmds.warning("PXL TurnTable: Could not open Arnold RenderView — {}".format(exc))

    def render_with_arnold(self):
        """Render all frames through RenderView (play sequence behavior)."""
        import maya.mel as mel
        try:
            mel.eval('renderWindowRender renderSequence renderView;')
        except Exception as exc:
            cmds.warning("PXL TurnTable: Render failed — {}".format(exc))

    def toggle_denoiser(self, state):
        """Enable/disable the scene's OptiX denoiser imager (aiImagerDenoiserOptix)."""
        nodes = cmds.ls(type="aiImagerDenoiserOptix") or []
        if not nodes:
            cmds.warning(
                "PXL TurnTable: OptiX denoiser not found — load the turntable scene first."
            )
            return
        for n in nodes:
            try:
                cmds.setAttr("{}.enable".format(n), bool(state))
            except Exception as exc:
                _log.warning("Could not toggle denoiser '%s': %s", n, exc)
        _log.info("OptiX denoiser %s", "enabled" if state else "disabled")

    def toggle_size_ref_cubes(self, state):
        """Show/hide size-ref cubes.
        Off  → sizeRef_grp hidden (both cubes off).
        On   → sizeRef_grp shown, then enforce current grid unit:
               1mt active → cube_1mt_REF on,  cube_10cm_REF off.
               cm  active → cube_10cm_REF on, cube_1mt_REF off.
        """
        if not self._require_scene():
            if self._lighting_size_ref_ck:
                self._lighting_size_ref_ck.blockSignals(True)
                self._lighting_size_ref_ck.setChecked(not state)
                self._lighting_size_ref_ck.blockSignals(False)
            return
        ns = self._get_active_namespace() or self.TT_NAMESPACE
        grp = "{}:sizeRef_grp".format(ns)
        if cmds.objExists(grp):
            try:
                cmds.setAttr("{}.visibility".format(grp), bool(state))
            except Exception as exc:
                _log.warning("toggle_size_ref_cubes (grp): %s", exc)
        else:
            _log.warning("toggle_size_ref_cubes: sizeRef_grp not found in namespace %s", ns)

        if state:
            # Determine the active grid unit from button state (default: mt)
            active_unit = "cm" if (
                self._grid_btn_cm and
                self._grid_btn_cm.objectName() == "btnToggleActive"
            ) else "mt"
            cube_mt = "{}:cube_1mt_REF".format(ns)
            cube_cm = "{}:cube_10cm_REF".format(ns)
            for cube, vis in ((cube_mt, active_unit == "mt"),
                              (cube_cm, active_unit == "cm")):
                if cmds.objExists(cube):
                    try:
                        cmds.setAttr("{}.visibility".format(cube), bool(vis))
                    except Exception as exc:
                        _log.warning("toggle_size_ref_cubes (cube %s): %s", cube, exc)

    def set_grid_unit(self, unit):
        """Switch grid texture unit and matching size-reference cube.
        'mt' → aiSwitchMeasures.index=0 (1mt grid),  cube_1mt_REF visible,  cube_10cm_REF hidden.
        'cm' → aiSwitchMeasures.index=1 (10cm grid), cube_10cm_REF visible, cube_1mt_REF hidden.
        """
        if not self._require_scene():
            return
        ns = self._get_active_namespace() or self.TT_NAMESPACE

        # Drive aiSwitchMeasures.index directly (expression2 removed in v003 scene)
        sw_meas = "{}:aiSwitchMeasures".format(ns)
        if cmds.objExists(sw_meas):
            try:
                cmds.setAttr("{}.index".format(sw_meas), 1 if unit == "mt" else 0)
            except Exception as exc:
                _log.warning("set_grid_unit (aiSwitchMeasures): %s", exc)
        else:
            _log.warning("set_grid_unit: aiSwitchMeasures not found in namespace %s", ns)

        # Show matching size-reference cube, hide the other
        cube_mt = "{0}:cube_1mt_REF".format(ns)
        cube_cm = "{0}:cube_10cm_REF".format(ns)
        for node, vis in ((cube_mt, unit == "mt"), (cube_cm, unit == "cm")):
            if cmds.objExists(node):
                try:
                    cmds.setAttr("{}.visibility".format(node), bool(vis))
                except Exception as exc:
                    _log.warning("set_grid_unit (cube %s): %s", node, exc)

        self._update_grid_unit_ui(unit)

    def _update_grid_unit_ui(self, active_unit):
        for btn, unit in ((self._grid_btn_mt, "mt"), (self._grid_btn_cm, "cm")):
            if btn is None:
                continue
            name = "btnToggleActive" if unit == active_unit else "btnToggleInactive"
            btn.setObjectName(name)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # ─────────────────────────────────────────────────────────────────────────
    # Viewport helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _switch_viewport_to_main_cam(self):
        cam_candidates = (
            cmds.ls("{}:main_CAM".format(self.TT_NAMESPACE)) or
            cmds.ls("*:main_CAM")
        )
        if not cam_candidates:
            return
        cam = cam_candidates[0]

        # Resolve the VISIBLE viewport (not getPanel('modelPanel')[0], which is
        # creation order and can be a hidden panel) and promote it to active view.
        target_panel = self._resolve_visible_model_panel()
        if not target_panel:
            return
        try:
            editor = cmds.modelPanel(target_panel, query=True, modelEditor=True)
            cmds.modelEditor(editor, edit=True, activeView=True)
            cmds.lookThru(target_panel, cam)
        except Exception as exc:
            _log.warning("Viewport switch failed: %s", exc)
            return

        try:
            shapes    = cmds.listRelatives(cam, shapes=True) or []
            cam_shape = shapes[0] if shapes else cam
            cmds.setAttr("{}.displayResolution".format(cam_shape), 1)
            cmds.setAttr("{}.displayFilmGate".format(cam_shape), 0)
            cmds.setAttr("{}.displayGateMask".format(cam_shape), 0)
        except Exception:
            pass

        try:
            cmds.modelEditor(target_panel, edit=True, grid=False)
        except Exception:
            pass

        # Frame on shaderBall_grp — main_CAM is the shaderBall camera
        active_ns = self._get_active_namespace() or self.TT_NAMESPACE
        sb_grp = "{}:shaderBall_grp".format(active_ns)
        fallback_grp = "{}:TT_SCENE_grp".format(active_ns)
        fit_target = sb_grp if cmds.objExists(sb_grp) else fallback_grp
        try:
            prev_sel = cmds.ls(selection=True)
            if cmds.objExists(fit_target):
                cmds.select(fit_target)
            cmds.viewFit(target_panel, fitFactor=0.85)
            if prev_sel:
                cmds.select(prev_sel)
            else:
                cmds.select(clear=True)
        except Exception as exc:
            _log.warning("viewFit failed: %s", exc)

    def _resolve_visible_model_panel(self):
        """Return the modelPanel the user is ACTUALLY looking at.

        Focus is unreliable from a Qt button (focus is on the widget), and
        getPanel(type='modelPanel')[0] is CREATION order — not visibility — so it can
        return a hidden panel. Resolve: underPointer -> withFocus -> first VISIBLE
        modelPanel. (Verified against Autodesk forums + the maya-capture reference.)"""
        p = cmds.getPanel(underPointer=True)
        if p and cmds.getPanel(typeOf=p) == "modelPanel":
            return p
        p = cmds.getPanel(withFocus=True)
        if p and cmds.getPanel(typeOf=p) == "modelPanel":
            return p
        visible = cmds.getPanel(visiblePanels=True) or []
        model_panels = [v for v in visible if cmds.getPanel(typeOf=v) == "modelPanel"]
        if model_panels:
            return model_panels[0]
        all_model = cmds.getPanel(type="modelPanel") or []
        return all_model[0] if all_model else None

    def _frame_main_cam_to_asset(self, fit_factor=0.8):
        """Switch the VISIBLE viewport to main_CAM and frame the captured asset's
        bounding box with ~10% breathing room top/bottom.

        Verified fix — the earlier attempts had two real bugs:
          - they targeted getPanel('modelPanel')[0] (CREATION order), so the camera
            switch hit a HIDDEN panel while the user stayed on 'top'. Now we resolve
            the VISIBLE panel and promote it to the ACTIVE view via
            modelEditor(activeView=True) instead of trusting Qt focus;
          - viewFit's FIRST POSITIONAL ARG IS A CAMERA, not a panel — passing the
            panel (what the old code did) silently mis-fit. Now we pass the camera.
        fitFactor 0.8 => asset fills ~80% of the frame (≈10% top/bottom)."""
        targets = [n for n in (self.captured_nodes or []) if cmds.objExists(n)]
        if not targets:
            targets = [l for l in (self._user_rig_locators or []) if cmds.objExists(l)]
        if not targets:
            cmds.warning("PXL TurnTable: frame skipped — no captured model found.")
            return

        cam_candidates = (
            cmds.ls("{}:main_CAM".format(self.TT_NAMESPACE)) or cmds.ls("*:main_CAM")
        )
        if not cam_candidates:
            cmds.warning("PXL TurnTable: frame skipped — main_CAM not found.")
            return
        cam = cam_candidates[0]

        panel = self._resolve_visible_model_panel()
        if not panel:
            cmds.warning("PXL TurnTable: frame skipped — no visible 3D viewport.")
            return

        try:
            prev_sel = cmds.ls(selection=True)
            # 1) Promote this panel to the ACTIVE view (don't rely on Qt focus).
            editor = cmds.modelPanel(panel, query=True, modelEditor=True)
            cmds.modelEditor(editor, edit=True, activeView=True)
            # 2) Switch the camera. lookThru takes the PANEL + cam (transform/shape).
            cmds.lookThru(panel, cam)
            cmds.refresh(force=True)
            # 3) Frame — pass the CAMERA to viewFit (NOT the panel; first arg = camera).
            cmds.select(targets, replace=True)
            cmds.viewFit(cam, fitFactor=fit_factor)
            if prev_sel:
                cmds.select(prev_sel, replace=True)
            else:
                cmds.select(clear=True)
            cmds.inViewMessage(
                amg="TurnTable: viewport set to <hl>main_CAM</hl>, framed on your model.",
                pos="midCenter", fade=True)
            _log.info("Framed main_CAM (panel=%s, editor=%s, cam=%s, %d nodes, fit=%.2f)",
                      panel, editor, cam, len(targets), fit_factor)
        except Exception as exc:
            cmds.warning("PXL TurnTable: frame failed — {}".format(exc))
            _log.warning("Frame to asset failed: %s", exc)

    # ─────────────────────────────────────────────────────────────────────────
    # Load scene
    # ─────────────────────────────────────────────────────────────────────────

    def _remap_textures_to_root(self):
        # Anchor-based path remap, scoped to the turntable reference ONLY.
        # The .ma may have absolute paths baked in from another machine; this
        # rewrites file/aiImage nodes that belong to the turntable namespace
        # so they resolve under self.root_folder. Nodes outside that namespace
        # — the user's own assets, with their own materials and local-disk
        # textures — are never touched. Idempotent, UDIM-safe.
        if not self.root_folder:
            return

        ns = self._get_active_namespace() or self.TT_NAMESPACE
        if not ns:
            _log.info("PXL TurnTable: no turntable namespace resolved; "
                      "texture remap skipped.")
            return
        ns_prefix = ns + ":"

        root = self.root_folder.replace("\\", "/").rstrip("/")

        # Longest-first so 'sourceimages/HDRIs' wins over 'sourceimages'.
        ANCHORS = (
            "sourceimages/HDRIs/preview",
            "sourceimages/HDRIs/previews",
            "sourceimages/HDRIs",
            "sourceimages/shaders",
            "sourceimages/utilities",
            "sourceimages",
            "scenes",
            "presets",
        )
        TARGETS = (
            ("file",    "fileTextureName"),
            ("aiImage", "filename"),
        )

        remapped = 0
        skipped_missing = 0
        for node_type, attr in TARGETS:
            all_of_type = cmds.ls(type=node_type) or []
            # Scope: only nodes inside the turntable namespace (covers
            # nested sub-namespaces under it as well).
            scoped = [n for n in all_of_type if n.startswith(ns_prefix)]
            for node in scoped:
                try:
                    current = cmds.getAttr("{}.{}".format(node, attr)) or ""
                except Exception:
                    continue
                if not current:
                    continue
                cur_norm  = current.replace("\\", "/")
                cur_lower = cur_norm.lower()

                new_path = None
                for anchor in ANCHORS:
                    a_lower = anchor.lower()
                    idx = cur_lower.find("/" + a_lower + "/")
                    if idx >= 0:
                        rel = cur_norm[idx + 1:]  # keep anchor + tail
                        new_path = "{}/{}".format(root, rel)
                        break
                    if cur_lower.startswith(a_lower + "/"):
                        new_path = "{}/{}".format(root, cur_norm)
                        break
                if not new_path or new_path == cur_norm:
                    continue
                try:
                    cmds.setAttr("{}.{}".format(node, attr),
                                 new_path, type="string")
                    remapped += 1
                    if not os.path.isfile(new_path.replace("<UDIM>", "1001")):
                        skipped_missing += 1
                except Exception as exc:
                    _log.warning("Texture remap failed on %s: %s", node, exc)

        if skipped_missing:
            _log.warning("PXL TurnTable: %d remapped path(s) do not "
                         "exist on disk under %s — check sourceimages/ layout.",
                         skipped_missing, root)
        _log.info("PXL TurnTable: remapped %d texture path(s) in "
                  "namespace '%s' under %s", remapped, ns, root)

    def load_turntable_scene(self):
        if not self._is_root_valid():
            cmds.warning("PXL TurnTable: Set the root folder first.")
            return
        if not (self.scene_path and os.path.isfile(self.scene_path)):
            cmds.warning(
                "PXL TurnTable: Scene file not found — {}".format(self.scene_path)
            )
            return
        if self._is_turntable_loaded():
            cmds.warning("PXL TurnTable: Scene is already referenced.")
            return

        try:
            cmds.file(
                self.scene_path, reference=True,
                namespace=self.TT_NAMESPACE,
                mergeNamespacesOnClash=False,
                returnNewNodes=True
            )
        except Exception as exc:
            _log.error("Scene load failed: %s", exc)
            cmds.warning("PXL TurnTable: Load failed — {}".format(exc))
            return

        # Texture paths baked into the .ma may be absolute from another
        # machine — rewrite them under the active root_folder before anything
        # else inspects the scene.
        self._remap_textures_to_root()

        self._set_scene_status(loaded=True)

        # Your Model is the default mode — hide the shader ball geometry on
        # load. It only appears when the user switches to Shader Ball mode.
        active_ns = self._get_active_namespace() or self.TT_NAMESPACE
        sb_grp = "{}:shaderBall_grp".format(active_ns)
        if cmds.objExists(sb_grp):
            try:
                cmds.setAttr("{}.visibility".format(sb_grp), False)
            except Exception:
                pass

        # OptiX denoiser OFF by default on load (matches the unchecked UI toggle)
        for dn in (cmds.ls(type="aiImagerDenoiserOptix") or []):
            try:
                cmds.setAttr("{}.enable".format(dn), False)
            except Exception:
                pass
        if self._denoiser_ck:
            self._denoiser_ck.blockSignals(True)
            self._denoiser_ck.setChecked(False)
            self._denoiser_ck.blockSignals(False)

        # Ensure size ref cubes are hidden on fresh load (off by default)
        sizeref_grp = "{}:sizeRef_grp".format(active_ns)
        if cmds.objExists(sizeref_grp):
            try:
                cmds.setAttr("{}.visibility".format(sizeref_grp), False)
            except Exception:
                pass

        # Default: LIMBO backdrop visible, floor geo hidden
        #          Floor Grid ON (measurements mode) = aiSwitchBackdrop.index = 1
        util_env  = "|{0}:TT_SCENE_grp|{0}:utilities_grp|{0}:ENV_grp".format(active_ns)
        setup_env = "|{0}:TT_SCENE_grp|{0}:_TT_setup_grp|{0}:ENV_grp".format(active_ns)
        for node, vis in ((util_env, True), (setup_env, False)):
            if cmds.objExists(node):
                try:
                    cmds.setAttr("{}.visibility".format(node), vis)
                except Exception:
                    pass
        sw_bd = "{}:aiSwitchBackdrop".format(active_ns)
        if cmds.objExists(sw_bd):
            try:
                cmds.setAttr("{}.index".format(sw_bd), 1)  # Floor Grid ON
            except Exception:
                pass
        # Default unit: 1mt (aiSwitchMeasures.index=1 per user spec: 0=CM, 1=MT)
        sw_meas = "{}:aiSwitchMeasures".format(active_ns)
        if cmds.objExists(sw_meas):
            try:
                cmds.setAttr("{}.index".format(sw_meas), 1)
            except Exception:
                pass

        # Sync UI to match scene defaults (shader ball checked = visible)
        for _ck in (self._lighting_shaderball_ck, self._sb_main_ck):
            if _ck:
                _ck.blockSignals(True)
                _ck.setChecked(True)
                _ck.blockSignals(False)

        self._switch_viewport_to_main_cam()
        self._rebuild_hdri_grid()
        self._sync_ui_from_scene()
        # Default starting HDRI = Studio (applied to the scene + orange-selected).
        try:
            self.select_hdri(self._default_hdri_index())
        except Exception as _exc:
            _log.warning("Default Studio HDRI selection failed: %s", _exc)
        self._advance_to_section(1)
        # Guided-flow: Step 1 done -> Apply lights up; Model/Render unlock
        self._update_scene_steps()
        self._update_render_steps()
        self._update_model_section_state()

    # ─────────────────────────────────────────────────────────────────────────
    # Frame range
    # ─────────────────────────────────────────────────────────────────────────

    def apply_frame_range(self):
        if not self._require_scene():
            return
        if not self._start_frame_field:
            return

        start = self._start_frame_field.value()
        end   = self._end_frame_field.value()

        if end <= start:
            cmds.warning("PXL TurnTable: End frame must be greater than start frame.")
            return

        cmds.playbackOptions(
            min=start, max=end,
            animationStartTime=start, animationEndTime=end
        )
        cmds.currentTime(start)
        self._create_locator_animation(start, end)

        self.frame_start = start
        self.frame_end   = end
        self._save_config(frame_start=start, frame_end=end)
        _log.info("Frame range applied: %d – %d", start, end)
        self._frames_applied = True
        self._advance_to_section(2)
        # Guided-flow: Step 2 done -> Section 01 complete (pale green)
        self._update_scene_steps()

    def _get_active_namespace(self):
        if cmds.ls("{}:*".format(self.TT_NAMESPACE)):
            return self.TT_NAMESPACE
        for node_suffix in ("asset_ROT", "lights_ROT", "mainModel_grp", "TT_SCENE_grp"):
            candidates = cmds.ls("*:{}".format(node_suffix)) or []
            if candidates:
                return candidates[0].rsplit(":", 1)[0]
        return None

    def _create_locator_animation(self, new_start, new_end):
        active_ns = self._get_active_namespace()
        if not active_ns:
            cmds.warning("PXL TurnTable: Load the scene before applying frame range.")
            return

        midpoint = new_start + (new_end - new_start) // 2
        locator_specs = [
            ("asset_ROT",  new_start,    midpoint),
            ("lights_ROT", midpoint + 1, new_end),
        ]
        for suffix, t_start, t_end in locator_specs:
            node = "{}:{}".format(active_ns, suffix)
            if not cmds.objExists(node):
                continue
            cmds.cutKey(node, attribute="rotateY", clear=True,
                        option="keys", time=(-100000, 100000))
            cmds.setKeyframe(node, attribute="rotateY", time=t_start, value=0.0,
                             inTangentType="linear", outTangentType="linear")
            cmds.setKeyframe(node, attribute="rotateY", time=t_end, value=360.0,
                             inTangentType="linear", outTangentType="linear")

    # ─────────────────────────────────────────────────────────────────────────
    # Render layer pipeline (TURNTABLE tab)
    # ─────────────────────────────────────────────────────────────────────────

    def create_tt_render_layers(self):
        """Create legacy render layers for the turntable pipeline.

        For each selected HDRI slot:
          RL_hdri_XX   — mainModel_grp + ENV_grp (vis ON) + aiSkyDome_HDRI + main_CAM
                         Override: aiSwitchHDRI.index = slot, ENV_grp.visibility = 1
                         XX = slot_idx + 1 (e.g. slot 0 → RL_hdri_01, slot 2 → RL_hdri_03)
          RL_charts_XX — _TT_setup_grp/charts_grp (vis ON) + aiSkyDome_HDRI + chart_CAM
                         Override: aiSwitchHDRI.index = slot, charts_grp.visibility = 1
                         XX follows same numbering as RL_hdri_XX
        """
        if not self._require_scene():
            return

        selected_slots = [i for i, ck in enumerate(self._rl_slot_checks) if ck.isChecked()]
        if not selected_slots:
            cmds.warning("PXL TurnTable: No HDRI slots selected — tick at least one slot.")
            return

        include_charts = self._rl_charts_ck.isChecked() if self._rl_charts_ck else False

        # Switch to legacy render layers
        try:
            if cmds.mayaHasRenderSetup():
                cmds.optionVar(intValue=("renderSetupEnable", 0))
        except Exception:
            pass

        ns              = self._get_active_namespace()
        switch_node     = self._get_switch_node()
        sky_dome        = self._get_tt_sky_dome_transform()
        main_grp        = self._get_tt_render_grp()
        charts_grp      = self._get_tt_charts_grp()
        env_grp         = "|{ns}:TT_SCENE_grp|{ns}:_TT_setup_grp|{ns}:ENV_grp".format(ns=ns)
        env_grp         = env_grp if cmds.objExists(env_grp) else None
        main_cam        = "{}:main_CAM".format(ns)
        chart_cam       = "{}:chart_CAM".format(ns)
        main_cam_shape  = "{}:main_CAMShape".format(ns)
        chart_cam_shape = "{}:chart_CAMShape".format(ns)

        if not main_grp or not cmds.objExists(main_grp):
            cmds.warning("PXL TurnTable: mainModel_grp not found.")
            return

        created = []
        try:
            for slot_idx in selected_slots:
                padded = "{:02d}".format(slot_idx + 1)

                # ── HDRI layer ────────────────────────────────────────────────
                layer = self._create_tt_layer(
                    layer_name    = "RL_hdri_{}".format(padded),
                    content_grp   = main_grp,
                    sky_dome      = sky_dome,
                    camera        = main_cam,
                    camera_shape  = main_cam_shape,
                    switch_node   = switch_node,
                    hdri_index    = slot_idx,
                    visibility_on = False,
                    extra_vis_grp = env_grp,
                )
                if layer:
                    created.append(layer)

                # ── Charts layer ──────────────────────────────────────────────
                if include_charts and charts_grp and cmds.objExists(charts_grp):
                    layer = self._create_tt_layer(
                        layer_name    = "RL_charts_{}".format(padded),
                        content_grp   = charts_grp,
                        sky_dome      = sky_dome,
                        camera        = chart_cam,
                        camera_shape  = chart_cam_shape,
                        switch_node   = switch_node,
                        hdri_index    = slot_idx,
                        visibility_on = True,
                    )
                    if layer:
                        created.append(layer)

        finally:
            cmds.editRenderLayerGlobals(currentRenderLayer="defaultRenderLayer")

        if created:
            # ── Set render globals: file name prefix ──────────────────────────
            try:
                cmds.setAttr(
                    "defaultRenderGlobals.imageFilePrefix",
                    "<RenderLayer>/<Scene>_<RenderLayer>",
                    type="string"
                )
            except Exception as exc:
                _log.warning("Could not set imageFilePrefix: %s", exc)

            # ── Set animation format: name.####.ext, padding 4 ────────────────
            try:
                cmds.setAttr("defaultRenderGlobals.animation",         True)
                cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", 1)
                cmds.setAttr("defaultRenderGlobals.extensionPadding",  4)
                cmds.setAttr("defaultRenderGlobals.periodInExt",       1)
                cmds.setAttr("defaultRenderGlobals.outFormatControl",  0)
            except Exception as exc:
                _log.warning("Could not set animation format globals: %s", exc)

            # ── Arnold: enable Merge AOVs ─────────────────────────────────────
            try:
                cmds.setAttr("defaultArnoldDriver.mergeAOVs", 1)
            except Exception as exc:
                _log.warning("Could not enable mergeAOVs: %s", exc)

            # ── Render Sequence optionVars — set once at layer creation ──────────
            # renderSequenceAllLayers=1: renderSequence() iterates all enabled layers.
            # renderSequenceAllCameras=1: uses per-layer renderable override for camera.
            # Both are read by the MEL proc internally — do NOT loop in Python.
            try:
                cmds.optionVar(intValue=("renderSequenceAllLayers",  1))
                cmds.optionVar(intValue=("renderSequenceAllCameras", 1))
            except Exception as exc:
                _log.warning("Could not set renderSequence optionVars: %s", exc)

            # ── Enable Render Turntable button ────────────────────────────────
            if self._rt_render_btn:
                self._rt_render_btn.setEnabled(True)
            # Guided-flow: Step 1 (Create) done -> Step 2 (Render) unlocks.
            # Collapse the Render Layers Setup and open Render Turntable below.
            self._update_render_steps()
            if self._rl_section_frame:
                self._rl_section_frame.set_collapsed(True)
            if self._rt_section_frame:
                self._rt_section_frame.set_collapsed(False)

            # ── Disable master layer, enable all TT layers ────────────────────
            try:
                cmds.setAttr("defaultRenderLayer.renderable", 0)
                _log.info("Disabled defaultRenderLayer (master layer).")
            except Exception as exc:
                _log.warning("Could not disable defaultRenderLayer: %s", exc)
            for layer in created:
                try:
                    cmds.setAttr("{}.renderable".format(layer), 1)
                except Exception as exc:
                    _log.warning("Could not enable render layer %s: %s", layer, exc)

            listed = "\n".join("  - " + l for l in created[:20])
            if len(created) > 20:
                listed += "\n  ... and {} more".format(len(created) - 20)
            cmds.confirmDialog(
                title="Render Layers Created",
                message="Created {} render layer(s):\n{}".format(len(created), listed),
                button=["OK"]
            )
            _log.info("Created %d TT render layer(s): %s", len(created), created)
        else:
            cmds.warning("PXL TurnTable: No render layers were created.")

    def _create_tt_layer(self, layer_name, content_grp, sky_dome, camera, camera_shape,
                         switch_node, hdri_index, visibility_on=False, extra_vis_grp=None):
        """Create a single legacy render layer with all turntable overrides.

        Args:
            layer_name:    Name for the new render layer.
            content_grp:   Root group whose full hierarchy is added as members.
            sky_dome:      aiSkyDome_HDRI transform node.
            camera:        Camera transform to make renderable on this layer.
            camera_shape:  Camera shape node name (for .renderable override).
            switch_node:   aiSwitchHDRI node — HDRI index will be overridden.
            hdri_index:    Slot index to set on aiSwitchHDRI for this layer.
            visibility_on: If True, add visibility=1 override on content_grp
                           (required for charts_grp which is hidden in default layer).
            extra_vis_grp: Optional extra group to add as members AND override
                           visibility=1 (e.g. ENV_grp which is hidden by default).
        Returns:
            Layer name string if successful, None on failure.
        """
        try:
            # ── Collect layer members ─────────────────────────────────────────
            members = []
            if content_grp and cmds.objExists(content_grp):
                members.append(content_grp)
                desc = cmds.listRelatives(content_grp, ad=True, fullPath=True) or []
                members.extend(desc)
            if extra_vis_grp and cmds.objExists(extra_vis_grp):
                members.append(extra_vis_grp)
                desc = cmds.listRelatives(extra_vis_grp, ad=True, fullPath=True) or []
                members.extend(desc)
            if sky_dome and cmds.objExists(sky_dome):
                members.append(sky_dome)
            if camera and cmds.objExists(camera):
                members.append(camera)

            if not members:
                _log.warning("_create_tt_layer: no valid members for '%s' — skipping", layer_name)
                return None

            # ── Create empty layer and populate ───────────────────────────────
            layer = cmds.createRenderLayer(name=layer_name, empty=True)
            cmds.editRenderLayerMembers(layer, members)

            # ── Switch to layer to set per-layer overrides ────────────────────
            cmds.editRenderLayerGlobals(currentRenderLayer=layer)

            # ── Camera renderable overrides ───────────────────────────────────
            default_shapes = {"frontShape", "topShape", "sideShape"}
            for cam_shp in cmds.ls(type="camera"):
                if cam_shp in default_shapes:
                    continue
                try:
                    cmds.editRenderLayerAdjustment("{}.renderable".format(cam_shp))
                    cmds.setAttr("{}.renderable".format(cam_shp),
                                 1 if cam_shp == camera_shape else 0)
                except Exception as exc:
                    _log.debug("Renderable override skipped for %s: %s", cam_shp, exc)

            # ── HDRI switch index override ────────────────────────────────────
            if switch_node and cmds.objExists(switch_node):
                try:
                    cmds.editRenderLayerAdjustment("{}.index".format(switch_node))
                    cmds.setAttr("{}.index".format(switch_node), hdri_index)
                except Exception as exc:
                    _log.warning("HDRI index override failed on '%s': %s", layer_name, exc)

            # ── Visibility override on content_grp (e.g. charts_grp) ──────────
            if visibility_on and content_grp and cmds.objExists(content_grp):
                try:
                    cmds.editRenderLayerAdjustment("{}.visibility".format(content_grp))
                    cmds.setAttr("{}.visibility".format(content_grp), 1)
                except Exception as exc:
                    _log.warning("Visibility override failed on '%s': %s", layer_name, exc)

            # ── Visibility override on extra_vis_grp (e.g. ENV_grp) ───────────
            if extra_vis_grp and cmds.objExists(extra_vis_grp):
                try:
                    cmds.editRenderLayerAdjustment("{}.visibility".format(extra_vis_grp))
                    cmds.setAttr("{}.visibility".format(extra_vis_grp), 1)
                except Exception as exc:
                    _log.warning(
                        "Visibility override failed for extra_vis_grp on '%s': %s",
                        layer_name, exc
                    )

            _log.info(
                "Created render layer: %s (HDRI slot %d, vis_on=%s, extra_vis_grp=%s)",
                layer, hdri_index, visibility_on, extra_vis_grp
            )
            return layer

        except Exception as exc:
            _log.error("Failed to create render layer '%s': %s", layer_name, exc)
            cmds.warning(
                "PXL TurnTable: Failed to create layer {} — {}".format(layer_name, exc)
            )
            return None

    def _tt_layers_exist(self):
        """Return True if any RL_hdri_* or RL_charts_* layers exist in the scene."""
        return any(
            l.startswith("RL_hdri_") or l.startswith("RL_charts_")
            for l in (cmds.ls(type="renderLayer") or [])
            if l != "defaultRenderLayer"
        )

    def render_tt_layers(self):
        """Render all TT layers in sequence using the active renderer.

        Sets frame range and resolution, then calls renderSequence() once.
        Maya reads renderSequenceAllLayers=1 and renderSequenceAllCameras=1 optionVars
        (set at layer creation time) and handles all layer/camera iteration internally.
        """
        if not self._require_scene():
            return

        tt_layers = [
            l for l in (cmds.ls(type="renderLayer") or [])
            if l != "defaultRenderLayer" and (
                l.startswith("RL_hdri_") or l.startswith("RL_charts_")
            )
        ]
        if not tt_layers:
            cmds.warning(
                "PXL TurnTable: No TT render layers found — create them first."
            )
            return

        start    = self._rt_start_spin.value() if self._rt_start_spin else self.frame_start
        end      = self._rt_end_spin.value()   if self._rt_end_spin   else self.frame_end
        by_frame = self._rt_step_spin.value()  if self._rt_step_spin  else 1

        if end <= start:
            cmds.warning("PXL TurnTable: End frame must be greater than start frame.")
            return

        # Resolution preset
        _RES_PRESETS = [
            (1280, 720,  1.7778),   # HD 720
            (1920, 1080, 1.7778),   # HD 1080
            (3840, 2160, 1.7778),   # 4K
        ]
        res_idx = self._rt_res_combo.currentIndex() if self._rt_res_combo else 1
        res_w, res_h, res_aspect = _RES_PRESETS[max(0, min(res_idx, len(_RES_PRESETS) - 1))]
        try:
            cmds.setAttr("defaultResolution.width",              res_w)
            cmds.setAttr("defaultResolution.height",             res_h)
            cmds.setAttr("defaultResolution.deviceAspectRatio",  res_aspect)
            _log.info("Resolution set to %dx%d", res_w, res_h)
        except Exception as exc:
            _log.warning("Could not set resolution: %s", exc)

        # Apply frame range and step only — renderAll was set at layer creation time
        try:
            cmds.setAttr("defaultRenderGlobals.startFrame",  start)
            cmds.setAttr("defaultRenderGlobals.endFrame",    end)
            cmds.setAttr("defaultRenderGlobals.byFrameStep", by_frame)
        except Exception as exc:
            _log.warning("Could not set render globals: %s", exc)

        import maya.mel as mel

        _log.info(
            "Render Turntable: %d layer(s), frames %d–%d by %d",
            len(tt_layers), start, end, by_frame
        )

        # Single call — Maya iterates all enabled layers and cameras internally
        # via renderSequenceAllLayers=1 and renderSequenceAllCameras=1 optionVars
        try:
            mel.eval("renderSequence()")
            self._rendered = True
            self._update_render_steps()   # Step 2 done -> section pale green
        except Exception as exc:
            _log.error("renderSequence failed: %s", exc)
            cmds.warning("PXL TurnTable: renderSequence failed — {}".format(exc))

    def delete_tt_render_layers(self):
        """Delete all TT render layers (RL_hdri_* and RL_charts_*) from the scene."""
        tt_layers = [
            l for l in cmds.ls(type="renderLayer")
            if l != "defaultRenderLayer" and (
                l.startswith("RL_hdri_") or l.startswith("RL_charts_")
            )
        ]
        if not tt_layers:
            cmds.confirmDialog(
                title="No Layers Found",
                message="No TT render layers (RL_hdri_* / RL_charts_*) found in the scene.",
                button=["OK"]
            )
            return

        result = cmds.confirmDialog(
            title="Delete TT Render Layers",
            message="Delete {} TT render layer(s)?".format(len(tt_layers)),
            button=["Delete", "Cancel"],
            defaultButton="Cancel",
            cancelButton="Cancel",
            dismissString="Cancel"
        )
        if result != "Delete":
            return

        cmds.editRenderLayerGlobals(currentRenderLayer="defaultRenderLayer")
        deleted = 0
        for layer in tt_layers:
            try:
                cmds.delete(layer)
                deleted += 1
            except Exception as exc:
                _log.warning("Could not delete render layer '%s': %s", layer, exc)

        cmds.confirmDialog(
            title="Done",
            message="Deleted {} render layer(s).".format(deleted),
            button=["OK"]
        )
        _log.info("Deleted %d TT render layer(s).", deleted)
        # Disable render button — no layers exist any more
        if self._rt_render_btn:
            self._rt_render_btn.setEnabled(False)
        # Guided-flow: back to Step 1 (Create) active, Step 2 (Render) locked
        self._rendered = False
        self._update_render_steps()

    # ─────────────────────────────────────────────────────────────────────────
    # HDRI selection
    # ─────────────────────────────────────────────────────────────────────────

    def select_hdri(self, slot_index):
        if not self._require_scene():
            return
        switch_node = self._get_switch_node()
        if not switch_node:
            cmds.warning("PXL TurnTable: HDRI switch node not found.")
            return

        index_attr = "{}.index".format(switch_node)
        try:
            cmds.setAttr(index_attr, slot_index)
        except Exception:
            in_conns = (
                cmds.listConnections(index_attr, source=True, destination=False, plugs=True) or []
            )
            set_ok = False
            for conn in in_conns:
                try:
                    cmds.setAttr(conn, slot_index)
                    set_ok = True
                    break
                except Exception:
                    continue
            if not set_ok:
                cmds.warning("PXL TurnTable: Could not set HDRI index.")
                return

        self._active_hdri_index = slot_index
        self._update_hdri_highlight(slot_index)
        self._save_config(active_hdri_index=slot_index)

    def browse_custom_hdri(self, slot_index):
        if not self._require_scene():
            return
        result = cmds.fileDialog2(
            fileMode=1, caption="Select Custom HDRI",
            fileFilter="HDRI Files (*.hdr *.exr *.hdri);;All Files (*.*)",
            okCaption="Load"
        )
        if not result:
            return

        hdri_path  = result[0].replace("\\", "/")
        active_ns  = self._get_active_namespace()
        if not active_ns:
            cmds.warning("PXL TurnTable: Load the scene before loading custom HDRIs.")
            return

        custom_num  = slot_index - self.HDRI_PRESET_COUNT + 1
        target_node = "{}:HDRI_Custom_0{}".format(active_ns, custom_num)
        if not cmds.objExists(target_node):
            cmds.warning(
                "PXL TurnTable: Custom HDRI node not found: {}.".format(target_node)
            )
            return

        try:
            dest_path = self._copy_hdri_to_root(hdri_path)
            use_path  = dest_path if dest_path else hdri_path

            node_type = cmds.nodeType(target_node)
            file_attr = (
                "{}.fileTextureName".format(target_node)
                if node_type == "file"
                else "{}.filename".format(target_node)
            )
            cmds.setAttr(file_attr, use_path, type="string")
            try:
                cmds.setAttr(
                    "{}.colorSpace".format(target_node),
                    "Utility - Linear - sRGB", type="string"
                )
            except Exception:
                pass

            thumb_path = self._generate_hdri_thumbnail(use_path)
            self._update_custom_slot_ui(slot_index, use_path, thumb_path)
            self._custom_hdri_paths[slot_index] = use_path
            self._save_config(custom_hdri_paths=self._custom_hdri_paths)
            self.select_hdri(slot_index)

        except Exception as exc:
            _log.error("Custom HDRI load failed: %s", exc)
            cmds.warning("PXL TurnTable: Custom HDRI failed — {}".format(exc))

    def _copy_hdri_to_root(self, hdri_path):
        if not self.hdri_dir or not os.path.isdir(self.hdri_dir):
            return None
        dest = os.path.join(self.hdri_dir, os.path.basename(hdri_path)).replace("\\", "/")
        if os.path.normcase(os.path.abspath(hdri_path)) == os.path.normcase(os.path.abspath(dest)):
            return dest
        try:
            import shutil
            shutil.copy2(hdri_path, dest)
            return dest
        except Exception as exc:
            _log.warning("Could not copy HDRI: %s", exc)
            return None

    def _get_preview_images(self):
        if not self.hdri_preview_dir or not os.path.isdir(self.hdri_preview_dir):
            return []
        EXT   = {".jpg", ".jpeg", ".png", ".tga", ".bmp", ".tiff", ".tif"}
        files = sorted([
            os.path.join(self.hdri_preview_dir, f)
            for f in os.listdir(self.hdri_preview_dir)
            if os.path.splitext(f)[1].lower() in EXT
        ])
        return files[: self.HDRI_PRESET_COUNT]

    def _generate_hdri_thumbnail(self, hdri_path):
        if not self.hdri_dir:
            return None
        previews_dir = os.path.join(self.hdri_dir, "previews").replace("\\", "/")
        try:
            os.makedirs(previews_dir, exist_ok=True)
        except Exception:
            return None
        basename   = os.path.splitext(os.path.basename(hdri_path))[0]
        thumb_path = os.path.join(previews_dir, basename + ".jpg").replace("\\", "/")
        if self._thumbnail_via_opencv(hdri_path, thumb_path):
            return thumb_path
        if self._thumbnail_via_kbyte_adaptive(hdri_path, thumb_path):
            return thumb_path
        return None

    # ─────────────────────────────────────────────────────────────────────────
    # OpenCV helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _prelim_complete(self):
        # Root folder is the only required prelim action; ACES/OpenCV are checks.
        return self._is_root_valid()

    @staticmethod
    def _is_aces_configured():
        """Return True if ACES 1.2 is active — checks system OCIO env var first,
        then Maya local colour management preferences."""
        import os
        # 1. System-level: OCIO environment variable
        ocio_env = os.environ.get("OCIO", "")
        if "aces_1.2" in ocio_env.lower() or "aces-1.2" in ocio_env.lower():
            return True
        # 2. Maya-local: colour management preferences
        try:
            if not cmds.colorManagementPrefs(q=True, cmEnabled=True):
                return False
            cfg = cmds.colorManagementPrefs(q=True, configFilePath=True) or ""
            if "aces_1.2" in cfg.lower() or "aces-1.2" in cfg.lower():
                return True
            rs = cmds.colorManagementPrefs(q=True, renderingSpaceName=True) or ""
            return "acescg" in rs.lower()
        except Exception:
            return False

    @staticmethod
    def _is_opencv_available():
        try:
            import cv2  # noqa: F401
            return True
        except ImportError:
            return False

    @staticmethod
    def _write_maya_env_exr_flag():
        maya_env  = os.path.join(
            os.path.expanduser("~"), "Documents", "maya", "2025", "Maya.env"
        )
        flag_line = "OPENCV_IO_ENABLE_OPENEXR=1"
        try:
            existing = ""
            if os.path.isfile(maya_env):
                with open(maya_env, "r") as fh:
                    existing = fh.read()
            if flag_line in existing:
                return True
            with open(maya_env, "a") as fh:
                if existing and not existing.endswith("\n"):
                    fh.write("\n")
                fh.write(flag_line + "\n")
            return True
        except Exception as exc:
            _log.warning("Could not write Maya.env: %s", exc)
            return False

    def install_opencv(self):
        import threading
        import importlib
        try:
            from PySide6.QtCore import QTimer
        except ImportError:
            from PySide2.QtCore import QTimer
        try:
            from PySide6 import QtWidgets
        except ImportError:
            from PySide2 import QtWidgets

        target = _OPENCV_LIBS
        try:
            os.makedirs(target, exist_ok=True)
        except Exception as exc:
            cmds.confirmDialog(
                title="Install Error",
                message="Could not create install directory:\n{}\n\n{}".format(target, exc),
                button=["OK"], defaultButton="OK"
            )
            return

        if self._opencv_install_btn:
            self._opencv_install_btn.setEnabled(False)
            self._opencv_install_btn.setText("Installing…")

        STAGES = [
            (0,  "Resolving package from PyPI…"),
            (20, "Downloading opencv-python-headless…"),
            (65, "Installing to local library folder…"),
            (90, "Verifying installation…"),
        ]

        maya_ptr  = __import__("maya.OpenMayaUI", fromlist=["OpenMayaUI"]).MQtUtil.mainWindow()
        maya_main = (__import__("shiboken6", fromlist=["wrapInstance"]) if _PYSIDE_VER == 6 else __import__("shiboken2", fromlist=["wrapInstance"])).wrapInstance(
            int(maya_ptr), QtWidgets.QWidget
        )
        progress_dlg = QtWidgets.QProgressDialog(
            STAGES[0][1], None, 0, 100, maya_main
        )
        progress_dlg.setWindowTitle("OpenCV Installation")
        try:
            from PySide6.QtCore import Qt
        except ImportError:
            from PySide2.QtCore import Qt
        progress_dlg.setWindowModality(Qt.ApplicationModal)
        progress_dlg.setMinimumDuration(0)
        progress_dlg.setValue(0)
        progress_dlg.show()

        state = {"done": False, "rc": None, "error": None, "output": ""}

        def _worker():
            import io as _io
            try:
                from pip._internal.cli.main import main as _pip
            except ImportError:
                try:
                    from pip._internal import main as _pip
                except ImportError:
                    try:
                        from pip import main as _pip
                    except ImportError:
                        state["error"] = "pip API not found."
                        state["done"]  = True
                        return

            buf = _io.StringIO()
            old_out, old_err, old_in = sys.stdout, sys.stderr, sys.stdin
            sys.stdout = buf
            sys.stderr = buf
            sys.stdin  = _io.StringIO()
            try:
                rc = _pip([
                    "install", "opencv-python-headless",
                    "--target", target,
                    "--disable-pip-version-check", "--quiet",
                ])
                state["rc"] = rc
            except SystemExit as se:
                state["rc"] = int(se.code) if se.code is not None else 0
            except Exception as exc:
                state["error"] = str(exc)
                state["rc"]    = -1
            finally:
                sys.stdout      = old_out
                sys.stderr      = old_err
                sys.stdin       = old_in
                state["output"] = buf.getvalue()
                state["done"]   = True

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

        self._install_timer   = QTimer()
        self._install_elapsed = 0

        def _on_tick():
            self._install_elapsed += 1
            elapsed_s = self._install_elapsed * 0.4

            if not state["done"]:
                if   elapsed_s <  4:  idx = 0
                elif elapsed_s < 20:  idx = 1
                elif elapsed_s < 45:  idx = 2
                else:                 idx = 3
                cap      = STAGES[idx]
                next_pct = STAGES[idx + 1][0] if idx < len(STAGES) - 1 else 95
                band     = max(next_pct - cap[0], 1)
                elap_in  = max(0.0, elapsed_s - [0, 4, 20, 45][idx])
                pct      = int(min(cap[0] + (elap_in / band) * band, next_pct - 1))
                progress_dlg.setValue(pct)
                progress_dlg.setLabelText(cap[1])
                return

            self._install_timer.stop()
            progress_dlg.close()

            if state["error"]:
                if self._opencv_install_btn:
                    self._opencv_install_btn.setEnabled(True)
                    self._opencv_install_btn.setText("Install OpenCV")
                cmds.confirmDialog(
                    title="Install Error", message=state["error"],
                    button=["OK"], defaultButton="OK"
                )
                return

            if state["rc"] not in (0, None):
                out = state["output"].strip()[-800:] or "(no output)"
                if self._opencv_install_btn:
                    self._opencv_install_btn.setEnabled(True)
                    self._opencv_install_btn.setText("Install OpenCV")
                cmds.confirmDialog(
                    title="Install Failed",
                    message="pip exited with code {}:\n\n{}".format(state["rc"], out),
                    button=["OK"], defaultButton="OK"
                )
                return

            if target not in sys.path:
                sys.path.insert(0, target)
            importlib.invalidate_caches()
            try:
                import cv2  # noqa: F401
                cv2_ok = True
            except ImportError:
                cv2_ok = False

            if cv2_ok:
                env_written = self._write_maya_env_exr_flag()
                if self._opencv_install_btn:
                    self._opencv_install_btn.setVisible(False)
                if self._opencv_status_label:
                    self._opencv_status_label.setText(
                        "  ✓  OpenCV installed — restart Maya to enable EXR previews."
                    )
                    self._opencv_status_label.setObjectName("statusOk")
                    self._opencv_status_label.setStyleSheet(
                        "background: #1e2e1e; color: #6aaa6a; "
                        "border: 1px solid #2a3a2a; border-radius: 2px; "
                        "padding: 4px 8px; font-size: 9px;"
                    )
                if self._prelim_complete() and self._preliminary_frame:
                    self._preliminary_frame.set_collapsed(True)
                self._update_prelim_ui()   # Step 3 badge -> green

                msg = (
                    "OpenCV installed successfully.\n\n"
                    "IMPORTANT: Please restart Maya once.\n\n"
                    "EXR codec activation requires OPENCV_IO_ENABLE_OPENEXR=1 "
                    "in Maya.env before Maya starts."
                )
                if not env_written:
                    msg += (
                        "\n\nNote: Could not write to Maya.env automatically.\n"
                        "Add this line manually:\n    OPENCV_IO_ENABLE_OPENEXR=1"
                    )
                cmds.confirmDialog(
                    title="Restart Maya Required", message=msg,
                    button=["OK"], defaultButton="OK"
                )
            else:
                if self._opencv_install_btn:
                    self._opencv_install_btn.setEnabled(True)
                    self._opencv_install_btn.setText("Install OpenCV")
                cmds.confirmDialog(
                    title="Verification Failed",
                    message="pip succeeded but cv2 could not be imported.\n\nInstall location:\n{}".format(target),
                    button=["OK"], defaultButton="OK"
                )

        self._install_timer.timeout.connect(_on_tick)
        self._install_timer.start(400)

    def _thumbnail_via_opencv(self, hdri_path, thumb_path):
        try:
            os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
            import cv2
            import numpy as np

            hdr = cv2.imread(hdri_path, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
            if hdr is None:
                return False
            hdr = hdr.astype(np.float32)
            hdr = np.maximum(hdr, 0.0)
            if hdr.ndim == 2:
                hdr = cv2.cvtColor(hdr, cv2.COLOR_GRAY2BGR)
            elif hdr.shape[2] == 4:
                hdr = hdr[:, :, :3]
            tonemap = cv2.createTonemapDrago(gamma=1.0, saturation=1.0, bias=0.85)
            ldr     = tonemap.process(hdr)
            p_lo    = float(np.percentile(ldr, 2))
            p_hi    = float(np.percentile(ldr, 98))
            span    = max(p_hi - p_lo, 1e-4)
            ldr     = np.clip((ldr - p_lo) / span, 0.0, 1.0)
            ldr     = np.power(ldr, 1.0 / 2.2)
            ldr     = np.clip(ldr * 255.0, 0, 255).astype(np.uint8)
            ldr     = cv2.resize(ldr, (self.CELL_W, self.CELL_H - 22),
                                 interpolation=cv2.INTER_LANCZOS4)
            cv2.imwrite(thumb_path, ldr, [cv2.IMWRITE_JPEG_QUALITY, 85])
            return True
        except ImportError:
            return False
        except Exception as exc:
            _log.warning("OpenCV thumbnail failed: %s", exc)
            return False

    def _thumbnail_via_kbyte_adaptive(self, hdri_path, thumb_path):
        import tempfile
        tmp_path = None
        try:
            import maya.api.OpenMaya as om
            import numpy as np
            from PIL import Image as PilImage

            img = om.MImage()
            img.readFromFile(hdri_path, om.MImage.kByte)
            tmp_path = os.path.join(
                tempfile.gettempdir(),
                os.path.splitext(os.path.basename(hdri_path))[0] + "_pxl_tmp.png"
            ).replace("\\", "/")
            img.writeToFile(tmp_path, "png")

            arr    = np.array(PilImage.open(tmp_path).convert("RGB"), dtype=np.float32) / 255.0
            p_low  = float(np.percentile(arr, 2))
            p_high = float(np.percentile(arr, 98))
            span   = p_high - p_low
            arr    = (arr - p_low) / span if span > 1e-4 else arr * 20.0
            arr    = np.clip(arr, 0.0, 1.0)
            arr    = np.power(arr, 1.0 / 2.2)
            thumb  = PilImage.fromarray((arr * 255).astype(np.uint8), mode="RGB")
            thumb  = thumb.resize((self.CELL_W, self.CELL_H - 22), PilImage.LANCZOS)
            thumb.save(thumb_path, "JPEG", quality=85)
            return True
        except Exception as exc:
            _log.warning("kByte thumbnail failed: %s", exc)
            return False
        finally:
            if tmp_path and os.path.isfile(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    # ─────────────────────────────────────────────────────────────────────────
    # Model operations (Section 2)
    # ─────────────────────────────────────────────────────────────────────────

    def capture_selection(self):
        """Capture selected nodes, create a locator at the base of each, parent them under it."""
        if not self._require_scene():
            return
        sel = cmds.ls(selection=True)
        if not sel:
            cmds.warning(
                "PXL TurnTable: Nothing selected. "
                "Select your model(s) or root group(s) first."
            )
            return

        # Clean up any existing locators from a previous capture (revert objects to world)
        self._cleanup_user_rigs(revert_objects=True)

        # Reset downstream steps to locked
        for i in (1, 2):
            self._update_step_ui(i, done=False, unlock_next=False)
            btn = self._step_btns[i]
            if btn:
                btn.setEnabled(False)
                btn.setObjectName("btnStepLocked")
                btn.setStyleSheet("")  # clear any inline style so themed QSS drives
                btn.style().unpolish(btn)
                btn.style().polish(btn)
            circle = self._step_circles[i]
            if circle:
                circle.setObjectName("stepLocked")
                circle.setStyleSheet("")
                circle.style().unpolish(circle)
                circle.style().polish(circle)
                circle.setText(str(i + 1))

        main_grp = self._get_tt_render_grp()
        if not main_grp:
            cmds.warning("PXL TurnTable: mainModel_grp not found — load the scene first.")
            return

        self.captured_nodes     = list(sel)
        self._user_rig_locators = []

        try:
            for node in sel:
                bbox = cmds.exactWorldBoundingBox(node)
                cx   = (bbox[0] + bbox[3]) / 2.0
                cz   = (bbox[2] + bbox[5]) / 2.0
                ymin = bbox[1]

                # Place locator at the BASE-CENTER of the object's bounding box
                safe = node.replace(":", "_").replace("|", "_")
                loc  = cmds.spaceLocator(name="TT_loc_{}".format(safe))[0]
                cmds.move(cx, ymin, cz, loc, absolute=True, worldSpace=True)
                cmds.parent(loc, main_grp)

                # Parent object under its locator — object stays in world position
                cmds.parent(node, loc)
                self._user_rig_locators.append(loc)

            display = (
                ", ".join(sel) if len(sel) <= 3
                else "{}, {} … (+{} more)".format(sel[0], sel[1], len(sel) - 2)
            )
            if self._selection_label:
                self._selection_label.setText("  Captured: {}".format(display))
            self._update_step_ui(0, done=True, unlock_next=True)
            _log.info("Captured %d node(s) with locator rigs at base positions", len(sel))
        except Exception as exc:
            _log.error("Capture selection failed: %s", exc)
            cmds.warning("PXL TurnTable: Capture failed — {}".format(exc))

    def align_to_ground(self):
        """Move each locator to Y=0 — the parented object grounds with it automatically."""
        if not self._require_scene():
            return
        if not self._user_rig_locators:
            cmds.warning("PXL TurnTable: No locator rigs — use Capture Selection first.")
            return
        valid_locs = [loc for loc in self._user_rig_locators if cmds.objExists(loc)]
        if not valid_locs:
            cmds.warning("PXL TurnTable: Locator rigs no longer exist.")
            return
        try:
            for loc in valid_locs:
                loc_y = cmds.xform(loc, query=True, worldSpace=True, translation=True)[1]
                if abs(loc_y) > 1e-4:
                    cmds.move(0, -loc_y, 0, loc, relative=True, worldSpace=True)
            self._update_step_ui(1, done=True, unlock_next=True)
            _log.info("Aligned %d locator rig(s) to ground", len(valid_locs))
        except Exception as exc:
            _log.error("Align to ground failed: %s", exc)
            cmds.warning("PXL TurnTable: Align to ground failed — {}".format(exc))

    def attach_to_turntable(self):
        """Finalise attachment. If Maintain Offset is OFF, center locators to XZ origin."""
        if not self._require_scene():
            return
        if not self._user_rig_locators:
            cmds.warning("PXL TurnTable: No locator rigs — use Capture Selection first.")
            return
        valid_locs = [loc for loc in self._user_rig_locators if cmds.objExists(loc)]
        if not valid_locs:
            cmds.warning("PXL TurnTable: Locator rigs no longer exist.")
            return

        maintain = self._maintain_offset_ck.isChecked() if self._maintain_offset_ck else True

        ns = self._get_active_namespace()
        asset_rot = "{}:asset_ROT".format(ns)
        if not cmds.objExists(asset_rot):
            cmds.warning(
                "PXL TurnTable: asset_ROT not found — load the turntable scene first."
            )
            return

        try:
            for loc in valid_locs:
                # Optionally center locator to XZ origin (Y already grounded by Align to Ground)
                if not maintain:
                    loc_ws = cmds.xform(loc, query=True, worldSpace=True, translation=True)
                    cmds.move(-loc_ws[0], 0, -loc_ws[2], loc, relative=True, worldSpace=True)

                # Orient-constrain locator Y to asset_ROT so objects spin on their own pivots
                existing = cmds.listConnections(loc, type="orientConstraint") or []
                if not existing:
                    cmds.orientConstraint(
                        asset_rot, loc, maintainOffset=True, skip=["x", "z"]
                    )

            self._update_step_ui(2, done=True, unlock_next=False)
            self._advance_to_section(3)
            self._update_model_section_state()   # Model section -> pale green
            # Auto-frame main_CAM on the asset bounding box (centred, breathing room)
            self._frame_main_cam_to_asset()
            _log.info(
                "Attached %d locator rig(s), Y-constrained to %s (maintainOffset=%s)",
                len(valid_locs), asset_rot, maintain
            )
        except Exception as exc:
            _log.error("Attach failed: %s", exc)
            cmds.warning("PXL TurnTable: Attach failed — {}".format(exc))

    # ─────────────────────────────────────────────────────────────────────────
    # Foster parent cleanup
    # ─────────────────────────────────────────────────────────────────────────

    def _cleanup_foster_parents(self):
        foster_nodes = cmds.ls("*fosterParent*", type="transform") or []
        if not foster_nodes:
            return
        for fp in foster_nodes:
            if not cmds.objExists(fp):
                continue
            children = cmds.listRelatives(fp, children=True, fullPath=True) or []
            for child in children:
                try:
                    cmds.parent(child, world=True)
                except Exception as exc:
                    _log.warning("Could not re-parent '%s': %s", child, exc)
            remaining = cmds.listRelatives(fp, children=True) or []
            if not remaining:
                try:
                    cmds.delete(fp)
                except Exception:
                    pass

    # ─────────────────────────────────────────────────────────────────────────
    # Locator rig cleanup helper
    # ─────────────────────────────────────────────────────────────────────────

    def _cleanup_user_rigs(self, revert_objects=False):
        """Delete all user locator rigs.
        If revert_objects=True, un-parent child objects to world space first.
        """
        for loc in list(self._user_rig_locators):
            if not cmds.objExists(loc):
                continue
            if revert_objects:
                children = cmds.listRelatives(loc, children=True, fullPath=True) or []
                for child in children:
                    try:
                        if cmds.nodeType(child) == "transform":
                            cmds.parent(child, world=True)
                    except Exception as exc:
                        _log.warning("Re-parent issue for '%s': %s", child, exc)
            try:
                cmds.delete(loc)
            except Exception as exc:
                _log.warning("Could not delete locator '%s': %s", loc, exc)
        self._user_rig_locators = []

    # ─────────────────────────────────────────────────────────────────────────
    # Clear scene
    # ─────────────────────────────────────────────────────────────────────────

    def clear_scene(self):
        if not self._require_scene():
            return
        ref_node = None
        for ref in (cmds.ls(type="reference") or []):
            try:
                if self.TT_SCENE_FILENAME in cmds.referenceQuery(ref, filename=True):
                    ref_node = ref
                    break
            except Exception:
                continue

        if not ref_node:
            cmds.warning("PXL TurnTable: No turntable reference found.")
            return

        confirm = cmds.confirmDialog(
            title="Clear TurnTable Scene",
            message="Remove the turntable reference?\nYour model will be re-parented to world.",
            button=["Clear", "Cancel"],
            defaultButton="Clear", cancelButton="Cancel", dismissString="Cancel"
        )
        if confirm != "Clear":
            return

        # Tear down locator rigs — unparent user objects to world, delete locators
        self._cleanup_user_rigs(revert_objects=True)

        # Legacy fallback: re-parent objects attached directly (old-style, no locators)
        if self.captured_nodes:
            valid = [n for n in self.captured_nodes if cmds.objExists(n)]
            if valid:
                try:
                    cmds.parent(valid, world=True)
                except Exception as exc:
                    _log.warning("Re-parent issue (legacy): %s", exc)

        try:
            cmds.file(referenceNode=ref_node, removeReference=True)
        except Exception as exc:
            _log.error("Reference removal failed: %s", exc)
            cmds.warning("PXL TurnTable: Could not remove reference — {}".format(exc))
            return

        self._cleanup_foster_parents()
        self._set_scene_status(loaded=False)

        # Full clean (checkbox, on by default): also delete the TT render layers,
        # so clearing the scene doesn't leave RL_hdri_* / RL_charts_* behind.
        if self._clear_layers_ck and self._clear_layers_ck.isChecked():
            try:
                cmds.editRenderLayerGlobals(currentRenderLayer="defaultRenderLayer")
            except Exception:
                pass
            removed = 0
            for layer in [l for l in (cmds.ls(type="renderLayer") or [])
                          if l != "defaultRenderLayer"
                          and (l.startswith("RL_hdri_") or l.startswith("RL_charts_"))]:
                try:
                    cmds.delete(layer)
                    removed += 1
                except Exception as exc:
                    _log.warning("Could not delete render layer '%s': %s", layer, exc)
            if removed:
                _log.info("Clear Scene: also removed %d TT render layer(s).", removed)
            if self._rt_render_btn:
                self._rt_render_btn.setEnabled(False)

        # Guided-flow: scene gone -> Scene/Model/Render sections reset
        self._frames_applied = False
        self._rendered = False
        self._update_scene_steps()
        self._update_render_steps()
        self._update_model_section_state()

        if self._selection_label:
            self._selection_label.setText("  No model captured — select the model you want to capture")

        self._active_hdri_index = -1
        self._update_hdri_highlight(-1)

        self._step_done = [False, False, False]
        for i in range(3):
            self._update_step_ui(i, done=False, unlock_next=False)
        # Lock steps 2 and 3
        for i in (1, 2):
            btn = self._step_btns[i]
            if btn:
                btn.setEnabled(False)
                btn.setObjectName("btnStepLocked")
                btn.setStyleSheet("")  # clear inline so themed QSS drives
                btn.style().unpolish(btn)
                btn.style().polish(btn)
            circle = self._step_circles[i]
            if circle:
                circle.setObjectName("stepLocked")
                circle.setStyleSheet("")
                circle.style().unpolish(circle)
                circle.style().polish(circle)
                circle.setText(str(i + 1))

        for panel in (cmds.getPanel(type="modelPanel") or []):
            try:
                if cmds.modelEditor(panel, query=True, camera=True) == "main_CAM":
                    cmds.modelEditor(panel, edit=True, camera="persp", grid=True)
                    break
            except Exception:
                continue


# ── Entry point ───────────────────────────────────────────────────────────────

def run():
    """Launch the PXL TurnTable Builder."""
    TurnTableBuilder()


run()
