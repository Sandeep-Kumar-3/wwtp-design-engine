import pytest

from app.calculations.process_selection import (
    select_treatment_process,
)


def test_municipal_process_selection():

    result = select_treatment_process(
        wastewater_type="municipal",
        average_flow_m3_day=10000,
        influent_bod_mg_l=250,
        influent_cod_mg_l=500,
        influent_tss_mg_l=300,
        ammonia_mg_l=25,
        target_bod_mg_l=20,
        target_tss_mg_l=10,
        nitrification_required=True,
    )

    assert result.treatment_level == "Secondary + Tertiary Treatment"

    assert "Screening" in result.process_flow
    assert "Grit Removal" in result.process_flow
    assert "Primary Clarifier" in result.process_flow
    assert "Secondary Clarifier" in result.process_flow
    assert "Tertiary Filtration" in result.process_flow
    assert "Disinfection" in result.process_flow


def test_industrial_process_selection():

    result = select_treatment_process(
        wastewater_type="industrial",
        average_flow_m3_day=5000,
        influent_bod_mg_l=300,
        influent_cod_mg_l=600,
        influent_tss_mg_l=400,
        ammonia_mg_l=30,
        target_bod_mg_l=20,
        target_tss_mg_l=10,
        nitrification_required=True,
    )

    assert "Screening" in result.process_flow
    assert "Grit Removal" in result.process_flow
    assert "Equalization Tank" in result.process_flow
    assert "Primary Clarifier" in result.process_flow
    assert "Secondary Clarifier" in result.process_flow
    assert "Disinfection" in result.process_flow


def test_nitrification_selection():

    result = select_treatment_process(
        wastewater_type="municipal",
        average_flow_m3_day=10000,
        influent_bod_mg_l=250,
        influent_cod_mg_l=500,
        influent_tss_mg_l=300,
        ammonia_mg_l=25,
        nitrification_required=True,
    )

    assert result.biological_process == (
        "Activated Sludge with Nitrification"
    )


def test_invalid_flow():

    with pytest.raises(ValueError):

        select_treatment_process(
            wastewater_type="municipal",
            average_flow_m3_day=0,
            influent_bod_mg_l=250,
            influent_cod_mg_l=500,
            influent_tss_mg_l=300,
            ammonia_mg_l=25,
        )