from dataclasses import dataclass

@dataclass(frozen=True)
class Measurements:
    """Body measurements in centimetres."""
    waist: float
    hip: float
    waist_to_hip: float
    crotch_depth: float
    waist_to_knee: float
    waist_to_ankle: float

@dataclass(frozen=True)
class DraftConfig:
    hip_ease: float = 2.0
    crotch_ease: float = 1.5
    back_crotch_plus: float = 3.0
    front_waist_plus: float = 1.5
    back_waist_plus: float = 0.5
    hem_circ: float = 46.0
    auto_seam_walk: bool = True
    seam_tolerance: float = 0.02
    max_back_crotch_drop: float = 2.0
    max_side_bulge: float = 4.0
