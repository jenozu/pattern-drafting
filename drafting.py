from geometry import interpolate_x_at_y, segment_length
from measurements import Measurements, DraftConfig

def _line(start, end, name):
    return {"type": "line", "name": name, "start": start, "end": end}

def _curve(start, c1, c2, end, name):
    return {"type": "cubic", "name": name, "start": start, "c1": c1, "c2": c2, "end": end}

def _named_lengths(segments):
    return {seg["name"]: segment_length(seg) for seg in segments}

def draft_basic_pants_block(m: Measurements, cfg: DraftConfig):
    """Draft the Shapes of Fabric basic pants block in centimetres.

    Coordinates mirror the tutorial's shared construction rectangle: front on
    the left, back on the right. The SVG exporter later separates the pieces.
    """
    half_hip = m.hip / 2.0
    half_waist = m.waist / 2.0
    width = half_hip + cfg.hip_ease
    height = m.waist_to_ankle
    y_hip = m.waist_to_hip
    y_crotch = m.crotch_depth + cfg.crotch_ease
    y_knee = m.waist_to_knee
    y_hem = height
    x_side = width / 2.0
    x_cf = 0.0
    x_cb = width

    extension = half_hip / 8.0
    front_crotch_extension = extension
    back_crotch_extension = extension + cfg.back_crotch_plus
    front_waist_width = (half_waist / 2.0) + cfg.front_waist_plus
    back_waist_width = (half_waist / 2.0) + cfg.back_waist_plus
    half_hem = cfg.hem_circ / 2.0
    front_hem_width = half_hem - 1.0
    back_hem_width = half_hem + 1.0

    f_crotch = (x_cf - front_crotch_extension, y_crotch)
    b_crotch = (x_cb + back_crotch_extension, y_crotch)
    f_center_hip = (x_cf, y_hip)
    b_center_hip = (x_cb, y_hip)
    f_center_waist = (x_cf + 0.5, 1.0)

    back_top_guide = (x_cb - 4.0, 0.0)
    vx = back_top_guide[0] - b_center_hip[0]
    vy = back_top_guide[1] - b_center_hip[1]
    scale = 2.5 / ((vx*vx + vy*vy) ** 0.5)
    b_center_waist = (back_top_guide[0] + vx * scale, back_top_guide[1] + vy * scale)

    f_side_waist = (f_center_waist[0] + front_waist_width, 0.0)
    b_side_waist = (b_center_waist[0] - back_waist_width, 0.0)
    f_side_hip = (x_side, y_hip)
    b_side_hip = (x_side, y_hip)
    f_side_crotch = (x_side, y_crotch)
    b_side_crotch = (x_side, y_crotch)

    f_grain_x = (f_crotch[0] + f_side_crotch[0]) / 2.0
    side_to_grain = f_side_crotch[0] - f_grain_x
    b_grain_x = b_side_crotch[0] + side_to_grain

    f_inseam_hem = (f_grain_x - front_hem_width / 2.0, y_hem)
    f_side_hem = (f_grain_x + front_hem_width / 2.0, y_hem)
    b_side_hem = (b_grain_x - back_hem_width / 2.0, y_hem)
    b_inseam_hem = (b_grain_x + back_hem_width / 2.0, y_hem)

    f_knee_guide_x = interpolate_x_at_y(f_crotch, f_inseam_hem, y_knee)
    f_inseam_knee = (f_knee_guide_x + 1.0, y_knee)
    f_knee_half = f_grain_x - f_inseam_knee[0]
    f_side_knee = (f_grain_x + f_knee_half, y_knee)

    b_knee_half = f_knee_half + 1.0
    b_side_knee = (b_grain_x - b_knee_half, y_knee)
    b_inseam_knee = (b_grain_x + b_knee_half, y_knee)

    front_points = {
        "center_waist": f_center_waist, "side_waist": f_side_waist,
        "side_hip": f_side_hip, "side_crotch": f_side_crotch,
        "side_knee": f_side_knee, "side_hem": f_side_hem,
        "inseam_hem": f_inseam_hem, "inseam_knee": f_inseam_knee,
        "crotch_point": f_crotch, "center_hip": f_center_hip,
    }
    front_segments = [
        _curve(f_center_waist, (f_center_waist[0] + 0.8, f_center_waist[1]), (f_side_waist[0] - 2.0, 0.0), f_side_waist, "waist"),
        _curve(f_side_waist, (f_side_waist[0] + 1.5, 4.0), (f_side_hip[0], y_hip - 4.0), f_side_hip, "hip_side"),
        _curve(f_side_hip, (x_side, y_hip + 3.0), (x_side, y_crotch - 3.0), f_side_crotch, "upper_side"),
        _curve(f_side_crotch, (x_side, y_crotch + 8.0), (f_side_knee[0], y_knee - 8.0), f_side_knee, "side_thigh"),
        _line(f_side_knee, f_side_hem, "side_lower_leg"),
        _line(f_side_hem, f_inseam_hem, "hem"),
        _line(f_inseam_hem, f_inseam_knee, "inseam_lower_leg"),
        _curve(f_inseam_knee, (f_inseam_knee[0] - 0.2, y_knee - 9.0), (f_crotch[0] + 2.0, y_crotch + 7.0), f_crotch, "inseam_thigh"),
        _curve(f_crotch, (f_crotch[0] + 3.0, y_crotch), (x_cf - 0.2, y_crotch - 3.5), f_center_hip, "front_crotch_curve"),
        _line(f_center_hip, f_center_waist, "center_front"),
    ]

    back_points = {
        "center_waist": b_center_waist, "side_waist": b_side_waist,
        "side_hip": b_side_hip, "side_crotch": b_side_crotch,
        "side_knee": b_side_knee, "side_hem": b_side_hem,
        "inseam_hem": b_inseam_hem, "inseam_knee": b_inseam_knee,
        "crotch_point": b_crotch, "center_hip": b_center_hip,
    }
    back_segments = [
        _curve(b_center_waist, (b_center_waist[0] - 0.7, b_center_waist[1]), (b_side_waist[0] + 2.0, 0.0), b_side_waist, "waist"),
        _curve(b_side_waist, (b_side_waist[0] - 1.2, 4.0), (b_side_hip[0], y_hip - 4.0), b_side_hip, "hip_side"),
        _curve(b_side_hip, (x_side, y_hip + 3.0), (x_side, y_crotch - 3.0), b_side_crotch, "upper_side"),
        _curve(b_side_crotch, (x_side, y_crotch + 8.0), (b_side_knee[0], y_knee - 8.0), b_side_knee, "side_thigh"),
        _line(b_side_knee, b_side_hem, "side_lower_leg"),
        _line(b_side_hem, b_inseam_hem, "hem"),
        _line(b_inseam_hem, b_inseam_knee, "inseam_lower_leg"),
        _curve(b_inseam_knee, (b_inseam_knee[0] + 0.4, y_knee - 10.0), (b_crotch[0] - 3.5, y_crotch + 8.0), b_crotch, "inseam_thigh"),
        _curve(b_crotch, (b_crotch[0] - 4.5, y_crotch), (x_cb + 1.0, y_crotch - 6.5), b_center_hip, "back_crotch_curve"),
        _line(b_center_hip, b_center_waist, "center_back"),
    ]

    dart_center_x = (b_center_waist[0] + b_side_waist[0]) / 2.0
    back_dart = {
        "left": (dart_center_x - 1.0, 0.0),
        "right": (dart_center_x + 1.0, 0.0),
        "tip": (dart_center_x, 10.0),
    }

    f_lengths = _named_lengths(front_segments)
    b_lengths = _named_lengths(back_segments)
    checks = {
        "front_lower_side": f_lengths["side_lower_leg"],
        "back_lower_side": b_lengths["side_lower_leg"],
        "front_lower_inseam": f_lengths["inseam_lower_leg"],
        "back_lower_inseam": b_lengths["inseam_lower_leg"],
        "upper_side_difference": (b_lengths["hip_side"] + b_lengths["upper_side"] + b_lengths["side_thigh"]) - (f_lengths["hip_side"] + f_lengths["upper_side"] + f_lengths["side_thigh"]),
        "upper_inseam_difference": (b_lengths["inseam_thigh"] + b_lengths["back_crotch_curve"]) - (f_lengths["inseam_thigh"] + f_lengths["front_crotch_curve"]),
    }

    return {
        "guides": {
            "width": width, "height": height, "y_hip": y_hip, "y_crotch": y_crotch,
            "y_knee": y_knee, "y_hem": y_hem, "x_split": x_side,
            "front_crease_x": f_grain_x, "back_crease_x": b_grain_x,
            "front_waist_width": front_waist_width, "back_waist_width": back_waist_width,
        },
        "points": {
            "top_left": (0.0, 0.0), "top_right": (width, 0.0),
            "split_top": (x_side, 0.0), "split_bottom": (x_side, y_hem),
            "front_crotch_point": f_crotch, "front_crotch_side": f_side_crotch,
            "back_crotch_point": b_crotch, "back_crotch_side": b_side_crotch,
            "front_hem_left": f_inseam_hem, "front_hem_right": f_side_hem,
            "back_hem_left": b_side_hem, "back_hem_right": b_inseam_hem,
        },
        "pieces": {
            "front": {"points": front_points, "segments": front_segments, "grain_x": f_grain_x, "markings": {}},
            "back": {"points": back_points, "segments": back_segments, "grain_x": b_grain_x, "markings": {"dart": back_dart}},
        },
        "checks": checks,
    }
