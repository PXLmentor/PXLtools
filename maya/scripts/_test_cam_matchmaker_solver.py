"""Standalone analytical self-test for the CP022 solver math.

Runs WITHOUT Maya. Synthesises vanishing points from a known rotation,
feeds them through the fSpy-exact solver, and confirms the recovered
Euler angles and forward projection match within 1e-3.

Copy the solver functions from PXLmentor_Camera_Matchmaker_v0_2_0_alpha.py
line-for-line and keep them in sync with the production file.
"""
import math
import random


# ─── Utils (same as production) ────────────────────────────────────────────
def _cross3(a, b):
    return (a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0])


def _pixel_to_image_plane(px, py, w, h):
    if w >= h:
        return (2.0 * px / w - 1.0, (h - 2.0 * py) / w)
    else:
        return ((2.0 * px - w) / h, 1.0 - 2.0 * py / h)


def _image_plane_to_pixel(x_ip, y_ip, w, h):
    if w >= h:
        px = (x_ip + 1.0) * w / 2.0
        py = (h - y_ip * w) / 2.0
    else:
        px = (x_ip * h + w) / 2.0
        py = (1.0 - y_ip) * h / 2.0
    return (px, py)


# ─── Maya-equivalent independent pixel-to-ray mapping (NO reliance on fSpy code) ─
def _maya_pixel_to_camera_ray(px, py, w, h, focal_mm, hfa_mm):
    """What Maya actually does when mapping a pixel on the image plane (fit=horizontal,
       with verticalFilmAperture = horizontalFilmAperture * h/w so gate_AR = image_AR)
       to a camera-space ray direction.  Principal point = image center.

       Returns (dx, dy, dz) in camera space — unnormalised.
    """
    vfa_mm = hfa_mm * h / w
    # Image plane pixel (px, py) maps to (x_cam, y_cam) on the physical gate in mm.
    # Column 0   → left edge  = -hfa_mm/2
    # Column w   → right edge = +hfa_mm/2
    # Row 0      → top edge   = +vfa_mm/2   (image Y-down ↔ camera Y-up)
    # Row h      → bottom     = -vfa_mm/2
    x_cam_mm = hfa_mm * (px / w - 0.5)
    y_cam_mm = vfa_mm * (0.5 - py / h)
    # Ray direction in camera space: (x_cam, y_cam, -focal_mm)
    return (x_cam_mm, y_cam_mm, -focal_mm)


def _compute_focal_relative(Fu, Fv, P=(0.0, 0.0)):
    dx, dy = Fu[0] - Fv[0], Fu[1] - Fv[1]
    d = math.sqrt(dx*dx + dy*dy)
    if d < 1e-10:
        return None
    dir_uv = (dx / d, dy / d)
    FvP = (P[0] - Fv[0], P[1] - Fv[1])
    proj = dir_uv[0] * FvP[0] + dir_uv[1] * FvP[1]
    Puv = (proj * dir_uv[0] + Fv[0], proj * dir_uv[1] + Fv[1])
    PPuv  = math.sqrt((P[0]  - Puv[0])**2 + (P[1]  - Puv[1])**2)
    FvPuv = math.sqrt((Fv[0] - Puv[0])**2 + (Fv[1] - Puv[1])**2)
    FuPuv = math.sqrt((Fu[0] - Puv[0])**2 + (Fu[1] - Puv[1])**2)
    f_sq = FvPuv * FuPuv - PPuv * PPuv
    return math.sqrt(f_sq) if f_sq > 0 else None


def _compute_camera_rotation(Fu, Fv, f_rel):
    ofu_mag = math.sqrt(Fu[0]*Fu[0] + Fu[1]*Fu[1] + f_rel*f_rel)
    ofv_mag = math.sqrt(Fv[0]*Fv[0] + Fv[1]*Fv[1] + f_rel*f_rel)
    if ofu_mag < 1e-12 or ofv_mag < 1e-12:
        return None
    u = (Fu[0] / ofu_mag, Fu[1] / ofu_mag, -f_rel / ofu_mag)
    v = (Fv[0] / ofv_mag, Fv[1] / ofv_mag, -f_rel / ofv_mag)

    def _build(u_in, v_in):
        y = _cross3(v_in, u_in)
        ym = math.sqrt(y[0]*y[0] + y[1]*y[1] + y[2]*y[2])
        if ym < 1e-10:
            return None, None
        y = (y[0]/ym, y[1]/ym, y[2]/ym)
        return y, [list(u_in), list(y), list(v_in)]

    y, R = _build(u, v)
    if y is None:
        return None
    if y[1] < 0:
        v = (-v[0], -v[1], -v[2])
        y, R = _build(u, v)
        if y is None:
            return None
    if R[0][0] < 0:
        u = (-u[0], -u[1], -u[2])
        v = (-v[0], -v[1], -v[2])
        y, R = _build(u, v)
        if y is None:
            return None
    return R


def _maya_xyz_euler_from_rctw(R):
    sin_b = max(-1.0, min(1.0, R[0][2]))
    ry = math.asin(sin_b)
    if abs(math.cos(ry)) > 1e-6:
        rx = math.atan2(-R[1][2], R[2][2])
        rz = math.atan2(-R[0][1], R[0][0])
    else:
        rx = math.atan2(R[2][1], R[1][1])
        rz = 0.0
    return (math.degrees(rx), math.degrees(ry), math.degrees(rz))


def _project_world_point(world_pt, cam_pos, R_ctw, f_rel, w, h):
    rel = (world_pt[0] - cam_pos[0],
           world_pt[1] - cam_pos[1],
           world_pt[2] - cam_pos[2])
    p_cam = (
        R_ctw[0][0]*rel[0] + R_ctw[1][0]*rel[1] + R_ctw[2][0]*rel[2],
        R_ctw[0][1]*rel[0] + R_ctw[1][1]*rel[1] + R_ctw[2][1]*rel[2],
        R_ctw[0][2]*rel[0] + R_ctw[1][2]*rel[1] + R_ctw[2][2]*rel[2],
    )
    if p_cam[2] >= -1e-9:
        return None
    x_ip = f_rel * p_cam[0] / (-p_cam[2])
    y_ip = f_rel * p_cam[1] / (-p_cam[2])
    return _image_plane_to_pixel(x_ip, y_ip, w, h)


# ─── Oracle: build R_ctw from known Euler, project VPs, round-trip ────────
def _rx(a):
    ca, sa = math.cos(a), math.sin(a)
    return [[1, 0, 0], [0, ca, -sa], [0, sa, ca]]


def _ry(a):
    ca, sa = math.cos(a), math.sin(a)
    return [[ca, 0, sa], [0, 1, 0], [-sa, 0, ca]]


def _rz(a):
    ca, sa = math.cos(a), math.sin(a)
    return [[ca, -sa, 0], [sa, ca, 0], [0, 0, 1]]


def _mat3_mul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _R_ctw_from_euler(rx_deg, ry_deg, rz_deg):
    """Maya XYZ intrinsic: R = Rx * Ry * Rz  ->  camera-to-world."""
    return _mat3_mul(_mat3_mul(_rx(math.radians(rx_deg)), _ry(math.radians(ry_deg))),
                     _rz(math.radians(rz_deg)))


def _project_vp_pixel(world_axis, R_ctw, f_rel, w, h):
    """Return the pixel where the infinite point in direction world_axis appears.
       A world direction d projects to image plane coords (f * d_cam.x / (-d_cam.z), ...)."""
    # d_cam = R_wtc @ d_world = R_ctw^T @ d_world
    d_cam = (
        R_ctw[0][0]*world_axis[0] + R_ctw[1][0]*world_axis[1] + R_ctw[2][0]*world_axis[2],
        R_ctw[0][1]*world_axis[0] + R_ctw[1][1]*world_axis[1] + R_ctw[2][1]*world_axis[2],
        R_ctw[0][2]*world_axis[0] + R_ctw[1][2]*world_axis[1] + R_ctw[2][2]*world_axis[2],
    )
    if abs(d_cam[2]) < 1e-9:
        return None  # VP at infinity on horizon
    x_ip = f_rel * d_cam[0] / (-d_cam[2])
    y_ip = f_rel * d_cam[1] / (-d_cam[2])
    return _image_plane_to_pixel(x_ip, y_ip, w, h)


# ─── Round-trip test ──────────────────────────────────────────────────────
def run_self_test(n_cases=20, seed=42):
    random.seed(seed)
    W, H = 1920, 1080
    # f_true chosen to correspond to ~60deg horizontal FOV
    f_rel_true = 1.0 / math.tan(math.radians(60.0) / 2.0)
    print(f"Self-test: {n_cases} random cases, {W}x{H}, f_rel_true={f_rel_true:.4f}")

    rot_pass = 0
    proj_pass = 0
    maya_pass = 0
    worst_rot_err = 0.0
    worst_proj_err = 0.0
    worst_maya_err = 0.0
    # Maya gate matches fSpy f_rel_true: 36mm horizontal aperture, focal_mm = 18 * f_rel
    HFA_MM = 36.0
    FOCAL_MM = 18.0 * f_rel_true

    for case in range(n_cases):
        # Random rotation within reasonable photo limits
        rx_deg = random.uniform(-35.0, 35.0)    # tilt (up/down)
        ry_deg = random.uniform(-60.0, 60.0)    # pan (left/right)
        rz_deg = random.uniform(-10.0, 10.0)    # roll (minor)

        R_true = _R_ctw_from_euler(rx_deg, ry_deg, rz_deg)

        # Project world X and world Z to pixels to get the VP positions
        vp_x_px = _project_vp_pixel((1, 0, 0), R_true, f_rel_true, W, H)
        vp_z_px = _project_vp_pixel((0, 0, 1), R_true, f_rel_true, W, H)
        if vp_x_px is None or vp_z_px is None:
            print(f"  case {case:2d}: SKIP (VP at horizon)")
            continue

        # Feed through solver
        Fu = _pixel_to_image_plane(vp_x_px[0], vp_x_px[1], W, H)
        Fv = _pixel_to_image_plane(vp_z_px[0], vp_z_px[1], W, H)
        f_rel_solved = _compute_focal_relative(Fu, Fv)
        if f_rel_solved is None:
            print(f"  case {case:2d}: SKIP (focal undefined — VPs on same side?)")
            continue
        R_solved = _compute_camera_rotation(Fu, Fv, f_rel_solved)
        if R_solved is None:
            print(f"  case {case:2d}: SKIP (rotation degenerate)")
            continue

        rx_s, ry_s, rz_s = _maya_xyz_euler_from_rctw(R_solved)

        # Check 1: focal length recovered
        f_err = abs(f_rel_solved - f_rel_true)

        # Check 2: Euler angles recovered
        def _ang_diff(a, b):
            d = (a - b) % 360.0
            return min(d, 360.0 - d)
        rot_err = max(_ang_diff(rx_s, rx_deg),
                      _ang_diff(ry_s, ry_deg),
                      _ang_diff(rz_s, rz_deg))

        # Check 3: world-origin-like point forward-projects consistently.
        # Place the camera on the -forward direction of the solved rotation, 10 units out,
        # so world origin is guaranteed to be in front of the camera.
        fwd = (-R_solved[0][2], -R_solved[1][2], -R_solved[2][2])  # camera forward in world
        fwd_mag = math.sqrt(sum(c*c for c in fwd))
        fwd = tuple(c / fwd_mag for c in fwd)
        cam_pos = (-fwd[0] * 10.0, max(-fwd[1] * 10.0, 1.0), -fwd[2] * 10.0)
        pix = _project_world_point((0.0, 0.0, 0.0), cam_pos, R_solved, f_rel_solved, W, H)
        if pix is not None:
            # Cast ray through that pixel back and check it points toward (0-cam_pos)
            x_ip, y_ip = _pixel_to_image_plane(pix[0], pix[1], W, H)
            d_cam = (x_ip, y_ip, -f_rel_solved)
            d_w = [R_solved[i][0]*d_cam[0] + R_solved[i][1]*d_cam[1] + R_solved[i][2]*d_cam[2]
                   for i in range(3)]
            # Normalise d_w and compare direction with (origin - cam_pos)
            m = math.sqrt(sum(v*v for v in d_w))
            d_w = [v/m for v in d_w]
            to_origin = (-cam_pos[0], -cam_pos[1], -cam_pos[2])
            mo = math.sqrt(sum(v*v for v in to_origin))
            to_origin = [v/mo for v in to_origin]
            dot = d_w[0]*to_origin[0] + d_w[1]*to_origin[1] + d_w[2]*to_origin[2]
            proj_err = math.degrees(math.acos(max(-1.0, min(1.0, dot))))
        else:
            proj_err = float('inf')

        # Check 4: Maya-equivalent cross-check.
        # Does the solver's forward-projection of world (0,0,0) match the pixel
        # where Maya would actually render it? (independent pixel-to-ray computation)
        maya_err_px = 0.0
        if pix is not None:
            # Maya's view of where (0,0,0) renders: back-solve from the ray
            # _maya_pixel_to_camera_ray gives (xc, yc, -f). For world origin at
            # P_world = (0,0,0), camera-space point = R_wtc @ (P_world - cam_pos)
            #   = R_solved^T @ -cam_pos.
            P_rel = (-cam_pos[0], -cam_pos[1], -cam_pos[2])
            p_cam_maya = (
                R_solved[0][0]*P_rel[0] + R_solved[1][0]*P_rel[1] + R_solved[2][0]*P_rel[2],
                R_solved[0][1]*P_rel[0] + R_solved[1][1]*P_rel[1] + R_solved[2][1]*P_rel[2],
                R_solved[0][2]*P_rel[0] + R_solved[1][2]*P_rel[1] + R_solved[2][2]*P_rel[2],
            )
            if p_cam_maya[2] < 0:
                # Maya pinhole projection: x_film = focal * x_cam / -z_cam (mm)
                xf_mm = FOCAL_MM * p_cam_maya[0] / (-p_cam_maya[2])
                yf_mm = FOCAL_MM * p_cam_maya[1] / (-p_cam_maya[2])
                # Film mm -> pixel (fit=horizontal, gate_AR = image_AR)
                vfa_mm = HFA_MM * W / H if W < H else HFA_MM * H / W
                hfa_mm = HFA_MM
                maya_pix_x = (xf_mm / hfa_mm + 0.5) * W
                maya_pix_y = (0.5 - yf_mm / vfa_mm) * H
                maya_err_px = math.sqrt((maya_pix_x - pix[0])**2 + (maya_pix_y - pix[1])**2)
        rot_ok = rot_err < 0.01
        proj_ok = proj_err < 0.01 and f_err < 1e-4
        maya_ok = maya_err_px < 0.5   # tight — sub-pixel agreement
        rot_pass += rot_ok
        proj_pass += proj_ok
        maya_pass += maya_ok
        worst_rot_err = max(worst_rot_err, rot_err)
        worst_proj_err = max(worst_proj_err, proj_err)
        worst_maya_err = max(worst_maya_err, maya_err_px)

        status = "OK" if (rot_ok and proj_ok and maya_ok) else "FAIL"
        print(f"  case {case:2d}: {status}  "
              f"rx={rx_deg:+6.2f}->{rx_s:+6.2f}  "
              f"ry={ry_deg:+6.2f}->{ry_s:+6.2f}  "
              f"rz={rz_deg:+6.2f}->{rz_s:+6.2f}  "
              f"rot_err={rot_err:.4f}deg  proj_err={proj_err:.4f}deg  maya_px_err={maya_err_px:.3f}")

    print(f"\nResult: rotation {rot_pass}/{n_cases} pass, projection {proj_pass}/{n_cases} pass, "
          f"Maya-match {maya_pass}/{n_cases} pass")
    print(f"Worst rotation error: {worst_rot_err:.6f}deg")
    print(f"Worst projection error: {worst_proj_err:.6f}deg")
    print(f"Worst Maya-match pixel error: {worst_maya_err:.6f}px")
    if rot_pass == n_cases and proj_pass == n_cases and maya_pass == n_cases:
        print("ALL TESTS PASSED - solver matches Maya's rendering.")
        return 0
    else:
        print("FAILURES DETECTED - do NOT deploy.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_self_test())
