import pytest

from app.calculations.energy import calculate_energy
from app.calculations.chemicals import design_chemicals
from app.calculations.hydraulic_profile import (
    create_hydraulic_profile,
)
from app.calculations.equipment_schedule import (
    generate_equipment_schedule,
)


def test_energy():

    result = calculate_energy(
        average_flow_m3_day=10000,
        aeration_power_kw=100,
        pumping_power_kw=30,
        uv_power_kw=10,
    )

    assert result.total_power_kw == pytest.approx(140)
    assert result.daily_energy_kwh == pytest.approx(3360)
    assert result.annual_energy_kwh > 0
    assert result.specific_energy_kwh_m3 > 0


def test_chemicals():

    result = design_chemicals(
        flow_m3_day=10000,
        chlorine_dose_mg_l=5,
    )

    assert result.chlorine_required_kg_day == pytest.approx(50)
    assert result.chlorine_annual_kg == pytest.approx(18250)


def test_hydraulic_profile():

    result = create_hydraulic_profile()

    assert len(result.units) == 9
    assert result.total_headloss_m > 0
    assert result.final_water_level_m < 100


def test_equipment_schedule():

    result = generate_equipment_schedule()

    assert len(result) == 8
    assert result[0].equipment == "Mechanical Screen"


def test_invalid_energy():

    with pytest.raises(ValueError):
        calculate_energy(
            average_flow_m3_day=10000,
            aeration_power_kw=-1,
        )


def test_invalid_chemical():

    with pytest.raises(ValueError):
        design_chemicals(
            flow_m3_day=10000,
            chlorine_dose_mg_l=-5,
        )