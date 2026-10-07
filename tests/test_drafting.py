import pytest

from drafting import draft_basic_pants_block
from geometry import distance, outline_self_intersections, segment_length
from measurements import DraftConfig, Measurements

PROFILES = [
    Measurements(64, 88, 18, 25, 56, 100),
    Measurements(74, 96, 20, 26, 60, 104),
    Measurements(88, 110, 22, 30, 64, 108),
    Measurements(80, 102, 21, 29, 67, 115),
]

def sample():
    return Measurements(74, 96, 20, 26, 60, 104)

def draft(m=None, cfg=None):
    return draft_basic_pants_block(
        m or sample(),
        cfg or DraftConfig(hem_circ=46),
    )

def test_reference_formulas():
    d = draft()
    assert d["guides"]["width"] == pytest.approx(50.0)
    assert d["guides"]["y_crotch"] == pytest.approx(27.5)
    assert d["points"]["front_crotch_point"][0] == pytest.approx(-6.0)
    assert d["points"]["back_crotch_point"][0] == pytest.approx(59.0)
    assert d["guides"]["front_crease_x"] == pytest.approx(9.5)
    assert d["guides"]["back_crease_x"] == pytest.approx(40.5)

@pytest.mark.parametrize("piece_name", ["front", "back"])
def test_outline_segments_are_continuous_and_closed(piece_name):
    segs = draft()["pieces"][piece_name]["segments"]
    for a, b in zip(segs, segs[1:]):
        assert distance(a["end"], b["start"]) < 1e-9
    assert distance(segs[-1]["end"], segs[0]["start"]) < 1e-9

@pytest.mark.parametrize("m", PROFILES)
@pytest.mark.parametrize("piece_name", ["front", "back"])
def test_outlines_do_not_self_intersect(m, piece_name):
    d = draft(m, DraftConfig(hem_circ=46 if m.hip <= 102 else 50))
    hits = outline_self_intersections(d["pieces"][piece_name]["segments"], curve_steps=32)
    assert hits == []

def test_front_knee_is_derived_from_crotch_to_hem_guide():
    p = draft()["pieces"]["front"]["points"]
    assert p["inseam_knee"][0] == pytest.approx(-3.0882352941)
    assert p["side_knee"][0] == pytest.approx(22.0882352941)

def test_back_knee_adds_one_cm_each_side_over_front():
    d = draft()
    fg = d["pieces"]["front"]["grain_x"]
    bg = d["pieces"]["back"]["grain_x"]
    fp = d["pieces"]["front"]["points"]
    bp = d["pieces"]["back"]["points"]
    assert (bg - bp["side_knee"][0]) == pytest.approx((fp["side_knee"][0] - fg) + 1.0)

def test_lower_leg_seams_match_front_to_back():
    c = draft()["checks"]
    assert c["front_lower_side"] == pytest.approx(c["back_lower_side"])
    assert c["front_lower_inseam"] == pytest.approx(c["back_lower_inseam"])

@pytest.mark.parametrize("m", PROFILES)
def test_automatic_seam_walk_equalizes_upper_seams(m):
    hem = 42 if m.hip < 90 else 46 if m.hip <= 102 else 50
    d = draft(m, DraftConfig(hem_circ=hem))
    walk = d["seam_walk"]
    assert abs(walk["after"]["upper_side_difference_cm"]) <= 0.001
    assert abs(walk["after"]["upper_inseam_difference_cm"]) <= 0.001
    assert walk["adjustments"]["back_crotch_drop_cm"] <= 2.0
    assert walk["adjustments"]["back_side_bulge_cm"] <= 4.0

def test_seam_walk_uses_actual_inseam_not_center_crotch_curve():
    d = draft()
    before = d["seam_walk"]["before"]["upper_inseam_difference_cm"]
    assert before == pytest.approx(0.333, abs=0.01)

def test_raw_mode_preserves_unwalked_differences():
    d = draft(cfg=DraftConfig(hem_circ=46, auto_seam_walk=False))
    assert abs(d["seam_walk"]["after"]["upper_side_difference_cm"]) > 0.1
    assert abs(d["seam_walk"]["after"]["upper_inseam_difference_cm"]) > 0.1
    assert d["seam_walk"]["adjustments"]["back_crotch_drop_cm"] == 0.0

def test_back_dart_is_two_cm_wide_and_ten_cm_long():
    d = draft()
    dart = d["pieces"]["back"]["markings"]["dart"]
    assert distance(dart["left"], dart["right"]) == pytest.approx(2.0, abs=0.01)
    assert distance(dart["center"], dart["tip"]) == pytest.approx(10.0, abs=1e-9)

def test_waistlines_start_at_right_angles_to_center_seams():
    d = draft()
    for piece_name, center_name in (("front", "center_front"), ("back", "center_back")):
        segs = d["pieces"][piece_name]["segments"]
        waist = next(s for s in segs if s["name"] == "waist")
        center = next(s for s in segs if s["name"] == center_name)
        waist_tangent = (
            waist["c1"][0] - waist["start"][0],
            waist["c1"][1] - waist["start"][1],
        )
        center_tangent = (
            center["start"][0] - center["end"][0],
            center["start"][1] - center["end"][1],
        )
        dot = waist_tangent[0] * center_tangent[0] + waist_tangent[1] * center_tangent[1]
        assert dot == pytest.approx(0.0, abs=1e-8)

def test_effective_half_waist_is_close_to_body_measurement_after_dart():
    d = draft()
    front_waist = next(s for s in d["pieces"]["front"]["segments"] if s["name"] == "waist")
    back_waist = next(s for s in d["pieces"]["back"]["segments"] if s["name"] == "waist")
    effective = segment_length(front_waist) + segment_length(back_waist) - 2.0
    assert effective == pytest.approx(sample().waist / 2.0, abs=0.5)


@pytest.mark.parametrize("m", PROFILES)
@pytest.mark.parametrize("piece_name", ["front", "back"])
def test_seam_walk_keeps_hip_and_crotch_side_tangents_smooth(m, piece_name):
    hem = 42 if m.hip < 90 else 46 if m.hip <= 102 else 50
    segs = draft(m, DraftConfig(hem_circ=hem))["pieces"][piece_name]["segments"]
    by_name = {seg["name"]: seg for seg in segs}

    for incoming_name, outgoing_name in (
        ("hip_side", "upper_side"),
        ("upper_side", "side_thigh"),
    ):
        incoming = by_name[incoming_name]
        outgoing = by_name[outgoing_name]
        join = incoming["end"]
        assert outgoing["start"] == join

        incoming_tangent = (
            join[0] - incoming["c2"][0],
            join[1] - incoming["c2"][1],
        )
        outgoing_tangent = (
            outgoing["c1"][0] - join[0],
            outgoing["c1"][1] - join[1],
        )
        cross = (
            incoming_tangent[0] * outgoing_tangent[1]
            - incoming_tangent[1] * outgoing_tangent[0]
        )
        dot = (
            incoming_tangent[0] * outgoing_tangent[0]
            + incoming_tangent[1] * outgoing_tangent[1]
        )
        assert cross == pytest.approx(0.0, abs=1e-8)
        assert dot > 0
