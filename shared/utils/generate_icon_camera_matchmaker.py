"""
PXLmentor Icon — Camera Matchmaker  (Set C style)
96x96px RGBA. Matches generate_icons_setC.py palette and conventions:
  - Symbol + PXL 4-pixel mosaic corner accent (orange/cyan/pink/gold, top-right)
  - STROKE outlines, DIM secondaries, ORANGE focal accent
  - No red/blue — single-accent language

Design: reference photo frame with faint VP lines inside, orange solved-VP X
marker at right edge, camera body + lens at bottom, pixel mosaic top-right.
"""

from PIL import Image, ImageDraw
import shutil

SIZE   = 96
ICONS  = "J:/ClaudeCode/projects/PXLtools/maya/scripts/icons/"
DEPLOY = "C:/Users/Evil Knight/Documents/maya/2025/prefs/icons/"

BG     = (14,  16,  24)
PANEL  = (22,  26,  38)
ORANGE = (232, 130,  12)
CYAN   = ( 60, 195, 210)
PINK   = (210,  65, 130)
GOLD   = (255, 185,  40)
STROKE = (180, 188, 210)
DIM    = ( 95, 105, 128)


def base():
    img  = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, SIZE-1, SIZE-1], radius=18, fill=(*BG, 255))
    draw.rounded_rectangle([7, 7, SIZE-8,  SIZE-8], radius=13, fill=(*PANEL, 255))
    return img, draw


def pixel_accent(draw):
    colors = [ORANGE, CYAN, PINK, GOLD]
    px = 6
    positions = [(SIZE-22, 10), (SIZE-14, 10), (SIZE-22, 18), (SIZE-14, 18)]
    for i, (px_, py_) in enumerate(positions):
        draw.rectangle([px_, py_, px_+px-1, py_+px-1], fill=(*colors[i], 220))


img, draw = base()

# Reference photo frame
fx, fy, fw, fh = 12, 14, 60, 44
draw.rectangle([fx, fy, fx+fw, fy+fh], outline=(*STROKE, 160), width=1)
hy = fy + fh // 2 + 1
draw.line([(fx+2, hy), (fx+fw-2, hy)], fill=(*DIM, 120), width=1)

# VP lines — faint, both axes converging (DIM)
vp1x = 80
draw.line([(fx+2, fy+9),      (vp1x, hy)], fill=(*DIM, 140), width=1)
draw.line([(fx+2, fy+fh-9),   (vp1x, hy)], fill=(*DIM, 110), width=1)
vp2x = 8
draw.line([(fx+fw-2, fy+6),   (vp2x, hy)], fill=(*DIM, 140), width=1)
draw.line([(fx+fw-2, fy+fh-6),(vp2x, hy)], fill=(*DIM, 110), width=1)

# Orange solved VP X marker (right side)
vx, vy, s = 77, hy, 4
draw.line([(vx-s, vy-s),(vx+s, vy+s)], fill=(*ORANGE, 240), width=2)
draw.line([(vx+s, vy-s),(vx-s, vy+s)], fill=(*ORANGE, 240), width=2)

# Camera body (bottom)
cx, cy2, cw, ch = 16, 64, 48, 18
draw.rounded_rectangle([cx, cy2, cx+cw, cy2+ch], radius=3,
                        outline=(*STROKE, 200), width=2)
lx, ly = cx + cw//2, cy2 + ch//2
draw.ellipse([lx-6, ly-6, lx+6, ly+6], outline=(*ORANGE, 230), width=2)
draw.ellipse([lx-2, ly-2, lx+2, ly+2], fill=(*ORANGE, 200))
draw.rectangle([cx+17, cy2-4, cx+31, cy2+1], fill=(*DIM, 100))

# 4-pixel mosaic corner accent
pixel_accent(draw)

img.save(ICONS + "icon_camera_matchmaker.png")
print("Saved: icon_camera_matchmaker.png")

shutil.copy2(ICONS + "icon_camera_matchmaker.png", DEPLOY + "icon_camera_matchmaker.png")
print("Deployed: icon_camera_matchmaker.png")
