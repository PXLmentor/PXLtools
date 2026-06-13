"""
PXLtools — drag-and-drop installer for Maya.

HOW TO USE: drag this file from a file browser into a running Maya viewport.
It downloads the latest PXLtools release from GitHub and installs it as a Maya
module (and wires the Nuke toolbox), then builds the PXLtools shelf. Re-dragging
it later UPDATES to the newest release (the previous install is archived).

No dependencies — pure Python 3 stdlib (Maya 2025 = 3.11). Public repo, so no
token needed. Internet required at install time.
"""
import json
import os
import shutil
import ssl
import sys
import tempfile
import urllib.request
import zipfile

REPO          = "PXLmentor/PXLtools"
API_LATEST    = "https://api.github.com/repos/{}/releases/latest".format(REPO)
API_ALL       = "https://api.github.com/repos/{}/releases".format(REPO)
CODE_ASSET    = "PXLtools-code"      # zip name prefix
SHELF_MODULE  = "PXLtools_Setup_Shelf"


# ── GitHub release discovery ──────────────────────────────────────────────────

def _get_json(url):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "PXLtools-Installer"})
    with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def _latest_release():
    """Prefer the latest STABLE release; fall back to the newest prerelease so the
    installer also works while only betas exist."""
    try:
        return _get_json(API_LATEST)              # newest non-prerelease
    except Exception:
        rels = _get_json(API_ALL)
        if not rels:
            raise RuntimeError("No PXLtools releases found on GitHub yet.")
        return rels[0]                            # newest of any kind (incl prerelease)


def _code_zip_url(release):
    for a in release.get("assets", []):
        if a["name"].startswith(CODE_ASSET) and a["name"].endswith(".zip"):
            return a["browser_download_url"], a["name"]
    raise RuntimeError("Release {} has no {} zip.".format(release.get("tag_name"), CODE_ASSET))


def _download(url, dest):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "PXLtools-Installer"})
    with urllib.request.urlopen(req, context=ctx, timeout=120) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)


# ── install ───────────────────────────────────────────────────────────────────

def _maya_modules_dir():
    import maya.cmds as cmds
    # ~/Documents/maya/modules (version-independent, always on MAYA_MODULE_PATH)
    app_dir = cmds.internalVar(userAppDir=True)          # .../Documents/maya/
    d = os.path.join(app_dir, "modules")
    os.makedirs(d, exist_ok=True)
    return d


def _write_mod(modules_dir, module_root, version):
    """Write PXLtools.mod registering the module's scripts + icons paths."""
    mod_path = os.path.join(modules_dir, "PXLtools.mod")
    rel = os.path.relpath(module_root, modules_dir).replace("\\", "/")
    lines = [
        "+ PXLtools {} {}".format(version, rel),
        "scripts: maya/scripts",
        "icons: maya/icons",
        "PYTHONPATH +:= maya/scripts",
        "XBMLANGPATH +:= maya/icons",
        "",
    ]
    with open(mod_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return mod_path


def _archive_existing(path):
    if os.path.exists(path):
        bak = path + "_OLD"
        if os.path.exists(bak):
            shutil.rmtree(bak, ignore_errors=True)
        shutil.move(path, bak)


def _install_maya(extracted, version):
    import maya.cmds as cmds
    modules_dir = _maya_modules_dir()
    module_root = os.path.join(modules_dir, "PXLtools")
    _archive_existing(module_root)
    # the extracted code zip has maya/ and nuke/ at its top; the Maya module wants
    # maya/scripts + maya/icons under module_root.
    os.makedirs(module_root, exist_ok=True)
    shutil.copytree(os.path.join(extracted, "maya"), os.path.join(module_root, "maya"), dirs_exist_ok=True)
    if os.path.isfile(os.path.join(extracted, "manifest.json")):
        shutil.copy2(os.path.join(extracted, "manifest.json"), os.path.join(module_root, "manifest.json"))
    _write_mod(modules_dir, module_root, version)

    # Make the new scripts importable THIS session (so the shelf builds now,
    # before the .mod takes effect on next Maya launch).
    scripts = os.path.join(module_root, "maya", "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    # icons available this session too
    cmds.internalVar(userAppDir=True)
    os.environ["XBMLANGPATH"] = os.path.join(module_root, "maya", "icons") + os.pathsep + os.environ.get("XBMLANGPATH", "")

    # Build the shelf
    import importlib
    if SHELF_MODULE in sys.modules:
        importlib.reload(sys.modules[SHELF_MODULE])
    else:
        __import__(SHELF_MODULE)
    return module_root


def _install_nuke(extracted):
    """Copy the Nuke toolbox to ~/.nuke/PXLtools and ensure init.py/menu.py at ~/.nuke."""
    nuke_src = os.path.join(extracted, "nuke")
    if not os.path.isdir(nuke_src):
        return None
    home_nuke = os.path.join(os.path.expanduser("~"), ".nuke")
    os.makedirs(home_nuke, exist_ok=True)
    tb = os.path.join(home_nuke, "PXLtools")
    _archive_existing(tb)
    os.makedirs(tb, exist_ok=True)
    for sub in ("scripts", "icons"):
        s = os.path.join(nuke_src, sub)
        if os.path.isdir(s):
            shutil.copytree(s, os.path.join(tb, sub), dirs_exist_ok=True)
    # init.py / menu.py at ~/.nuke root (Nuke auto-runs these)
    for f in ("init.py", "menu.py"):
        s = os.path.join(nuke_src, f)
        if os.path.isfile(s):
            shutil.copy2(s, os.path.join(home_nuke, f))
    return tb


def install():
    import maya.cmds as cmds
    try:
        rel = _latest_release()
        version = rel.get("tag_name", "?").lstrip("v")
        url, name = _code_zip_url(rel)
        tmp = tempfile.mkdtemp(prefix="pxltools_")
        zpath = os.path.join(tmp, name)
        _download(url, zpath)
        extracted = os.path.join(tmp, "extracted")
        with zipfile.ZipFile(zpath, "r") as zf:
            zf.extractall(extracted)

        module_root = _install_maya(extracted, version)
        nuke_tb = _install_nuke(extracted)

        msg = ("PXLtools v{} installed.\n\n"
               "Maya module: {}\n"
               "Nuke toolbox: {}\n\n"
               "The PXLtools shelf is ready. (Nuke picks up its menu on next launch.)\n"
               "Tip: use the shelf Update button for future releases."
               ).format(version, module_root, nuke_tb or "(skipped)")
        cmds.confirmDialog(title="PXLtools Installer", message=msg, button=["Great"])
        try:
            cmds.inViewMessage(amg="PXLtools v{} installed.".format(version),
                               pos="midCenter", fade=True)
        except Exception:
            pass
    except Exception as exc:
        try:
            cmds.confirmDialog(title="PXLtools Installer — failed",
                               message="Install failed:\n\n{}".format(exc), button=["OK"])
        except Exception:
            print("PXLtools install failed:", exc)
        raise


# Maya calls this automatically when the file is dragged into the viewport.
def onMayaDroppedPythonFile(*args):
    install()


# Also runnable directly (Script Editor): exec/import this file.
if __name__ == "__main__":
    try:
        import maya.cmds  # noqa: F401
        install()
    except ImportError:
        print("Run this inside Maya (drag it into the viewport).")
