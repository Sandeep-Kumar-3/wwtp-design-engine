import pytest

from app.calculations.aeration import design_aeration
from app.calculations.blower import design_blowers
from app.calculations.pumps import design_pumps


def test_aeration():

    result = design_aeration(
        average_flow_m3_day=10000,
        influent_bod_mg_l=250,
        target_bod_mg_l=20,
        ammonia_mg_l=25,
        nitrification_required=True,
    )

    assert result.bod_load_kg_day == pytest.approx(2500)
    assert result.bod_removed_kg_day > 0
    assert result.oxygen_for_bod_kg_day > 0
    assert result.oxygen_for_nitrification_kg_day > 0
    assert result.design_oxygen_demand_kg_day > 0
    assert result.aeration_tank_volume_m3 > 0


def test_aeration_without_nitrification():

    result = design_aeration(
        average_flow_m3_day=10000,
        influent_bod_mg_l=250,
        nitrification_required=False,
    )

    assert result.oxygen_for_nitrification_kg_day == 0


def test_blowers():

    result = design_blowers(
        oxygen_demand_kg_day=4000
    )

    assert result.required_air_kg_day > 0
    assert result.required_air_m3_day > 0
    assert result.required_air_m3_min > 0
    assert result.blower_capacity_m3_min > 0
    assert result.estimated_power_kw > 0
    assert result.standby_blowers == 1


def test_pumps():

    result = design_pumps(
        flow_m3_day=10000
    )

    assert result.total_dynamic_head_m == pytest.approx(9)
    assert result.required_power_kw > 0
    assert result.capacity_per_pump_m3_day > 0
    assert result.standby_pumps == 1


def test_invalid_aeration_flow():

    with pytest.raises(ValueError):
        design_aeration(
            average_flow_m3_day=0,
            influent_bod_mg_l=250,
        )


def test_invalid_pump_efficiency():

    with pytest.raises(ValueError):
        design_pumps(
            flow_m3_day=10000,
            pump_efficiency=1.5,
        )