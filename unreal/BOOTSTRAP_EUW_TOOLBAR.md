# Bootstrap: PXLmentor MU Bridge Toolbar Icon (Editor Utility Widget)

**One-time manual work in UE 5.6 to put the actual `icon_mu_bridge.png` brand icon on the Level Editor toolbar.** Same pattern as the `M_PXL_PBR_Master.uasset` bootstrap. Do this once per UE project; commit the resulting `.uasset` files; `pxl_mu_bridge.py` registers the widget on the toolbar on every UE startup thereafter.

**Estimated time:** ~15 minutes.

**You need:** UE 5.6 open with your test project (`E:\TestTools\TestTools`).

---

## Step 1 — Import the MU Bridge icon as a Texture2D

1. In the Content Browser, navigate to `/Game/` (or create `/Game/PXLbridge/Icons/`).
2. Right-click in the Content Browser → **Import to /Game/PXLbridge/Icons/**.
   (If the folder doesn't exist, right-click in `/Game/`, choose **New Folder**, name it `PXLbridge`. Inside, create another folder named `Icons`. Then right-click in `Icons/` → Import.)
3. Pick this file:
   ```
   C:\Users\Evil Knight\Documents\maya\2025\prefs\icons\icon_mu_bridge.png
   ```
4. After import, the new asset is named `icon_mu_bridge` — **rename it to `T_MUBridge`** (right-click → Rename, or F2).
5. **Double-click `T_MUBridge`** to open the Texture Editor.
6. In the Texture Editor, set:
   - **Texture Group**: `UI`
   - **Compression Settings**: `UserInterface2D (RGBA)` (preserves transparency, no compression artefacts at small sizes)
   - **sRGB**: ON
7. Save (Ctrl+S), close the Texture Editor.

Final path: `/Game/PXLbridge/Icons/T_MUBridge`.

---

## Step 2 — Create the Editor Utility Widget

1. Navigate to `/Game/PXLbridge/` in the Content Browser.
2. Right-click → **Editor Utilities → Editor Utility Widget**.
   (If you don't see "Editor Utilities" in the right-click menu, enable the **Blutility** plugin: Edit → Plugins → search "Blutility" → Enable → restart UE → retry.)
3. Name the new asset **`W_MUBridge_Toolbar`**.
4. Double-click `W_MUBridge_Toolbar` to open the Widget Editor.

---

## Step 3 — Build the button

1. The Widget Editor opens with a `[Designer]` tab. The canvas is empty.
2. In the **Palette** (left side), find **Common → Button**. Drag it onto the canvas.
3. In the **Hierarchy** (left side), select the **Button** you just dropped.
4. In the **Details** panel (right side), set:
   - **Style → Normal → Image**:
     - Click the dropdown next to `None`, search for `T_MUBridge`, select it.
     - Below `Image`, set **Image Size → X = 40, Y = 40** (matches the standard UE toolbar icon size).
     - **Tiling**: `NoTile`.
   - **Style → Hovered → Image**: same texture (`T_MUBridge`), same size. Optionally set **Tint** to a slightly brighter color so hover is visible.
   - **Style → Pressed → Image**: same texture, slightly darker tint.
   - **Style → Disabled → Image**: same texture, gray tint.
5. **Size the button**. With the Button still selected:
   - In the **Slot (Canvas Panel Slot)** section of Details, set:
     - **Anchors**: stretch to fill (top-left default is fine if the canvas itself is 40x40)
     - Or simpler: set **Size To Content** = OFF, and set width/height explicitly to 40x40.
6. **Set the root canvas size** so the EUW renders as a 40x40 button on the toolbar:
   - In the Hierarchy, click `CanvasPanel` (the root).
   - In Details, find the **Editor → Desired Size on Screen** (or similar field) and set **X = 40, Y = 40**.

---

## Step 4 — Wire the click

1. In the Widget Editor, switch to the **[Graph]** tab (top-right of the editor).
2. In the **Variables** panel (left), select **Button_0** (or whatever your button is named) → drag it into the graph → choose **Get Button_0**.
3. Right-click the Button reference node → **Add Event → On Clicked**.
4. From the `On Clicked` execution pin, drag a wire and search for **Execute Python Command**. Connect it.
5. In the `Execute Python Command` node, set the **Python Command** field to exactly:
   ```
   import pxl_mu_bridge; pxl_mu_bridge._open_mu_bridge()
   ```
6. **Compile** (top-left of the Widget Editor) and **Save** (Ctrl+S).

---

## Step 5 — Test the widget standalone

1. In the Content Browser, right-click `W_MUBridge_Toolbar` → **Run Editor Utility Widget**.
2. A small window/tab opens with your MU Bridge icon as a clickable button.
3. **Click the icon**. The MU Bridge window should open.
4. If it does — wiring is correct. Close the tab.
5. If it doesn't — check that the Python Command string in Step 4.5 is EXACTLY `import pxl_mu_bridge; pxl_mu_bridge._open_mu_bridge()` (no quotes, no extra spaces).

---

## Step 6 — Restart UE

After UE restart, `pxl_mu_bridge.py` detects `W_MUBridge_Toolbar` at `/Game/PXLbridge/W_MUBridge_Toolbar` and registers it on the Level Editor toolbar automatically. The MU Bridge icon appears on the toolbar.

**Check the log** at `J:\tmp\pxl_toolbar_LATEST.txt` — should now include a `--- EUW toolbar registration attempt ---` section showing whether the EUW registration succeeded.

If the EUW is registered but you still don't see the icon on the toolbar, the log tells us why and we adjust the registration call.

---

## Step 7 — Commit the assets

Once verified, commit:
- `<Project>/Content/PXLbridge/Icons/T_MUBridge.uasset`
- `<Project>/Content/PXLbridge/W_MUBridge_Toolbar.uasset`

These two assets are the one-time bootstrap. Every UE project that wants the MU Bridge toolbar icon needs them; the Python side picks them up automatically.

---

## Troubleshooting

- **"Editor Utility Widget" missing from right-click menu** → Enable the **Blutility** plugin (Edit → Plugins → search "Blutility").
- **Python Command in Step 4 errors** → Open Window → Python Console → try the command manually. Should open the MU Bridge window. If it errors, check the Output Log for the traceback.
- **Icon is fuzzy/pixelated at small sizes** → In Step 1.6, confirm **Compression Settings = UserInterface2D (RGBA)** and **Texture Group = UI**. Default settings will compress the PNG and look bad at 40x40.
- **Button doesn't render** → In Step 3, confirm the Button's Style → Normal → Image has `T_MUBridge` selected (not `None`). The image preview should show the M→U icon.
