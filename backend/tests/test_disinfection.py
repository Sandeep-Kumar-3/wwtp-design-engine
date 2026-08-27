import pytest

from app.calculations.disinfection import (
    design_chlorination,
)


def test_chlorination():

    result = design_chlorination(
        flow_m3_day=10000,
        chlorine_dose_mg_l=5,
        contact_time_min=30,
        water_depth_m=2.0,
        tank_length_to_width_ratio=3,
    )

    assert result.chlorine_required_kg_day == pytest.approx(
        50
    )

    assert result.contact_volume_m3 == pytest.approx(
        10000 * 30 / 1440
    )

    assert result.tank_area_m2 == pytest.approx(
        result.contact_volume_m3 / 2
    )

    assert result.tank_length_m == pytest.approx(
        result.tank_width_m * 3
    )


def test_negative_dose():

    with pytest.raises(ValueError):

        design_chlorination(
            flow_m3_day=10000,
            chlorine_dose_mg_l=-5,
            contact_time_min=30,
            water_depth_m=2,
        )