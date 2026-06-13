"""
PXLmentor Icon Set C — Label/Symbol + PXL pixel mosaic corner accent.
Based on initial test Option C.
Each icon: clean central symbol + colorful pixel grid corner (brand DNA).
"""
from PIL import Image, ImageDraw, ImageFont
import math

SIZE = 96
OUT  = r"C:/Users/Evil Knight/Documents/maya/2025/prefs/icons/set_C/"

BG     = (14,  16,  24)
PANEL  = (22,  26,  38)
ORANGE = (232, 130,  12)
CYAN   = ( 60, 195, 210)
PINK   = (210,  65, 130)
GOLD   = (255, 185,  40)
STROKE = (180, 188, 210)
DIM    = ( 95, 105, 128)


def font(size, bold=True):
    try:
        path = "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def base():
    img  = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, SIZE-1, SIZE-1], radius=18, fill=(*BG, 255))
    draw.rounded_rectangle([7, 7, SIZE-8,  SIZE-8], radius=13, fill=(*PANEL, 255))
    return img, draw


def ctext(draw, text, fnt, cx, cy, fill):
    bb = draw.textbbox((0, 0), text, font=fnt)
    w, h = bb[2]-bb[0], bb[3]-bb[1]
    draw.text((cx - w//2, cy - h//2), text, fill=fill, font=fnt)


def pixel_accent(draw, corner="TR"):
    """4-pixel mosaic in brand colors — top-right corner by default."""
    colors = [ORANGE, CYAN, PINK, GOLD]
    px = 6
    if corner == "TR":
        positions = [(SIZE-22, 10), (SIZE-14, 10), (SIZE-22, 18), (SIZE-14, 18)]
    elif corner == "TL":
        positions = [(10, 10), (18, 10), (10, 18), (18, 18)]
    elif corner == "BR":
        positions = [(SIZE-22, SIZE-22), (SIZE-14, SIZE-22),
                     (SIZE-22, SIZE-14), (SIZE-14, SIZE-14)]
    for i, (px_, py_) in enumerate(positions):
        draw.rectangle([px_, py_, px_+px-1, py_+px-1], fill=(*colors[i], 220))


def orange_bar(draw, y1=68, y2=74, x1=14, x2=82):
    """Thin orange accent bar."""
    draw.rounded_rectangle([x1, y1, x2, y2], radius=3, fill=(*ORANGE, 200))


# ── 1. Batch Renamer  ─────────────────────────────────────────────────────────
img, draw = base()
# Label tag shape
draw.rounded_rectangle([14, 24, 70, 62], radius=6,
                        outline=(*STROKE, 200), width=2)
# Tag hole
draw.ellipse([20, 30, 30, 40], outline=(*STROKE, 200), width=2)
# Text lines inside tag
draw.rounded_rectangle([36, 31, 64, 37], radius=2, fill=(*DIM, 200))
draw.rounded_rectangle([36, 42, 56, 48], radius=2, fill=(*DIM, 150))
# Orange pen stroke — rename indicator
draw.rounded_rectangle([14, 66, 70, 72], radius=3, fill=(*ORANGE, 200))
# Pixel accent
pixel_accent(draw, "TR")
img.save(OUT + "icon_batch_renamer.png")
print("Saved: icon_batch_renamer.png")

# ── 2. mAIa  ──────────────────────────────────────────────────────────────────
img, draw = base()
# Chat bubble
draw.rounded_rectangle([14, 20, 72, 58], radius=10,
                        fill=(*PANEL, 255), outline=(*STROKE, 200), width=2)
# Bubble tail
draw.polygon([(22, 58), (16, 70), (36, 58)], fill=(*PANEL, 255))
draw.line([(22, 58), (16, 70)], fill=(*STROKE, 200), width=2)
draw.line([(16, 70), (36, 58)], fill=(*STROKE, 200), width=2)
# AI text inside bubble
ctext(draw, "AI", font(22), 44, 38, (*ORANGE, 255))
# Pixel accent
pixel_accent(draw, "TR")
img.save(OUT + "icon_claude_for_maya.png")
print("Saved: icon_claude_for_maya.png")

# ── 3. Animatic Builder  ──────────────────────────────────────────────────────
img, draw = base()
# Clapperboard body
draw.rounded_rectangle([14, 36, 76, 74], radius=5,
                        fill=(*PANEL, 255), outline=(*STROKE, 200), width=2)
# Clapper bar
draw.rounded_rectangle([14, 24, 76, 38], radius=5, fill=(*STROKE, 220))
# Clapper stripes
for i in range(7):
    x1 = 16 + i * 9
    col = ORANGE if i % 2 == 0 else BG
    draw.polygon([(x1, 24),(x1+6, 24),(x1+3, 38),(x1-3, 38)], fill=(*col, 230))
# Play triangle
draw.polygon([(34, 48),(34, 66),(54, 57)], fill=(*ORANGE, 240))
# Pixel accent
pixel_accent(draw, "TR")
img.save(OUT + "icon_animatic_builder.png")
print("Saved: icon_animatic_builder.png")

# ── 4. GLB Importer  ──────────────────────────────────────────────────────────
img, draw = base()
# Rounded rect card (import container)
draw.rounded_rectangle([14, 18, 68, 68], radius=7,
                        outline=(*STROKE, 190), width=2)
# "3D" label inside
ctext(draw, "GLB", font(16), 41, 38, (*STROKE, 220))
# Orange import arrow at bottom
ax, ay = 41, 60
draw.line([(ax, ay-6),(ax, ay+2)], fill=(*ORANGE, 255), width=3)
draw.polygon([(ax-6, ay),(ax, ay+8),(ax+6, ay)], fill=(*ORANGE, 255))
# Pixel accent
pixel_accent(draw, "TR")
img.save(OUT + "icon_glb_importer.png")
print("Saved: icon_glb_importer.png")

# ── 5. OBJ Batch Exporter  ────────────────────────────────────────────────────
img, draw = base()
# Stack of 3 cards (batch)
offsets = [(6, 0), (3, 0), (0, 0)]
for i, (ox, oy) in enumerate(offsets):
    alpha = 120 + i * 50
    draw.rounded_rectangle([14+ox, 30+oy*3, 66+ox, 56+oy*3],
                            radius=5, outline=(*STROKE, alpha), width=2)
# Lines on top card
for j, w in enumerate([28, 20]):
    y = 38 + j * 8
    draw.rounded_rectangle([20, y, 20+w, y+4], radius=2, fill=(*DIM, 180))
# Orange up-arrow (export)
ax, ay = 74, 44
draw.line([(ax, ay+10),(ax, ay-4)], fill=(*ORANGE, 255), width=3)
draw.polygon([(ax-5, ay),(ax, ay-10),(ax+5, ay)], fill=(*ORANGE, 255))
# Pixel accent
pixel_accent(draw, "TR")
img.save(OUT + "icon_obj_exporter.png")
print("Saved: icon_obj_exporter.png")

# ── 6. Arnold PBR Material  ───────────────────────────────────────────────────
img, draw = base()
cx, cy, r = 44, 42, 24
# Sphere fill
draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*PANEL, 255))
# Shading gradient (concentric)
for i in range(5):
    t   = i / 4.0
    rr  = max(3, r - i*4)
    ox_ = int(-8*(1-t))
    oy_ = int(-8*(1-t))
    col = (
        int(PANEL[0]+(ORANGE[0]-PANEL[0])*t),
        int(PANEL[1]+(ORANGE[1]-PANEL[1])*t),
        int(PANEL[2]+(ORANGE[2]-PANEL[2])*t),
    )
    draw.ellipse([cx+ox_-rr, cy+oy_-rr, cx+ox_+rr, cy+oy_+rr],
                 fill=(*col, int(80+t*175)))
draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(*STROKE, 160), width=2)
# Specular
draw.ellipse([cx-14, cy-16, cx-6, cy-9], fill=(255, 255, 255, 90))
# Orange bar below
orange_bar(draw, y1=70, y2=76, x1=14, x2=72)
# Pixel accent
pixel_accent(draw, "TR")
img.save(OUT + "icon_arnold_material.png")
print("Saved: icon_arnold_material.png")

# ── 7. Render Layer Creator  ──────────────────────────────────────────────────
img, draw = base()
# Three stacked layer cards
layer_defs = [
    (12, 54, 74, 66, ORANGE, 220),
    (12, 40, 72, 52, STROKE, 170),
    (12, 26, 70, 38, STROKE, 110),
]
for (x1,y1,x2,y2,col,alpha) in layer_defs:
    draw.rounded_rectangle([x1,y1,x2,y2], radius=4,
                            outline=(*col, alpha), width=2)
# Tiny camera icon over top layer
cam_x, cam_y = 54, 10
draw.rounded_rectangle([cam_x, cam_y, cam_x+16, cam_y+11],
                        radius=3, fill=(*DIM, 180))
draw.ellipse([cam_x+4, cam_y+2, cam_x+12, cam_y+10],
             fill=(*PANEL, 255), outline=(*STROKE, 180), width=1)
draw.ellipse([cam_x+6, cam_y+4, cam_x+10, cam_y+8],
             fill=(*ORANGE, 200))
# Pixel accent
pixel_accent(draw, "TR")
img.save(OUT + "icon_render_layers.png")
print("Saved: icon_render_layers.png")

# ── 8. TurnTable Builder  ─────────────────────────────────────────────────────
img, draw = base()
cx, cy = 44, 46
# Platform ellipse (base)
draw.ellipse([20, 58, 68, 72], fill=(*DIM, 120), outline=(*STROKE, 180), width=2)
# Object on platform (simple rounded cube)
draw.rounded_rectangle([30, 32, 58, 60], radius=6,
                        fill=(*PANEL, 255), outline=(*STROKE, 200), width=2)
# Highlight edge on cube
draw.line([(30, 32),(30, 60)], fill=(*STROKE, 80), width=1)
draw.line([(30, 32),(58, 32)], fill=(*STROKE, 80), width=1)
# Rotation arc around the object
draw.arc([14, 22, 74, 78], start=200, end=160,
         fill=(*ORANGE, 220), width=3)
# Arrowhead
angle = math.radians(160)
arx = 44 + 30*math.cos(angle)
ary = 50 + 28*math.sin(angle)
tang = math.radians(160+90)
apts = [
    (arx+6*math.cos(tang-0.5), ary+6*math.sin(tang-0.5)),
    (arx+6*math.cos(tang+0.5), ary+6*math.sin(tang+0.5)),
    (arx-5*math.cos(tang),     ary-5*math.sin(tang)),
]
draw.polygon(apts, fill=(*ORANGE, 255))
# Pixel accent
pixel_accent(draw, "TR")
img.save(OUT + "icon_turntable_builder.png")
print("Saved: icon_turntable_builder.png")

print("\nSet C complete —", OUT)
