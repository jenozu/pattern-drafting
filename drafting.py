from measurements import Measurements, DraftConfig

def draft_basic_pants_block(m: Measurements, cfg: DraftConfig):
    """Recovered latest-known drafting scaffold. See PROJECT_STATUS.md."""
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
    }
