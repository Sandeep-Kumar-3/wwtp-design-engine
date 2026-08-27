import pytest

from app.calculations.mass_balance import (
    calculate_mass_balance,
)


def test_primary_clarifier_bod_removal():

    result = calculate_mass_balance(
        parameter="BOD",
        influent_concentration_mg_l=250,
        flow_m3_day=10000,
        removal_efficiency_percent=30,
    )

    assert result.influent_load_kg_day == pytest.approx(2500)

    assert result.removed_load_kg_day == pytest.approx(750)

    assert result.effluent_load_kg_day == pytest.approx(1750)

    assert result.effluent_concentration_mg_l == pytest.approx(175)


def test_zero_removal():

    result = calculate_mass_balance(
        parameter="TSS",
        influent_concentration_mg_l=300,
        flow_m3_day=10000,
        removal_efficiency_percent=0,
    )

    assert result.effluent_concentration_mg_l == pytest.approx(300)


def test_complete_removal():

    result = calculate_mass_balance(
        parameter="TSS",
        influent_concentration_mg_l=300,
        flow_m3_day=10000,
        removal_efficiency_percent=100,
    )

    assert result.effluent_concentration_mg_l == pytest.approx(0)