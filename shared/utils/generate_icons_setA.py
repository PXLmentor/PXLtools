"""
PXLmentor Icon Set A — Pixel grid style.
Based on initial test Option A: icons built from small pixel squares.
Each pixel = 7x7px with 2px gap. Grid is 8x8 usable cells.
Gray pixels = source/inactive. Orange pixels = active/result/key element.
"""
from PIL import Image, ImageDraw
import math

SIZE = 96
OUT  = r"C:/Users/Evil Knight/Documents/maya/2025/prefs/icons/set_A/"

BG     = (14,  16,  24)
PANEL  = (22,  26,  38)
ORANGE = (232, 130,  12)
GRAY   = (100, 110, 132)
GRAY_L = (155, 165, 185)
DIM    = ( 55,  62,  80)

PX  = 7   # pixel square size
GAP = 2   # gap between pixels
STEP = PX + GAP  # 9px per cell

# Grid origin — centred in the 82x82 inner panel
GX = 12   # grid start x
GY = 12   # grid start y


def base():
    img  = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, SIZE-1, SIZE-1], radius=18, fill=(*BG, 255))
    draw.rounded_rectangle([7, 7, SIZE-8,  SIZE-8], radius=13, fill=(*PANEL, 255))
    return img, draw


def px(draw, col, r, c, alpha=255):
    """Draw one pixel square at grid row r, col c."""
    x = GX + c * STEP
    y = GY + r * STEP
    draw.rectangle([x, y, x+PX-1, y+PX-1], fill=(*col, alpha))


# ── 1. Batch Renamer — gray rows → orange rows with arrows ───────────────────
img, draw = base()
for row in range(3):
    y_off = row * 3  # slight vertical offset per row
    left_len  = [4, 3, 4][row]
    right_len = [3, 4, 3][row]
    r = 1 + row * 2
    # Left pixels (gray)
    for c in range(left_len):
        px(draw, GRAY_L, r, c, 200 - row*20)
    # Arrow pixel (orange dot)
    ax = GX + 4 * STEP + PX//2
    ay = GY + r * STEP + PX//2
    draw.ellipse([ax-2, ay-2, ax+2, ay+2], fill=(*ORANGE, 255))
    draw.polygon([(ax+1,ay-3),(ax+6,ay),(ax+1,ay+3)], fill=(*ORANGE,255))
    # Right pixels (orange)
    for c in range(right_len):
        px(draw, ORANGE, r, c + 5, 255 - row*25)
img.save(OUT + "icon_batch_renamer.png")
print("Saved: icon_batch_renamer.png")

# ── 2. mAIa — diamond spark + pixel brain grid ────────────────────────────────
img, draw = base()
# Pixel brain: 5x4 grid with brain shape
brain = [
    [0,1,1,1,0],
    [1,1,1,1,1],
    [1,1,1,1,1],
    [0,1,0,1,0],
]
for r, row in enumerate(brain):
    for c, val in enumerate(row):
        if val:
            col = ORANGE if (r == 1 and c == 2) else GRAY_L
            px(draw, col, r+1, c+1, 200)
# Orange spark above
spark_cx = GX + 3*STEP + PX//2
spark_cy = GY + 0*STEP
pts = [(spark_cx, spark_cy-4),(spark_cx+4,spark_cy+2),(spark_cx,spark_cy+1),(spark_cx-4,spark_cy+2)]
draw.polygon(pts, fill=(*ORANGE,255))
# Bottom label pixels
for c in range(6):
    col = ORANGE if c in [1,2,4] else DIM
    px(draw, col, 6, c, 160)
img.save(OUT + "icon_claude_for_maya.png")
print("Saved: icon_claude_for_maya.png")

# ── 3. Animatic Builder — pixel play triangle + film strip rows ───────────────
img, draw = base()
# Film strip top row
for c in range(8):
    col = GRAY_L if c % 2 == 0 else DIM
    px(draw, col, 0, c, 160)
# Pixel play triangle (rows of increasing width)
tri = [
    (3, [3]),
    (3, [3,4]),
    (3, [3,4,5]),
    (3, [3,4,5,6]),
    (3, [3,4,5]),
    (3, [3,4]),
    (3, [3]),
]
# Centre the triangle
tri_data = [1, 2, 3, 4, 3, 2, 1]
for r, width in enumerate(tri_data):
    start_c = 3
    for w in range(width):
        px(draw, ORANGE, r+1, start_c+w, 240)
# Film strip bottom row
for c in range(8):
    col = GRAY_L if c % 2 == 0 else DIM
    px(draw, col, 8, c, 160)
img.save(OUT + "icon_animatic_builder.png")
print("Saved: icon_animatic_builder.png")

# ── 4. GLB Importer — pixel cube + down arrow ────────────────────────────────
img, draw = base()
# Cube front face (3x3 pixels)
cube_cols = [GRAY_L, GRAY_L, GRAY_L,
             GRAY_L, DIM,    GRAY_L,
             GRAY_L, GRAY_L, GRAY_L]
for i, col in enumerate(cube_cols):
    r, c = divmod(i, 3)
    px(draw, col, r+1, c+1, 200)
# Cube top (offset)
for c in range(3):
    px(draw, GRAY_L, 0, c+2, 150)
# Cube right side
for r in range(3):
    px(draw, GRAY_L, r+1, 4, 130)
# Down arrow (orange) — bottom right
for r in range(3):
    px(draw, ORANGE, r+4, 5, 255-r*30)
# Arrowhead
ax = GX + 5*STEP + PX//2
ay = GY + 7*STEP
draw.polygon([(ax-5,ay),(ax,ay+7),(ax+5,ay)], fill=(*ORANGE,255))
img.save(OUT + "icon_glb_importer.png")
print("Saved: icon_glb_importer.png")

# ── 5. OBJ Batch Exporter — pixel box + up arrow ─────────────────────────────
img, draw = base()
# Box outline (pixel squares forming a U)
box = [(2,1),(2,2),(2,3),(2,4),(2,5),  # left wall
       (6,1),(6,2),(6,3),(6,4),(6,5),  # right wall
       (7,1),(7,2),(7,3),(7,4),(7,5)]  # bottom
for r,c in box:
    px(draw, GRAY_L, r, c, 190)
# Batch lines inside box
for i, w in enumerate([2, 3, 2]):
    for cw in range(w):
        px(draw, DIM, 4+i, 2+cw, 180-i*30)
# Up arrow pixels (orange) — above box
for r in range(3):
    px(draw, ORANGE, r, 7, 255-r*40)
# Arrowhead
ax = GX + 7*STEP + PX//2
ay = GY + 0*STEP
draw.polygon([(ax-5,ay),(ax,ay-7),(ax+5,ay)], fill=(*ORANGE,255))
img.save(OUT + "icon_obj_exporter.png")
print("Saved: icon_obj_exporter.png")

# ── 6. Arnold PBR Material — pixel sphere (circle of pixels) ─────────────────
img, draw = base()
# Build a pixel circle — mark cells inside radius
cx_f, cy_f = 3.5, 3.5  # centre in grid coords
radius = 3.2
for r in range(8):
    for c in range(8):
        dist = math.sqrt((c-cx_f)**2 + (r-cy_f)**2)
        if dist <= radius:
            # Shading: brighter toward top-left
            t = 1.0 - min(1.0, math.sqrt((c-1.5)**2+(r-1.0)**2)/3.5)
            col = (
                int(PANEL[0] + (ORANGE[0]-PANEL[0])*t),
                int(PANEL[1] + (ORANGE[1]-PANEL[1])*t),
                int(PANEL[2] + (ORANGE[2]-PANEL[2])*t),
            )
            alpha = int(160 + t*95)
            px(draw, col, r, c, alpha)
        elif abs(dist - radius) < 0.6:
            px(draw, GRAY_L, r, c, 120)
# Specular highlight pixel
px(draw, (255,255,255), 1, 2, 180)
img.save(OUT + "icon_arnold_material.png")
print("Saved: icon_arnold_material.png")

# ── 7. Render Layer Creator — stacked pixel layer bands ──────────────────────
img, draw = base()
layer_configs = [
    (7, 6, ORANGE, 240),   # bottom layer — orange, full width
    (5, 5, GRAY_L, 200),   # middle
    (3, 4, GRAY_L, 160),   # top
]
for start_r, width, col, alpha in layer_configs:
    for c in range(width):
        offset = (6 - width) // 2
        px(draw, col, start_r, c + offset, alpha)
# Camera pixels top-left
cam = [(0,0),(0,1),(0,2),(1,0),(1,2),(2,0),(2,1),(2,2)]
for r, c in cam:
    px(draw, GRAY_L, r, c, 160)
# Lens orange pixel
px(draw, ORANGE, 1, 1, 255)
img.save(OUT + "icon_render_layers.png")
print("Saved: icon_render_layers.png")

# ── 8. TurnTable Builder — pixel rotation arc + centre object ────────────────
img, draw = base()
# Draw arc as pixel cells that fall on a circle outline
cx_f, cy_f = 3.5, 3.5
r_out, r_in = 3.8, 2.8
for r in range(8):
    for c in range(8):
        dist = math.sqrt((c-cx_f)**2 + (r-cy_f)**2)
        if r_in <= dist <= r_out:
            # Only draw ~270° arc (skip bottom-right quadrant)
            angle = math.degrees(math.atan2(r-cy_f, c-cx_f))
            if not (20 < angle < 90):
                col = ORANGE if angle < 20 else GRAY_L
                px(draw, col, r, c, 220)
# Centre object pixels (diamond)
centre_pixels = [(3,3),(3,4),(4,3),(4,4),(2,3),(5,3),(3,2),(3,5)]
for r, c in centre_pixels:
    px(draw, GRAY_L, r, c, 180)
px(draw, ORANGE, 3, 3, 255)
# Arrowhead pixel at arc end
px(draw, ORANGE, 1, 6, 255)
px(draw, ORANGE, 0, 7, 200)
img.save(OUT + "icon_turntable_builder.png")
print("Saved: icon_turntable_builder.png")

print("\nSet A complete —", OUT)
