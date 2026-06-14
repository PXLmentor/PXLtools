"""
PXLtools — installer / updater for Maya AND Nuke.

MAYA:  drag this file from a file browser into a running Maya viewport.
       -> installs the Maya module + the Nuke toolbox + (prompted) the assets,
          and builds the PXLtools shelf. Re-drag to update.

NUKE:  Nuke can't run a dragged .py, so paste this ONE line into Nuke's Script
       Editor (Python) and run it — it installs/updates ONLY the Nuke side and
       rebuilds the PXLtools menu live (no restart):

         import urllib.request as u; exec(u.urlopen("https://github.com/PXLmentor/PXLtools/raw/main/INSTALL.py").read().decode())

No dependencies — pure Python 3 stdlib. Public repo, no token needed. Internet
required at install time.
"""
import json
import os
import shutil
import ssl
import sys
import tempfile
import urllib.request
import zipfile

REPO         = "PXLmentor/PXLtools"
API_LATEST   = "https://api.github.com/repos/{}/releases/latest".format(REPO)
API_ALL      = "https://api.github.com/repos/{}/releases".format(REPO)
CODE_ASSET   = "PXLtools-code"      # code zip name prefix
ASSET_PACK   = "PXLtools-assets"    # turntable scene/comp/HDRIs zip prefix
SHELF_MODULE = "PXLtools_Setup_Shelf"


# ── GitHub release discovery + download ───────────────────────────────────────

def _get_json(url):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "PXLtools-Installer"})
    with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def _latest_release():
    """Latest STABLE release; fall back to newest prerelease while only betas exist."""
    try:
        return _get_json(API_LATEST)
    except Exception:
        rels = _get_json(API_ALL)
        if not rels:
            raise RuntimeError("No PXLtools releases found on GitHub yet.")
        return rels[0]


def _asset_url(release, prefix):
    for a in release.get("assets", []):
        if a["name"].startswith(prefix) and a["name"].endswith(".zip"):
            return a["browser_download_url"], a["name"]
    return None, None


def _download(url, dest):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "PXLtools-Installer"})
    with urllib.request.urlopen(req, context=ctx, timeout=180) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)


def _fetch_release():
    """Download + extract the latest code zip. Returns (release, extracted_dir, version)."""
    rel = _latest_release()
    version = rel.get("tag_name", "?").lstrip("v")
    url, name = _asset_url(rel, CODE_ASSET)
    if not url:
        raise RuntimeError("Release {} has no {} zip.".format(rel.get("tag_name"), CODE_ASSET))
    tmp = tempfile.mkdtemp(prefix="pxltools_")
    zpath = os.path.join(tmp, name)
    _download(url, zpath)
    extracted = os.path.join(tmp, "extracted")
    with zipfile.ZipFile(zpath, "r") as zf:
        zf.extractall(extracted)
    return rel, extracted, version


def _archive_existing(path):
    if os.path.exists(path):
        bak = path + "_OLD"
        if os.path.exists(bak):
            shutil.rmtree(bak, ignore_errors=True)
        shutil.move(path, bak)


# ── assets (shared) ───────────────────────────────────────────────────────────

def _assets_root():
    return os.path.join(os.path.expanduser("~"), "Documents", "PXLtools", "TurnTable_ROOT")


def _download_assets(release):
    dest_root = os.path.dirname(_assets_root())          # ~/Documents/PXLtools
    url, name = _asset_url(release, ASSET_PACK)
    if not url:
        return "(asset pack not on this release)"
    os.makedirs(dest_root, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="pxltools_assets_")
    zpath = os.path.join(tmp, name)
    _download(url, zpath)
    with zipfile.ZipFile(zpath, "r") as zf:
        zf.extractall(dest_root)                          # contains TurnTable_ROOT/ at top
    shutil.rmtree(tmp, ignore_errors=True)
    return _assets_root()


# ── Maya install ──────────────────────────────────────────────────────────────

def _maya_modules_dir():
    import maya.cmds as cmds
    d = os.path.join(cmds.internalVar(userAppDir=True), "modules")
    os.makedirs(d, exist_ok=True)
    return d


def _write_mod(modules_dir, module_root, version):
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


def _install_maya(extracted, version):
    import maya.cmds as cmds
    modules_dir = _maya_modules_dir()
    module_root = os.path.join(modules_dir, "PXLtools")
    _archive_existing(module_root)
    os.makedirs(module_root, exist_ok=True)
    shutil.copytree(os.path.join(extracted, "maya"), os.path.join(module_root, "maya"), dirs_exist_ok=True)
    mani = os.path.join(extracted, "manifest.json")
    if os.path.isfile(mani):
        shutil.copy2(mani, os.path.join(module_root, "manifest.json"))
    _write_mod(modules_dir, module_root, version)
    scripts = os.path.join(module_root, "maya", "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    os.environ["XBMLANGPATH"] = (os.path.join(module_root, "maya", "icons")
                                 + os.pathsep + os.environ.get("XBMLANGPATH", ""))
    for _name in list(sys.modules):
        if (_name == SHELF_MODULE or _name.startswith("PXLtools_")
                or _name.startswith("PXLmentor_")
                or _name == "pxl_ui" or _name.startswith("pxl_ui.")):
            del sys.modules[_name]
    __import__(SHELF_MODULE)   # builds the shelf
    return module_root


def _copy_nuke_toolbox(extracted):
    """Copy nuke/scripts + nuke/icons to ~/.nuke/PXLtools, and init.py/menu.py to ~/.nuke."""
    nuke_src = os.path.join(extracted, "nuke")
    if not os.path.isdir(nuke_src):
        return None, None
    home_nuke = os.path.join(os.path.expanduser("~"), ".nuke")
    os.makedirs(home_nuke, exist_ok=True)
    tb = os.path.join(home_nuke, "PXLtools")
    _archive_existing(tb)
    os.makedirs(tb, exist_ok=True)
    for sub in ("scripts", "icons"):
        s = os.path.join(nuke_src, sub)
        if os.path.isdir(s):
            shutil.copytree(s, os.path.join(tb, sub), dirs_exist_ok=True)
    mani = os.path.join(extracted, "manifest.json")
    if os.path.isfile(mani):
        shutil.copy2(mani, os.path.join(tb, "manifest.json"))
    for f in ("init.py", "menu.py"):
        s = os.path.join(nuke_src, f)
        if os.path.isfile(s):
            shutil.copy2(s, os.path.join(home_nuke, f))
    return home_nuke, tb


def install():
    """Full install from Maya (Maya module + Nuke toolbox + assets + shelf)."""
    import maya.cmds as cmds
    try:
        rel, extracted, version = _fetch_release()
        module_root = _install_maya(extracted, version)
        _home_nuke, nuke_tb = _copy_nuke_toolbox(extracted)
        # assets (prompted) — Maya dialog
        assets = _assets_root() + "  (already present)" if os.path.isdir(_assets_root()) else None
        if assets is None:
            ans = cmds.confirmDialog(
                title="PXLtools — turntable assets",
                message=("The turntable scene + comp + HDRIs (~210 MB) are needed to load the "
                         "TurnTable scene.\n\nDownload + install them now?"),
                button=["Download", "Skip"], defaultButton="Download", cancelButton="Skip")
            assets = _download_assets(rel) if ans == "Download" else "(skipped)"
        cmds.confirmDialog(
            title="PXLtools Installer",
            message=("PXLtools v{} installed.\n\nMaya module: {}\nNuke toolbox: {}\n"
                     "Turntable assets: {}\n\nThe PXLtools shelf is ready.\n"
                     "Re-drag this INSTALL.py anytime to update."
                     ).format(version, module_root, nuke_tb or "(skipped)", assets),
            button=["Great"])
    except Exception as exc:
        try:
            cmds.confirmDialog(title="PXLtools Installer — failed",
                               message="Install failed:\n\n{}".format(exc), button=["OK"])
        except Exception:
            print("PXLtools install failed:", exc)
        raise


# ── Nuke install (standalone, no Maya needed) ─────────────────────────────────

def install_nuke():
    """Install/update ONLY the Nuke side and rebuild the menu live (no restart)."""
    import nuke
    try:
        rel, extracted, version = _fetch_release()
        home_nuke, tb = _copy_nuke_toolbox(extracted)
        if not tb:
            nuke.message("PXLtools: this release has no Nuke component.")
            return
        # Make the freshly-installed paths importable THIS session.
        for p in (os.path.join(tb, "scripts"), os.path.join(tb, "icons")):
            try:
                nuke.pluginAddPath(p)
            except Exception:
                pass
        if os.path.join(tb, "scripts") not in sys.path:
            sys.path.insert(0, os.path.join(tb, "scripts"))
        # Purge cached PXLtools modules so the new code loads.
        for _n in list(sys.modules):
            if _n.startswith("PXLtools_") or _n == "pxl_ui" or _n.startswith("pxl_ui."):
                del sys.modules[_n]
        # Rebuild the toolbar menu live by executing the freshly-copied menu.py.
        menu_path = os.path.join(home_nuke, "menu.py")
        if os.path.isfile(menu_path):
            with open(menu_path, "r", encoding="utf-8") as fh:
                exec(compile(fh.read(), menu_path, "exec"),
                     {"__name__": "__pxltools_menu_install__", "__file__": menu_path})
        # assets (prompted) — Nuke dialog
        if os.path.isdir(_assets_root()):
            assets = _assets_root() + "  (already present)"
        elif nuke.ask("Download the TurnTable assets (scene + comp + HDRIs, ~210 MB) now?\n"
                      "Needed to import the comp template / load the scene."):
            assets = _download_assets(rel)
        else:
            assets = "(skipped — point the tool at an existing TurnTable_ROOT)"
        nuke.message("PXLtools v{} (Nuke) installed.\n\nToolbox: {}\nAssets: {}\n\n"
                     "The PXLtools menu (Nodes toolbar) has been rebuilt — no restart needed."
                     .format(version, tb, assets))
    except Exception as exc:
        try:
            nuke.message("PXLtools Nuke install failed:\n\n{}".format(exc))
        except Exception:
            print("PXLtools Nuke install failed:", exc)
        raise


# ── Entry points ──────────────────────────────────────────────────────────────

def _host():
    try:
        import maya.cmds  # noqa: F401
        return "maya"
    except Exception:
        pass
    try:
        import nuke  # noqa: F401
        return "nuke"
    except Exception:
        return None


# Maya calls this automatically when the file is dragged into the viewport.
def onMayaDroppedPythonFile(*args):
    install()


# When exec'd from Nuke's Script Editor (the one-line bootstrap), auto-install Nuke.
# In Maya the drag triggers onMayaDroppedPythonFile instead, so we skip here.
if __name__ != "__main__" and _host() == "nuke":
    install_nuke()

if __name__ == "__main__":
    h = _host()
    if h == "maya":
        install()
    elif h == "nuke":
        install_nuke()
    else:
        print("Run inside Maya (drag the file in) or Nuke (paste the one-line bootstrap).")
