# PXLtools Tool-Icon Family — Concept Brief

> Art-direction brief. Words only — no images generated here. The
> prompt-engineer + creative-designer execute the set next, using this as the
> contract. Anchor reference studied:
> `J:\ClaudeCode\projects\PXLtools\nuke\icons\icon_turntable_builder.png`.

---

## Scope

- **What this is:** a unified icon family for ~13 PXLtools production tools spanning Maya, Nuke and Unreal-bridge. These are shelf buttons and launcher tiles, not marketing art — they ride next to native DCC icons all day.
- **Who uses it:** working VFX/CG artists (Maya 2025, Nuke 15) under PXLmentor / BlackMamba3D. They scan a crowded shelf at 96px and must hit the right tool in under a second. Insider register: these people read an isometric cube as "geometry," a shader ball as "material," a clapper as "edit" without a label.
- **Non-negotiable strategic anchor:** "feels like ONE tool." Every icon must read as a member of the same family as the anchor — same tile, same light, same greyscale-3D + single-orange language (PXLsuite CONVENTIONS §"ONE shared kit"; PXLtools CLAUDE.md §03 "Icons follow the same design system").
- **Visual territory to claim:** dark squircle app-tiles, top-lit greyscale isometric 3D objects, exactly ONE PXL-orange (`#E8820C`) accent per tile that names what the tool *does*.
- **Visual territory to avoid:** flat 2D line-icon sets (Lucide/Feather look), multi-color glyphs, gradient-fill "SaaS" icons, photorealistic skeuomorphism, and the generic Maya/Nuke native-icon flat-grey look. We are not making a sticker pack and not imitating Autodesk's own iconography.

**The accent-color note (read before you start):** PXLtools' *app UI chrome* migrated to gold `#f2b705` at v2.0.0 (CLAUDE.md §03). The **icon family does NOT** — icons are a separate surface and the anchor, this brief, and PXLsuite CONVENTIONS all mandate PXL Orange `#E8820C`. Use `#E8820C` for every icon accent. Do not substitute gold.

---

## 1 · The Shared Visual System

This is what stays CONSTANT across all 13 icons. The only thing that varies is the central greyscale object and where the single orange accent lands.

### Tile (constant)
- **Shape:** rounded square (squircle / iOS-style superellipse), not a plain rounded rect. Match the anchor's corner softness.
- **Corner radius:** ~22% of tile edge (≈ 56px on a 256px tile, ≈ 21px on 96px). Matches the anchor.
- **Background gradient:** vertical, top charcoal `#1e1e1e` → bottom near-black `#0a0a0a`/`#000`. Subtle — it reads as "lit from above," not as a banded gradient.
- **Edge:** a 1px inner highlight on the top edge and a faint inner shadow at the bottom give the tile its physical "tile" feel (as in the anchor). No outer drop shadow baked into the PNG — the DCC shelf provides its own background.
- **No text.** No tool name, no letters baked into the tile. The glyph carries it.

### Lighting & material (constant)
- **Light direction:** single key light from top, slightly front — top faces of every 3D object are the brightest, the object's right/under faces fall to mid-grey, the contact area is darkest. Identical across the set so every object looks lit by the same lamp.
- **Material:** matte-to-satin greyscale. Object value range roughly `#dcdcdc` (lit top) → `#8a8a8a` (mid) → `#4a4a4a` (shadow face). No saturated color on the object itself — color is reserved entirely for the accent.
- **Rendering style:** clean isometric / near-isometric 3D, soft ambient occlusion at contact, gentle bevels on hard edges (a hair of edge-light, not chrome). Think "matte product render," not "toon line art" and not "glossy 3D logo."

### The orange accent (constant rule, varies in form)
- **Exactly ONE accent element per icon,** always PXL Orange `#E8820C`.
- It is the part that does the **conceptual work** — it names the *verb* of the tool while the greyscale object names the *noun*. In the anchor: cube = the asset (noun), orange circular arrow = "turn it" (verb).
- The accent may be a path/arrow, a glowing edge, a small emitted element, or a single highlighted facet — but never a second color and never two separate accent ideas competing on one tile.
- Allow a faint orange bloom/glow where the accent meets the dark tile, so the accent feels lit, not pasted (matches the anchor's warm halo on the arrow).

### Safe area & padding (constant)
- **Glyph live area:** central ~76% of the tile. Keep a ~12% margin on all sides clear so the object + accent never touch the corner radius.
- The orange accent may extend into the outer margin (the anchor's arrow nearly reaches the edges) but the **greyscale object stays inside the inner 60–64%** so it never crowds the corners.

### 96px legibility rules (constant — this is the gate)
- **One object + one accent. Never more.** At 96px a second small object becomes mud.
- **Silhouette test:** the greyscale object must be identifiable by outline alone. If two tools share a similar silhouette (e.g. two box-like objects), differentiate by accent form and object proportion, not by tiny surface detail.
- **No detail finer than ~3px at 96px.** No text, no thin filigree, no small repeated elements (no contact-sheet "grid of 9 tiny frames" — abstract it).
- **Accent stroke weight:** the orange element reads at a minimum ~4px stroke at 96px. The anchor's arrow is bold for this reason — keep that weight family-wide.
- **Test deliverable:** every icon is reviewed at 96px FIRST, then refined at 256px. If it fails at 96px it's wrong, however nice it looks at 256px.

### What is CONSTANT vs what VARIES

| Constant (the family DNA) | Varies (per tool) |
|---|---|
| Tile shape, radius, gradient, edge treatment | The central greyscale 3D object (the noun) |
| Top-key lighting direction | The form the orange accent takes (the verb) |
| Greyscale matte material + value range | Where the accent sits relative to the object |
| Single `#E8820C` accent, one idea only | — |
| Safe-area margins, glyph live area | — |

---

## 2 · Per-Tool Glyph Concepts

Each entry: the noun (greyscale 3D object), the verb (orange accent), why it's right, and the 96px distinguisher. All share the system above.

---

### TurnTable Builder (Maya) — THE ANCHOR
**Object:** centered top-lit greyscale isometric **cube**.
**Accent:** PXL-orange **circular rotation arrow** wrapping the cube (clockwise, arrowhead bottom-right).
**Why:** the cube = the asset being reviewed; the orbit arrow = the turntable spin. Already approved house style.
**Lives on:** Maya shelf, launcher hero.
**Distinguisher:** the full 360° orbit ring is unique to the two turntable tools.
**Risk:** none — this is the reference. Keep it exactly.
**Confidence:** high.

### TurnTable Comp Setup (Nuke) — sibling of the anchor
**Object:** same greyscale cube, but seated on a thin **greyscale node/plate** beneath it (a flat slab reading as a comp backdrop), OR the cube shown inside a subtle frame corner.
**Accent:** the same PXL-orange circular rotation arrow, **plus nothing else** — the difference from the Maya version is the slab/frame underneath, not a second orange element.
**Why:** same turntable concept, but the Nuke tool is the *comp/finishing* half — the slab says "this is the plate stage." Keeps the pair obviously related (they're the same feature across two DCCs).
**Lives on:** Nuke toolbar, launcher.
**Distinguisher:** orbit arrow (shared with Maya twin) + a baseplate the Maya one lacks.
**Risk:** if the slab is too big it stops reading as a turntable. Keep the cube dominant.
**Confidence:** high.

### PBR Material (Arnold PBR Material Creator)
**Object:** a top-lit greyscale **sphere on a small pedestal** — the universal shader/material ball, matte-to-satin so the lighting falloff reads as "a surface you can shade."
**Accent:** one PXL-orange **specular highlight / rim arc** on the sphere — a crescent of orange light catching the top-left, the one bright spec that says "this is about how the surface responds to light."
**Why:** the shader ball is the instantly-read insider symbol for "material." The orange spec hit is the verb — defining the surface response is what a PBR creator does. Removes if this weren't a material tool.
**Lives on:** Maya shelf.
**Distinguisher:** the only sphere in the set; orange appears as a light *on* the object, not a path *around* it.
**Risk:** generic "3D sphere icon." Avoid by keeping the pedestal + the single deliberate orange spec — not a glossy chrome ball.
**Confidence:** high.

### GLB Import/Export (GLB Manager)
**Object:** greyscale isometric **cube with one corner/face opened** like a shipping box (a parcel), reading as a packaged 3D asset.
**Accent:** two PXL-orange **arrows on one axis** — one entering the box, one leaving — forming a single in/out gesture (treated as ONE accent idea, the bidirectional exchange, not two separate marks).
**Why:** GLB is a transport/container format; the open parcel + in/out arrows = "package an asset and move it across the boundary." Removes if this weren't an import/export container tool.
**Lives on:** Maya shelf.
**Distinguisher:** the only opened/parcel box; the two-way arrow is unique vs the orbit ring and single arrows.
**Risk:** reads as a generic "download/upload" cloud icon if the box loses its 3D form. Keep it a solid isometric parcel.
**Confidence:** high.

### Advanced Batch Renamer
**Object:** a short **stack of 3 identical greyscale slabs/cards** in isometric (a batch of items), offset like a deck.
**Accent:** a PXL-orange **text-cursor / I-beam caret** sitting on the front slab (the edit point), OR an orange underline-with-caret across the front slab's "label" zone.
**Why:** the stack = many items at once (batch); the caret = renaming/editing. The caret is the one element that says "you're changing the name," not the file. Removes if this weren't a bulk rename tool.
**Lives on:** Maya shelf.
**Distinguisher:** the only stacked-deck object; the only caret accent.
**Risk:** the caret is small — at 96px enforce the 4px min weight and keep the slab face clean so the caret pops. Don't add fake text glyphs (they'll mud out).
**Confidence:** medium — caret legibility at 96px needs a render-and-look.

### Legacy Render Layer Creator
**Object:** **three greyscale slabs stacked in depth with visible gaps** (separated layers / an exploded stack) — clearly distinct from the renamer's tight deck by the air between layers.
**Accent:** a thin PXL-orange **bracket or connecting spine** down the left edge tying the separated layers into one group (the "these belong to one render" gesture), or a single orange layer among the greys is NOT allowed (one accent, and it should be the verb, not a colored noun) — use the orange grouping spine.
**Why:** render layers = the same scene split into separated passes; the exploded stack is that separation, the orange spine is the act of authoring/grouping them. "Legacy" doesn't need to be visualized — the tool's job (create layers) does. Removes if this weren't a layer-authoring tool.
**Lives on:** Maya shelf.
**Distinguisher:** separated-with-gaps stack (vs renamer's flush deck); orange spine vs caret.
**Risk:** confusable with the renamer at a glance. Lean hard on the gap/exploded spacing to separate them.
**Confidence:** medium.

### OBJ Batch Exporter
**Object:** greyscale isometric **faceted/low-poly form** (a clearly polygonal blob or icosa-ish solid) — OBJ is raw geometry, so the object should read as "mesh," visibly faceted unlike the smooth cube.
**Accent:** a single PXL-orange **arrow exiting to the right/down** out of the form (export only — one direction, distinct from GLB's two-way).
**Why:** faceted solid = OBJ mesh data; the one-way out-arrow = export. The contrast with GLB (smooth parcel + two-way) keeps the two file-tools distinct. Removes if this weren't a mesh-export tool.
**Lives on:** Maya shelf.
**Distinguisher:** the only visibly faceted/low-poly object; single out-arrow (vs GLB's in+out).
**Risk:** the faceting can turn to noise at 96px — keep facet count low (≈8–12 visible faces) and bold.
**Confidence:** medium.

### Animatic Builder
**Object:** a short **row of 2–3 greyscale film frames / a strip-segment in isometric** (a cut sequence), abstracted — NOT a literal filmstrip with tiny sprocket holes (those die at 96px).
**Accent:** a PXL-orange **play triangle** sitting on/over the first frame, OR an orange forward-arrow joining the frames (sequence/playback = the verb).
**Why:** an animatic is a timed sequence of frames; the frame-row is the noun, the play/forward accent is "make it move in order." Removes if this weren't a timeline/sequence-assembly tool.
**Lives on:** Maya shelf.
**Distinguisher:** the only frame-row object; the only play-triangle accent.
**Risk:** "generic video player" cliché. Avoid by keeping the frames clearly 3D/isometric blocks (assembled shots), not a flat YouTube play button.
**Confidence:** medium.

### AI Assistant ("Claude for Maya" / mAIa)
**Object:** a top-lit greyscale **rounded node/orb or a soft cube with a chamfered front face** acting as an "assistant" body — calm, singular, slightly more organic than the hard asset-cube so it reads as an agent, not a file.
**Accent:** a single PXL-orange **spark / 4-point glint** (the "intelligence" mark) at the top-right of the object, with a soft orange bloom — the one element that says "thinking/assist."
**Why:** mAIa is the in-DCC AI agent; the spark is the established shorthand for AI assistance and is the verb. The softer body distinguishes "an assistant" from "an asset." Removes if this weren't the AI helper. (Naming nod: mAIa = Maya + AI — the orange glint living *on* a Maya-flavored object carries that without text.)
**Lives on:** Maya shelf, and likely the launcher hero for the AI feature.
**Distinguisher:** the only orb/organic body; the only spark accent.
**Risk:** the AI-spark is the single most overused tech cliché in this whole set — confidence is capped here. It earns its place only because it's the literal "assist" verb and pairs with a non-generic body. If it reads as a generic "AI app," rework the body before the accent.
**Confidence:** medium — watch the cliché; it's the riskiest accent in the family.

### Camera Matchmaker
**Object:** a greyscale isometric **camera body** (compact, blocky — a cine camera silhouette, not a DSLR), top-lit.
**Accent:** a single PXL-orange **tracking corner-bracket / crosshair lock** in front of the lens (the "match/solve lock" reticle) — the verb is *matching* the camera to the plate, so the accent is a solve reticle, not a generic lens flare.
**Why:** matchmove = aligning a CG camera to footage; camera body = noun, solve reticle = the match. The reticle (not a flare/aperture) is what keeps this off the generic-camera-trope list. Removes if this weren't a matchmove/camera-align tool.
**Lives on:** Maya shelf.
**Distinguisher:** the only camera object; orange reticle is unique.
**Risk:** slides into generic camera/aperture cliché if the accent becomes a lens or shutter. Hold the line: the accent is a tracking reticle, the "match" verb.
**Confidence:** medium-high.

### Contact Sheet Generator (Nuke)
**Object:** a greyscale isometric **2×2 grid of thin plates / tiles** (an abstracted contact sheet — four panels max, NOT a 3×3 of tiny frames which dies at 96px).
**Accent:** a single PXL-orange **frame/bracket sweeping around the whole grid** (the "assemble these into one sheet" gesture), or one orange highlighted plate-edge unifying the set.
**Why:** a contact sheet collects many renders into one laid-out sheet; the 2×2 plate-grid is the noun, the orange unifying frame is the act of laying out/generating the sheet. Removes if this weren't a multi-image layout tool.
**Lives on:** Nuke toolbar.
**Distinguisher:** the only multi-plate grid object.
**Risk:** too many cells = mud at 96px. Cap at 2×2 and keep cells chunky. Don't confuse with Render Layer's stack — the contact grid is co-planar (a sheet), the layers are stacked in depth.
**Confidence:** medium.

### Image Option Changer (Nuke)
**Object:** a single greyscale isometric **image plate / frame** (one panel, top-lit) — distinct from the contact sheet's grid by being a solo plate.
**Accent:** a PXL-orange **toggle / swap arc** at the corner of the plate — two short curved arrows or a slider-dot — saying "change this image's settings." The verb is *swap/change options*.
**Why:** the tool retargets/changes image read options on a node; one plate = the image, the orange swap-toggle = changing its options. Removes if this weren't an image-option editor.
**Lives on:** Nuke toolbar.
**Distinguisher:** single plate (vs contact-sheet grid); swap/toggle accent (vs others' arrows).
**Risk:** confusable with the single-frame look of Animatic. Differentiate: Animatic = a *row* of frames + play; this = ONE plate + a toggle/swap.
**Confidence:** medium.

### MU Bridge (Maya → Unreal)
**Object:** **two greyscale isometric forms** — a cube (Maya asset) on the left and a distinct angular/pylon form (Unreal) on the right, OR one cube approaching a doorway/portal plate. Keep it to two simple masses so it survives 96px.
**Accent:** a single PXL-orange **arrow/conduit arcing left→right** from the Maya form into the Unreal form (the bridge/transfer). One direction, one accent.
**Why:** MU Bridge moves assets Maya→Unreal; two masses = the two apps, the orange conduit = the bridge. The directional arc (M→U) is the literal product. Removes if this weren't a cross-DCC bridge.
**Lives on:** Maya shelf (and Unreal-side if the bridge surfaces there).
**Distinguisher:** the only two-object icon with a connecting conduit; left→right directional.
**Risk:** two objects + an arrow is the most crowded tile in the set — the 96px gate is tightest here. Keep both masses bold and simple; the arc carries the meaning. If it muds out, drop to one cube entering a portal plate.
**Confidence:** medium — most likely to need a 96px rework.

---

## 3 · Output Filename + Size Spec

Naming follows the existing `icon_<slug>.png` convention (anchor:
`icon_turntable_builder.png`). Each tool ships **two PNGs**: a 96px shelf icon
and a 256px hero. Suggested layout — 256px masters in an `@256/` (or
`hero/`) subfolder, 96px in the icon root the DCC reads, so the shelf path
stays `icon_<slug>.png` at 96px and there's no name collision.

| Tool | Slug / filename (96px, DCC-facing) | Hero (256px) |
|---|---|---|
| TurnTable Builder (Maya) | `icon_turntable_builder.png` | `@256/icon_turntable_builder.png` |
| TurnTable Comp Setup (Nuke) | `icon_turntable_comp_setup.png` | `@256/icon_turntable_comp_setup.png` |
| PBR Material | `icon_pbr_material.png` | `@256/icon_pbr_material.png` |
| GLB Import/Export | `icon_glb_manager.png` | `@256/icon_glb_manager.png` |
| Advanced Batch Renamer | `icon_batch_renamer.png` | `@256/icon_batch_renamer.png` |
| Legacy Render Layer Creator | `icon_render_layer_creator.png` | `@256/icon_render_layer_creator.png` |
| OBJ Batch Exporter | `icon_obj_exporter.png` | `@256/icon_obj_exporter.png` |
| Animatic Builder | `icon_animatic_builder.png` | `@256/icon_animatic_builder.png` |
| AI Assistant (mAIa) | `icon_maia.png` | `@256/icon_maia.png` |
| Camera Matchmaker | `icon_camera_matchmaker.png` | `@256/icon_camera_matchmaker.png` |
| Contact Sheet Generator (Nuke) | `icon_contact_sheet.png` | `@256/icon_contact_sheet.png` |
| Image Option Changer (Nuke) | `icon_image_option_changer.png` | `@256/icon_image_option_changer.png` |
| MU Bridge (Maya→Unreal) | `icon_mu_bridge.png` | `@256/icon_mu_bridge.png` |

**Format:** PNG, RGBA, transparent corners outside the squircle (so the tile
reads as a tile on any shelf background). 96px is the legibility master; 256px
is the same composition rendered larger with more material/AO refinement — not
a different composition.

---

## 4 · Hand-off Note to the Creative-Designer

To make all 13 read as ONE family, execute in this order — do not produce them
as 13 independent one-offs:

1. **Build the tile + lighting template ONCE.** Lock the squircle, the
   `#1e1e1e → #000` vertical gradient, the corner radius (~22%), the top-edge
   inner highlight, and the single top-key light rig. Every icon is composited
   into this exact template. The anchor `icon_turntable_builder.png` is the
   ground-truth reference for tile + light + material + accent weight — match
   it, don't reinterpret it.
2. **Render the greyscale objects in a shared 3D look** — same matte material,
   same value range (`#dcdcdc` top → `#4a4a4a` shadow), same near-isometric
   camera, same soft contact AO. Objects should look like they were rendered in
   one scene under one lamp.
3. **Add exactly one `#E8820C` accent per icon,** with the faint warm bloom seen
   on the anchor's arrow. One accent = one idea. If a tool seems to need two
   orange elements, it's two ideas — pick the stronger verb.
4. **Gate at 96px.** Render each at 96px FIRST and look at all 13 in a single
   row on a dark Maya-shelf-grey strip. Reject anything that muds out, anything
   whose silhouette collides with a neighbor, or any accent under ~4px weight.
   Only then refine the 256px masters.
5. **Watch the four highest-risk tiles:** MU Bridge (two objects — most likely
   to crowd), Batch Renamer vs Render Layer Creator (similar stacked silhouettes
   — must be distinct at 96px), Animatic vs Image Option Changer (frame-vs-plate
   confusion), and mAIa (AI-spark cliché). These four are where the family
   succeeds or fails.
6. **Accent = verb, object = noun** is the single rule that keeps the set
   coherent and distinguishable. If a designer is unsure what the orange should
   be, ask "what does this tool DO?" — that's the accent.

The prompt-engineer should translate each entry above into generation prompts
that explicitly carry the constant system (tile, gradient, radius, top-key
light, greyscale matte, single `#E8820C` accent + bloom, 96px-safe) into EVERY
prompt, varying only the object and accent per the per-tool sections.
