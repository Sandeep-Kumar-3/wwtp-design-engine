import math
import pytest

from app.calculations.secondary_clarifier import (
    design_secondary_clarifier,
)


def test_secondary_clarifier_design():

    result = design_secondary_clarifier(
        average_flow_m3_day=10000,
        peak_flow_m3_day=25000,

        mlss_mg_l=3000,
        ras_flow_m3_day=3000,

        number_of_units=2,

        surface_overflow_rate_m3_m2_day=25,
        solids_loading_rate_kg_m2_day=100,

        water_depth_m=3.5,
        weir_loading_m3_m_day=250,
    )

    expected_hydraulic_area = 25000 / 25

    assert result.hydraulic_area_m2 == pytest.approx(
        expected_hydraulic_area
    )

    solids_load = (
        3000 / 1000
        * (10000 + 3000)
    )

    expected_solids_area = solids_load / 100

    assert result.solids_area_m2 == pytest.approx(
        expected_solids_area
    )

    expected_area = max(
        expected_hydraulic_area,
        expected_solids_area,
    )

    assert result.required_area_m2 == pytest.approx(
        expected_area
    )

    expected_area_per_unit = expected_area / 2

    assert result.area_per_unit_m2 == pytest.approx(
        expected_area_per_unit
    )

    expected_diameter = math.sqrt(
        4 * expected_area_per_unit / math.pi
    )

    assert result.diameter_m == pytest.approx(
        expected_diameter
    )

    assert result.total_volume_m3 == pytest.approx(
        expected_area * 3.5
    )


def test_invalid_mlss():

    with pytest.raises(ValueError):

        design_secondary_clarifier(
            average_flow_m3_day=10000,
            peak_flow_m3_day=25000,
            mlss_mg_l=0,
            ras_flow_m3_day=3000,
            number_of_units=2,
            surface_overflow_rate_m3_m2_day=25,
            solids_loading_rate_kg_m2_day=100,
            water_depth_m=3.5,
            weir_loading_m3_m_day=250,
        )