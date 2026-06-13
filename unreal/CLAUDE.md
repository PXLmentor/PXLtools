# Claude for Unreal — VFX Tools
# Sub-context for J:\ClaudeCode\projects\PXLtools\unreal\
# Parent project context: J:\ClaudeCode\projects\PXLtools\CLAUDE.md (identity, versioning, engineering standards)

---

## 06 · Claude for Unreal

**Target:** Unreal Engine 5.6 | **Connection:** TCP Socket via `remote_execution.py` | **Status:** v0.2.0-alpha (post-overhaul)

**Next resume point: CP003** — implement corrected agent loop. The system prompt with the response decision tree was written and approved. Implementation was interrupted by API credit exhaustion — not a code issue.

### Behavioral Architecture — Mode Separation
| Mode      | Behavior |
|-----------|----------|
| THINKING  | Blocks autonomous execution. Presents plan for user approval. No code runs until explicitly approved. |
| EXECUTING | Post-approval. Runs steps autonomously. No interruption dialogs mid-execution. |

### Four-Phase Creative Pipeline
1. **Phase 1 — Style Agreement:** Align on creative vision before any asset work
2. **Phase 2 — Asset Discovery:** Identify available assets in UE Content Browser
3. **Phase 3 — Block-out:** Create stand-in geometry / rough layout
4. **Phase 4 — Asset Replacement:** Replace block-out with final assets

### Ambiguity Rule
- Never write code until the full vision is agreed upon
- Ask clarifying questions for anything ambiguous
- Only auto-execute zero-ambiguity mechanical commands (e.g., "create empty actor")

### TCP Connection
- Module: `remote_execution.py`
- Protocol: TCP socket to Unreal Engine 5.6 Editor
- Image handling: conversation trimming must NOT discard image-containing messages (fixed in v0.2.0-alpha)

---

## Unreal — Environment

| Component | Details |
|-----------|---------|
| Unreal    | Unreal Engine 5.6 |
| UE Connection | `remote_execution.py` TCP socket |
| Asset Sources | UE Content Browser, Fab.com marketplace |

---

## Unreal Tool Catalog

### MU Bridge (Maya -> Unreal asset bridge)
- **Entry:** `unreal/python/pxl_mu_bridge.py` (registers ONE toolbar icon on the Level Editor toolbar; click -> opens the window) — v0.1.2-alpha CP008
- **Window UI:** `unreal/python/pxl_mu_bridge_pkg/ui.py` (PySide6 with PySide2 fallback; matches PXLMENTOR_TOOL_STANDARD v1.2.0) — v0.1.2-alpha CP005
- **Startup hook (install once):** copy `unreal/python/init_unreal.py` to `<YourUEProject>/Content/Python/init_unreal.py` and restart UE. The file's docstring is the install guide. **CP005:** the UI now has a one-click "INSTALL STARTUP HOOK INTO ACTIVE PROJECT" button that does this automatically for any open UE project (backup-before-overwrite if a file already exists).
- **Logic package:** `unreal/python/pxl_mu_bridge_pkg/` (7 modules: __init__, ui, importer, material_factory, texture_setup, aces_configurator, report)
- **Shared schema:** `J:\ClaudeCode\projects\PXLtools\shared\pxl_mu_bridge_schema\` (cross-DCC with Maya side)
- **Master Material:** `unreal/content/PXLbridge/M_PXL_PBR_Master.uasset` — one-time bootstrap; the canonical authoring guide is `unreal/content/PXLbridge/BOOTSTRAP_MASTER_MATERIAL.md` (step-by-step node + parameter + wire spec). If the user hasn't followed the doc yet, `material_factory.py` (CP004) falls back to a programmatic auto-builder marked DIAGNOSTIC — visible output works but MI scalar/vector parameter overrides silently no-op until the real master is authored.
- **EUW toolbar icon:** branded icon (`icon_mu_bridge.png`) needs `W_MUBridge_Toolbar` Editor Utility Widget at `/Game/PXLbridge/`. Authoring guide: `unreal/BOOTSTRAP_EUW_TOOLBAR.md` (~15 min, one-time per UE project). Until bootstrapped, the bridge falls back to a stock toolbar icon + the always-visible Tools menu entry.
- **User-facing install guide:** `unreal/MU_Bridge_README.md` is the single-page top-to-bottom install + day-to-day usage doc — links to both bootstrap docs.
- **Status:** ALPHA (v0.1.2-alpha) — paired with Maya side v0.1.2-alpha. v0.1.2 blocker-closure pass (CP004/CP005/CP009) completed 2026-05-18.
- **Description:** Toolbar icon (or Tools menu entry) -> single window with three actions: (0) **INSTALL STARTUP HOOK INTO ACTIVE PROJECT** — one-shot per UE project, copies init_unreal.py. (1) **CONFIGURE ACES (OCIO ASSET + VIEWPORT)** — Phase 1+2 of the real ACES automation: creates an `OpenColorIOConfiguration` asset at `/Game/OCIO/OCIO_ACES_1_2` from `$OCIO`, populates `desired_color_spaces` (ACES - ACEScg + Utility - Linear - sRGB) and `desired_display_views` (display=`ACES` / view=`sRGB`), probes viewport activation via `OpenColorIOEditorBlueprintLibrary`. Full step log written to `J:\tmp\pxl_aces_LATEST.txt`. **CP009:** if OpenColorIO plugin is missing, the configurator auto-edits the active `.uproject` to enable it (with `.pxl_bak` backup) and prompts UE restart. (2) **IMPORT .PXLBRIDGE** — pick a `.pxlbridge.json` manifest produced by the Maya MU Bridge tool, ingest the sibling FBX + textures with correct color space (sRGB / Linear / ACEScg / Raw), flip Green on normal maps (Maya OpenGL -> UE DirectX), build a `MaterialInstanceConstant` parented to `M_PXL_PBR_Master`, bind to mesh slots.
- **Direction (V0.1):** Maya -> Unreal only. Reverse direction and utility-node translation (aiColorCorrect, aiMultiply, hsvToRgb) deferred to V0.2+ (v0.2 runs in parallel with v0.1.5 hardening per the 2026-05-18 plan).
- **Bootstrap surface (now all bridge-assisted):** (1) `init_unreal.py` — one-click install button in the UI. (2) `M_PXL_PBR_Master.uasset` — author once per `BOOTSTRAP_MASTER_MATERIAL.md`, programmatic DIAGNOSTIC fallback covers users who haven't. (3) OpenColorIO plugin — `.uproject` auto-edit with restart prompt (CP009). (4) `W_MUBridge_Toolbar` EUW — author once per `BOOTSTRAP_EUW_TOOLBAR.md`, Tools-menu fallback always present.
- **ACES automation phases (V0.1.2+):** Phase 1 (v0.1.2 DONE) creates the OCIOConfiguration asset. Phase 2 (v0.1.2 probe-stage in `_step_9_enable_viewport`, locks down in v0.1.3) applies it to the viewport via `unreal.OpenColorIOEditorBlueprintLibrary`. Phase 3 (v0.1.4) writes `WorkingColorSpace` + `WorkingColorSpaceChoice` INI keys. Phase 4 (PPV tonemapping) **skipped — out of bridge scope per 2026-05-18 decision**. v0.1.5 is the production-hardening phase (pytest suite, central logging, path normalisation audit).
- **V0.2 roadmap:** custom MU Bridge Slate icon (replaces stock MaterialInstance icon), Material Instance browser inside the window, reverse direction (Unreal -> Maya), utility-node translation.

### Claude for Unreal
- **File:** `unreal/python/claude_for_unreal.py`
- **Status:** ALPHA (v0.2.0-alpha) — Resume at CP003
- **Description:** AI agent integrated into Unreal Engine 5.6 via TCP socket. Enforces THINKING/EXECUTING mode separation and four-phase creative pipeline.
