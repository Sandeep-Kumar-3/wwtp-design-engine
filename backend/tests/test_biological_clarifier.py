import pytest

from app.calculations.biological import (
    design_biological_treatment,
)

from app.calculations.clarifier import (
    design_secondary_clarifier,
)


def test_biological_design():

    result = design_biological_treatment(
        design_flow_m3_day=10000,
        influent_bod_mg_l=250,
        effluent_bod_mg_l=20,
    )

    assert result.bod_load_kg_day == pytest.approx(2500)

    assert result.bod_removed_kg_day == pytest.approx(2300)

    assert result.aeration_volume_m3 > 0

    assert result.oxygen_requirement_kg_o2_day > 0

    assert result.air_requirement_m3_day > 0


def test_biological_invalid_flow():

    with pytest.raises(ValueError):

        design_biological_treatment(
            design_flow_m3_day=0,
            influent_bod_mg_l=250,
        )


def test_clarifier_design():

    result = design_secondary_clarifier(
        design_flow_m3_day=10000,
        surface_overflow_rate_m3_m2_day=25,
        number_of_clarifiers=2,
    )

    assert result.required_surface_area_m2 == pytest.approx(400)

    assert result.area_per_clarifier_m2 == pytest.approx(200)

    assert result.diameter_per_clarifier_m > 0

    assert result.total_volume_m3 > 0

    assert result.hydraulic_retention_time_hr > 0


def test_clarifier_invalid_flow():

    with pytest.raises(ValueError):

        design_secondary_clarifier(
            design_flow_m3_day=0
        )