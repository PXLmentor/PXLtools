#!/usr/bin/env python3
"""
PXLtools release builder.

Assembles the distribution zips from THIS repo and cuts a GitHub Release via the
`gh` CLI. Run from anywhere; it locates the repo root relative to this file.

  Code zip   (PXLtools-code-v<ver>.zip)  — scripts + pxl_ui + icons + manifest.
                                            Small; rebuilt every release.
  Asset zip  (PXLtools-assets.zip)        — TurnTable_ROOT (scene .ma, comp .nk,
                                            HDRIs, dirt/LUT textures). Large; only
                                            built/uploaded with --assets.

Channels:
  beta   -> GitHub Release marked PRERELEASE (internal; updater ignores unless opted in)
  stable -> normal Release (this is the deliberate "public now" step)

Usage (from the repo, with GH_TOKEN for the PXLmentor account in env or master secrets):
  python tools/release.py --version 1.0.0 --channel beta
  python tools/release.py --version 1.0.0 --channel beta --assets
  python tools/release.py --channel stable            # re-publish current manifest version as stable

The GitHub token is read from $GH_TOKEN, else from the master secrets file
(J:/ClaudeCode/.secrets/credentials.env -> GITHUB_PXLMENTOR_TOKEN). Never hard-code it.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import zipfile

REPO_OWNER = "PXLmentor"
REPO_NAME  = "PXLtools"
REPO       = "{}/{}".format(REPO_OWNER, REPO_NAME)

HERE      = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
BUILD_DIR = os.path.join(REPO_ROOT, "build")
MANIFEST  = os.path.join(REPO_ROOT, "manifest.json")
SECRETS   = "J:/ClaudeCode/.secrets/credentials.env"

ASSET_SRC = os.path.join(REPO_ROOT, "docs", "TurnTable_Package", "TurnTable_ROOT")

# Public package ships ONLY the TurnTable tool (the 9 legacy PXLmentor_* tools stay
# internal until each is rewritten). A Maya tool file ships if its name starts with
# any of these stems; the shelf + Nuke menu skip buttons whose file is absent.
SHIP_MAYA_STEMS = ("PXLtools_TurnTable_Builder", "PXLtools_Setup_Shelf")
SHIP_NUKE_STEMS = ("PXLtools_TurnTable_Comp_Setup",)


# ── helpers ───────────────────────────────────────────────────────────────────

def _token():
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_PXLMENTOR_TOKEN")
    if tok:
        return tok.strip()
    if os.path.isfile(SECRETS):
        with open(SECRETS, "r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                if line.startswith("GITHUB_PXLMENTOR_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip()
    sys.exit("ERROR: no GitHub token. Set GH_TOKEN or GITHUB_PXLMENTOR_TOKEN in the master secrets.")


def _gh(args, token):
    env = dict(os.environ, GH_TOKEN=token)
    return subprocess.run(["gh"] + args, env=env, capture_output=True, text=True)


def _load_manifest():
    with open(MANIFEST, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_manifest(m):
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(m, fh, indent=2)
        fh.write("\n")


def _copytree(src, dst):
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
        return True
    return False


def _copyfile(src, dst):
    if os.path.isfile(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        return True
    return False


def _zipdir(src_root, zip_path):
    """Zip the contents of src_root into zip_path (paths relative to src_root)."""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(src_root):
            for f in files:
                full = os.path.join(root, f)
                rel  = os.path.relpath(full, src_root)
                zf.write(full, rel)


# ── code zip ────────────────────────────────────────────────────────────────

def build_code_zip(version):
    """Stage the deployable code layout and zip it. INSTALL.py mirrors this layout:
       <stage>/manifest.json
       <stage>/maya/scripts/   (tools + PXLtools_Setup_Shelf.py + pxl_ui/)
       <stage>/maya/icons/
       <stage>/nuke/scripts/   (tools + pxl_ui/)
       <stage>/nuke/icons/  + init.py + menu.py
    """
    stage = os.path.join(BUILD_DIR, "PXLtools-code")
    if os.path.isdir(stage):
        shutil.rmtree(stage)
    os.makedirs(stage)

    # manifest
    shutil.copy2(MANIFEST, os.path.join(stage, "manifest.json"))

    pxl_ui = os.path.join(REPO_ROOT, "shared", "pxl_ui")

    # Maya — copy ONLY the shipped tool files (TurnTable + shelf) + pxl_ui + icons.
    maya_scripts_src = os.path.join(REPO_ROOT, "maya", "scripts")
    maya_scripts_dst = os.path.join(stage, "maya", "scripts")
    os.makedirs(maya_scripts_dst, exist_ok=True)
    for name in os.listdir(maya_scripts_src):
        full = os.path.join(maya_scripts_src, name)
        if (os.path.isfile(full) and name.endswith(".py")
                and name.startswith(SHIP_MAYA_STEMS)):
            shutil.copy2(full, os.path.join(maya_scripts_dst, name))
    _copytree(pxl_ui, os.path.join(maya_scripts_dst, "pxl_ui"))
    _copytree(os.path.join(maya_scripts_src, "icons"), os.path.join(stage, "maya", "icons"))

    # Nuke — ONLY the shipped tool files + pxl_ui + icons + init.py + menu.py
    nuke_scripts_src = os.path.join(REPO_ROOT, "nuke", "scripts")
    nuke_scripts_dst = os.path.join(stage, "nuke", "scripts")
    os.makedirs(nuke_scripts_dst, exist_ok=True)
    if os.path.isdir(nuke_scripts_src):
        for name in os.listdir(nuke_scripts_src):
            full = os.path.join(nuke_scripts_src, name)
            if (os.path.isfile(full) and name.endswith(".py")
                    and name.startswith(SHIP_NUKE_STEMS)):
                shutil.copy2(full, os.path.join(nuke_scripts_dst, name))
    _copytree(pxl_ui, os.path.join(nuke_scripts_dst, "pxl_ui"))
    _copytree(os.path.join(REPO_ROOT, "nuke", "icons"), os.path.join(stage, "nuke", "icons"))
    _copyfile(os.path.join(REPO_ROOT, "nuke", "init.py"), os.path.join(stage, "nuke", "init.py"))
    _copyfile(os.path.join(REPO_ROOT, "nuke", "menu.py"), os.path.join(stage, "nuke", "menu.py"))

    out = os.path.join(BUILD_DIR, "PXLtools-code-v{}.zip".format(version))
    if os.path.isfile(out):
        os.remove(out)
    _zipdir(stage, out)
    print("  code zip:  {} ({:.1f} MB)".format(out, os.path.getsize(out) / 1e6))
    return out


def build_asset_zip():
    if not os.path.isdir(ASSET_SRC):
        print("  WARNING: asset source not found, skipping asset zip:", ASSET_SRC)
        return None
    out = os.path.join(BUILD_DIR, "PXLtools-assets.zip")
    if os.path.isfile(out):
        os.remove(out)
    # Never ship these: Arnold-generated .tx mip textures (regenerated on load, ~hundreds of MB),
    # Maya swatch/autosave caches, and session scratch files. Keeps the pack lean + reproducible.
    SKIP_EXT  = (".tx",)
    SKIP_DIRS = (".mayaSwatches", "autosave")
    SKIP_FILE = ("tt_session.json",)
    skipped = 0
    # Zip ONLY TurnTable_ROOT, stored under a top-level "TurnTable_ROOT/" prefix
    # (NOT the whole TurnTable_Package — that holds the old 210MB zip + stale copies).
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(ASSET_SRC):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]   # prune junk dirs in-place
            for f in files:
                if f.lower().endswith(SKIP_EXT) or f in SKIP_FILE:
                    skipped += 1
                    continue
                full = os.path.join(root, f)
                rel  = os.path.join("TurnTable_ROOT", os.path.relpath(full, ASSET_SRC))
                zf.write(full, rel)
    print("  asset zip: {} ({:.1f} MB)  [skipped {} junk/.tx files]".format(
        out, os.path.getsize(out) / 1e6, skipped))
    return out


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", help="package version X.Y.Z (default: manifest.version)")
    ap.add_argument("--channel", choices=["beta", "stable"], default="beta")
    ap.add_argument("--assets", action="store_true", help="also build + upload the asset pack")
    ap.add_argument("--notes", default="", help="release notes (markdown)")
    args = ap.parse_args()

    token = _token()
    manifest = _load_manifest()
    version = args.version or manifest["version"]
    manifest["version"] = version
    manifest["channel"] = args.channel
    _save_manifest(manifest)

    os.makedirs(BUILD_DIR, exist_ok=True)
    print("Building PXLtools v{} ({})".format(version, args.channel))
    zips = [build_code_zip(version)]
    if args.assets:
        a = build_asset_zip()
        if a:
            zips.append(a)

    tag = "v{}".format(version)
    title = "PXLtools {} ({})".format(tag, args.channel)
    notes = args.notes or "PXLtools {} — {} release.".format(tag, args.channel)

    exists = _gh(["release", "view", tag, "--repo", REPO], token).returncode == 0
    if exists:
        # Update IN PLACE: clobber only the zips we built (keeps other assets, e.g.
        # the large asset pack, when doing a code-only re-cut).
        up = _gh(["release", "upload", tag, "--repo", REPO, "--clobber"] + zips, token)
        if up.returncode != 0:
            sys.exit("gh release upload failed:\n" + up.stderr)
        edit = ["release", "edit", tag, "--repo", REPO, "--title", title, "--notes", notes]
        edit += ["--prerelease"] if args.channel == "beta" else ["--prerelease=false", "--latest"]
        _gh(edit, token)
        print("Updated release:", tag)
    else:
        cmd = ["release", "create", tag, "--repo", REPO, "--title", title, "--notes", notes]
        if args.channel == "beta":
            cmd.append("--prerelease")
        cmd += zips
        res = _gh(cmd, token)
        if res.returncode != 0:
            sys.exit("gh release create failed:\n" + res.stderr)
        print("Released:", res.stdout.strip() or tag)
    print("Channel :", args.channel, "(prerelease)" if args.channel == "beta" else "(STABLE — public)")


if __name__ == "__main__":
    main()
