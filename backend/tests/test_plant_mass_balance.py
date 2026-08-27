import pytest

from app.calculations.plant_mass_balance import calculate_plant_mass_balance


def test_plant_mass_balance_conserves_flow_load_relationship():
    result = calculate_plant_mass_balance(
        flow_m3_day=10000,
        influent_bod_mg_l=250,
        influent_cod_mg_l=500,
        influent_tss_mg_l=300,
        target_bod_mg_l=20,
        target_tss_mg_l=10,
    )

    bod = result.parameters["BOD"]
    assert bod.influent_load_kg_day == pytest.approx(2500)
    assert bod.final_concentration_mg_l == pytest.approx(20)
    assert bod.final_load_kg_day == pytest.approx(200)
    assert bod.overall_removal_percent == pytest.approx(92)


def test_tss_balance_reaches_target():
    result = calculate_plant_mass_balance(
        flow_m3_day=10000,
        influent_bod_mg_l=250,
        influent_cod_mg_l=500,
        influent_tss_mg_l=300,
        target_bod_mg_l=20,
        target_tss_mg_l=10,
    )
    tss = result.parameters["TSS"]
    assert tss.final_concentration_mg_l == pytest.approx(10)
    assert tss.final_load_kg_day == pytest.approx(100)


def test_invalid_flow_is_rejected():
    with pytest.raises(ValueError):
        calculate_plant_mass_balance(0, 250, 500, 300, 20, 10)
