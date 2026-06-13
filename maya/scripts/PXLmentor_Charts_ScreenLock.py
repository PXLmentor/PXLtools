"""
PXLmentor TurnTable — Charts Screen Lock  (Scene Bake Script)
=============================================================
Bakes a distanceBetween node + expression directly into the TurnTable scene
file so that scaleMove_GRP.scale tracks camera distance automatically at
runtime, giving the Macbeth chart and reference balls a constant apparent
screen size at any camera position.

Run this script with the TurnTable .ma file open DIRECTLY in Maya
(File > Open — not as a reference into another scene).
After running, save as a new version (e.g. v004.ma).

imagePlane equation applied in world space:
    apparent_size  =  world_size  /  distance
    →  world_size(d) = apparent_size_target × d
    →  scale(d) = d / d_reference

At d_reference (camera position when this script runs): scale = 1.0
At 2× d_reference: scale = 2.0 — twice as large in world space but
reads identically on screen because it is twice as far away.

Implementation
--------------
One distanceBetween node reads worldMatrix from both main_CAM and
scaleMove_GRP and outputs live Euclidean distance each frame.
A single expression divides that by the baked reference constant and
drives scaleMove_GRP.scaleX/Y/Z.

The TurnTable Builder's scale slider drives macbeth_grp.scale and
refBall_grp.scale (children of scaleMove_GRP) — untouched by this script.
Effective screen size = base_scale × (ref_distance / distance) = constant.

Usage
-----
1. File > Open  →  PXLmentor_TB3DTT_ACES_2025_v003.ma  (open directly)
2. Run this script in the Script Editor (Python tab)
3. File > Save As  →  PXLmentor_TB3DTT_ACES_2025_v004.ma

Re-run at any time to rebake the reference distance if the default
camera or chart position is changed in the source file.

To remove: run the REMOVE BLOCK at the bottom, then save.
"""

import maya.cmds as cmds

# ─────────────────────────────────────────────────────────────────────────────
# Node names — bare (no namespace: file is open directly, not referenced)
# ─────────────────────────────────────────────────────────────────────────────

cam       = 'main_CAM'
grp       = 'scaleMove_GRP'
dist_node = 'cam_charts_dist'
expr_node = 'charts_screen_lock'

for _n in (cam, grp):
    if not cmds.objExists(_n):
        raise RuntimeError(
            'Node not found: {}\n'
            'Make sure you opened the TurnTable .ma file directly '
            '(File > Open), not as a reference.'.format(_n)
        )


# ─────────────────────────────────────────────────────────────────────────────
# Remove any previous version of this setup
# ─────────────────────────────────────────────────────────────────────────────

for _n in (expr_node, dist_node):
    if cmds.objExists(_n):
        cmds.delete(_n)
        print('Removed previous node: {}'.format(_n))


# ─────────────────────────────────────────────────────────────────────────────
# distanceBetween: main_CAM <-> scaleMove_GRP  (world space, both inputs)
# ─────────────────────────────────────────────────────────────────────────────

dist = cmds.createNode('distanceBetween', name=dist_node)
cmds.connectAttr('{}.worldMatrix[0]'.format(cam), '{}.inMatrix1'.format(dist))
cmds.connectAttr('{}.worldMatrix[0]'.format(grp), '{}.inMatrix2'.format(dist))

# Reference distance: actual Euclidean distance RIGHT NOW
# (not COI — COI changes when camera is re-framed)
ref_dist = cmds.getAttr('{}.distance'.format(dist))

if ref_dist < 0.001:
    cmds.delete(dist)
    raise RuntimeError(
        'Reference distance is essentially zero ({:.6f}).\n'
        'main_CAM and scaleMove_GRP are at the same world position — '
        'move one of them and re-run.'.format(ref_dist)
    )

print('Reference distance (baked) : {:.4f} units'.format(ref_dist))


# ─────────────────────────────────────────────────────────────────────────────
# Expression
#
# imagePlane equation:
#   scale(d) = d / d_reference
#
# d_reference is baked as a literal float — no divide-by-zero risk.
# Node names are bare (no namespace); Maya resolves them relative to the
# reference namespace automatically when the file is used as a reference.
# ─────────────────────────────────────────────────────────────────────────────

expr_str = (
    '// PXLmentor Charts Screen Lock\n'
    '// imagePlane math: scale proportional to camera distance\n'
    '//   scale(d) = d / d_reference\n'
    '// Reference distance baked at setup: {ref:.6f} units\n'
    'float $d = {dist}.distance;\n'
    '{grp}.scaleX = $d / {ref:.6f};\n'
    '{grp}.scaleY = $d / {ref:.6f};\n'
    '{grp}.scaleZ = $d / {ref:.6f};\n'
).format(
    dist = dist_node,
    grp  = grp,
    ref  = ref_dist,
)

cmds.expression(
    name           = expr_node,
    string         = expr_str,
    object         = grp,
    alwaysEvaluate = False,   # only fires when distanceBetween.distance changes
    unitConversion = 'all',
)

print('Expression created : {}'.format(expr_node))
print()
print('scaleMove_GRP.scale now tracks camera distance.')
print('  base chart size       = macbeth_grp / refBall_grp scale (TT Builder slider)')
print('  distance compensator  = scaleMove_GRP.scale  (this expression)')
print('  effective screen size = constant at all distances')
print()
print('NOW SAVE AS A NEW VERSION:')
print('  File > Save As  ->  PXLmentor_TB3DTT_ACES_2025_v004.ma')


# ─────────────────────────────────────────────────────────────────────────────
# REMOVE BLOCK — uncomment and run to tear down the setup, then save
# ─────────────────────────────────────────────────────────────────────────────
# import maya.cmds as cmds
# for _n in ('charts_screen_lock', 'cam_charts_dist'):
#     if cmds.objExists(_n):
#         cmds.delete(_n)
#         print('Deleted: {}'.format(_n))
#
# # Reset scale to 1.0 after removal
# if cmds.objExists('scaleMove_GRP'):
#     for ax in ('scaleX', 'scaleY', 'scaleZ'):
#         cmds.setAttr('scaleMove_GRP.{}'.format(ax), 1.0)
#     print('scaleMove_GRP.scale reset to 1.0')
