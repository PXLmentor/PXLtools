"""
PXLmentor Icon Set B — Glyph/Outline style
Thin white strokes on dark, orange as single focal accent.
Inspired by Nuke/Houdini/Blender icon language.
"""
from PIL import Image, ImageDraw, ImageFont
import math

SIZE  = 96
OUT   = r"C:/Users/Evil Knight/Documents/maya/2025/prefs/icons/set_B/"

BG      = (14,  16,  24)
PANEL   = (18,  21,  32)
ORANGE  = (232, 130,  12)
STROKE  = (200, 208, 225)
DIM     = (100, 110, 132)
WHITE   = (235, 240, 250)


def font(size, bold=True):
    try:
        path = "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def base():
    img  = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Subtle gradient feel — slightly lighter inner glow
    draw.rounded_rectangle([0, 0, SIZE-1, SIZE-1], radius=18, fill=(*BG, 255))
    draw.rounded_rectangle([5, 5, SIZE-6, SIZE-6], radius=14, fill=(*PANEL, 255))
    # Faint border
    draw.rounded_rectangle([5, 5, SIZE-6, SIZE-6], radius=14,
                            outline=(*STROKE, 25), width=1)
    return img, draw


def ctext(draw, text, fnt, cx, cy, fill):
    bb = draw.textbbox((0, 0), text, font=fnt)
    w, h = bb[2]-bb[0], bb[3]-bb[1]
    draw.text((cx - w//2, cy - h//2), text, fill=fill, font=fnt)


def orange_dot(draw, x, y, r=3):
    draw.ellipse([x-r, y-r, x+r, y+r], fill=(*ORANGE, 255))


# ── 1. Batch Renamer  — two text lines with orange cursor ────────────────────
img, draw = base()
# Line 1 — source (dim)
draw.rounded_rectangle([16, 28, 56, 36], radius=3, fill=(*DIM, 180))
# Line 2 — result (brighter)
draw.rounded_rectangle([16, 44, 64, 52], radius=3, fill=(*STROKE, 200))
# Orange I-beam cursor on line 2
draw.line([(66, 41), (66, 55)], fill=(*ORANGE, 255), width=2)
draw.line([(63, 41), (69, 41)], fill=(*ORANGE, 255), width=2)
draw.line([(63, 55), (69, 55)], fill=(*ORANGE, 255), width=2)
# Third dim line
draw.rounded_rectangle([16, 60, 48, 68], radius=3, fill=(*DIM, 120))
img.save(OUT + "icon_batch_renamer.png")
print("Saved: icon_batch_renamer.png")

# ── 2. mAIa  — circuit brain outline ────────────────────────────────────────
img, draw = base()
cx, cy = 48, 44
# Brain outline (simplified as rounded square with nodes)
draw.rounded_rectangle([cx-18, cy-16, cx+18, cy+16], radius=8,
                        outline=(*STROKE, 200), width=2)
# Inner circuit lines
draw.line([(cx-8, cy-8), (cx-8, cy+8)],  fill=(*DIM, 200), width=1)
draw.line([(cx+8, cy-8), (cx+8, cy+8)],  fill=(*DIM, 200), width=1)
draw.line([(cx-8, cy),   (cx+8, cy)],    fill=(*DIM, 200), width=1)
# Node dots at intersections
for nx, ny in [(cx-8, cy-8),(cx-8, cy),(cx-8, cy+8),
               (cx+8, cy-8),(cx+8, cy),(cx+8, cy+8),
               (cx,   cy)]:
    draw.ellipse([nx-2, ny-2, nx+2, ny+2], fill=(*DIM, 220))
# Orange pulse — single bright dot at center-top
orange_dot(draw, cx, cy-8, r=3)
# Connector lines outside brain
draw.line([(cx-18, cy-8), (cx-26, cy-8)], fill=(*STROKE, 160), width=1)
draw.line([(cx+18, cy),   (cx+26, cy)],   fill=(*STROKE, 160), width=1)
draw.line([(cx,    cy+16),(cx,    cy+24)], fill=(*STROKE, 160), width=1)
orange_dot(draw, cx-26, cy-8, r=2)
orange_dot(draw, cx+26, cy,   r=2)
orange_dot(draw, cx,    cy+24,r=2)
# label
ctext(draw, "mAIa", font(9, bold=False), 48, 78, (*DIM, 200))
img.save(OUT + "icon_claude_for_maya.png")
print("Saved: icon_claude_for_maya.png")

# ── 3. Animatic Builder  — clapperboard ─────────────────────────────────────
img, draw = base()
# Board body
draw.rounded_rectangle([16, 38, 78, 76], radius=4,
                        outline=(*STROKE, 220), width=2)
# Clapper top bar
draw.rounded_rectangle([16, 28, 78, 40], radius=4,
                        fill=(*STROKE, 200))
# Clapper stripes (alternating orange/dark)
for i in range(6):
    x1 = 18 + i*10
    x2 = x1 + 6
    col = ORANGE if i % 2 == 0 else PANEL
    draw.polygon([(x1,28),(x2,28),(x2-3,40),(x1-3,40)], fill=(*col,220))
# Orange play triangle on board
ptx, pty = 47, 57
draw.polygon([(ptx-9, pty-10),(ptx-9, pty+10),(ptx+11, pty)],
             fill=(*ORANGE, 240))
img.save(OUT + "icon_animatic_builder.png")
print("Saved: icon_animatic_builder.png")

# ── 4. GLB Importer  — isometric 3D cube, clean outline ─────────────────────
img, draw = base()
ox, oy, s = 46, 46, 20
# Bottom front edge
front = [(ox-s, oy+s), (ox+s, oy+s), (ox+s, oy-s), (ox-s, oy-s)]
draw.polygon(front, outline=(*STROKE, 220), width=2)
# Top face
top = [(ox-s, oy-s), (ox-s+12, oy-s-10),
       (ox+s+12, oy-s-10), (ox+s, oy-s)]
draw.polygon(top, outline=(*STROKE, 200), width=2)
# Right face
right = [(ox+s, oy-s), (ox+s+12, oy-s-10),
         (ox+s+12, oy+s-10), (ox+s, oy+s)]
draw.polygon(right, outline=(*STROKE, 180), width=2)
# Orange down-arrow (import) bottom right
ax, ay = 70, 68
draw.line([(ax, ay-10),(ax, ay+2)], fill=(*ORANGE, 255), width=2)
draw.polygon([(ax-5, ay),(ax, ay+8),(ax+5, ay)], fill=(*ORANGE, 255))
img.save(OUT + "icon_glb_importer.png")
print("Saved: icon_glb_importer.png")

# ── 5. OBJ Batch Exporter  — open box outline, up-arrow ─────────────────────
img, draw = base()
# Box — open top
draw.line([(20,46),(20,74),(72,74),(72,46)], fill=(*STROKE,220), width=2)
# Box flaps open at top
draw.line([(20,46),(34,34)], fill=(*STROKE,160), width=2)
draw.line([(72,46),(58,34)], fill=(*STROKE,160), width=2)
draw.line([(34,34),(58,34)], fill=(*STROKE,120), width=1)
# Three lines inside (batch)
for i, w in enumerate([24, 18, 20]):
    y = 52 + i * 7
    draw.rounded_rectangle([28, y, 28+w, y+3], radius=1, fill=(*DIM, 180-i*30))
# Orange up-arrow coming out of box
ax = 46
draw.line([(ax, 42),(ax, 18)], fill=(*ORANGE, 230), width=2)
draw.polygon([(ax-6,24),(ax,14),(ax+6,24)], fill=(*ORANGE,255))
img.save(OUT + "icon_obj_exporter.png")
print("Saved: icon_obj_exporter.png")

# ── 6. Arnold PBR Material  — sphere with equator + meridian lines ───────────
img, draw = base()
cx, cy, r = 48, 44, 26
# Sphere outline
draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(*STROKE, 220), width=2)
# Equator ellipse
draw.arc([cx-r, cy-6, cx+r, cy+6], start=0, end=180,
         fill=(*DIM, 180), width=1)
draw.arc([cx-r, cy-6, cx+r, cy+6], start=180, end=360,
         fill=(*DIM, 100), width=1)
# Meridian ellipse
draw.arc([cx-8, cy-r, cx+8, cy+r], start=0, end=180,
         fill=(*DIM, 180), width=1)
draw.arc([cx-8, cy-r, cx+8, cy+r], start=180, end=360,
         fill=(*DIM, 100), width=1)
# Orange specular highlight
draw.ellipse([cx-14, cy-18, cx-4, cy-10], fill=(*ORANGE, 200))
# Small PBR label
ctext(draw, "PBR", font(9, bold=False), 48, 78, (*DIM, 200))
img.save(OUT + "icon_arnold_material.png")
print("Saved: icon_arnold_material.png")

# ── 7. Render Layer Creator  — stacked layer outlines + camera glyph ─────────
img, draw = base()
layers = [(18, 58, 74, 68), (15, 45, 71, 55), (12, 32, 68, 42)]
for i, (x1, y1, x2, y2) in enumerate(layers):
    col   = ORANGE if i == 0 else STROKE
    alpha = 230 - i * 50
    draw.rounded_rectangle([x1, y1, x2, y2], radius=3,
                            outline=(*col, alpha), width=2)
# Camera glyph top-right
cx2, cy2 = 66, 18
draw.rounded_rectangle([cx2-10, cy2-7, cx2+10, cy2+7],
                        radius=3, outline=(*STROKE, 200), width=1)
draw.ellipse([cx2-5, cy2-4, cx2+5, cy2+4],
             outline=(*STROKE, 180), width=1)
orange_dot(draw, cx2, cy2, r=2)
img.save(OUT + "icon_render_layers.png")
print("Saved: icon_render_layers.png")

# ── 8. TurnTable Builder  — rotation arc + wireframe sphere ──────────────────
img, draw = base()
cx, cy, r = 48, 46, 22
# Outer rotation arc
draw.arc([cx-r-6, cy-r-6, cx+r+6, cy+r+6], start=50, end=310,
         fill=(*STROKE, 160), width=2)
# Main rotation arc (orange, partial)
draw.arc([cx-r-6, cy-r-6, cx+r+6, cy+r+6], start=310, end=50,
         fill=(*ORANGE, 255), width=3)
# Arrowhead
angle = math.radians(50)
arx = cx + (r+6) * math.cos(angle)
ary = cy + (r+6) * math.sin(angle)
tang = math.radians(50 + 90)
apts = [
    (arx + 7*math.cos(tang-0.5), ary + 7*math.sin(tang-0.5)),
    (arx + 7*math.cos(tang+0.5), ary + 7*math.sin(tang+0.5)),
    (arx - 5*math.cos(tang),     ary - 5*math.sin(tang)),
]
draw.polygon(apts, fill=(*ORANGE, 255))
# Wireframe sphere inside
draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(*STROKE, 160), width=1)
draw.arc([cx-r, cy-5, cx+r, cy+5], start=0, end=180,
         fill=(*DIM, 140), width=1)
draw.arc([cx-5, cy-r, cx+5, cy+r], start=0, end=180,
         fill=(*DIM, 140), width=1)
img.save(OUT + "icon_turntable_builder.png")
print("Saved: icon_turntable_builder.png")

print("\nSet B complete — saved to", OUT)
