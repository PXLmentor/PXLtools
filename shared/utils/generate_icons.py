from PIL import Image, ImageDraw, ImageFont
import math

SIZE   = 96
ICONS  = r"J:/ClaudeCode/projects/PXLtools/maya/scripts/icons/"
DEPLOY = r"C:/Users/Evil Knight/Documents/maya/2025/prefs/icons/"

BG     = (14,  16,  24)
PANEL  = (22,  26,  38)
ORANGE = (232, 130,  12)
GRAY   = (130, 140, 162)
WHITE  = (220, 225, 235)


def font(size, bold=True):
    paths = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


def base():
    img  = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, SIZE-1, SIZE-1], radius=18, fill=(*BG, 255))
    draw.rounded_rectangle([7, 7, SIZE-8,  SIZE-8], radius=13, fill=(*PANEL, 255))
    return img, draw


def centered_text(draw, text, fnt, cx, cy, fill):
    bb = draw.textbbox((0, 0), text, font=fnt)
    w, h = bb[2]-bb[0], bb[3]-bb[1]
    draw.text((cx - w//2, cy - h//2), text, fill=fill, font=fnt)


def batch_dots(draw, cy=74, alpha=140):
    for i in range(3):
        cx = 40 + i * 9
        draw.ellipse([cx-2, cy-2, cx+2, cy+2], fill=(*GRAY, max(0, alpha - i*25)))


def two_color_centered(draw, left_char, right_char, fnt, cy, lc, rc, gap=2):
    """Render two characters as one horizontally-centered group, each in its own color.

    Measures each glyph's true bounding box and offsets so the combined pair
    is centered on x=SIZE/2 - not the naive midpoint between letter centers.
    """
    bb_l = draw.textbbox((0, 0), left_char,  font=fnt)
    bb_r = draw.textbbox((0, 0), right_char, font=fnt)
    w_l  = bb_l[2] - bb_l[0]
    w_r  = bb_r[2] - bb_r[0]
    h    = max(bb_l[3] - bb_l[1], bb_r[3] - bb_r[1])
    total = w_l + gap + w_r
    left  = (SIZE - total) // 2
    top   = cy - h // 2
    draw.text((left - bb_l[0],                top - bb_l[1]), left_char,  fill=lc, font=fnt)
    draw.text((left + w_l + gap - bb_r[0],    top - bb_r[1]), right_char, fill=rc, font=fnt)


# ── 1. Advanced Batch Renamer  A → B ────────────────────────────────────────
img, draw = base()
f30 = font(30)
centered_text(draw, "A", f30, 28, 44, (*GRAY, 255))
draw.line([(40, 44), (50, 44)], fill=(*ORANGE, 255), width=2)
draw.polygon([(48, 40), (54, 44), (48, 48)], fill=(*ORANGE, 255))
centered_text(draw, "B", f30, 66, 44, (*ORANGE, 255))
batch_dots(draw)
img.save(ICONS + "icon_batch_renamer.png")
print("Saved: icon_batch_renamer.png")

# ── 2. mAIa  AI + spark ─────────────────────────────────────────────────────
img, draw = base()
f28 = font(28)
f11 = font(11, bold=False)
spark_cx, spark_cy = 48, 20
pts = [(spark_cx, spark_cy-7), (spark_cx+5, spark_cy),
       (spark_cx, spark_cy+7), (spark_cx-5, spark_cy)]
draw.polygon(pts, fill=(*ORANGE, 255))
centered_text(draw, "AI", f28, 48, 52, (*WHITE, 255))
centered_text(draw, "for Maya", f11, 48, 73, (*GRAY, 200))
img.save(ICONS + "icon_claude_for_maya.png")
print("Saved: icon_claude_for_maya.png")

# ── 3. Animatic Builder  play triangle + film strips ─────────────────────────
img, draw = base()
for i in range(5):
    x = 16 + i * 14
    draw.rectangle([x, 13, x+8, 21], fill=(*GRAY, 120))
cx, cy = 48, 50
r = 22
pts = [(cx - r//2 + 2, cy - r//2 - 2),
       (cx - r//2 + 2, cy + r//2 + 2),
       (cx + r//2 + 4, cy)]
draw.polygon(pts, fill=(*ORANGE, 255))
for i in range(5):
    x = 16 + i * 14
    draw.rectangle([x, 72, x+8, 80], fill=(*GRAY, 120))
img.save(ICONS + "icon_animatic_builder.png")
print("Saved: icon_animatic_builder.png")

# ── 4. GLB Importer  cube wireframe + down arrow ─────────────────────────────
img, draw = base()
ox, oy, s = 44, 44, 15
# Front face
draw.rectangle([ox-s, oy-s, ox+s, oy+s], outline=(*GRAY, 200), width=2)
# Top face
top = [(ox-s, oy-s), (ox-s+10, oy-s-8), (ox+s+10, oy-s-8), (ox+s, oy-s)]
draw.line([top[0], top[1]], fill=(*GRAY, 200), width=2)
draw.line([top[1], top[2]], fill=(*GRAY, 200), width=2)
draw.line([top[2], top[3]], fill=(*GRAY, 200), width=2)
# Right face
draw.line([top[2], (ox+s+10, oy+s-8)], fill=(*GRAY, 200), width=2)
draw.line([(ox+s+10, oy+s-8), (ox+s, oy+s)], fill=(*GRAY, 200), width=2)
# Import arrow bottom-right
ax, ay = 67, 64
draw.line([(ax, ay-8), (ax, ay+2)], fill=(*ORANGE, 255), width=3)
draw.polygon([(ax-5, ay), (ax, ay+8), (ax+5, ay)], fill=(*ORANGE, 255))
img.save(ICONS + "icon_glb_importer.png")
print("Saved: icon_glb_importer.png")

# ── 5. OBJ Batch Exporter  box + up arrow ───────────────────────────────────
img, draw = base()
draw.rounded_rectangle([20, 42, 62, 74], radius=5, outline=(*ORANGE, 220), width=2)
for i, w in enumerate([26, 20, 22]):
    y = 50 + i * 8
    draw.rounded_rectangle([26, y, 26+w, y+4], radius=2,
                            fill=(*ORANGE, 150 - i*30))
draw.line([(72, 62), (72, 20)], fill=(*ORANGE, 200), width=2)
draw.polygon([(67, 26), (72, 16), (77, 26)], fill=(*ORANGE, 255))
img.save(ICONS + "icon_obj_exporter.png")
print("Saved: icon_obj_exporter.png")

# ── 6. Arnold PBR Material Creator  shaded sphere ───────────────────────────
img, draw = base()
cx, cy, r = 48, 44, 26
draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*PANEL, 255))
for i in range(7):
    t   = i / 6.0
    rr  = max(2, r - i*3)
    ox_ = int(-10 * (1-t))
    oy_ = int(-10 * (1-t))
    col = (
        int(PANEL[0] + (ORANGE[0]-PANEL[0]) * t),
        int(PANEL[1] + (ORANGE[1]-PANEL[1]) * t),
        int(PANEL[2] + (ORANGE[2]-PANEL[2]) * t),
    )
    draw.ellipse([cx+ox_-rr, cy+oy_-rr, cx+ox_+rr, cy+oy_+rr],
                 fill=(*col, int(50 + t*200)))
draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(*ORANGE, 180), width=2)
draw.ellipse([cx-14, cy-16, cx-5, cy-8], fill=(*WHITE, 100))
f10 = font(10)
centered_text(draw, "PBR", f10, 48, 78, (*GRAY, 200))
img.save(ICONS + "icon_arnold_material.png")
print("Saved: icon_arnold_material.png")

# ── 7. Legacy Render Layer Creator  stacked layers + camera ──────────────────
img, draw = base()
layers = [(20, 56, 76, 66), (17, 43, 73, 53), (14, 30, 70, 40)]
alphas = [255, 200, 150]
for i, (x1, y1, x2, y2) in enumerate(layers):
    col = ORANGE if i == 0 else GRAY
    draw.rounded_rectangle([x1, y1, x2, y2], radius=4,
                            fill=(*col, alphas[i]))
cam_x, cam_y = 60, 12
draw.rounded_rectangle([cam_x, cam_y, cam_x+20, cam_y+13],
                        radius=3, outline=(*GRAY, 200), width=2)
draw.ellipse([cam_x+5, cam_y+2, cam_x+14, cam_y+11],
             outline=(*GRAY, 200), width=1)
draw.polygon([(cam_x+18, cam_y+3), (cam_x+24, cam_y+1),
              (cam_x+24, cam_y+12), (cam_x+18, cam_y+10)],
             fill=(*GRAY, 160))
img.save(ICONS + "icon_render_layers.png")
print("Saved: icon_render_layers.png")

# ── 8. TurnTable Builder  rotation arc + object ──────────────────────────────
img, draw = base()
cx, cy, r = 48, 46, 24
draw.arc([cx-r, cy-r, cx+r, cy+r], start=60, end=340,
         fill=(*ORANGE, 255), width=4)
angle = math.radians(340)
ax_ = cx + r * math.cos(angle)
ay_ = cy + r * math.sin(angle)
tang = math.radians(340 + 90)
arrow_pts = [
    (ax_ + 7*math.cos(tang-0.4), ay_ + 7*math.sin(tang-0.4)),
    (ax_ + 7*math.cos(tang+0.4), ay_ + 7*math.sin(tang+0.4)),
    (ax_ - 5*math.cos(tang),     ay_ - 5*math.sin(tang)),
]
draw.polygon(arrow_pts, fill=(*ORANGE, 255))
obj_pts = [(cx, cy-10), (cx+8, cy), (cx, cy+10), (cx-8, cy)]
draw.polygon(obj_pts, fill=(*GRAY, 200))
draw.polygon(obj_pts, outline=(*WHITE, 120))
batch_dots(draw, cy=78)
img.save(ICONS + "icon_turntable_builder.png")
print("Saved: icon_turntable_builder.png")

# ── 9. MU Bridge  Centered MU monogram (gray + orange) + BRIDGE label ───────
img, draw = base()
two_color_centered(draw, "M", "U", font(46), cy=40,
                   lc=(*GRAY, 255), rc=(*ORANGE, 255), gap=2)
centered_text(draw, "BRIDGE", font(10), 48, 78, (*GRAY, 200))
img.save(ICONS + "icon_mu_bridge.png")
print("Saved: icon_mu_bridge.png")

print("\nAll 9 icons complete.")

# --- Deploy to Maya prefs ---
import shutil, os
for fname in os.listdir(ICONS):
    if fname.endswith(".png"):
        shutil.copy2(ICONS + fname, DEPLOY + fname)
        print(f"Deployed: {fname}")
print("Deploy complete.")
