# PXLmentor TurnTable Suite — Quick Start

**Maya TurnTable Builder** v1.0.17-beta  
**Nuke TurnTable Comp Setup** v1.1.0-alpha

For the full user guide see: `../TurnTable_Suite_User_Guide_Maya-v1.0.17-beta_Nuke-v1.1.0-alpha.md`

---

## What's in this Package

```
TurnTable_Package/
├── scripts/
│   ├── maya/   PXLmentor_TurnTable_Builder_v1_0_17_beta.py
│   └── nuke/   PXLmentor_TurnTable_Comp_Setup_v1_1_0_alpha.py
├── icons/
│   ├── icon_turntable_builder.png      (Maya)
│   └── PXLmentor_TurnTable_Comp_Setup.png  (Nuke)
├── PXLmentor_TurnTable_Suite_User_Guide_Maya-v1.0.17-beta_Nuke-v1.1.0-alpha.pdf
└── TurnTable_ROOT/          ← self-contained turntable asset folder
    ├── scenes/              Maya scene: PXLmentor_TB3DTT_ACES_2025_v003.ma
    ├── sourceimages/
    │   ├── HDRIs/           6 EXR HDRIs + thumbnail previews
    │   └── utilities/       Shader ball, Macbeth chart, misc textures
    └── _COMP/               Nuke comp template + dirt overlays + LUT
```

---

## Maya — Quick Install

1. Copy the Maya script to:
   ```
   C:\Users\<YourUsername>\Documents\maya\2025\scripts\
   ```
2. Copy `icons/icon_turntable_builder.png` to:
   ```
   C:\Users\<YourUsername>\Documents\maya\2025\prefs\icons\
   ```
3. In the Maya Script Editor (Python tab), paste and press Ctrl+Enter:
   ```python
   import importlib, sys
   mod = "PXLmentor_TurnTable_Builder_v1_0_17_beta"
   if mod in sys.modules:
       importlib.reload(sys.modules[mod])
   m = sys.modules.get(mod) or __import__(mod)
   m.show()
   ```
4. Copy the `TurnTable_ROOT/` folder from this package to a permanent location on your machine.
5. On first run: open **Preliminary Steps** and point the Root Folder field at your `TurnTable_ROOT/` location.

---

## Nuke — Quick Install

1. Copy the Nuke script to:
   ```
   C:\Users\<YourUsername>\.nuke\PXLmentorToolbox\scripts\
   ```
2. Copy `icons/PXLmentor_TurnTable_Comp_Setup.png` to:
   ```
   C:\Users\<YourUsername>\.nuke\PXLmentorToolbox\icons\
   ```
3. In the Nuke Script Editor (Python tab), paste and press Ctrl+Enter:
   ```python
   import importlib, sys
   mod = "PXLmentor_TurnTable_Comp_Setup_v1_1_0_alpha"
   if mod in sys.modules:
       importlib.reload(sys.modules[mod])
   else:
       __import__(mod)
   sys.modules[mod].launch()
   ```
4. Click **Import Comp Template** and follow the three setup steps.

---

## Nuke Toolbar (permanent install)

Add to `~/.nuke/init.py`:
```python
import nuke, os
toolbox = os.path.join(os.path.expanduser("~"), ".nuke", "PXLmentorToolbox")
nuke.pluginAddPath(os.path.join(toolbox, "scripts"))
nuke.pluginAddPath(os.path.join(toolbox, "icons"))
```

Add to `~/.nuke/menu.py`:
```python
import nuke
_toolbar  = nuke.toolbar("Nodes")
_pxl_menu = _toolbar.addMenu("PXLmentor", icon="PixelMentor_Logo_SQUARE_64.png")
try:
    import PXLmentor_TurnTable_Comp_Setup_v1_1_0_alpha as _ttcs
    _pxl_menu.addCommand("TurnTable Comp Setup", _ttcs.launch,
                         icon="PXLmentor_TurnTable_Comp_Setup.png")
except Exception as e:
    nuke.warning(f"PXLmentor: could not load TurnTable Comp Setup — {e}")
```

Restart Nuke. The tool appears under **Nodes > PXLmentor > TurnTable Comp Setup**.
