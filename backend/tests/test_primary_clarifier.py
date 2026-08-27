import math
import pytest

from app.calculations.primary_clarifier import (
    design_primary_clarifier,
)


def test_primary_clarifier_design():

    result = design_primary_clarifier(
        average_flow_m3_day=10000,
        peak_flow_m3_day=25000,
        number_of_units=2,
        surface_overflow_rate_m3_m2_day=30,
        detention_time_h=2.0,
        weir_loading_m3_m_day=250,
    )

    expected_area = 10000 / 30

    assert result.required_area_m2 == pytest.approx(
        expected_area
    )

    assert result.area_per_unit_m2 == pytest.approx(
        expected_area / 2
    )

    expected_diameter = math.sqrt(
        4 * (expected_area / 2) / math.pi
    )

    assert result.diameter_m == pytest.approx(
        expected_diameter
    )

    expected_volume = (
        10000 * 2 / 24
    )

    assert result.total_volume_m3 == pytest.approx(
        expected_volume
    )

    assert result.volume_per_unit_m3 == pytest.approx(
        expected_volume / 2
    )

    expected_depth = (
        (expected_volume / 2)
        / (expected_area / 2)
    )

    assert result.water_depth_m == pytest.approx(
        expected_depth
    )

    assert result.total_weir_length_m == pytest.approx(
        10000 / 250
    )


def test_invalid_primary_clarifier_flow():

    with pytest.raises(ValueError):

        design_primary_clarifier(
            average_flow_m3_day=0,
            peak_flow_m3_day=25000,
            number_of_units=2,
            surface_overflow_rate_m3_m2_day=30,
            detention_time_h=2.0,
            weir_loading_m3_m_day=250,
        )