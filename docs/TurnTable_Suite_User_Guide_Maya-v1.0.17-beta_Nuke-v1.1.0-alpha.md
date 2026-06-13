# PXLmentor TurnTable Suite — User Guide

**Maya TurnTable Builder** v1.0.17-beta · **Nuke TurnTable Comp Setup** v1.1.0-alpha  
DCC: Autodesk Maya 2025 · Foundry Nuke 15 · Python 3 · Arnold · ACES 1.2

---

## Contents

1. [Overview](#1-overview)
2. [What's in the Package](#2-whats-in-the-package)
3. [Part A — Maya TurnTable Builder](#part-a--maya-turntable-builder)
   - [A1. Installation](#a1-installation)
   - [A2. Running the Tool](#a2-running-the-tool)
   - [A3. UI at a Glance](#a3-ui-at-a-glance)
   - [A4. Preliminary Steps](#a4-preliminary-steps)
   - [A5. Section 01 — Scene Setup](#a5-section-01--scene-setup)
   - [A6. Section 02 — Model](#a6-section-02--model)
   - [A7. Section 03 — Lighting](#a7-section-03--lighting)
   - [A8. HDRI Grid](#a8-hdri-grid)
   - [A9. Clear Scene](#a9-clear-scene)
   - [A10. Tips & Notes](#a10-tips--notes)
4. [Part B — Nuke TurnTable Comp Setup](#part-b--nuke-turntable-comp-setup)
   - [B1. Installation](#b1-installation)
   - [B2. Running the Tool](#b2-running-the-tool)
   - [B3. UI at a Glance](#b3-ui-at-a-glance)
   - [B4. Connecting to a Comp Node](#b4-connecting-to-a-comp-node)
   - [B5. COMP SETUP Section](#b5-comp-setup-section)
   - [B6. Visual Options](#b6-visual-options)
   - [B7. Comp Effects](#b7-comp-effects)
   - [B8. Tech Settings](#b8-tech-settings)
   - [B9. References](#b9-references)
   - [B10. Export](#b10-export)
   - [B11. Session Persistence](#b11-session-persistence)
   - [B12. Tips & Notes](#b12-tips--notes)
5. [Troubleshooting](#5-troubleshooting)

---

## 1. Overview

The PXLmentor TurnTable Suite is a two-tool pipeline for building and rendering professional CG turntables:

| Tool | DCC | Purpose |
|---|---|---|
| **TurnTable Builder** | Maya 2025 | Load the turntable rig, attach your model or shader ball, set lighting and HDRI environment, preview in Arnold |
| **TurnTable Comp Setup** | Nuke 15 | Live control panel for the turntable comp — drives all comp nodes directly, no Apply button needed |

The two tools are designed to work together. You set up and render in Maya, then open Nuke to composite with the comp template.

---

## 2. What's in the Package

```
TurnTable_Package/
├── README.md
├── scripts/
│   ├── maya/
│   │   └── PXLmentor_TurnTable_Builder_v1_0_17_beta.py
│   └── nuke/
│       └── PXLmentor_TurnTable_Comp_Setup_v1_1_0_alpha.py
└── icons/
    ├── maya/
    │   └── icon_turntable_builder.png           (96 x 96 px)
    └── nuke/
        └── PXLmentor_TurnTable_Comp_Setup.png
```

> The TurnTable Root Folder (`TurnTable_ROOT/`) is a separate asset folder that lives on disk wherever you store production assets. The tools will ask you to browse to it on first launch. It is not included in this package — it ships separately.

---

# Part A — Maya TurnTable Builder

**Version:** 1.0.17-beta  
**Requires:** Maya 2022+ · Arnold · ACES 1.2  
**No external installs required** — PySide6 is bundled with Maya 2025.

---

## A1. Installation

### Quick Load — Script Editor (fastest)

1. Copy `PXLmentor_TurnTable_Builder_v1_0_17_beta.py` to your Maya scripts folder:

   ```
   C:\Users\<YourUsername>\Documents\maya\2025\scripts\
   ```

2. Open the **Maya Script Editor** (Windows > Script Editor), set the tab language to **Python**, paste the following, and press **Ctrl + Enter**:

   ```python
   import importlib, sys
   mod = "PXLmentor_TurnTable_Builder_v1_0_17_beta"
   if mod in sys.modules:
       importlib.reload(sys.modules[mod])
   m = sys.modules.get(mod) or __import__(mod)
   m.show()
   ```

   The tool window opens immediately. Re-running the same snippet on a live session raises the existing window instead of spawning a duplicate.

---

### Full Maya Shelf Integration

This method creates a permanent shelf button with the tool icon.

**Step 1 — Copy the script**

```
C:\Users\<YourUsername>\Documents\maya\2025\scripts\
    └── PXLmentor_TurnTable_Builder_v1_0_17_beta.py
```

**Step 2 — Copy the icon**

```
C:\Users\<YourUsername>\Documents\maya\2025\prefs\icons\
    └── icon_turntable_builder.png
```

**Step 3 — Create the shelf button**

Option A — drag from Script Editor:
1. Paste the launch snippet above into the Script Editor Python tab.
2. Select all the text (Ctrl + A).
3. Middle-mouse-drag it onto any Maya shelf tab.
4. Right-click the new button → **Edit**.
5. Set **Icon Name** to `icon_turntable_builder.png`.
6. Set **Tooltip** to `TurnTable Builder v1.0.17-beta`.
7. Click **Save**.

Option B — MEL shelf button block (paste into Script Editor MEL tab):

```mel
shelfButton
    -enableCommandRepeat 1
    -enable 1
    -width 35
    -height 34
    -annotation "TurnTable Builder v1.0.17-beta"
    -image "icon_turntable_builder.png"
    -image1 "icon_turntable_builder.png"
    -style "iconOnly"
    -command "import importlib, sys\nmod = 'PXLmentor_TurnTable_Builder_v1_0_17_beta'\nif mod in sys.modules:\n    importlib.reload(sys.modules[mod])\nm = sys.modules.get(mod) or __import__(mod)\nm.show()"
    -sourceType "python"
    -flat 1
;
```

---

## A2. Running the Tool

Every time you want to open the tool, use the Script Editor snippet from A1 or click your shelf button. The tool is a singleton — re-running it when the window is already open simply raises and focuses the existing window.

> **Maya 2024 and earlier:** The tool uses PySide2. Maya 2025 uses PySide6. The script handles both automatically.

---

## A3. UI at a Glance

The tool window is 550 px wide and auto-resizes vertically as sections expand and collapse.

```
┌─────────────────────────────────────────────────────┐
│  [icon]       PXLmentor                             │
│               TurnTable Builder  v1.0.17-beta        │  ← header (dark teal)
├───────────────[ PREP ]──[ TURNTABLE ]───────────────┤  ← tab bar
│                                                     │
│  ▾ Instructions  ─────────────────────────────────  │  ← compact collapsible (expanded)
│    1. Set Root Folder in Preliminary Steps           │
│    2. Configure Scene Setup                          │
│    3. Configure Model                                │
│    4. Configure Lighting                             │
│    5. Click Render in Arnold                         │
│    ▾ Preliminary Steps  ──────────────────────────  │  ← compact collapsible (nested)
│       TURNTABLE ROOT FOLDER                         │
│       [ /path/to/TurnTable_ROOT ........] Browse…   │
│       [ Set Root Folder ]                            │
│       hint / status                                  │
│       ────────────────                               │
│       ACES 1.2 COLOUR MANAGEMENT                    │
│       [✓ ACES active]  or  [⚠ not detected + link] │
│       ────────────────                               │
│       OPENCV INSTALLATION                            │
│       [✓ installed]  or  [○ not installed] [Install]│
│                                                     │
│  ⚠ Set root folder in Preliminary Steps...          │  ← warning banner (hides when root OK)
│                                                     │
│  ▾ 01  SCENE SETUP  ──────────────────────────────  │
│    [ Load Turntable Scene ]  ←── primary CTA        │
│    — Scene: Not loaded                               │
│    Frame Range:  [1001] — [1200]  [Apply]            │
│    ⚠ Apply frame range before rendering              │
│                                                     │
│  ▸ 02  MODEL  ────────────────────────────────────  │  ← collapsed until scene loads
│    [ SHADER BALL ]  [ YOUR MODEL ]                   │
│    SHADER BALL mode:                                 │
│      [✓] Shader Ball  [ ] Cloth  [ ] Liquid          │
│    YOUR MODEL mode:                                  │
│      [ No model captured yet ]                       │
│      ①  [ Capture Selection  ]  hint text            │
│      ②  [ Attach to Turntable ]  hint text           │
│      ③  [ Center to Ground    ]  hint text           │
│                                                     │
│  ▸ 03  LIGHTING  ─────────────────────────────────  │  ← collapsed until ② done
│    ┌────────────────────┬────────────────────┐       │
│    │  VISIBILITY        │  SIZE REFERENCES   │       │
│    │  [✓] Model         │  [✓] Floor Grid    │       │
│    │  [✓] Shader Ball   │  [ ] Ref Cubes     │       │
│    │  [✓] Charts        │  [ 10 cm ][ 1 mt ] │       │
│    ├────────────────────┼────────────────────┤       │
│    │  BACKDROP          │  ARNOLD RENDER     │       │
│    │  [ HDRI ][ LIMBO ] │  [RenderView]      │       │
│    │                    │  [Render]          │       │
│    └────────────────────┴────────────────────┘       │
│    CHARTS PLACEMENT                                  │
│    Scale   [────────────────────────────] [1.00]     │
│    REF BALL              │  MACBETH                  │
│    X [──────────] [0.00] │  X [──────────] [0.00]    │
│    Y [──────────] [0.00] │  Y [──────────] [0.00]    │
│    HDRI ENVIRONMENT                                  │
│    ┌──────┬──────┬──────┬──────┐                     │
│    │ H 01 │ H 02 │ H 03 │ H 04 │ ← preset thumbnails │
│    ├──────┼──────┼──────┼──────┤                     │
│    │ H 05 │ H 06 │  +   │  +   │ ← 6 preset, 2 custom│
│    └──────┴──────┴──────┴──────┘                     │
│                                                     │
│  [ Clear Scene · removes turntable, keeps model ]   │  ← always visible
└─────────────────────────────────────────────────────┘
```

The **TURNTABLE** tab (second tab) is a placeholder for the full render pipeline — coming in a future release.

---

## A4. Preliminary Steps

The **Instructions** collapsible is expanded by default and contains a numbered workflow summary. Inside it, **Preliminary Steps** is a nested collapsible that auto-collapses once the root folder and OpenCV are both configured.

### TURNTABLE ROOT FOLDER

The root folder is the asset directory that contains scenes, HDRIs, and utilities. It can be anywhere on disk.

| Control | Action |
|---|---|
| **Browse…** | Opens a folder picker. Navigate to and select your `TurnTable_ROOT` folder. |
| **Set Root Folder** | Validates the folder, locates the Maya scene file and HDRI previews, and saves the path to config. |
| Status hint | Confirms whether the root is valid and whether the `.ma` scene was found. |

Once the root is set, the orange warning banner disappears and the Preliminary Steps section auto-collapses.

> Config is saved to: `~/Documents/maya/PXLmentor/turntable_builder_config.json`  
> Delete this file to reset the tool to a clean state.

### ACES 1.2 COLOUR MANAGEMENT

The tool detects whether your Maya project has ACES 1.2 active. If it does, you'll see a green confirmation. If not, a warning is shown with a link to a setup guide video.

> The turntable scene is built for ACES 1.2. Rendering without it will produce incorrect colours.

### OPENCV INSTALLATION

OpenCV is used only to generate preview thumbnails for custom HDRIs. It is optional — preset HDRI thumbnails work without it.

| State | Display |
|---|---|
| Installed | Green confirmation — custom HDRI previews enabled |
| Not installed | Grey notice + **Install OpenCV** button |

Clicking **Install OpenCV** runs a one-time `pip install` into Maya's Python environment. No admin rights required.

---

## A5. Section 01 — Scene Setup

**Purpose:** Load the pre-built turntable rig into your Maya session and set the animation frame range.

| Control | Description |
|---|---|
| **Load Turntable Scene** | References `PXLmentor_TB3DTT_ACES_2025_v003.ma` into your scene under the `TT_SCENE` namespace. Switches the active viewport to `main_CAM` and enables resolution gate and gate mask. |
| **Frame Range** fields | Set your desired start and end frames. Defaults: `1001 — 1200`. |
| **Apply** | Writes the playback range to Maya, creates rotation keyframes on `asset_ROT` (first half) and `lights_ROT` (second half), both 0 → 360° on Y with linear tangents. Clears and rebuilds keys every time you click. |
| Scene status | Shows `[OK] Loaded` when the reference is active. |

> **Apply frame range before rendering.** Without this step there is no animation — the warning bar below the fields reminds you.

After a successful load, Section 01 auto-collapses and Section 02 opens.

---

## A6. Section 02 — Model

**Purpose:** Choose what to render — the built-in shader ball or your own model.

### Mode Toggle

Two buttons at the top of the section select the active mode:

| Button | Mode |
|---|---|
| **SHADER BALL** (default, orange) | Renders the turntable's built-in material test sphere. No model import needed. |
| **YOUR MODEL** | Reveals the three-step workflow for attaching your own geometry. |

---

### Shader Ball Mode

When **SHADER BALL** is active, three checkboxes control which elements of the shader ball assembly are visible in the scene:

| Checkbox | Controls |
|---|---|
| **Shader Ball** | The main spherical material test object |
| **Cloth** | Fabric drape geometry |
| **Liquid** | Liquid simulation geometry |

All three are on by default. Toggle them to simplify the shot or test specific material types in isolation.

---

### Your Model Mode

Follow steps ① ② ③ in order. Each step unlocks the next.

```
[ No model captured yet ]    ← status label, updates after step ①

①  [ Capture Selection  ]    Select your model or root group
②  [ Attach to Turntable ]   Parents model under the rig group
③  [ Center to Ground    ]   Centers to origin, base at Y=0
```

#### ① Capture Selection

1. In the Maya viewport or Outliner, select your model's root transform or group.
2. Click **Capture Selection**.
3. The status label updates to confirm what was captured.

You can re-capture at any point before proceeding to step ②.

#### ② Attach to Turntable

Parents the captured nodes under `TT_SCENE:mainModel_grp` — the pivot group that rotates during the animation. Your model will now spin with the rig.

Step ③ unlocks after this succeeds.

#### ③ Center to Ground

Calculates the bounding box of your model and:
- Moves it so its centre is at **X=0, Z=0**.
- Snaps its lowest point to **Y=0** (the ground plane).

After Center to Ground succeeds, Section 02 auto-collapses and Section 03 opens.

---

## A7. Section 03 — Lighting

**Purpose:** Control the environment, reference objects, and run an Arnold preview render.

### 2x2 Control Grid

```
┌────────────────────────┬────────────────────────┐
│  VISIBILITY            │  SIZE REFERENCES       │
│                        │                        │
│  [✓] Model             │  [✓] Floor Grid        │
│  [✓] Shader Ball       │  [ ] Ref Cubes         │
│  [✓] Charts            │                        │
│                        │  [ 10 cm ]  [ 1 mt ]   │
├────────────────────────┼────────────────────────┤
│  BACKDROP              │  ARNOLD RENDER         │
│                        │                        │
│  [ HDRI ]  [ LIMBO ]   │  [ RenderView ]        │
│                        │  [ Render     ]        │
└────────────────────────┴────────────────────────┘
```

#### VISIBILITY

| Checkbox | Controls |
|---|---|
| **Model** | Shows / hides the attached model or shader ball geometry |
| **Shader Ball** | Shows / hides the shader ball assembly specifically |
| **Charts** | Shows / hides the Macbeth colour chart and reference ball assembly |

#### SIZE REFERENCES

| Control | Description |
|---|---|
| **Floor Grid** | Overlays a measurement grid on the limbo backdrop. Grid unit is set by the unit buttons below. |
| **Ref Cubes** | Shows / hides the size reference cube geometry (hidden by default). |
| **10 cm** | Sets the grid and ref cube to 10-centimetre scale. |
| **1 mt** (default) | Sets the grid and ref cube to 1-metre scale. |

#### BACKDROP

| Button | Description |
|---|---|
| **HDRI** | Physical floor and environment geometry, lit by the active HDRI. |
| **LIMBO** (default) | Infinite white limbo backdrop. Enable **Floor Grid** to overlay the measurement texture. |

#### ARNOLD RENDER

| Button | Description |
|---|---|
| **RenderView** | Opens the Arnold RenderView window for interactive IPR rendering. |
| **Render** | Triggers a full frame render sequence through the Arnold RenderView (play behaviour). |

---

### Charts Placement

Below the 2×2 grid, sliders position the colour charts in the scene. Click a slider label to reset it to its default value.

| Slider | Range | Default | Controls |
|---|---|---|---|
| **Scale** | 0.5 — 1.5 | 1.0 | Scales `macbeth_grp` and `refBall_grp` together |

Two-column layout for individual axis control:

| Column | Slider | Range | Default | Controls |
|---|---|---|---|---|
| **REF BALL** | X | -100 — 100 | 0.0 | `refBall_grp` translateX |
| | Y | -100 — 100 | 0.0 | `refBall_grp` translateY |
| **MACBETH** | X | -100 — 100 | 0.0 | `macbeth_grp` translateX |
| | Y | -100 — 100 | 0.0 | `macbeth_grp` translateY |

> Each slider has an editable spinbox on the right. Type any value beyond the slider range for manual override.

---

## A8. HDRI Grid

The HDRI grid appears at the bottom of the Lighting section. It selects the active environment light.

```
┌──────────┬──────────┬──────────┬──────────┐
│  Studio  │ D.Ovcst  │  D.Sun   │  Cloudy  │  ← row 1: preset slots 01–04
├──────────┼──────────┼──────────┼──────────┤
│  Night   │  N.Neon  │    +     │    +     │  ← row 2: presets 05–06, custom 07–08
└──────────┴──────────┴──────────┴──────────┘
```

| Slot type | Behaviour |
|---|---|
| **Preset (01–06)** | Shows a JPEG preview thumbnail. Click to activate. Active slot gets an orange border. |
| **Custom (07–08) — empty** | Shows a `+` symbol. Click to browse for a `.hdr` or `.exr` file. |
| **Custom — loaded** | Shows the generated preview thumbnail. Click to activate. |

**When you load a custom HDRI the tool will:**
1. Target the existing `TT_SCENE:Custom_HDRI_01` or `_02` file node.
2. Copy the HDRI file into `TurnTable_ROOT/sourceimages/HDRIs/`.
3. Generate a tone-mapped JPEG preview and save it to the `previews/` subfolder (requires OpenCV).
4. Set the colorspace to `Utility - Linear - sRGB`.
5. Update the slot thumbnail.

> Custom HDRI colorspace defaults to `Utility - Linear - sRGB`. If your file requires a different colorspace, set it manually on the file node in the Attribute Editor after loading.

---

## A9. Clear Scene

```
[ Clear Scene · removes turntable, keeps model ]
```

Always visible at the bottom of the PREP tab. Styled red (destructive).

Removes the `TT_SCENE` Maya reference and safely re-parents your model back to the world root. Foster-parent cleanup runs automatically — no stray `fosterParent` nodes are left behind.

> Your geometry is never deleted. After clearing, you can reload a fresh turntable and re-attach the model.

---

## A10. Tips & Notes

| Topic | Note |
|---|---|
| **Apply frame range** | Click **Apply** every time you change the frame range fields. The animation is not updated live — you will see a reminder warning in the UI. |
| **Re-attach model** | You can run steps ① ② ③ multiple times — for example after swapping the model — without clearing the scene first. |
| **Camera** | The tool switches the viewport to `main_CAM` on scene load. Do not rename `main_CAM` in the turntable scene. Resolution gate and gate mask are enabled automatically. |
| **ACES** | Always activate ACES 1.2 in your Maya project before loading the turntable scene. The Preliminary Steps section shows a link to a setup guide if it is not detected. |
| **Updating the script** | Drop the new `.py` file into your scripts folder and re-run the launch snippet. The singleton check will close the old window automatically. |
| **Config reset** | Delete `~/Documents/maya/PXLmentor/turntable_builder_config.json` to reset all saved paths and start fresh. |
| **Shader Ball defaults** | The shader ball, cloth, and liquid elements start matching the state of the scene. The UI reads live scene state on load so the checkboxes are always accurate. |

---

# Part B — Nuke TurnTable Comp Setup

**Version:** 1.1.0-alpha  
**Requires:** Nuke 15 · Python 3 · PySide2 · ACES 1.2  
**Live Mode** — all controls update the comp immediately. No Apply button.

---

## B1. Installation

### Quick Load — Script Console (fastest)

1. Copy `PXLmentor_TurnTable_Comp_Setup_v1_1_0_alpha.py` to a folder Nuke can find.

   The easiest location is the Nuke user scripts folder:
   ```
   C:\Users\<YourUsername>\.nuke\
       └── PXLmentor_TurnTable_Comp_Setup_v1_1_0_alpha.py
   ```
   Or any folder already registered in `nuke.pluginPath()`.

2. Open the **Nuke Script Editor** (or Script Console), set the language to **Python**, paste the following, and press **Ctrl + Enter**:

   ```python
   import importlib, sys
   mod = "PXLmentor_TurnTable_Comp_Setup_v1_1_0_alpha"
   if mod in sys.modules:
       importlib.reload(sys.modules[mod])
   else:
       __import__(mod)
   sys.modules[mod].launch()
   ```

   Re-running raises the existing window if it is already open.

---

### Full Nuke Toolbar Integration

This method adds the tool permanently to the **Nodes** toolbar under a **PXLmentor** submenu, with the correct icon.

**Step 1 — Create the toolbox folder** (if it does not exist):

```
C:\Users\<YourUsername>\.nuke\PXLmentorToolbox\
    ├── scripts\
    └── icons\
```

**Step 2 — Copy the script**

```
.nuke\PXLmentorToolbox\scripts\
    └── PXLmentor_TurnTable_Comp_Setup_v1_1_0_alpha.py
```

**Step 3 — Copy the icon**

```
.nuke\PXLmentorToolbox\icons\
    └── PXLmentor_TurnTable_Comp_Setup.png
```

**Step 4 — Edit `~/.nuke/init.py`**

Add these lines so Nuke can find the scripts and icons on startup:

```python
import nuke, os
toolbox = os.path.join(os.path.expanduser("~"), ".nuke", "PXLmentorToolbox")
nuke.pluginAddPath(os.path.join(toolbox, "scripts"))
nuke.pluginAddPath(os.path.join(toolbox, "icons"))
```

**Step 5 — Edit `~/.nuke/menu.py`**

Add these lines to register the tool in the Nodes toolbar:

```python
import nuke

_toolbar  = nuke.toolbar("Nodes")
_pxl_menu = _toolbar.addMenu("PXLmentor", icon="PixelMentor_Logo_SQUARE_64.png")

try:
    import PXLmentor_TurnTable_Comp_Setup_v1_1_0_alpha as _ttcs
    _pxl_menu.addCommand(
        "TurnTable Comp Setup",
        _ttcs.launch,
        icon="PXLmentor_TurnTable_Comp_Setup.png"
    )
except Exception as e:
    nuke.warning(f"PXLmentor: could not load TurnTable Comp Setup — {e}")
```

> If other PXLmentor tools are already in `menu.py`, add only the `try/except` block to the existing `_pxl_menu`.

**Step 6 — Restart Nuke**

The PXLmentor submenu will appear in the Nodes toolbar.

---

## B2. Running the Tool

Use the Script Console snippet from B1 or click the toolbar button. The panel is modeless — it stays open while you work in Nuke.

To reload the latest version of the script without restarting Nuke:

```python
import glob, os, sys, importlib
_scripts = r"C:\Users\<YourUsername>\.nuke\PXLmentorToolbox\scripts"
_matches = sorted(glob.glob(os.path.join(_scripts, "PXLmentor_TurnTable_Comp_Setup_v*.py")))
if _matches:
    _mod = os.path.splitext(os.path.basename(_matches[-1]))[0]
    if _mod in sys.modules:
        importlib.reload(sys.modules[_mod])
    else:
        importlib.import_module(_mod)
    sys.modules[_mod].launch()
```

---

## B3. UI at a Glance

```
┌─────────────────────────────────────────────────────────┐
│  [icon]       PXLmentor                                 │
│               TurnTable Comp Setup                      │  ← header (dark teal, 100px)
│               v1.1.0-alpha — Live Mode                  │
├─────────────────────────────────────────────────────────┤
│  ●  No comp loaded                      [Reconnect]     │  ← node indicator bar (fixed)
├─────────────────────────────────────────────────────────┤  ← scrollable area begins
│  ▼   COMP SETUP                                         │  ← starts expanded
│    ▼  1  IMPORT TEMPLATE                                │    ▼ starts open
│       [ Import Comp Template ]                          │
│       status label                                      │
│    ▶  2  RENDER LOCATION & FRAMES                       │
│    ▶  3  ASSET INFO                                     │
├─────────────────────────────────────────────────────────┤
│  ▼   VISUAL OPTIONS                                     │  ← starts expanded
│       HDRI / Render / Background / Comp FX              │
│       BG Color  [■]    Wire Color  [■]                  │
├─────────────────────────────────────────────────────────┤
│  ▶   COMP EFFECTS                                       │  ← collapsed by default
│  ▶   TECH SETTINGS                                      │
│  ▶   REFERENCES                                         │
│  ▶   EXPORT                                             │  ← closes all others when opened
├─────────────────────────────────────────────────────────┤
│  status label                                           │
├─────────────────────────────────────────────────────────┤
│                                          [Close]        │
└─────────────────────────────────────────────────────────┘
```

All controls are **live** — values are pushed to the comp nodes immediately on change.

---

## B4. Connecting to a Comp Node

The **node indicator bar** shows which comp group is currently bound to the panel:

| Dot colour | Meaning |
|---|---|
| Green | Comp connected — all required nodes found in `TB3DTT` group |
| Yellow | Group exists but some nodes are missing |
| Grey | No comp loaded |

### Reconnect Button

Click **Reconnect** to bind the panel to a different TB3DTT comp group:

1. In the Nuke Node Graph, select the `TB3DTT` group node you want to control.
2. Click **Reconnect** in the panel.
3. The indicator bar updates to show the new group name. All UI controls are synced from that node's saved state.

This is also the correct way to re-open control of an existing comp after closing and re-opening the tool.

---

## B5. COMP SETUP Section

Three sequential sub-steps, each as a collapsible. They advance automatically on success.

### Step 1 — Import Template

| Control | Description |
|---|---|
| **Import Comp Template** | Pastes `PXLmentor_TB3DTT_COMP_v005.nk` into the current Nuke script. Imports all comp nodes, creates the `TB3DTT` group, and connects the viewer. Auto-applies a default state to the comp (Studio HDRI, lens dirt on, vignette on, etc.). |
| Status label | Reports success or any missing file errors. |

After a successful import, Step 1 collapses and Step 2 opens.

### Step 2 — Render Location & Frames

| Control | Description |
|---|---|
| **Render Folder** | Browse to the folder where your Maya renders live (the folder containing `RL_hdri_01`, `RL_hdri_02`, etc. subfolders). |
| **Format** | Target output format combo (e.g. HD_1080). |
| **FPS** | Output frame rate (23.976 / 24 / 25 / 29.97 / 30 / 48 / 50 / 59.94 / 60). |
| **Start / End** | Frame range fields. |
| **Apply Project Settings** | Writes format, FPS, and frame range to the Nuke project. |

After the folder is set, Step 2 collapses and Step 3 opens.

### Step 3 — Asset Info

| Control | Description |
|---|---|
| **Type** | Asset type code (CHR / ENV / PRO / VHC). |
| **Name** | Asset name field. |
| **Dept** | Department code (mdl / tex / shd / dtl / grm / rig / cfx / fx / …). |
| **Version** | Version string (e.g. `v001`). |
| **User** | User ID. |
| **Auto-fill from Folder** | Parses the render folder name to extract type, name, dept, version, and user. Works when the folder follows the `TYPE_Name_dept_vXXX_user_RL_...` naming convention. |
| Preview | Live colour-coded string showing the assembled asset info as it will appear in the comp. |

After a successful auto-fill, Step 3 collapses.

---

## B6. Visual Options

Controls that affect the comp's look in real time.

| Control | Options | Description |
|---|---|---|
| **HDRI** | 01 Studio / 02 Day Overcast / 03 Direct Sun / 04 Cloudy Sun / 05 Night / 06 Night Neon / 07 / 08 | Selects the HDRI environment used in the background plate. |
| **Render** | Beauty / Clay / UV / Wireframe | Switches the comp's render mode via `Switch_Mode` node. |
| **Background** | HDRI / Color | Switches between HDRI environment background and a flat colour background. |
| **Comp FX** | on / off | Enables or disables the full comp effects chain (`COMPFX_switch`). |
| **BG Color** | colour swatch | Click to open a colour picker. Sets the solid background colour when Background is set to Color. |
| **Wire Color** | colour swatch | Click to open a colour picker. Sets the wireframe overlay colour. |

---

## B7. Comp Effects

Individual post-processing effects. Each has an enable toggle — changes take effect immediately.

### ZDefocus

Depth-of-field blur using Z-depth data.

| Control | Description |
|---|---|
| Enable toggle | Checkbox — off by default |
| **Center** | Focus plane position (normalised X,Y) |
| **DoF** | Depth of field range |
| **Size** | Blur size |
| **Output** | Result (final comp) / Focal Plane (debug visualisation of the focus plane) |

### Lens Dirt

Simulates lens dirt as a screen-space overlay.

| Control | Description |
|---|---|
| Enable toggle | Checkbox — on by default |
| **Mix** | Blend strength (0.0 — 1.0). Default: 0.35 |

### LUT

Applies an OCIO LUT file to the image.

| Control | Description |
|---|---|
| Enable toggle | Checkbox — on by default |
| **Path** | Browse to a `.cube` or compatible LUT file |
| **Mix** | Blend strength. Default: 0.35 |

### Vignette

Darkens the frame edges.

| Control | Description |
|---|---|
| Enable toggle | Checkbox — on by default |

### BG Ramp

Gradient ramp on the background.

| Control | Description |
|---|---|
| Enable toggle | Checkbox — on by default |

---

## B8. Tech Settings

Controls for scene elements that are generally left on during production.

| Control | Default | Description |
|---|---|---|
| **Occlusion** | Off | Enable ambient occlusion pass contribution |
| **Shadow** | On | Enable shadow pass contribution |
| **Text Info** | On | Show asset info text overlay (`Text_Info` node) |
| **Font Scale** | 1.0 | Scale factor for the asset info text |

> These checkboxes use inverse disable logic compared to Comp Effects — checked = feature ON.

---

## B9. References

Controls for the reference assets that appear alongside the model in the comp.

| Control | Default | Description |
|---|---|---|
| **Ref Ball** | On | Show / hide the reference chrome/grey ball |
| **HDRI Preview** | On | Show / hide the HDRI environment reference image |
| **Ref Images** | On | Show / hide the reference image slot group |
| **Translate** | 0, 0 | X / Y offset for the reference image group |
| **Scale** | 1.0 | Scale for the reference image group |

### Reference Image Layout

Toggle between two display modes:

| Mode | Description |
|---|---|
| **Single** | One large reference image fills the reference area |
| **6-slot contact sheet** | Six drag-and-drop cards (16:9 aspect) arranged in a 3×2 grid |

Each card accepts images by drag-and-drop or click-to-browse. Supported formats: JPG, PNG, TIFF, EXR. EXR files show an orange placeholder (no preview). Slots 05 and 06 have an individual on/off toggle in the card header.

---

## B10. Export

Configure and create the Write node for rendering out the comp.

> Opening the EXPORT section automatically closes all other collapsibles to give it full focus.

| Control | Description |
|---|---|
| **Name** | Auto-generated from asset info: `TYPE_name_dept_ver_user_TT_HDRIxx_Mode`. Edit manually if needed. |
| **Add version** | Checkbox + field to append a version suffix to the output name. |
| **Folder** | Browse to the output directory. |
| **Format** | Output format (exr / png / tiff / etc.). |
| **Colorspace** | OCIO colorspace for the Write node. |
| **CREATE Write Node** | Creates a new `Write_TT` node (or `Write_TT_2`, etc. if one already exists) at the Nuke root level, connected to the `TB3DTT` group output. Sets `create_dir=True`. |
| **APPLY to Selected** | Applies the current path, format, and colorspace to the currently selected Write node (falls back to `Write_TT` if nothing is selected). |

---

## B11. Session Persistence

The tool stores UI state as JSON inside an invisible knob (`pxl_tt_panel_state`) on the `TB3DTT` group node. This means:

- State travels with the `.nk` file.
- Multiple TB3DTT instances in the same script each carry their own state.
- Clicking **Reconnect** restores the full UI from the saved state of the target node.
- The Export folder / name / format / colorspace are also saved and restored.

Global prefs (e.g. tool window geometry) are saved separately to:

```
C:\Users\<YourUsername>\.nuke\PXLmentorToolbox\tt_comp_setup_prefs.json
```

---

## B12. Tips & Notes

| Topic | Note |
|---|---|
| **Live mode** | Every control pushes changes to the comp immediately. There is no Apply or Update button. |
| **Multiple comps** | You can have several TB3DTT groups in one Nuke script. Select the target group and click **Reconnect** to switch control between them. |
| **ACES 1.2** | The comp template is built for ACES 1.2. Make sure your Nuke project uses the correct OCIO config before importing. |
| **Comp template path** | Hard-coded to `D:/TB3DTT/TurnTable_ROOT/_COMP/PXLmentor_TB3DTT_COMP_v005.nk`. If the template is in a different location, edit `COMP_TEMPLATE_PATH` at the top of the script. |
| **ZDefocus output** | Use **Focal Plane** output to visually inspect the focus plane position before committing to the blur. |
| **Ref images — EXR** | EXR reference images display an orange placeholder in the panel. The actual EXR is still connected to the comp correctly. |
| **Export — CREATE vs APPLY** | Use **CREATE** the first time. Use **APPLY** to update an existing Write node without creating a new one. |
| **Reconnect after reopen** | If you close and reopen the tool on an existing script, click **Reconnect** to resync the UI from the node's saved state. |

---

# 5. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| **Maya: Tool window does not open** | Script not in Maya scripts folder | Copy the `.py` to `~/Documents/maya/2025/scripts/` |
| **Maya: Orange warning banner won't go away** | Root folder not set or invalid | Open Preliminary Steps, click Browse, select the correct `TurnTable_ROOT` folder, click Set Root Folder |
| **Maya: HDRI thumbnails not showing** | Preview images missing from `TurnTable_ROOT/sourceimages/HDRIs/previews/` | Ensure the previews folder contains matching JPEG files |
| **Maya: Custom HDRI has no preview** | OpenCV not installed | Click Install OpenCV in Preliminary Steps |
| **Maya: Frame range not applying** | Apply not clicked after changing fields | Always click Apply after editing the frame range |
| **Maya: Model does not spin** | Apply frame range never clicked | Click Apply in Section 01 to create the rotation keyframes |
| **Nuke: Panel opens but shows "No comp loaded"** | Comp template not imported | Run through COMP SETUP — Import Template |
| **Nuke: Reconnect does nothing** | No group node selected in the Node Graph | Select the TB3DTT group in the Node Graph first, then click Reconnect |
| **Nuke: Controls have no effect on the comp** | Panel is bound to the wrong group | Select the correct TB3DTT group and click Reconnect |
| **Nuke: Import Template fails** | Comp template file not found at the hard-coded path | Edit `COMP_TEMPLATE_PATH` at the top of the script to point to your `_COMP` folder |
| **Nuke: Auto-fill does not populate fields** | Render folder name does not follow the naming convention | Fill Type / Name / Dept / Version / User manually |
| **Nuke: Export path has no effect** | APPLY clicked without a Write node selected | Use CREATE first to generate `Write_TT`, then use APPLY for subsequent updates |
