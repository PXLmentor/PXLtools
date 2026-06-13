# PXLmentor MU Bridge - UE 5.6 OCIO/ACES API probe
#
# WHAT IT DOES
#   The UE 5.6 OCIO + ACES configuration Python API is largely undocumented.
#   This script probes the actual API surface in YOUR UE 5.6 install and
#   dumps the result so we can build the real ACES configurator (V0.1.2)
#   against APIs that are confirmed to exist.
#
# HOW TO RUN (in your UE 5.6 editor)
#   1. Window -> Python -> Python Console
#   2. Run:
#        exec(open(r'J:\ClaudeCode\projects\PXLtools\unreal\python\probe_ocio_api.py').read())
#   3. Window -> Output Log
#   4. Filter by "PXL OCIO PROBE"
#   5. Copy ALL lines starting with "[PXL OCIO PROBE]" and send back
#
# WHAT YOU'RE LOOKING FOR IN THE OUTPUT
#   - Which OCIO classes / factories / subsystems actually exist
#   - What methods they expose (the real API surface)
#   - Whether the engine-shipped ACES 1.3 config is present
#   - Whether DefaultEngine.ini already has any working-color-space key
#
# Author: PXLmentor AI Pipeline TD

import sys
import inspect
import traceback
from pathlib import Path

import unreal


_TAG = "[PXL OCIO PROBE]"

# Bulletproof output: write to a fixed text file so you do not have to hunt
# for the Output Log. After the probe runs, just open this file.
_OUT_FILE = Path(r"J:\tmp\pxl_probe_LATEST.txt")
_OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
_LINES = []  # accumulates every line for the file dump at the end


def _log(msg=""):
    line = "{} {}".format(_TAG, msg)
    _LINES.append(line)
    try:
        unreal.log(line)
    except Exception:
        pass
    try:
        print(line)
    except Exception:
        pass


def _err(msg):
    line = "{} ERROR: {}".format(_TAG, msg)
    _LINES.append(line)
    try:
        unreal.log_error(line)
    except Exception:
        pass
    try:
        print(line)
    except Exception:
        pass


def _section(title):
    _log("")
    _log("=" * 60)
    _log(title)
    _log("=" * 60)


def _probe_class(cls):
    """Dump the methods + attributes of a class (limited to public symbols)."""
    if cls is None:
        _log("  (class is None)")
        return
    name = getattr(cls, "__name__", repr(cls))
    _log("  class: {}".format(name))
    try:
        members = sorted(set(dir(cls)))
    except Exception:
        members = []
    for m in members:
        if m.startswith("_"):
            continue
        try:
            attr = getattr(cls, m)
        except Exception:
            continue
        kind = "fn  " if callable(attr) else "attr"
        _log("    {} {}".format(kind, m))


def _exists(path: str) -> str:
    p = Path(path)
    return "EXISTS" if p.exists() else "MISSING"


def run_probe():
    _section("OCIO ENV VAR (THE config we will import as the UE OCIO asset)")
    import os
    ocio_env = os.environ.get("OCIO", "")
    if not ocio_env:
        _log("$OCIO is NOT SET. The V0.1.2 configurator REQUIRES this env var.")
        _log("Set it to the absolute path of your config.ocio (e.g. an ACES 1.2 or")
        _log("Studio Config v2 config file), restart UE, then re-run.")
    else:
        _log("$OCIO = {}".format(ocio_env))
        _log("file exists: {}".format(Path(ocio_env).exists()))
        try:
            sz = Path(ocio_env).stat().st_size
            _log("file size  : {} bytes".format(sz))
        except Exception:
            _log("file size  : <unreadable>")

    _section("UE VERSION + ENGINE PATHS")
    try:
        _log("ue version    : {}".format(unreal.SystemLibrary.get_engine_version()))
    except Exception:
        _err("could not read engine version")
    try:
        _log("project dir   : {}".format(unreal.SystemLibrary.get_project_directory()))
    except Exception:
        pass
    try:
        _log("project content: {}".format(unreal.SystemLibrary.get_project_content_directory()))
    except Exception:
        pass

    # --- engine-shipped OCIO configs (info only - V0.1.2 will NOT use these;
    #     we import whatever $OCIO points at instead so the UE side and the
    #     Maya side share the same config) ---
    _section("SHIPPED OCIO CONFIGS (informational - not used by configurator)")
    candidates = [
        r"C:\Program Files\Epic Games\UE_5.6\Engine\Plugins\Compositing\OpenColorIO\Content\Config\ACES_1.3\config.ocio",
        r"C:\Program Files\Epic Games\UE_5.6\Engine\Plugins\OpenColorIO\Content",
        r"C:\Program Files\Epic Games\UE_5.6\Engine\Plugins\Compositing\OpenColorIO\Content",
    ]
    for c in candidates:
        _log("{}  -> {}".format(_exists(c), c))

    # --- OpenColorIO plugin classes ---
    _section("OPENCOLORIO CLASSES IN unreal.*")
    ocio_class_names = [
        "OpenColorIOConfiguration",
        "OpenColorIOColorSpace",
        "OpenColorIOColorConversionSettings",
        "OpenColorIODisplayConfiguration",
        "OpenColorIOLibrary",
        "OpenColorIOConfigurationFactory",
        "OpenColorIOConfigurationFactoryNew",
        "OpenColorIODisplayExtensionSettings",
    ]
    for cls_name in ocio_class_names:
        cls = getattr(unreal, cls_name, None)
        if cls is None:
            _log("MISSING  unreal.{}".format(cls_name))
        else:
            _log("PRESENT  unreal.{}".format(cls_name))
            _probe_class(cls)

    # --- OCIO subsystems ---
    _section("OPENCOLORIO SUBSYSTEMS")
    subsystem_names = [
        "OpenColorIOConfigurationSubsystem",
        "OpenColorIOEditorSubsystem",
        "OpenColorIORuntimeSubsystem",
    ]
    for sub_name in subsystem_names:
        cls = getattr(unreal, sub_name, None)
        if cls is None:
            _log("MISSING  unreal.{}".format(sub_name))
            continue
        _log("PRESENT  unreal.{}".format(sub_name))
        _probe_class(cls)
        # Try to instance it
        try:
            inst = unreal.get_engine_subsystem(cls)
            _log("  engine subsystem instance: {}".format(inst))
        except Exception:
            try:
                inst = unreal.get_editor_subsystem(cls)
                _log("  editor subsystem instance: {}".format(inst))
            except Exception:
                _log("  could not get subsystem instance")

    # --- AssetImportTask + factory discovery ---
    _section("ASSET IMPORT TASK + OCIO FACTORY DISCOVERY")
    try:
        task = unreal.AssetImportTask()
        _log("AssetImportTask attributes:")
        for m in sorted(set(dir(task))):
            if m.startswith("_"):
                continue
            _log("    {}".format(m))
    except Exception:
        _err("could not create AssetImportTask:\n" + traceback.format_exc())

    # --- All unreal.* symbols matching OCIO / OpenColorIO ---
    _section("ALL unreal.* SYMBOLS MATCHING /opencolorio|ocio/i")
    try:
        matches = [n for n in dir(unreal) if "color" in n.lower() and ("io" in n.lower() or "ocio" in n.lower())]
        for n in sorted(set(matches)):
            _log("  unreal.{}".format(n))
    except Exception:
        _err("dir(unreal) failed")

    # --- Working Color Space - ini probe ---
    _section("DEFAULT ENGINE INI - WORKING COLOR SPACE KEYS")
    try:
        proj_dir = Path(unreal.SystemLibrary.get_project_directory())
        ini = proj_dir / "Config" / "DefaultEngine.ini"
        _log("ini path: {}".format(ini))
        _log("ini exists: {}".format(ini.exists()))
        if ini.exists():
            import configparser
            cp = configparser.ConfigParser(strict=False, interpolation=None)
            cp.optionxform = str
            try:
                cp.read(str(ini), encoding="utf-8")
            except Exception:
                _err("could not parse ini")
            section = "/Script/Engine.RendererSettings"
            if cp.has_section(section):
                _log("section [{}] present".format(section))
                for k in ("WorkingColorSpaceChoice", "WorkingColorSpace", "r.WorkingColorSpace"):
                    val = cp.get(section, k) if cp.has_option(section, k) else "<not set>"
                    _log("  {} = {}".format(k, val))
            else:
                _log("section [{}] MISSING".format(section))
    except Exception:
        _err("ini probe failed:\n" + traceback.format_exc())

    # --- RendererSettings class for set_editor_property feasibility ---
    _section("RendererSettings PYTHON API")
    cls = getattr(unreal, "RendererSettings", None)
    if cls is None:
        _log("unreal.RendererSettings MISSING - cannot use set_editor_property route")
    else:
        _probe_class(cls)
        try:
            settings = unreal.get_mutable_default(cls)
            _log("get_mutable_default instance: {}".format(settings))
        except Exception:
            _err("get_mutable_default failed:\n" + traceback.format_exc())

    # --- PostProcessVolume - OCIO-related properties ---
    _section("PostProcessVolume OCIO-RELATED PROPERTIES")
    cls = getattr(unreal, "PostProcessVolume", None)
    if cls is None:
        _log("unreal.PostProcessVolume MISSING")
    else:
        _log("PostProcessVolume props with 'color' or 'ocio' or 'tonemap':")
        for m in sorted(set(dir(cls))):
            if m.startswith("_"):
                continue
            ml = m.lower()
            if any(t in ml for t in ("ocio", "color", "tonemap")):
                _log("  {}".format(m))

    # --- PostProcessSettings struct - OCIO-related fields ---
    _section("PostProcessSettings STRUCT FIELDS RELATED TO OCIO")
    pps = getattr(unreal, "PostProcessSettings", None)
    if pps is None:
        _log("unreal.PostProcessSettings MISSING")
    else:
        try:
            inst = unreal.PostProcessSettings()
            for m in sorted(set(dir(inst))):
                if m.startswith("_"):
                    continue
                ml = m.lower()
                if any(t in ml for t in ("ocio", "color_grading", "tonemap")):
                    _log("  {}".format(m))
        except Exception:
            _err("could not instance PostProcessSettings")

    _log("")
    _log("DONE. Probe output saved to: {}".format(_OUT_FILE))


# Run the probe with a hard outer try/except so even a catastrophic failure
# still produces a readable file the user can send back.
try:
    run_probe()
except Exception:
    import traceback as _tb
    _err("UNHANDLED EXCEPTION IN PROBE:")
    for line in _tb.format_exc().splitlines():
        _err(line)

# Always dump to the text file, even on error.
try:
    _OUT_FILE.write_text("\n".join(_LINES), encoding="utf-8")
except Exception:
    pass

# Show a dialog so the user knows the probe finished and where to find the file.
try:
    unreal.EditorDialog.show_message(
        title="PXL OCIO Probe finished",
        message=(
            "Probe complete.\n\n"
            "Output saved to:\n  {}\n\n"
            "Open that file, copy everything, and send it back."
        ).format(_OUT_FILE),
        message_type=unreal.AppMsgType.OK,
        default_value=unreal.AppReturnType.OK,
    )
except Exception:
    pass

# Belt-and-braces: also print the file path to the Python Console.
try:
    print("\n>>> PXL OCIO Probe wrote {} <<<\n".format(_OUT_FILE))
except Exception:
    pass
