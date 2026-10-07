from geometry import (
    interpolate_x_at_y,
    point_on_segment_at_length,
    segment_length,
)
from measurements import Measurements, DraftConfig
from side_seam import fair_and_match_side_seams, upper_length

UPPER_SIDE_NAMES = ("hip_side", "upper_side", "side_thigh")

def _line(start, end, name):
    return {"type": "line", "name": name, "start": start, "end": end}

def _curve(start, c1, c2, end, name):
    return {"type": "cubic", "name": name, "start": start, "c1": c1, "c2": c2, "end": end}

def _named_lengths(segments):
    return {seg["name"]: segment_length(seg) for seg in segments}

def _seam_length(segments, names):
    wanted = set(names)
    return sum(segment_length(seg) for seg in segments if seg["name"] in wanted)

def _validate_inputs(m: Measurements, cfg: DraftConfig):
    for name, value in m.__dict__.items():
        if value <= 0:
            raise ValueError(f"{name} must be greater than 0 cm")
    if cfg.hem_circ <= 2.0:
        raise ValueError("hem_circ is too small to draft a positive front hem")
    if cfg.seam_tolerance <= 0:
        raise ValueError("seam_tolerance must be greater than 0")
    if cfg.max_back_crotch_drop < 0 or cfg.max_side_bulge < 0:
        raise ValueError("seam-walking adjustment limits cannot be negative")

    y_crotch = m.crotch_depth + cfg.crotch_ease
    if not (m.waist_to_hip < y_crotch < m.waist_to_knee < m.waist_to_ankle):
        raise ValueError(
            "Expected waist_to_hip < crotch depth + ease < waist_to_knee < waist_to_ankle"
        )

def _binary_solve_increasing(fn, target, low, high, tolerance=1e-5):
    low_value = fn(low)
    high_value = fn(high)
    if target < low_value - tolerance or target > high_value + tolerance:
        raise ValueError(
            f"Target {target:.4f} is outside solver range "
            f"{low_value:.4f}..{high_value:.4f}"
        )
    for _ in range(80):
        mid = (low + high) / 2.0
        value = fn(mid)
        if abs(value - target) <= tolerance:
            return mid
        if value < target:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0

def _binary_solve_decreasing(fn, target, low, high, tolerance=1e-5):
    low_value = fn(low)
    high_value = fn(high)
    if target > low_value + tolerance or target < high_value - tolerance:
        raise ValueError(
            f"Target {target:.4f} is outside solver range "
            f"{high_value:.4f}..{low_value:.4f}"
        )
    for _ in range(80):
        mid = (low + high) / 2.0
        value = fn(mid)
        if abs(value - target) <= tolerance:
            return mid
        if value > target:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0

def _right_angle_waist_control(center_waist, center_hip, handle_cm, side_direction):
    """Return a waist control point perpendicular to the center seam."""
    vx = center_hip[0] - center_waist[0]
    vy = center_hip[1] - center_waist[1]
    length = (vx * vx + vy * vy) ** 0.5
    if length == 0:
        raise ValueError("Center seam cannot have zero length")
    candidates = [(-vy / length, vx / length), (vy / length, -vx / length)]
    ux, uy = max(candidates, key=lambda p: p[0] * side_direction)
    return (center_waist[0] + ux * handle_cm, center_waist[1] + uy * handle_cm)

def _equalize_upper_side_seams(front_segments, back_segments, cfg):
    """Fair the upper side seams and, when enabled, walk them to equal length."""
    front_before = _seam_length(front_segments, UPPER_SIDE_NAMES)
    back_before = _seam_length(back_segments, UPPER_SIDE_NAMES)

    if not cfg.auto_seam_walk:
        return front_segments, back_segments, {
            "front_before": front_before,
            "back_before": back_before,
            "front_after": front_before,
            "back_after": back_before,
            "front_bulge": 0.0,
            "back_bulge": 0.0,
        }

    front_segments, back_segments, result = fair_and_match_side_seams(
        front_segments,
        back_segments,
        tolerance=cfg.seam_tolerance,
        max_adjustment=cfg.max_side_bulge,
    )
    return front_segments, back_segments, result

def _build_back_inseam(b_inseam_knee, b_crotch_x, base_y, drop=0.0, extra_bulge=0.0):
    crotch = (b_crotch_x, base_y + drop)
    segment = _curve(
        b_inseam_knee,
        (b_inseam_knee[0] + 0.4, b_inseam_knee[1] - 10.0),
        (crotch[0] - 3.5 - extra_bulge, crotch[1] + 8.0),
        crotch,
        "inseam_thigh",
    )
    return crotch, segment

def _equalize_upper_inseams(front_inseam, b_inseam_knee, b_crotch_x, base_y, cfg):
    target = segment_length(front_inseam)
    base_crotch, base_segment = _build_back_inseam(
        b_inseam_knee, b_crotch_x, base_y
    )
    before = segment_length(base_segment)
    drop = 0.0
    bulge = 0.0
    crotch = base_crotch
    segment = base_segment

    if cfg.auto_seam_walk and abs(before - target) > cfg.seam_tolerance:
        if before > target:
            fn = lambda amount: segment_length(
                _build_back_inseam(
                    b_inseam_knee, b_crotch_x, base_y, drop=amount
                )[1]
            )
            drop = _binary_solve_decreasing(
                fn, target, 0.0, cfg.max_back_crotch_drop
            )
            crotch, segment = _build_back_inseam(
                b_inseam_knee, b_crotch_x, base_y, drop=drop
            )
        else:
            fn = lambda amount: segment_length(
                _build_back_inseam(
                    b_inseam_knee, b_crotch_x, base_y, extra_bulge=amount
                )[1]
            )
            bulge = _binary_solve_increasing(
                fn, target, 0.0, cfg.max_side_bulge
            )
            crotch, segment = _build_back_inseam(
                b_inseam_knee, b_crotch_x, base_y, extra_bulge=bulge
            )

    return crotch, segment, {
        "front_before": target,
        "back_before": before,
        "front_after": target,
        "back_after": segment_length(segment),
        "back_crotch_drop": drop,
        "back_inseam_bulge": bulge,
    }

def _dart_on_back_waist(waist_segment):
    waist_length = segment_length(waist_segment)
    center_distance = waist_length / 2.0
    left = point_on_segment_at_length(waist_segment, center_distance - 1.0)
    right = point_on_segment_at_length(waist_segment, center_distance + 1.0)
    center = point_on_segment_at_length(waist_segment, center_distance)
    return {
        "left": left,
        "right": right,
        "tip": (center[0], center[1] + 10.0),
        "center": center,
    }

def draft_basic_pants_block(m: Measurements, cfg: DraftConfig):
    """Draft and seam-walk the Shapes of Fabric basic pants block in centimetres."""
    _validate_inputs(m, cfg)

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
    b_crotch_base = (x_cb + back_crotch_extension, y_crotch)
    f_center_hip = (x_cf, y_hip)
    b_center_hip = (x_cb, y_hip)
    f_center_waist = (x_cf + 0.5, 1.0)

    back_top_guide = (x_cb - 4.0, 0.0)
    vx = back_top_guide[0] - b_center_hip[0]
    vy = back_top_guide[1] - b_center_hip[1]
    scale = 2.5 / ((vx * vx + vy * vy) ** 0.5)
    b_center_waist = (
        back_top_guide[0] + vx * scale,
        back_top_guide[1] + vy * scale,
    )

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

    f_waist_c1 = _right_angle_waist_control(
        f_center_waist, f_center_hip, 2.0, +1.0
    )
    b_waist_c1 = _right_angle_waist_control(
        b_center_waist, b_center_hip, 2.0, -1.0
    )

    front_inseam = _curve(
        f_inseam_knee,
        (f_inseam_knee[0] - 0.2, y_knee - 9.0),
        (f_crotch[0] + 2.0, y_crotch + 7.0),
        f_crotch,
        "inseam_thigh",
    )
    b_crotch, back_inseam, inseam_walk = _equalize_upper_inseams(
        front_inseam,
        b_inseam_knee,
        b_crotch_base[0],
        y_crotch,
        cfg,
    )

    front_points = {
        "center_waist": f_center_waist,
        "side_waist": f_side_waist,
        "side_hip": f_side_hip,
        "side_crotch": f_side_crotch,
        "side_knee": f_side_knee,
        "side_hem": f_side_hem,
        "inseam_hem": f_inseam_hem,
        "inseam_knee": f_inseam_knee,
        "crotch_point": f_crotch,
        "center_hip": f_center_hip,
    }
    front_segments = [
        _curve(
            f_center_waist,
            f_waist_c1,
            (f_side_waist[0] - 2.0, 0.0),
            f_side_waist,
            "waist",
        ),
        _curve(
            f_side_waist,
            (f_side_waist[0] + 1.5, 4.0),
            (f_side_hip[0], y_hip - 4.0),
            f_side_hip,
            "hip_side",
        ),
        _curve(
            f_side_hip,
            (x_side, y_hip + 3.0),
            (x_side, y_crotch - 3.0),
            f_side_crotch,
            "upper_side",
        ),
        _curve(
            f_side_crotch,
            (x_side, y_crotch + 8.0),
            (f_side_knee[0], y_knee - 8.0),
            f_side_knee,
            "side_thigh",
        ),
        _line(f_side_knee, f_side_hem, "side_lower_leg"),
        _line(f_side_hem, f_inseam_hem, "hem"),
        _line(f_inseam_hem, f_inseam_knee, "inseam_lower_leg"),
        front_inseam,
        _curve(
            f_crotch,
            (f_crotch[0] + 3.0, y_crotch),
            (x_cf - 0.2, y_crotch - 3.5),
            f_center_hip,
            "front_crotch_curve",
        ),
        _line(f_center_hip, f_center_waist, "center_front"),
    ]

    back_points = {
        "center_waist": b_center_waist,
        "side_waist": b_side_waist,
        "side_hip": b_side_hip,
        "side_crotch": b_side_crotch,
        "side_knee": b_side_knee,
        "side_hem": b_side_hem,
        "inseam_hem": b_inseam_hem,
        "inseam_knee": b_inseam_knee,
        "crotch_point": b_crotch,
        "center_hip": b_center_hip,
    }
    back_segments = [
        _curve(
            b_center_waist,
            b_waist_c1,
            (b_side_waist[0] + 2.0, 0.0),
            b_side_waist,
            "waist",
        ),
        _curve(
            b_side_waist,
            (b_side_waist[0] - 1.2, 4.0),
            (b_side_hip[0], y_hip - 4.0),
            b_side_hip,
            "hip_side",
        ),
        _curve(
            b_side_hip,
            (x_side, y_hip + 3.0),
            (x_side, y_crotch - 3.0),
            b_side_crotch,
            "upper_side",
        ),
        _curve(
            b_side_crotch,
            (x_side, y_crotch + 8.0),
            (b_side_knee[0], y_knee - 8.0),
            b_side_knee,
            "side_thigh",
        ),
        _line(b_side_knee, b_side_hem, "side_lower_leg"),
        _line(b_side_hem, b_inseam_hem, "hem"),
        _line(b_inseam_hem, b_inseam_knee, "inseam_lower_leg"),
        back_inseam,
        _curve(
            b_crotch,
            (b_crotch[0] - 4.5, b_crotch[1]),
            (x_cb + 1.0, b_crotch[1] - 6.5),
            b_center_hip,
            "back_crotch_curve",
        ),
        _line(b_center_hip, b_center_waist, "center_back"),
    ]

    front_segments, back_segments, side_walk = _equalize_upper_side_seams(
        front_segments, back_segments, cfg
    )

    back_waist = next(seg for seg in back_segments if seg["name"] == "waist")
    back_dart = _dart_on_back_waist(back_waist)

    f_lengths = _named_lengths(front_segments)
    b_lengths = _named_lengths(back_segments)
    seam_walk = {
        "enabled": cfg.auto_seam_walk,
        "tolerance_cm": cfg.seam_tolerance,
        "before": {
            "upper_side_difference_cm": side_walk["back_before"] - side_walk["front_before"],
            "upper_inseam_difference_cm": inseam_walk["back_before"] - inseam_walk["front_before"],
        },
        "adjustments": {
            "front_side_bulge_cm": side_walk["front_bulge"],
            "back_side_bulge_cm": side_walk["back_bulge"],
            "back_crotch_drop_cm": inseam_walk["back_crotch_drop"],
            "back_inseam_bulge_cm": inseam_walk["back_inseam_bulge"],
        },
        "after": {
            "upper_side_difference_cm": side_walk["back_after"] - side_walk["front_after"],
            "upper_inseam_difference_cm": inseam_walk["back_after"] - inseam_walk["front_after"],
            "upper_side_residual_ease_cm": side_walk.get(
                "residual_ease_cm",
                abs(side_walk["back_after"] - side_walk["front_after"]),
            ),
        },
    }

    checks = {
        "front_lower_side": f_lengths["side_lower_leg"],
        "back_lower_side": b_lengths["side_lower_leg"],
        "front_lower_inseam": f_lengths["inseam_lower_leg"],
        "back_lower_inseam": b_lengths["inseam_lower_leg"],
        "upper_side_difference": seam_walk["after"]["upper_side_difference_cm"],
        "upper_inseam_difference": seam_walk["after"]["upper_inseam_difference_cm"],
    }

    return {
        "guides": {
            "width": width,
            "height": height,
            "y_hip": y_hip,
            "y_crotch": y_crotch,
            "y_knee": y_knee,
            "y_hem": y_hem,
            "x_split": x_side,
            "front_crease_x": f_grain_x,
            "back_crease_x": b_grain_x,
            "front_waist_width": front_waist_width,
            "back_waist_width": back_waist_width,
        },
        "points": {
            "top_left": (0.0, 0.0),
            "top_right": (width, 0.0),
            "split_top": (x_side, 0.0),
            "split_bottom": (x_side, y_hem),
            "front_crotch_point": f_crotch,
            "front_crotch_side": f_side_crotch,
            "back_crotch_point": b_crotch,
            "back_crotch_side": b_side_crotch,
            "front_hem_left": f_inseam_hem,
            "front_hem_right": f_side_hem,
            "back_hem_left": b_side_hem,
            "back_hem_right": b_inseam_hem,
        },
        "pieces": {
            "front": {
                "points": front_points,
                "segments": front_segments,
                "grain_x": f_grain_x,
                "markings": {
                    "notches": {
                        "side_knee": f_side_knee,
                        "inseam_knee": f_inseam_knee,
                    }
                },
            },
            "back": {
                "points": back_points,
                "segments": back_segments,
                "grain_x": b_grain_x,
                "markings": {
                    "dart": back_dart,
                    "notches": {
                        "side_knee": b_side_knee,
                        "inseam_knee": b_inseam_knee,
                    },
                },
            },
        },
        "seam_walk": seam_walk,
        "checks": checks,
    }
