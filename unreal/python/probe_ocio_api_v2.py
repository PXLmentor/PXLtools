# PXLmentor MU Bridge - UE 5.6 OCIO/ACES API probe v2
#
# Focused follow-up to probe_ocio_api.py. Drills into the four classes that
# probe v1 confirmed exist and that we need to actually USE:
#   1. OpenColorIOEditorBlueprintLibrary  (sets viewport OCIO display config)
#   2. OpenColorIODisplayExtensionWrapper (display extension wiring)
#   3. OpenColorIODisplayView             (struct fields for display+view pair)
#   4. OpenColorIOViewTransformDirection  (enum values)
#
# Also exercises the actual OCIO asset creation path against your $OCIO file
# so we know that recipe works before we ship it inside the V0.1.2 tool.
#
# HOW TO RUN (same as v1)
#   In UE Python Console:
#     exec(open(r'J:\ClaudeCode\projects\PXLtools\unreal\python\probe_ocio_api_v2.py').read())
#
#   When it finishes a dialog will pop. The output file is:
#     J:\tmp\pxl_probe_v2_LATEST.txt
#   Open it and send back the contents.
#
# Author: PXLmentor AI Pipeline TD

import os
import sys
import traceback
from pathlib import Path

import unreal

_TAG = "[PXL OCIO PROBE v2]"
_OUT = Path(r"J:\tmp\pxl_probe_v2_LATEST.txt")
_OUT.parent.mkdir(parents=True, exist_ok=True)
_LINES = []


def _log(msg=""):
    line = "{} {}".format(_TAG, msg)
    _LINES.append(line)
    try: unreal.log(line)
    except Exception: pass
    try: print(line)
    except Exception: pass


def _err(msg):
    line = "{} ERROR: {}".format(_TAG, msg)
    _LINES.append(line)
    try: unreal.log_error(line)
    except Exception: pass
    try: print(line)
    except Exception: pass


def _section(title):
    _log("")
    _log("=" * 60)
    _log(title)
    _log("=" * 60)


def _dump_class(cls):
    if cls is None:
        _log("  (None)")
        return
    name = getattr(cls, "__name__", repr(cls))
    _log("  class: {}".format(name))
    for m in sorted(set(dir(cls))):
        if m.startswith("_"):
            continue
        try:
            attr = getattr(cls, m)
        except Exception:
            continue
        kind = "fn  " if callable(attr) else "attr"
        # For functions, attempt to grab the doc / signature
        sig = ""
        if callable(attr):
            doc = getattr(attr, "__doc__", "") or ""
            doc = doc.strip().splitlines()[0] if doc else ""
            if doc:
                sig = "  -- {}".format(doc[:140])
        _log("    {} {}{}".format(kind, m, sig))


def run():
    # --- 1. Editor BP Library for OCIO ---
    _section("OpenColorIOEditorBlueprintLibrary - the viewport-set API")
    cls = getattr(unreal, "OpenColorIOEditorBlueprintLibrary", None)
    _dump_class(cls)

    # --- 2. Display extension wrapper ---
    _section("OpenColorIODisplayExtensionWrapper - display extension wiring")
    cls = getattr(unreal, "OpenColorIODisplayExtensionWrapper", None)
    _dump_class(cls)

    # --- 3. Display/View struct ---
    _section("OpenColorIODisplayView - struct fields")
    cls = getattr(unreal, "OpenColorIODisplayView", None)
    _dump_class(cls)

    # --- 4. Direction enum values ---
    _section("OpenColorIOViewTransformDirection - enum values")
    cls = getattr(unreal, "OpenColorIOViewTransformDirection", None)
    if cls is None:
        _log("  MISSING")
    else:
        for m in sorted(set(dir(cls))):
            if m.startswith("_"):
                continue
            try:
                v = getattr(cls, m)
                _log("    {} = {}".format(m, v))
            except Exception:
                _log("    {} = <unreadable>".format(m))

    # --- 5. Actual OCIO asset creation against $OCIO ---
    _section("END-TO-END TEST: create an OCIOConfiguration asset from $OCIO")
    ocio_env = os.environ.get("OCIO", "")
    if not ocio_env or not Path(ocio_env).exists():
        _log("$OCIO not set or file missing - skipping creation test.")
    else:
        _log("Source config: {}".format(ocio_env))
        try:
            factory_cls = getattr(unreal, "OpenColorIOConfigurationFactoryNew", None)
            if factory_cls is None:
                _err("OpenColorIOConfigurationFactoryNew missing")
            else:
                factory = factory_cls()
                _log("factory instantiated: {}".format(factory))

                asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
                pkg_path = "/Game/_PXL_PROBE_OCIO"
                asset_name = "OCIO_FromEnv_PROBE"

                # Clean up any prior probe asset
                full = "{}/{}".format(pkg_path, asset_name)
                try:
                    if unreal.EditorAssetLibrary.does_asset_exist(full):
                        unreal.EditorAssetLibrary.delete_asset(full)
                        _log("deleted prior probe asset at {}".format(full))
                except Exception:
                    pass

                asset = asset_tools.create_asset(
                    asset_name=asset_name,
                    package_path=pkg_path,
                    asset_class=unreal.OpenColorIOConfiguration,
                    factory=factory,
                )
                _log("create_asset returned: {}".format(asset))

                if asset is not None:
                    # Set the configuration_file property to point at $OCIO
                    # The attribute is a FilePath struct
                    try:
                        fp = unreal.FilePath()
                        fp.set_editor_property("file_path", ocio_env)
                        asset.set_editor_property("configuration_file", fp)
                        _log("set configuration_file -> {}".format(ocio_env))
                    except Exception:
                        _err("could not set configuration_file:\n" + traceback.format_exc())

                    # Trigger reload of color spaces
                    try:
                        asset.reload_existing_colorspaces()
                        _log("reload_existing_colorspaces() ok")
                    except Exception:
                        _err("reload_existing_colorspaces failed:\n" + traceback.format_exc())

                    # Read back desired_color_spaces / desired_display_views
                    try:
                        dcs = asset.get_editor_property("desired_color_spaces")
                        _log("desired_color_spaces type: {} value: {!r}".format(type(dcs).__name__, dcs))
                    except Exception:
                        _err("could not read desired_color_spaces:\n" + traceback.format_exc())
                    try:
                        ddv = asset.get_editor_property("desired_display_views")
                        _log("desired_display_views type: {} value: {!r}".format(type(ddv).__name__, ddv))
                    except Exception:
                        _err("could not read desired_display_views:\n" + traceback.format_exc())

                    # Save and verify it's on disk
                    try:
                        ok = unreal.EditorAssetLibrary.save_loaded_asset(asset)
                        _log("save_loaded_asset returned: {}".format(ok))
                    except Exception:
                        _err("save failed:\n" + traceback.format_exc())

                    # Now read it back fresh
                    try:
                        reloaded = unreal.EditorAssetLibrary.load_asset(full)
                        _log("reload from disk: {}".format(reloaded))
                        fp2 = reloaded.get_editor_property("configuration_file")
                        _log("configuration_file after reload: {!r}".format(fp2))
                    except Exception:
                        _err("reload from disk failed:\n" + traceback.format_exc())

        except Exception:
            _err("end-to-end test crashed:\n" + traceback.format_exc())

    # --- 6. FilePath struct shape ---
    _section("FilePath struct (used for OCIOConfiguration.configuration_file)")
    cls = getattr(unreal, "FilePath", None)
    if cls is None:
        _log("MISSING")
    else:
        try:
            inst = cls()
            for m in sorted(set(dir(inst))):
                if m.startswith("_"):
                    continue
                _log("  {}".format(m))
        except Exception:
            _err("could not instance FilePath")

    _log("")
    _log("DONE. Output saved to: {}".format(_OUT))


try:
    run()
except Exception:
    _err("UNHANDLED:\n" + traceback.format_exc())

try:
    _OUT.write_text("\n".join(_LINES), encoding="utf-8")
except Exception:
    pass

try:
    unreal.EditorDialog.show_message(
        title="PXL OCIO Probe v2 finished",
        message="Output saved to:\n  {}\n\nOpen it and send back.".format(_OUT),
        message_type=unreal.AppMsgType.OK,
        default_value=unreal.AppReturnType.OK,
    )
except Exception:
    pass
