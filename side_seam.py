"""C2-continuous, y-parameterized upper side seams.

The silhouette is interpolated through construction landmarks, preserving
their positions. A free waist-end slope controls seam length without a
localised bulge at the hip or crotch joins.
"""
from geometry import segment_length

NAMES = ("hip_side", "upper_side", "side_thigh")


def smooth_side_segments(segments, waist_slope=None):
    """Replace three Béziers with a C2 spline through their four endpoints.

    The lower endpoint is tangent to the knee-to-hem line.
    """
    by_name = {seg["name"]: seg for seg in segments}
    original = [by_name[name] for name in NAMES]
    waist, hip, crotch, knee = (
        original[0]["start"], original[0]["end"],
        original[1]["end"], original[2]["end"],
    )
    points = (waist, hip, crotch, knee)
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    h = [b - a for a, b in zip(y, y[1:])]
    if any(step <= 0 for step in h):
        raise ValueError("Upper side-seam landmarks must increase in y")

    if waist_slope is None:
        first = original[0]
        control_dy = first["c1"][1] - first["start"][1]
        if abs(control_dy) > 1e-9:
            waist_slope = (first["c1"][0] - first["start"][0]) / control_dy
        else:
            waist_slope = (x[1] - x[0]) / h[0]

    lower = by_name["side_lower_leg"]
    lower_dx = lower["end"][0] - lower["start"][0]
    lower_dy = lower["end"][1] - lower["start"][1]
    if lower_dy <= 0:
        raise ValueError("Lower side seam must descend from knee to hem")
    knee_slope = lower_dx / lower_dy

    # C2 continuity of adjacent Hermite cubics gives a 2x2 system
    # for the unknown hip and crotch derivatives.
    rhs1 = (
        6 * (x[1] - x[0]) / h[0]**2
        + 6 * (x[2] - x[1]) / h[1]**2
        - 2 * waist_slope / h[0]
    )
    rhs2 = (
        6 * (x[2] - x[1]) / h[1]**2
        + 6 * (x[3] - x[2]) / h[2]**2
        - 2 * knee_slope / h[2]
    )
    a = 4 / h[0] + 4 / h[1]
    b = 2 / h[1]
    c = 2 / h[1]
    d = 4 / h[1] + 4 / h[2]
    determinant = a * d - b * c
    hip_slope = (rhs1 * d - b * rhs2) / determinant
    crotch_slope = (a * rhs2 - rhs1 * c) / determinant
    slopes = (waist_slope, hip_slope, crotch_slope, knee_slope)

    replacement = {}
    for i, name in enumerate(NAMES):
        span = h[i]
        replacement[name] = {
            "type": "cubic",
            "name": name,
            "start": points[i],
            "c1": (x[i] + slopes[i] * span / 3, y[i] + span / 3),
            "c2": (x[i+1] - slopes[i+1] * span / 3, y[i+1] - span / 3),
            "end": points[i+1],
        }

    return [replacement.get(seg["name"], dict(seg)) for seg in segments]


def upper_length(segments):
    return sum(segment_length(seg) for seg in segments if seg["name"] in NAMES)


def fair_and_match_side_seams(front, back, tolerance, max_adjustment=4.0):
    """Smooth both pieces, then lengthen the shorter side without moving points.

    Fits the waist-end derivative of the shorter side using a bounded search.
    Only the upper-side curves are changed, and C2 joins stay intact.
    """
    front_raw = upper_length(front)
    back_raw = upper_length(back)
    fbase = smooth_side_segments(front)
    bbase = smooth_side_segments(back)
    fl = upper_length(fbase)
    bl = upper_length(bbase)

    if abs(fl - bl) <= tolerance:
        return fbase, bbase, {
            "front_before": front_raw, "back_before": back_raw,
            "front_after": fl, "back_after": bl,
            "front_bulge": 0.0, "back_bulge": 0.0,
        }

    shorten_front = fl < bl
    source = fbase if shorten_front else bbase
    other = bbase if shorten_front else fbase
    target = upper_length(other)
    hip = next(s for s in source if s["name"] == "hip_side")
    dy = hip["end"][1] - hip["start"][1]
    control_dy = hip["c1"][1] - hip["start"][1]
    if abs(control_dy) > 1e-9:
        base_slope = (hip["c1"][0] - hip["start"][0]) / control_dy
    else:
        base_slope = (hip["end"][0] - hip["start"][0]) / dy
    outward = +1 if shorten_front else -1

    def fit(amount):
        proposed = smooth_side_segments(source, base_slope + outward * amount)
        return upper_length(proposed), proposed

    start_length, _ = fit(0)
    maximum_length, maximum_proposal = fit(max_adjustment / dy)

    if maximum_length < target - tolerance:
        # A fair curve is more important than forcing an exact seam match by
        # creating another visible bulge. Use the full, bounded adjustment and
        # report the small residual as ease to be handled during fit validation.
        result = maximum_proposal
        adjustment = max_adjustment
    else:
        lo, hi = 0.0, max_adjustment / dy
        result = source
        adjustment = 0.0
        for _ in range(60):
            mid = (lo + hi) / 2
            length, proposal = fit(mid)
            result, adjustment = proposal, mid * dy
            if abs(length - target) <= min(tolerance, 1e-5):
                break
            if length < target:
                lo = mid
            else:
                hi = mid

    if shorten_front:
        fbase = result
        front_bulge, back_bulge = adjustment, 0.0
    else:
        bbase = result
        front_bulge, back_bulge = 0.0, adjustment

    fl, bl = upper_length(fbase), upper_length(bbase)
    return fbase, bbase, {
        "front_before": front_raw, "back_before": back_raw,
        "front_after": fl, "back_after": bl,
        "front_bulge": front_bulge,
        "back_bulge": back_bulge,
        "residual_ease_cm": abs(bl - fl),
    }
