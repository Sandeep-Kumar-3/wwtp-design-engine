import pytest

from app.calculations.thickening import (
    design_thickening,
)


def test_thickening():

    result = design_thickening(
        sludge_flow_m3_day=100,
        influent_solids_concentration_percent=1,
        target_solids_concentration_percent=4,
    )

    assert result.influent_solids_kg_day == pytest.approx(
        1000
    )

    assert result.thickened_sludge_flow_m3_day == pytest.approx(
        25
    )

    assert result.water_removed_m3_day == pytest.approx(
        75
    )


def test_invalid_target():

    with pytest.raises(ValueError):

        design_thickening(
            sludge_flow_m3_day=100,
            influent_solids_concentration_percent=4,
            target_solids_concentration_percent=2,
        )