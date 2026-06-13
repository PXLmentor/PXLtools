# Tool Name: PXLmentor MU Bridge - ACES Configurator (Phase 1+2: OCIO Asset + Viewport)
# Version: 0.1.2-alpha
# Author: PXLmentor AI Pipeline TD
# Description: User-triggered "CONFIGURE ACES (OCIO ASSET)" action. Creates an
#              OpenColorIOConfiguration asset in the Content Browser at
#              /Game/OCIO/OCIO_Project, points it at the OCIO config file
#              referenced by the $OCIO environment variable, then populates
#              its desired_color_spaces (ACES - ACEScg + Utility - Linear - sRGB)
#              and desired_display_views (display='ACES' / view='ACES - sRGB').
#              The configurator is DEFENSIVE: every set_editor_property goes
#              through _safe_set and the full step log is written to
#              J:\tmp\pxl_aces_LATEST.txt regardless of success or failure -
#              the user does not have to hunt the Output Log.
# Changelog:
#   0.1.2-alpha - CP009: _step_1_plugin_check now auto-enables OpenColorIO via
#                 .uproject edit when the plugin class is missing. Uses
#                 unreal.Paths.get_project_file_path() to locate the .uproject,
#                 parses the JSON, inserts or flips
#                 {"Name": "OpenColorIO", "Enabled": true} in the Plugins[]
#                 array, writes the file back, and prompts the user to restart
#                 UE so the editor process picks up the new plugin set. Falls
#                 back to the pure-instruction dialog if the .uproject cannot
#                 be located, parsed, or written. Reference schema:
#                 https://dev.epicgames.com/documentation/en-us/unreal-engine/uplugin-file
#   0.1.2-alpha - CP008: Removed the call to
#                 unreal.EditorAssetLibrary.refresh_asset_directories in
#                 _step_8_save. That method does not exist in UE 5.6.1; the
#                 AttributeError was non-fatal but cluttered the status file
#                 (visible in pxl_aces_LATEST.txt line 53-58). UE auto-refreshes
#                 the Content Browser when save_loaded_asset succeeds.
#   0.1.2-alpha - CP007: User feedback on CP003 first run:
#                 (a) renamed asset OCIO_Project -> OCIO_ACES_1_2 (user pref)
#                 (b) display view view name was wrong - changed
#                     display='ACES'/view='ACES - sRGB' -> display='ACES'/view='sRGB'
#                 (c) added Step 9: VIEWPORT OCIO activation via
#                     unreal.OpenColorIOEditorBlueprintLibrary - tries multiple
#                     likely method names defensively, logs every attempt.
#                 (d) added a probe step that lists available color spaces +
#                     display/view names exposed by OpenColorIOEditorBlueprintLibrary,
#                     so if a name is still wrong the log reveals what IS valid.
#   0.1.2-alpha - CP003: Phase 1 rewrite. Replaced the v0.1.1 INI-only stub
#                 with a real OCIOConfiguration asset pipeline driven by
#                 the $OCIO env var. Plugin presence is detected (not
#                 auto-enabled). Status file pattern matches init_unreal.py
#                 and probe_ocio_api.py.
#   0.1.1-alpha - CP002: INI-only stub (revoked). Wrote WorkingColorSpaceChoice
#                 instead of WorkingColorSpace - one of two wrong-ish keys.
#                 Did NOT create an OCIO asset, did NOT touch viewport.
#   0.1.0-alpha - CP001: Initial INI-only scaffold.
#
# NEXT PHASES (not in this file yet):
#   Phase 2 - apply the new OCIO Configuration to the viewport via
#             unreal.OpenColorIOEditorBlueprintLibrary.
#   Phase 3 - write WorkingColorSpace + WorkingColorSpaceChoice INI keys.
#   Phase 4 - optional Post Process Volume tonemapping wiring.

from __future__ import annotations

import json
import logging
import os
import traceback
from pathlib import Path
from typing import Any, List, Optional

import unreal  # noqa: F401  - injected by the Unreal Editor Python runtime

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ASSET_PACKAGE_PATH = "/Game/OCIO"
ASSET_NAME         = "OCIO_ACES_1_2"          # CP007: was OCIO_Project
ASSET_FULL_PATH    = "{}/{}".format(ASSET_PACKAGE_PATH, ASSET_NAME)

# Names the user confirmed for their D:\_OCIO\aces_1.2\config.ocio.
DESIRED_COLOR_SPACE_NAMES: List[str] = [
    "ACES - ACEScg",
    "Utility - Linear - sRGB",
]
# CP007: view was 'ACES - sRGB' which produced an invalid entry. The actual
# view under the 'ACES' display in ACES 1.2 Academy is just 'sRGB'.
DESIRED_DISPLAY_VIEW = {
    "display": "ACES",
    "view":    "sRGB",
}
# Viewport source color space (the working space we render in).
VIEWPORT_SOURCE_COLOR_SPACE = "ACES - ACEScg"

STATUS_FILE = Path(r"J:\tmp\pxl_aces_LATEST.txt")


# ---------------------------------------------------------------------------
# Logging helpers (tee to unreal.log + print + status file)
# ---------------------------------------------------------------------------

class _Log:
    """Accumulating logger so we can dump everything to a single file at the end."""

    TAG = "[PXL ACES]"

    def __init__(self) -> None:
        self.lines: List[str] = []

    def __call__(self, msg: str = "") -> None:
        line = "{} {}".format(self.TAG, msg)
        self.lines.append(line)
        try: unreal.log(line)
        except Exception: pass
        try: print(line)
        except Exception: pass

    def err(self, msg: str) -> None:
        line = "{} ERROR: {}".format(self.TAG, msg)
        self.lines.append(line)
        try: unreal.log_error(line)
        except Exception: pass
        try: print(line)
        except Exception: pass

    def section(self, title: str) -> None:
        self("")
        self("=" * 60)
        self(title)
        self("=" * 60)

    def write_file(self) -> None:
        try:
            STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
            STATUS_FILE.write_text("\n".join(self.lines), encoding="utf-8")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Defensive setter helper
# ---------------------------------------------------------------------------

def _safe_set(obj: Any, prop: str, value: Any, log: _Log) -> bool:
    """set_editor_property wrapped in try/except. Returns True on success.

    Logs both successes and failures so the status file shows exactly which
    Editor properties resolved vs which silently disappeared - the only way
    to deal with UE's undocumented Python API surface.
    """
    try:
        obj.set_editor_property(prop, value)
        log("ok  : {}.{} = {!r}".format(type(obj).__name__, prop, value))
        return True
    except Exception as exc:
        log.err("FAIL set {}.{} = {!r} - {}".format(
            type(obj).__name__, prop, value, exc,
        ))
        return False


def _safe_call(obj: Any, method_name: str, log: _Log, *args, **kwargs) -> Any:
    """Call an instance method with try/except + logging."""
    fn = getattr(obj, method_name, None)
    if fn is None:
        log.err("missing method {}.{}".format(type(obj).__name__, method_name))
        return None
    try:
        result = fn(*args, **kwargs)
        log("ok  : {}.{}() -> {!r}".format(type(obj).__name__, method_name, result))
        return result
    except Exception as exc:
        log.err("FAIL {}.{}() - {}".format(type(obj).__name__, method_name, exc))
        return None


# ---------------------------------------------------------------------------
# Confirm-overwrite dialog
# ---------------------------------------------------------------------------

def _confirm_overwrite(log: _Log) -> bool:
    """Prompt before overwriting an existing /Game/OCIO/OCIO_Project asset."""
    try:
        reply = unreal.EditorDialog.show_message(
            title="MU Bridge - OCIO asset already exists",
            message=(
                "An OCIOConfiguration asset already exists at:\n"
                "  {}\n\n"
                "OK  - delete the existing asset and rebuild it\n"
                "Cancel - leave existing asset alone, do nothing"
            ).format(ASSET_FULL_PATH),
            message_type=unreal.AppMsgType.OK_CANCEL,
            default_value=unreal.AppReturnType.CANCEL,
        )
        chosen = (reply == unreal.AppReturnType.OK)
        log("overwrite confirm dialog: {}".format("OK" if chosen else "CANCEL"))
        return chosen
    except Exception:
        log.err("could not show overwrite dialog:\n" + traceback.format_exc())
        return False


# ---------------------------------------------------------------------------
# The 8 steps
# ---------------------------------------------------------------------------

def _auto_enable_ocio_in_uproject(log: _Log) -> bool:
    """CP009: edit the active .uproject to enable OpenColorIO.

    Returns True if the .uproject was modified (caller prompts restart).
    Returns False if no edit was needed (already enabled) or if the edit
    failed (caller falls back to the pure-instruction dialog).

    Reference: https://dev.epicgames.com/documentation/en-us/unreal-engine/uplugin-file
    Plugins[] entries are {"Name": "<str>", "Enabled": <bool>}.
    """
    try:
        uproject_path_str = unreal.Paths.get_project_file_path()
    except Exception:
        log.err("unreal.Paths.get_project_file_path() failed:\n" + traceback.format_exc())
        return False

    uproject = Path(uproject_path_str)
    log("uproject path: {}".format(uproject))
    if not uproject.is_file():
        log.err("uproject does not exist on disk - cannot auto-enable.")
        return False

    try:
        raw = uproject.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception:
        log.err("Could not parse uproject JSON:\n" + traceback.format_exc())
        return False

    plugins = data.get("Plugins")
    if plugins is None:
        plugins = []
        data["Plugins"] = plugins
        log("uproject had no Plugins[] - creating it.")
    elif not isinstance(plugins, list):
        log.err("uproject Plugins field is not a list - refusing to edit.")
        return False

    # Look for existing entry (case-insensitive name match).
    existing_idx = None
    for i, entry in enumerate(plugins):
        if not isinstance(entry, dict):
            continue
        name = entry.get("Name")
        if isinstance(name, str) and name.lower() == "opencolorio":
            existing_idx = i
            break

    if existing_idx is not None:
        entry = plugins[existing_idx]
        if entry.get("Enabled") is True:
            log("ok  : Plugins[] already has OpenColorIO Enabled:true - no edit needed.")
            return False
        log("found existing OpenColorIO entry with Enabled={}; flipping to true.".format(
            entry.get("Enabled"),
        ))
        entry["Enabled"] = True
    else:
        log("OpenColorIO not in Plugins[] - inserting {Name: OpenColorIO, Enabled: true}.")
        plugins.append({"Name": "OpenColorIO", "Enabled": True})

    # Backup the .uproject once (per session) before writing.
    backup = uproject.with_suffix(uproject.suffix + ".pxl_bak")
    try:
        if not backup.exists():
            backup.write_text(raw, encoding="utf-8")
            log("backup written: {}".format(backup.name))
    except Exception:
        log.err("could not write backup (non-fatal):\n" + traceback.format_exc())

    try:
        # UE's own .uproject is 2-space indented, trailing newline. Match it.
        new_text = json.dumps(data, indent=2) + "\n"
        uproject.write_text(new_text, encoding="utf-8")
        log("ok  : uproject saved with OpenColorIO Enabled:true.")
        return True
    except Exception:
        log.err("could not write uproject:\n" + traceback.format_exc())
        return False


def _step_1_plugin_check(log: _Log) -> bool:
    log.section("Step 1 - OpenColorIO plugin check")
    cls = getattr(unreal, "OpenColorIOConfiguration", None)
    if cls is not None:
        log("ok  : unreal.OpenColorIOConfiguration present (plugin enabled).")
        return True

    log.err(
        "unreal.OpenColorIOConfiguration is missing. The OpenColorIO plugin is "
        "not enabled. CP009 will try to auto-enable it by editing the .uproject."
    )

    auto_ok = _auto_enable_ocio_in_uproject(log)

    if auto_ok:
        try:
            unreal.EditorDialog.show_message(
                title="MU Bridge - OpenColorIO plugin auto-enabled",
                message=(
                    "MU Bridge edited your .uproject to enable the OpenColorIO "
                    "plugin. A backup of the original was saved next to it "
                    "with a .pxl_bak suffix.\n\n"
                    "RESTART Unreal Editor now so the plugin is loaded, then "
                    "re-run CONFIGURE ACES.\n\n"
                    "Full step log: {}"
                ).format(STATUS_FILE),
                message_type=unreal.AppMsgType.OK,
                default_value=unreal.AppReturnType.OK,
            )
        except Exception:
            log.err("restart dialog failed (non-fatal):\n" + traceback.format_exc())
        return False  # Always abort - UE must restart to load the plugin.

    # Auto-enable failed (uproject missing / unparseable / write failed).
    # Fall back to the pure-instruction dialog from CP003.
    try:
        unreal.EditorDialog.show_message(
            title="MU Bridge - OpenColorIO plugin not enabled",
            message=(
                "The OpenColorIO plugin is not enabled in this project, and "
                "MU Bridge could not auto-edit your .uproject (see the log for "
                "the reason). Enable it manually:\n\n"
                "1) Edit -> Plugins\n"
                "2) Search 'OpenColorIO'\n"
                "3) Tick Enabled\n"
                "4) Restart the editor\n"
                "5) Re-run CONFIGURE ACES.\n\n"
                "Full step log: {}"
            ).format(STATUS_FILE),
            message_type=unreal.AppMsgType.OK,
            default_value=unreal.AppReturnType.OK,
        )
    except Exception:
        pass
    return False


def _step_2_read_env(log: _Log) -> Optional[str]:
    log.section("Step 2 - read $OCIO environment variable")
    ocio_env = os.environ.get("OCIO", "")
    if not ocio_env:
        log.err("$OCIO is not set in the UE Editor process environment.")
        try:
            unreal.EditorDialog.show_message(
                title="MU Bridge - $OCIO not set",
                message=(
                    "The OCIO environment variable is not set in the UE editor's "
                    "process environment.\n\n"
                    "Set OCIO to the absolute path of your config.ocio file "
                    "(e.g. D:\\_OCIO\\aces_1.2\\config.ocio) at the OS level, "
                    "RESTART UE so the editor process inherits it, then re-run."
                ),
                message_type=unreal.AppMsgType.OK,
                default_value=unreal.AppReturnType.OK,
            )
        except Exception:
            pass
        return None
    log("$OCIO = {}".format(ocio_env))
    if not Path(ocio_env).exists():
        log.err("$OCIO points at a file that does not exist on disk.")
        try:
            unreal.EditorDialog.show_message(
                title="MU Bridge - $OCIO file missing",
                message=(
                    "$OCIO is set to:\n"
                    "  {}\n"
                    "but no file exists at that path."
                ).format(ocio_env),
                message_type=unreal.AppMsgType.OK,
                default_value=unreal.AppReturnType.OK,
            )
        except Exception:
            pass
        return None
    log("file exists, size: {} bytes".format(Path(ocio_env).stat().st_size))
    return ocio_env


def _step_3_create_asset(log: _Log) -> Optional["unreal.OpenColorIOConfiguration"]:
    log.section("Step 3 - create OCIOConfiguration asset")
    if unreal.EditorAssetLibrary.does_asset_exist(ASSET_FULL_PATH):
        log("asset already exists at {}".format(ASSET_FULL_PATH))
        if not _confirm_overwrite(log):
            log("user cancelled at overwrite prompt - aborting.")
            return None
        try:
            unreal.EditorAssetLibrary.delete_asset(ASSET_FULL_PATH)
            log("ok  : deleted prior asset")
        except Exception:
            log.err("could not delete prior asset:\n" + traceback.format_exc())
            return None

    factory_cls = getattr(unreal, "OpenColorIOConfigurationFactoryNew", None)
    if factory_cls is None:
        log.err("OpenColorIOConfigurationFactoryNew missing - cannot create asset.")
        return None
    factory = factory_cls()
    log("factory instantiated: {!r}".format(factory))

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    try:
        asset = asset_tools.create_asset(
            asset_name=ASSET_NAME,
            package_path=ASSET_PACKAGE_PATH,
            asset_class=unreal.OpenColorIOConfiguration,
            factory=factory,
        )
    except Exception:
        log.err("AssetTools.create_asset raised:\n" + traceback.format_exc())
        return None
    if asset is None:
        log.err("AssetTools.create_asset returned None - aborting.")
        return None
    log("ok  : created asset at {}".format(ASSET_FULL_PATH))
    return asset


def _step_4_set_configuration_file(
    asset: "unreal.OpenColorIOConfiguration",
    ocio_path: str,
    log: _Log,
) -> bool:
    log.section("Step 4 - point configuration_file at $OCIO")
    fp_cls = getattr(unreal, "FilePath", None)
    if fp_cls is None:
        log.err("unreal.FilePath struct missing - cannot wrap OCIO path.")
        return False
    fp = fp_cls()
    # The struct attribute is conventionally `file_path` in UE 5.6; if the
    # build differs, _safe_set logs the actual error.
    if not _safe_set(fp, "file_path", ocio_path, log):
        return False
    return _safe_set(asset, "configuration_file", fp, log)


def _step_5_reload_colorspaces(
    asset: "unreal.OpenColorIOConfiguration",
    log: _Log,
) -> bool:
    log.section("Step 5 - reload_existing_colorspaces (populate the catalog)")
    result = _safe_call(asset, "reload_existing_colorspaces", log)
    # reload_existing_colorspaces typically returns None on success; the lack
    # of an exception is the real success signal.
    return True


def _build_color_space(name: str, log: _Log) -> Optional["unreal.OpenColorIOColorSpace"]:
    cs_cls = getattr(unreal, "OpenColorIOColorSpace", None)
    if cs_cls is None:
        log.err("OpenColorIOColorSpace struct missing.")
        return None
    cs = cs_cls()
    if not _safe_set(cs, "color_space_name", name, log):
        return None
    return cs


def _step_6_desired_color_spaces(
    asset: "unreal.OpenColorIOConfiguration",
    log: _Log,
) -> bool:
    log.section("Step 6 - populate desired_color_spaces")
    built: List["unreal.OpenColorIOColorSpace"] = []
    for name in DESIRED_COLOR_SPACE_NAMES:
        cs = _build_color_space(name, log)
        if cs is not None:
            built.append(cs)
    if not built:
        log.err("no color spaces could be built - aborting Step 6.")
        return False
    log("built {} color space struct(s).".format(len(built)))
    return _safe_set(asset, "desired_color_spaces", built, log)


def _step_7_desired_display_views(
    asset: "unreal.OpenColorIOConfiguration",
    log: _Log,
) -> bool:
    log.section("Step 7 - populate desired_display_views")
    dv_cls = getattr(unreal, "OpenColorIODisplayView", None)
    if dv_cls is None:
        log.err("OpenColorIODisplayView struct missing.")
        return False
    dv = dv_cls()
    # Field names are the most likely shape; if UE 5.6 uses something else,
    # _safe_set surfaces the actual property name in the status file.
    ok_display = _safe_set(dv, "display", DESIRED_DISPLAY_VIEW["display"], log)
    ok_view    = _safe_set(dv, "view",    DESIRED_DISPLAY_VIEW["view"],    log)
    if not (ok_display and ok_view):
        log.err("display/view setters failed - check status file for actual property names.")
    return _safe_set(asset, "desired_display_views", [dv], log)


def _step_8_save(
    asset: "unreal.OpenColorIOConfiguration",
    log: _Log,
) -> bool:
    log.section("Step 8 - save OCIO Configuration asset")
    saved = False
    try:
        saved = bool(unreal.EditorAssetLibrary.save_loaded_asset(asset))
        log("save_loaded_asset returned: {}".format(saved))
    except Exception:
        log.err("save_loaded_asset raised:\n" + traceback.format_exc())

    # CP008: refresh_asset_directories() does not exist on EditorAssetLibrary
    # in UE 5.6.1 - removed (AttributeError was non-fatal but cluttered the
    # status file). save_loaded_asset triggers Content Browser refresh on its
    # own; no explicit refresh call is needed.
    return saved


def _step_9_enable_viewport(
    asset: "unreal.OpenColorIOConfiguration",
    log: _Log,
) -> bool:
    """Build an OpenColorIODisplayConfiguration and apply it to the viewport.

    Equivalent to: View Mode -> OCIO Display -> Enable, Source = ACEScg,
    Destination = ACES / sRGB. The Python API for the apply step
    (OpenColorIOEditorBlueprintLibrary) is undocumented in UE 5.6.1, so we
    probe + try multiple likely method names and log every attempt.
    """
    log.section("Step 9 - enable VIEWPORT OCIO Display Configuration")

    display_cfg_cls = getattr(unreal, "OpenColorIODisplayConfiguration", None)
    cs_cls          = getattr(unreal, "OpenColorIOColorConversionSettings", None)
    src_cs_cls      = getattr(unreal, "OpenColorIOColorSpace", None)
    dv_cls          = getattr(unreal, "OpenColorIODisplayView", None)
    bp_lib_cls      = getattr(unreal, "OpenColorIOEditorBlueprintLibrary", None)
    direction_enum  = getattr(unreal, "OpenColorIOViewTransformDirection", None)
    if not all([display_cfg_cls, cs_cls, src_cs_cls, dv_cls, bp_lib_cls]):
        log.err("missing class: display_cfg={} cs={} src_cs={} dv={} bp_lib={}".format(
            display_cfg_cls, cs_cls, src_cs_cls, dv_cls, bp_lib_cls,
        ))
        return False

    display_cfg = display_cfg_cls()
    _safe_set(display_cfg, "is_enabled", True, log)

    cs_settings = cs_cls()
    _safe_set(cs_settings, "configuration_source", asset, log)

    src_cs = src_cs_cls()
    _safe_set(src_cs, "color_space_name", VIEWPORT_SOURCE_COLOR_SPACE, log)
    _safe_set(cs_settings, "source_color_space", src_cs, log)

    dest_dv = dv_cls()
    _safe_set(dest_dv, "display", DESIRED_DISPLAY_VIEW["display"], log)
    _safe_set(dest_dv, "view",    DESIRED_DISPLAY_VIEW["view"],    log)
    _safe_set(cs_settings, "destination_display_view", dest_dv, log)

    if direction_enum is not None:
        forward_val = (
            getattr(direction_enum, "FORWARD", None)
            or getattr(direction_enum, "DISPLAY_VIEW_FORWARD", None)
        )
        if forward_val is not None:
            _safe_set(cs_settings, "display_view_direction", forward_val, log)
        else:
            log("OpenColorIOViewTransformDirection has no FORWARD value")

    _safe_set(display_cfg, "color_configuration", cs_settings, log)

    # Probe the BP library so we see what's available even when our guesses miss
    log("OpenColorIOEditorBlueprintLibrary callable methods:")
    available_methods = []
    for m in sorted(set(dir(bp_lib_cls))):
        if m.startswith("_"):
            continue
        attr = getattr(bp_lib_cls, m, None)
        if callable(attr):
            available_methods.append(m)
            log("  fn  {}".format(m))

    # Try the most likely method names in priority order
    candidates = [
        "set_active_viewport_configuration",
        "set_default_viewport_configuration",
        "set_viewport_display_configuration",
        "set_active_color_transform",
        "set_active_viewport_color_transform",
        "set_color_transform",
        "set_active_display_configuration",
    ]
    for method_name in candidates:
        method = getattr(bp_lib_cls, method_name, None)
        if method is None:
            continue
        try:
            result = method(display_cfg)
            log("OK  : OpenColorIOEditorBlueprintLibrary.{}(display_cfg) -> {!r}".format(
                method_name, result,
            ))
            return True
        except Exception as exc:
            log.err("FAIL {}.{}({}) -> {}".format(
                bp_lib_cls.__name__, method_name, "display_cfg", exc,
            ))

    log.err(
        "no viewport activation method accepted the display_cfg. "
        "Available methods are listed above - the right one is one of those; "
        "next CP will target it precisely."
    )
    return False


def _final_summary(
    ocio_path: str,
    saved: bool,
    viewport_ok: bool,
    log: _Log,
) -> None:
    fail_count = sum(1 for ln in log.lines if "ERROR:" in ln or "FAIL " in ln)
    if fail_count == 0:
        pass_marker = "OK"
    elif viewport_ok and saved:
        pass_marker = "ASSET OK / VIEWPORT OK (with {} probe miss(es))".format(fail_count)
    else:
        pass_marker = "WITH {} ISSUE(S)".format(fail_count)

    summary = (
        "ACES configurator finished: {}.\n\n"
        "  OCIO asset    : {}    saved: {}\n"
        "  OCIO config   : {}\n"
        "  Color spaces  : {}\n"
        "  Display view  : {} / {}\n"
        "  Viewport apply: {}\n\n"
        "Verify in Content Browser: double-click the asset and confirm the "
        "Desired Color Spaces + Desired Display Views dropdowns are resolved "
        "cleanly (not red).\n\n"
        "Verify in viewport: View Mode menu -> OCIO Display section at the "
        "bottom should show Enabled + source ACEScg + destination ACES / sRGB.\n\n"
        "Full step log: {}"
    ).format(
        pass_marker,
        ASSET_FULL_PATH, saved,
        ocio_path,
        ", ".join(DESIRED_COLOR_SPACE_NAMES),
        DESIRED_DISPLAY_VIEW["display"], DESIRED_DISPLAY_VIEW["view"],
        "OK" if viewport_ok else "FAILED (see log for available methods)",
        STATUS_FILE,
    )
    log("")
    log(summary)

    try:
        unreal.EditorDialog.show_message(
            title="MU Bridge - CONFIGURE ACES finished ({})".format(pass_marker),
            message=summary,
            message_type=unreal.AppMsgType.OK,
            default_value=unreal.AppReturnType.OK,
        )
    except Exception:
        log.err("final summary dialog failed (non-fatal):\n" + traceback.format_exc())


# ---------------------------------------------------------------------------
# Public entry - called by the MU Bridge window's CONFIGURE ACES button
# ---------------------------------------------------------------------------

def configure_acescg_interactive() -> None:
    """V0.1.2 Phase 1 entry. Creates the OCIO Configuration asset end-to-end.

    The name is kept for backward compatibility with the ui.py button binding.
    """
    log = _Log()
    log.section("MU Bridge - CONFIGURE ACES (OCIO + VIEWPORT) - v0.1.2-alpha CP009")
    try:
        if not _step_1_plugin_check(log):
            return

        ocio_path = _step_2_read_env(log)
        if ocio_path is None:
            return

        asset = _step_3_create_asset(log)
        if asset is None:
            return

        _step_4_set_configuration_file(asset, ocio_path, log)
        _step_5_reload_colorspaces(asset, log)
        _step_6_desired_color_spaces(asset, log)
        _step_7_desired_display_views(asset, log)
        saved = _step_8_save(asset, log)
        viewport_ok = _step_9_enable_viewport(asset, log)
        _final_summary(ocio_path, saved, viewport_ok, log)
    except Exception:
        log.err("UNHANDLED EXCEPTION:\n" + traceback.format_exc())
        try:
            unreal.EditorDialog.show_message(
                title="MU Bridge - CONFIGURE ACES failed",
                message=(
                    "Unhandled exception. See full traceback in:\n  {}"
                ).format(STATUS_FILE),
                message_type=unreal.AppMsgType.OK,
                default_value=unreal.AppReturnType.OK,
            )
        except Exception:
            pass
    finally:
        log.write_file()


# Backward-compat alias (in case any other module calls the new name):
configure_aces_ocio_asset = configure_acescg_interactive
