import pytest
from drafting import draft_basic_pants_block
from geometry import distance
from measurements import DraftConfig, Measurements

def sample():
    return Measurements(74, 96, 20, 26, 60, 104)

def test_recovered_reference_formulas():
    draft = draft_basic_pants_block(sample(), DraftConfig(hem_circ=46))
    assert draft["guides"]["width"] == pytest.approx(50.0)
    assert draft["guides"]["y_crotch"] == pytest.approx(27.5)
    assert draft["points"]["front_crotch_point"][0] == pytest.approx(19.0)
    assert draft["points"]["back_crotch_point"][0] == pytest.approx(34.0)

@pytest.mark.parametrize("piece_name", ["front", "back"])
def test_outline_segments_are_continuous_and_closed(piece_name):
    piece = draft_basic_pants_block(sample(), DraftConfig(hem_circ=46))["pieces"][piece_name]
    segments = piece["segments"]
    for current, nxt in zip(segments, segments[1:]):
        assert distance(current["end"], nxt["start"]) < 1e-9, (
            f"{piece_name}: {current['name']} does not meet {nxt['name']}"
        )
    assert distance(segments[-1]["end"], segments[0]["start"]) < 1e-9

def test_front_crotch_and_inseam_use_same_junction():
    front = draft_basic_pants_block(sample(), DraftConfig(hem_circ=46))["pieces"]["front"]
    inseam = next(s for s in front["segments"] if s["name"] == "inseam_thigh")
    crotch = next(s for s in front["segments"] if s["name"] == "front_crotch_curve")
    assert inseam["end"] == crotch["start"] == front["points"]["crotch_point"]
