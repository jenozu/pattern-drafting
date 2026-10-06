import pytest

from drafting import draft_basic_pants_block
from measurements import DraftConfig, Measurements

@pytest.mark.parametrize(
    "m",
    [
        Measurements(0, 96, 20, 26, 60, 104),
        Measurements(74, -1, 20, 26, 60, 104),
        Measurements(74, 96, 30, 26, 60, 104),
        Measurements(74, 96, 20, 55, 50, 104),
        Measurements(74, 96, 20, 26, 110, 104),
    ],
)
def test_invalid_measurements_raise_clear_error(m):
    with pytest.raises(ValueError):
        draft_basic_pants_block(m, DraftConfig())

def test_invalid_hem_raises():
    with pytest.raises(ValueError):
        draft_basic_pants_block(
            Measurements(74, 96, 20, 26, 60, 104),
            DraftConfig(hem_circ=2.0),
        )
