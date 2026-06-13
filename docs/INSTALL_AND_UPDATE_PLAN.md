# PXLtools — Easiest Install & Update Plan

> Goal: the simplest possible experience for a **non-technical artist** to (a) install the
> tools in one action and (b) get future releases painlessly — for both Maya and Nuke.
> Drafted 2026-06-12. This is a PLAN — nothing built yet; awaiting go-ahead.

## Guiding principles
- **One action to install.** No manual file copying, no editing paths, no PYTHONPATH.
- **One action to update.** In-session button for hot reload; one re-drag for new releases.
- **Self-contained + idempotent.** Everything in ONE folder; re-running is always safe and
  archives the previous version.
- **Cross-DCC.** Same model for Maya and Nuke.

---

## Recommended approach: self-contained MODULE + drag-and-drop installer

### A) Ship as a Maya **module** (`.mod`), not loose files in `scripts/`
Today the tools scatter into `maya/2025/scripts/` + icons into `prefs/icons/`. Instead ship a
single self-contained folder:

```
PXLtools/
  scripts/      (all PXLtools_*.py tools + pxl_ui/)
  icons/        (tool icons, favicon, logo, update icon)
  scenes/       (PXLtools_TB3DTT_*.ma)
  plug-ins/     (if any)
  PXLtools.mod  (registers the paths above with Maya)
  manifest.json (package version + per-tool versions)
```

Why a module:
- **Update = replace ONE folder.** Uninstall = delete the folder + one `.mod` line.
- Maya auto-discovers scripts/icons/plug-ins via the `.mod` — no path hacks.
- Maps cleanly to Nuke (one `~/.nuke/PXLtools` toolbox + init.py/menu.py — already built).

### B) Install experience (what the artist does)
1. Download `PXLtools_vX.Y.Z.zip`, unzip anywhere.
2. **Drag `INSTALL.py` into a running Maya viewport.**
3. Done — the PXLtools shelf appears and every tool works. A confirmation dialog lists what
   was installed and the version.

(For Nuke: the same `INSTALL.py` also copies the Nuke toolbox to `~/.nuke/PXLtools` and wires
`init.py`/`menu.py`. If they only use one DCC, the other is skipped silently.)

### C) What `INSTALL.py` does (idempotent, drag-drop)
- Detect Maya version + user dirs (`internalVar`, modules dir).
- Copy the `PXLtools/` module into the user's modules dir
  (`~/Documents/maya/modules/PXLtools/`), archiving any previous copy.
- Write/refresh `PXLtools.mod` so Maya registers `scripts/`, `icons/`, `plug-ins/`.
- Build/refresh the PXLtools shelf (our existing version-aware `PXLtools_Setup_Shelf`).
- Nuke: copy `~/.nuke/PXLtools` + ensure `init.py`/`menu.py` are present.
- Safe to re-run any time (that IS the update path — see below).

---

## Updates — two tiers

### Tier 1 — In-session, already built ✅
The shelf **Update** button (Maya) and **"↻ Update PXLtools"** menu (Nuke) re-scan the module's
`scripts/` folder, resolve the NEWEST `PXLtools_<Tool>_v*.py` per tool, rebuild the shelf/menu,
and reload — **no DCC restart**. This already works for files already on disk.

### Tier 2 — New releases
- **Simplest (manual, zero knowledge):** download the new zip, **drag `INSTALL.py` again**. It
  swaps the module folder (archiving the old) and rebuilds. Then Tier-1 Update loads it.
- **Optional automated (phase 2):** a **"Check for Updates"** button that queries the latest
  release (GitHub Releases at `github.com/PXLmentor`, or a Gumroad/host URL + `manifest.json`
  version compare), downloads the zip, replaces the module folder, and rebuilds — fully in-app.

### Versioning that keeps updates safe
- Keep the `PXLtools_<Tool>_v<MAJOR>_<MINOR>_<PATCH>.py` filename convention — the shelf/menu
  already auto-pick the newest; a new release just drops new files and archives old ones.
- `manifest.json` holds the package version + per-tool versions so the installer and the
  update-checker can compare "installed vs latest".

---

## Build checklist (when you say go)
1. Restructure the deploy into the self-contained `PXLtools/` module (+ `PXLtools.mod`,
   `manifest.json`).
2. Write `INSTALL.py` — drag-drop, idempotent, Maya + Nuke, archives previous version,
   confirmation dialog.
3. Packaging script → `PXLtools_vX.Y.Z.zip` (module + INSTALL.py + README).
4. (Phase 2) "Check for Updates" button → GitHub Releases / host URL.
5. Test matrix: clean-machine install · re-install (update) · in-session Update button ·
   Nuke side · uninstall.

## Open questions for Cris
- Distribution channel for releases: **GitHub Releases** (github.com/PXLmentor) or **Gumroad**
  zip? (Drives the Tier-2 auto-update design.)
- Do we want the automated "Check for Updates" in v1, or ship with drag-drop re-install first
  and add auto-update later?
