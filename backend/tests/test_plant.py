import pytest

from app.calculations.plant import (
    calculate_design_basis,
)


def test_integrated_10_mld_plant():

    result = calculate_design_basis(
        average_flow_mld=10,
        peak_factor=2.5,
        bod_mg_l=250,
        cod_mg_l=500,
        tss_mg_l=300,
    )

    # Flow
    assert result.flow.average_m3_day == pytest.approx(10000)
    assert result.flow.peak_m3_day == pytest.approx(25000)

    # Loads
    assert result.loads.bod.load_kg_day == pytest.approx(2500)
    assert result.loads.cod.load_kg_day == pytest.approx(5000)
    assert result.loads.tss.load_kg_day == pytest.approx(3000)

    # Primary treatment
    assert (
        result.primary_treatment["bod"].effluent_concentration_mg_l
        == pytest.approx(175)
    )

    assert (
        result.primary_treatment["tss"].effluent_concentration_mg_l
        == pytest.approx(120)
    )