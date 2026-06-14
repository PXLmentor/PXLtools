"""
PXLtools auto-update — checks GitHub for a newer release when a tool launches and
offers a one-click update. No manual button.

Pure stdlib + the host DCC's Qt for the prompt. SAFE by design: every entry point
is wrapped so a network/parse failure can never block or crash the host tool.

Wire it from a tool's launch, deferred:
    try:
        from pxl_ui import pxl_update
        import maya.cmds as cmds
        cmds.evalDeferred(lambda: pxl_update.check(dcc="maya"), lowestPriority=True)
    except Exception:
        pass
"""
import json
import os
import shutil
import ssl
import sys
import tempfile
import urllib.request
import zipfile

REPO       = "PXLmentor/PXLtools"
API_LATEST = "https://api.github.com/repos/{}/releases/latest".format(REPO)
API_ALL    = "https://api.github.com/repos/{}/releases".format(REPO)
CODE_ASSET = "PXLtools-code"
SHELF_MODULE = "PXLtools_Setup_Shelf"
STATE_FILE = os.path.join(os.path.expanduser("~"), "Documents", "PXLtools", ".update_check.json")


# ── tiny helpers ──────────────────────────────────────────────────────────────

def _get_json(url):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "PXLtools-Updater"})
    with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))


def _download(url, dest):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "PXLtools-Updater"})
    with urllib.request.urlopen(req, context=ctx, timeout=180) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)


def _ver(s):
    out = []
    for p in str(s or "0").lstrip("v").replace("-", ".").split("."):
        if p.isdigit():
            out.append(int(p))
        else:
            break
    while len(out) < 3:
        out.append(0)
    return tuple(out[:3])


def _state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_state(d):
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(d, f)
    except Exception:
        pass


def _today():
    import datetime
    return datetime.date.today().isoformat()


def _scripts_dir():
    # this file: .../<scripts>/pxl_ui/pxl_update.py  ->  <scripts>
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def installed_version():
    """Read the package version from the nearest manifest.json above this module."""
    d = _scripts_dir()
    for _ in range(5):
        m = os.path.join(d, "manifest.json")
        if os.path.isfile(m):
            try:
                with open(m, "r", encoding="utf-8") as f:
                    return json.load(f).get("version", "0")
            except Exception:
                return "0"
        d = os.path.dirname(d)
    return "0"


def _latest_release(channel):
    if channel == "beta":
        rels = _get_json(API_ALL)               # newest of any kind (incl prerelease)
        return rels[0] if rels else None
    try:
        return _get_json(API_LATEST)            # STABLE only (newest non-prerelease)
    except Exception:
        return None                             # no stable yet -> offer nothing


def _code_zip_url(release):
    for a in release.get("assets", []):
        if a["name"].startswith(CODE_ASSET) and a["name"].endswith(".zip"):
            return a["browser_download_url"], a["name"]
    return None, None


# ── DCC dialog (Maya / Nuke) ──────────────────────────────────────────────────

def _prompt(latest, current):
    msg = ("PXLtools v{} is available (you have v{}).\n\nUpdate now?"
           .format(latest, current))
    try:
        import maya.cmds as cmds
        return cmds.confirmDialog(title="PXLtools update", message=msg,
                                  button=["Update", "Later", "Skip this version"],
                                  defaultButton="Update", cancelButton="Later")
    except Exception:
        pass
    try:
        import nuke
        if nuke.ask(msg + "\n(Yes = update, No = later)"):
            return "Update"
        return "Later"
    except Exception:
        return "Later"


def _info(text):
    try:
        import maya.cmds as cmds
        cmds.confirmDialog(title="PXLtools", message=text, button=["OK"])
        return
    except Exception:
        pass
    try:
        import nuke
        nuke.message(text)
    except Exception:
        print("PXLtools:", text)


# ── the update itself ─────────────────────────────────────────────────────────

def _do_update_maya(extracted, version):
    import maya.cmds as cmds
    modules_dir = os.path.join(cmds.internalVar(userAppDir=True), "modules")
    module_root = os.path.join(modules_dir, "PXLtools")
    bak = module_root + "_OLD"
    if os.path.isdir(bak):
        shutil.rmtree(bak, ignore_errors=True)
    if os.path.isdir(module_root):
        shutil.move(module_root, bak)
    os.makedirs(module_root, exist_ok=True)
    shutil.copytree(os.path.join(extracted, "maya"), os.path.join(module_root, "maya"), dirs_exist_ok=True)
    mani = os.path.join(extracted, "manifest.json")
    if os.path.isfile(mani):
        shutil.copy2(mani, os.path.join(module_root, "manifest.json"))
    scripts = os.path.join(module_root, "maya", "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    # purge cached PXLtools modules, rebuild shelf from the fresh code
    for name in list(sys.modules):
        if (name == SHELF_MODULE or name.startswith("PXLtools_")
                or name == "pxl_ui" or name.startswith("pxl_ui.")):
            del sys.modules[name]
    __import__(SHELF_MODULE)


def _do_update_nuke(extracted):
    home_nuke = os.path.join(os.path.expanduser("~"), ".nuke")
    tb = os.path.join(home_nuke, "PXLtools")
    bak = tb + "_OLD"
    if os.path.isdir(bak):
        shutil.rmtree(bak, ignore_errors=True)
    if os.path.isdir(tb):
        shutil.move(tb, bak)
    os.makedirs(tb, exist_ok=True)
    nuke_src = os.path.join(extracted, "nuke")
    for sub in ("scripts", "icons"):
        s = os.path.join(nuke_src, sub)
        if os.path.isdir(s):
            shutil.copytree(s, os.path.join(tb, sub), dirs_exist_ok=True)
    for f in ("init.py", "menu.py"):
        s = os.path.join(nuke_src, f)
        if os.path.isfile(s):
            shutil.copy2(s, os.path.join(home_nuke, f))


def check(channel="stable", dcc="maya", force=False):
    """Check GitHub for a newer release; if found, prompt + one-click update.
    Throttled to once per day unless force=True. Never raises into the host."""
    try:
        st = _state()
        if not force and st.get("last_check") == _today():
            return
        rel = _latest_release(channel)
        st["last_check"] = _today()
        _save_state(st)
        if not rel:
            return
        latest = rel.get("tag_name", "0").lstrip("v")
        current = installed_version()
        if _ver(latest) <= _ver(current):
            return
        if st.get("skip") == latest:
            return

        ans = _prompt(latest, current)
        if ans == "Skip this version":
            st["skip"] = latest
            _save_state(st)
            return
        if ans != "Update":
            return

        url, name = _code_zip_url(rel)
        if not url:
            _info("Update v{} has no code package — try again later.".format(latest))
            return
        tmp = tempfile.mkdtemp(prefix="pxltools_upd_")
        zpath = os.path.join(tmp, name)
        _download(url, zpath)
        extracted = os.path.join(tmp, "extracted")
        with zipfile.ZipFile(zpath, "r") as zf:
            zf.extractall(extracted)

        if dcc == "nuke":
            _do_update_nuke(extracted)
            _info("PXLtools updated to v{}. Restart Nuke (or reopen the menu) to use it."
                  .format(latest))
        else:
            _do_update_maya(extracted, latest)
            _info("PXLtools updated to v{}. The shelf has been rebuilt — reopen the tool."
                  .format(latest))
        shutil.rmtree(tmp, ignore_errors=True)
    except Exception as exc:
        # Never let an update check break the tool.
        print("PXLtools update check skipped:", exc)
