# Bootstrap: PXLmentor MU Bridge Master Material (`M_PXL_PBR_Master.uasset`)

**One-time manual authoring in UE 5.6.1 to create the master Material every MU Bridge imported asset parents to.** This is the V0.1 canonical path; the auto-builder fallback in `material_factory.py` only writes a minimal 5-texture variant and leaves scalar/vector parameter overrides dead. Build it once, commit the `.uasset` to the staged location, every UE project that imports from MU Bridge gets a polished master automatically.

**Estimated time:** ~25 minutes.

**You need:** UE 5.6 open with your test project (e.g. `E:\TestTools\TestTools`).

---

## Why this exists

`pxl_mu_bridge_pkg/material_factory.py` builds a `MaterialInstanceConstant` parented to `/Game/PXLbridge/M_PXL_PBR_Master`. The MI sets:

- **Scalar parameters** — `Metallic`, `Roughness`, `IOR`, `EmissiveStrength`, `Opacity`
- **Vector parameters** — `BaseColorTint`, `EmissiveColor`
- **Texture parameters** — `BaseColorTex`, `RoughnessTex`, `MetallicTex`, `NormalTex`, `EmissiveTex`, `OpacityTex`
- **Static-switch parameters** — `UseBaseColorTex`, `UseRoughnessTex`, `UseMetallicTex`, `UseNormalTex`, `UseEmissiveTex`, `UseOpacityTex`, `bMasked`

The master must expose ALL of these parameter names — otherwise the MI's overrides silently no-op.

---

## Step 1 — Create the Material asset

1. In the Content Browser, navigate to `/Game/` and create folder `PXLbridge` if not present.
2. Inside `/Game/PXLbridge/`, right-click → **Material**.
3. Name the new asset **`M_PXL_PBR_Master`**.
4. Double-click `M_PXL_PBR_Master` to open the Material Editor.

---

## Step 2 — Add Scalar parameters (5 total)

In the Material Graph, right-click the empty canvas → search for **ScalarParameter** → drop one node per scalar. For each, select the node and in **Details → Parameter Name** type the exact name from the table below. Set **Default Value** as shown.

| Parameter Name     | Default Value | Wires to              |
|--------------------|---------------|-----------------------|
| `Metallic`         | 0.0           | Material → Metallic   |
| `Roughness`        | 0.5           | Material → Roughness  |
| `IOR`              | 1.5           | (unused for now — keep for v0.2 refraction work) |
| `EmissiveStrength` | 1.0           | Multiplier on EmissiveTex × EmissiveColor |
| `Opacity`          | 1.0           | Material → Opacity (only used when blend mode is Translucent) |

---

## Step 3 — Add Vector (Color) parameters (2 total)

Right-click → **VectorParameter** → drop 2 nodes.

| Parameter Name   | Default Value             | Wires to                       |
|------------------|---------------------------|--------------------------------|
| `BaseColorTint`  | `(1.0, 1.0, 1.0, 1.0)` (white) | Multiplied with BaseColorTex.RGB |
| `EmissiveColor`  | `(0.0, 0.0, 0.0, 1.0)` (black) | Multiplied with EmissiveTex.RGB × EmissiveStrength |

---

## Step 4 — Add Texture parameters (6 total)

Right-click → **TextureSampleParameter2D** → drop 6 nodes. For each, set:
- **Parameter Name** — exact name from table
- **Sampler Type** — as shown
- **Texture** — leave as the default UE engine texture (e.g. `T_DefaultBaseColor`); the MI overrides this per asset

| Parameter Name | Sampler Type             | Default Texture                          |
|----------------|--------------------------|------------------------------------------|
| `BaseColorTex` | `Color`                  | `T_DefaultBaseColor` (UE default white)   |
| `MetallicTex`  | `LinearColor` (grayscale)| `T_DefaultMetallic` (UE default black)    |
| `RoughnessTex` | `LinearColor` (grayscale)| `T_DefaultRoughness` (UE default 0.5 gray)|
| `NormalTex`    | **`Normal`**             | UE default flat normal (`T_FlatNormal`)   |
| `EmissiveTex`  | `Color`                  | UE default black                         |
| `OpacityTex`   | `LinearColor` (grayscale)| UE default white                         |

---

## Step 5 — Add Static-switch parameters (7 total)

Right-click → **StaticSwitchParameter** → drop 7 nodes.

| Parameter Name      | Default Value | Purpose                                              |
|---------------------|---------------|------------------------------------------------------|
| `UseBaseColorTex`   | false         | When true: BaseColorTex × BaseColorTint → BaseColor; when false: BaseColorTint → BaseColor |
| `UseRoughnessTex`   | false         | When true: RoughnessTex.R × Roughness → Roughness; when false: Roughness scalar → Roughness |
| `UseMetallicTex`    | false         | When true: MetallicTex.R × Metallic → Metallic; when false: Metallic scalar → Metallic |
| `UseNormalTex`      | false         | When true: NormalTex → Normal; when false: flat normal (no normal map) |
| `UseEmissiveTex`    | false         | When true: EmissiveTex × EmissiveColor × EmissiveStrength → Emissive; when false: EmissiveColor × EmissiveStrength → Emissive |
| `UseOpacityTex`     | false         | When true: OpacityTex.R × Opacity → OpacityMask; when false: Opacity scalar → OpacityMask |
| `bMasked`           | false         | When true: blend mode = Masked, OpacityMask pin active; when false: blend mode = Opaque |

> Static switches do compile-time branching — they don't cost shader instructions like a runtime `if`. Use them anywhere the choice is "texture present or absent."

---

## Step 6 — Wire the branches

For each PBR channel with a "use texture" switch, build this pattern:

```
[TextureSampleParameter2D] --(channel)--+
                                        |
[Switch Off branch: ScalarParam] -------+--[StaticSwitch]-- Material pin
[Switch On  branch: Texture * Scalar] --+
```

### BaseColor branch
1. Drag `BaseColorTex.RGB` → into a **Multiply** node's A input.
2. Drag `BaseColorTint.RGB` → into the Multiply's B input.
3. The Multiply output → connects to `UseBaseColorTex.True` input.
4. `BaseColorTint.RGB` → also connects directly to `UseBaseColorTex.False` input.
5. `UseBaseColorTex` output → **Material → Base Color**.

### Metallic branch
1. `MetallicTex.R` × `Metallic` → `UseMetallicTex.True`.
2. `Metallic` → `UseMetallicTex.False`.
3. `UseMetallicTex` output → **Material → Metallic**.

### Roughness branch
1. `RoughnessTex.R` × `Roughness` → `UseRoughnessTex.True`.
2. `Roughness` → `UseRoughnessTex.False`.
3. `UseRoughnessTex` output → **Material → Roughness**.

### Normal branch
1. `NormalTex.RGB` → `UseNormalTex.True`.
2. A `Constant3Vector(0, 0, 1)` (flat normal) → `UseNormalTex.False`.
3. `UseNormalTex` output → **Material → Normal**.

### Emissive branch
1. `EmissiveTex.RGB` × `EmissiveColor.RGB` × `EmissiveStrength` (chain two Multiply nodes) → `UseEmissiveTex.True`.
2. `EmissiveColor.RGB` × `EmissiveStrength` → `UseEmissiveTex.False`.
3. `UseEmissiveTex` output → **Material → Emissive Color**.

### Opacity branch (used only when `bMasked` = true)
1. `OpacityTex.R` × `Opacity` → `UseOpacityTex.True`.
2. `Opacity` → `UseOpacityTex.False`.
3. `UseOpacityTex` output → connect to **`bMasked.True`** input.
4. `bMasked.False` input: leave unconnected (Opaque blend uses no OpacityMask).
5. `bMasked` output → **Material → Opacity Mask**.

---

## Step 7 — Material Details settings

With the Material output node selected, in **Details**:

| Property                     | Value             | Why                                              |
|------------------------------|-------------------|--------------------------------------------------|
| **Material Domain**          | `Surface`         | Standard PBR                                     |
| **Blend Mode**               | `Opaque`          | The MI flips this to `Masked` via `bMasked` switch when an OpacityTex or sub-1 opacity is present |
| **Shading Model**            | `Default Lit`     | Standard PBR                                     |
| **Two Sided**                | `false`           | Per-asset override if needed                     |
| **Used with Static Lighting**| `true`            | Allows baked lighting                            |
| **Used with Skeletal Mesh**  | `false`           | StaticMesh only in V0.1                          |
| **Used with Particle Sprites**| `false`          | Not a particle material                          |

> The `Masked` blend mode requires both `bMasked = true` (static switch) AND an `OpacityMask` value below the `Opacity Mask Clip Value` (default 1/3). The MI takes care of flipping `bMasked` when the manifest has an `opacity` texture or scalar opacity below 1.0.

---

## Step 8 — Compile and save

1. In the Material Editor toolbar, click **Apply** (or press Ctrl+Shift+Enter).
2. Wait for shader compilation (status bar shows progress).
3. Click **Save** (Ctrl+S).

If the compile fails, the Output Log shows the broken wire — check that every PBR pin has exactly one StaticSwitch output landing on it and no dangling parameters.

---

## Step 9 — Verify with a smoke test

1. In the Content Browser, right-click `M_PXL_PBR_Master` → **Create Material Instance**. Name it `MI_test`.
2. Open `MI_test`. You should see ALL these parameter rows in the editor:
   - **Scalar parameters:** Metallic, Roughness, IOR, EmissiveStrength, Opacity
   - **Vector parameters:** BaseColorTint, EmissiveColor
   - **Texture parameters:** BaseColorTex, RoughnessTex, MetallicTex, NormalTex, EmissiveTex, OpacityTex
   - **Static switch parameters:** UseBaseColorTex, UseRoughnessTex, UseMetallicTex, UseNormalTex, UseEmissiveTex, UseOpacityTex, bMasked

3. If any row is missing → return to that step above and add the parameter to the master. Parameter names are case-sensitive.

4. Toggle `bMasked = true` on `MI_test` and verify the material switches to Masked blend mode.

5. Discard `MI_test` (right-click → Delete) — it was just a smoke test.

---

## Step 10 — Commit the asset to the staged location

Once compile passes and the smoke test succeeds:

1. In the Content Browser, right-click `M_PXL_PBR_Master` → **Show in Explorer**. This opens the `.uasset` file location.
2. Copy `M_PXL_PBR_Master.uasset` to:
   ```
   J:\ClaudeCode\projects\PXLtools\unreal\content\PXLbridge\M_PXL_PBR_Master.uasset
   ```
3. Confirm the file is at the staged path — `ensure_master()` in `material_factory.py` looks here first, then auto-creates a minimal fallback if it's missing.

The staged `.uasset` is committed and every UE project that imports via MU Bridge now gets the polished master copied into its own `Content/PXLbridge/` on first import. The programmatic auto-builder is now strictly a "you forgot to bootstrap" warning fallback.

---

## Troubleshooting

- **"Parameter name not unique" error on compile** → two nodes share the same Parameter Name. Search the graph (Ctrl+F) for the duplicate and rename or delete one.
- **MI doesn't show some parameter row** → master doesn't expose that exact parameter name (case-sensitive). Re-open the master, check Details for the parameter, and confirm the name.
- **Compile takes >2 minutes** → normal for first compile on a fresh project; subsequent edits compile in seconds.
- **Black mesh after MI import** → `UseBaseColorTex` static switch is not flipping to `true` when the MI has a BaseColorTex assigned. Check `material_factory.py:_TEXTURE_PARAM_MAP` matches the static-switch parameter names exactly.

---

## After bootstrap

`material_factory.py` will:
1. Detect the master at `/Game/PXLbridge/M_PXL_PBR_Master` already exists in the project → use it.
2. If absent: copy the staged `.uasset` from `<PXLtools>/unreal/content/PXLbridge/M_PXL_PBR_Master.uasset` into the project's `Content/PXLbridge/`.
3. If staged file is also absent: fall back to the minimal auto-builder (5 texture pins only, scalars + colors do nothing).

After committing the staged `.uasset`, path 3 is dead. Path 1 hits on the second import; path 2 hits on the first.
