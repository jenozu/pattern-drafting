import pytest
from drafting import draft_basic_pants_block
from geometry import distance
from measurements import DraftConfig, Measurements

def sample():
    return Measurements(74, 96, 20, 26, 60, 104)

def draft():
    return draft_basic_pants_block(sample(), DraftConfig(hem_circ=46))

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

def test_back_dart_is_two_by_ten_cm():
    dart = draft()["pieces"]["back"]["markings"]["dart"]
    assert dart["right"][0] - dart["left"][0] == pytest.approx(2.0)
    assert dart["tip"][1] - dart["left"][1] == pytest.approx(10.0)
