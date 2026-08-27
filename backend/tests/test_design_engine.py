import pytest

from app.calculations.design_engine import (
    generate_wwtp_design,
    calculate_load_kg_day,
    calculate_peak_factor,
)


def test_bod_load():

    load = calculate_load_kg_day(
        flow_m3_day=10000,
        concentration_mg_l=250,
    )

    assert load == pytest.approx(2500)


def test_peak_factor():

    factor = calculate_peak_factor(
        average_flow_m3_day=10000,
        peak_flow_m3_day=25000,
    )

    assert factor == pytest.approx(2.5)


def test_complete_wwtp_design():

    result = generate_wwtp_design(
        project_name="Demo Municipal WWTP",
        wastewater_type="municipal",
        average_flow_m3_day=10000,
        peak_flow_m3_day=25000,
        influent_bod_mg_l=250,
        influent_cod_mg_l=500,
        influent_tss_mg_l=300,
        ammonia_mg_l=25,
        target_bod_mg_l=20,
        target_tss_mg_l=10,
        nitrification_required=True,
    )

    assert result.project_name == "Demo Municipal WWTP"

    assert result.peak_factor == pytest.approx(2.5)

    assert result.treatment_level == (
        "Secondary + Tertiary Treatment"
    )

    assert result.biological_process == (
        "Activated Sludge with Nitrification"
    )

    assert "Screening" in result.process_flow

    assert "Disinfection" in result.process_flow

    assert len(result.pollutant_loads) == 4


def test_invalid_peak_flow():

    with pytest.raises(ValueError):

        generate_wwtp_design(
            project_name="Invalid",
            wastewater_type="municipal",
            average_flow_m3_day=10000,
            peak_flow_m3_day=5000,
            influent_bod_mg_l=250,
            influent_cod_mg_l=500,
            influent_tss_mg_l=300,
            ammonia_mg_l=25,
        )