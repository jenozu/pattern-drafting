from measurements import Measurements, DraftConfig

def _line(start, end, name):
    return {"type": "line", "name": name, "start": start, "end": end}

def _curve(start, c1, c2, end, name):
    return {
        "type": "cubic",
        "name": name,
        "start": start,
        "c1": c1,
        "c2": c2,
        "end": end,
    }

def draft_basic_pants_block(m: Measurements, cfg: DraftConfig):
    """Draft a testable front/back basic trouser block in centimetres.

    The recovered formulas are preserved. The missing outline layer is rebuilt
    as explicit named points and ordered semantic segments so incorrect path
    connections are easy to detect and test.
    """
    half_hip = m.hip / 2.0
    half_waist = m.waist / 2.0
    width = half_hip + cfg.hip_ease
    height = m.waist_to_ankle

    y_hip = m.waist_to_hip
    y_crotch = m.crotch_depth + cfg.crotch_ease
    y_knee = m.waist_to_knee
    y_hem = height
    x_split = width / 2.0

    extension = half_hip / 8.0
    front_crotch_extension = extension
    back_crotch_extension = extension + cfg.back_crotch_plus
    front_waist_width = (half_waist / 2.0) + cfg.front_waist_plus
    back_waist_width = (half_waist / 2.0) + cfg.back_waist_plus

    half_hem = cfg.hem_circ / 2.0
    front_hem_width = half_hem - 1.0
    back_hem_width = half_hem + 1.0

    front_crotch_side = (x_split, y_crotch)
    back_crotch_side = (x_split, y_crotch)
    front_crotch_point = (x_split - front_crotch_extension, y_crotch)
    back_crotch_point = (x_split + back_crotch_extension, y_crotch)

    front_crease_x = (front_crotch_point[0] + front_crotch_side[0]) / 2.0
    back_crease_x = x_split + (x_split - front_crease_x)

    piece_body_width = x_split

    front_crotch_point_local = (0.0, y_crotch)
    front_center_crotch = (front_crotch_extension, y_crotch)
    front_side_crotch = (piece_body_width, y_crotch)
    front_center_waist = (front_crotch_extension, 0.0)
    front_side_waist = (front_center_waist[0] + front_waist_width, 0.0)
    front_side_hip = (piece_body_width, y_hip)
    front_crease_local = (front_crotch_point_local[0] + front_side_crotch[0]) / 2.0
    front_side_knee = (front_crease_local - front_hem_width * 0.45, y_knee)
    front_inseam_knee = (front_crease_local + front_hem_width * 0.45, y_knee)
    front_side_hem = (front_crease_local - front_hem_width / 2.0, y_hem)
    front_inseam_hem = (front_crease_local + front_hem_width / 2.0, y_hem)

    front_points = {
        "center_waist": front_center_waist,
        "side_waist": front_side_waist,
        "side_hip": front_side_hip,
        "side_crotch": front_side_crotch,
        "side_knee": front_side_knee,
        "side_hem": front_side_hem,
        "inseam_hem": front_inseam_hem,
        "inseam_knee": front_inseam_knee,
        "crotch_point": front_crotch_point_local,
        "center_crotch": front_center_crotch,
    }

    front_segments = [
        _line(front_center_waist, front_side_waist, "waist"),
        _curve(front_side_waist, (front_side_waist[0] + 1.2, y_hip * 0.30), (piece_body_width, y_hip * 0.72), front_side_hip, "upper_side"),
        _curve(front_side_hip, (piece_body_width, y_hip + (y_crotch-y_hip)*0.40), (piece_body_width, y_crotch - 1.0), front_side_crotch, "lower_side"),
        _curve(front_side_crotch, (front_side_crotch[0], y_crotch + 5.0), (front_side_knee[0], y_knee - 7.0), front_side_knee, "side_thigh"),
        _line(front_side_knee, front_side_hem, "side_lower_leg"),
        _line(front_side_hem, front_inseam_hem, "hem"),
        _line(front_inseam_hem, front_inseam_knee, "inseam_lower_leg"),
        _curve(front_inseam_knee, (front_inseam_knee[0], y_knee - 7.0), (front_crotch_point_local[0] + 1.0, y_crotch + 5.0), front_crotch_point_local, "inseam_thigh"),
        _curve(front_crotch_point_local, (1.8, y_crotch), (front_center_crotch[0] - 1.0, y_crotch - 4.0), front_center_crotch, "front_crotch_curve"),
        _curve(front_center_crotch, (front_center_crotch[0], y_hip * 0.62), (front_center_waist[0], y_hip * 0.18), front_center_waist, "center_front"),
    ]

    back_crotch_point_local = (0.0, y_crotch)
    back_center_crotch = (back_crotch_extension, y_crotch)
    back_side_crotch = (piece_body_width, y_crotch)
    back_center_waist = (back_crotch_extension, 0.0)
    back_side_waist = (back_center_waist[0] + back_waist_width, 0.0)
    back_side_hip = (piece_body_width + 1.0, y_hip)
    back_crease_local = (back_crotch_point_local[0] + back_side_crotch[0]) / 2.0
    back_side_knee = (back_crease_local - back_hem_width * 0.45, y_knee)
    back_inseam_knee = (back_crease_local + back_hem_width * 0.45, y_knee)
    back_side_hem = (back_crease_local - back_hem_width / 2.0, y_hem)
    back_inseam_hem = (back_crease_local + back_hem_width / 2.0, y_hem)

    back_points = {
        "center_waist": back_center_waist,
        "side_waist": back_side_waist,
        "side_hip": back_side_hip,
        "side_crotch": back_side_crotch,
        "side_knee": back_side_knee,
        "side_hem": back_side_hem,
        "inseam_hem": back_inseam_hem,
        "inseam_knee": back_inseam_knee,
        "crotch_point": back_crotch_point_local,
        "center_crotch": back_center_crotch,
    }

    back_segments = [
        _line(back_center_waist, back_side_waist, "waist"),
        _curve(back_side_waist, (back_side_waist[0] + 1.4, y_hip * 0.25), (back_side_hip[0], y_hip * 0.72), back_side_hip, "upper_side"),
        _curve(back_side_hip, (back_side_hip[0], y_hip + (y_crotch-y_hip)*0.40), (back_side_crotch[0], y_crotch - 1.0), back_side_crotch, "lower_side"),
        _curve(back_side_crotch, (back_side_crotch[0], y_crotch + 5.0), (back_side_knee[0], y_knee - 7.0), back_side_knee, "side_thigh"),
        _line(back_side_knee, back_side_hem, "side_lower_leg"),
        _line(back_side_hem, back_inseam_hem, "hem"),
        _line(back_inseam_hem, back_inseam_knee, "inseam_lower_leg"),
        _curve(back_inseam_knee, (back_inseam_knee[0], y_knee - 7.0), (back_crotch_point_local[0] + 1.2, y_crotch + 5.5), back_crotch_point_local, "inseam_thigh"),
        _curve(back_crotch_point_local, (2.8, y_crotch), (back_center_crotch[0] - 1.5, y_crotch - 6.0), back_center_crotch, "back_crotch_curve"),
        _curve(back_center_crotch, (back_center_crotch[0], y_hip * 0.58), (back_center_waist[0], y_hip * 0.12), back_center_waist, "center_back"),
    ]

    return {
        "guides": {
            "width": width, "height": height, "y_hip": y_hip,
            "y_crotch": y_crotch, "y_knee": y_knee, "y_hem": y_hem,
            "x_split": x_split, "front_crease_x": front_crease_x,
            "back_crease_x": back_crease_x,
            "front_waist_width": front_waist_width,
            "back_waist_width": back_waist_width,
        },
        "points": {
            "top_left": (0.0, 0.0), "top_right": (width, 0.0),
            "split_top": (x_split, 0.0), "split_bottom": (x_split, y_hem),
            "front_crotch_point": front_crotch_point,
            "front_crotch_side": front_crotch_side,
            "back_crotch_point": back_crotch_point,
            "back_crotch_side": back_crotch_side,
            "front_hem_left": (front_crease_x - front_hem_width / 2.0, y_hem),
            "front_hem_right": (front_crease_x + front_hem_width / 2.0, y_hem),
            "back_hem_left": (back_crease_x - back_hem_width / 2.0, y_hem),
            "back_hem_right": (back_crease_x + back_hem_width / 2.0, y_hem),
        },
        "pieces": {
            "front": {"points": front_points, "segments": front_segments},
            "back": {"points": back_points, "segments": back_segments},
        },
    }
