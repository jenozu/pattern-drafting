import pytest
from drafting import draft_basic_pants_block
from measurements import DraftConfig, Measurements

def sample():
    return Measurements(74, 96, 20, 26, 60, 104)

def test_recovered_reference_formulas():
    draft = draft_basic_pants_block(sample(), DraftConfig(hem_circ=46))
    assert draft["guides"]["width"] == pytest.approx(50.0)
    assert draft["guides"]["y_crotch"] == pytest.approx(27.5)
    assert draft["points"]["front_crotch_point"][0] == pytest.approx(19.0)
    assert draft["points"]["back_crotch_point"][0] == pytest.approx(34.0)
