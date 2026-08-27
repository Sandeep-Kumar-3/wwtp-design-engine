import pytest
from app.schemas.project import ProjectInput
from app.services.design_service import generate_design


def make_project(**overrides):
    data = dict(
        project_name="Engineering Checks Test",
        wastewater_type="municipal",
        average_flow_m3_day=10000,
        peak_flow_m3_day=25000,
        influent_bod_mg_l=250,
        influent_cod_mg_l=500,
        influent_tss_mg_l=300,
        ammonia_mg_l=30,
        target_bod_mg_l=20,
        target_tss_mg_l=10,
        nitrification_required=True,
    )
    data.update(overrides)
    return ProjectInput(**data)


def test_design_returns_criteria_and_engineering_checks():
    result = generate_design(make_project())

    assert result["metadata"]["version"] == "1.2.0"
    assert result["design_criteria"]["biological_process"]["mlss_mg_l"] == 3000
    checks = result["engineering_checks"]
    assert checks["total_checks"] >= 8
    assert checks["pass_count"] + checks["review_count"] == checks["total_checks"]


def test_municipal_criteria_drive_biological_design():
    result = generate_design(make_project())
    biological = result["biological_treatment"]["biological"]

    assert biological["mlss_mg_l"] == 3000
    assert biological["f_m_ratio_kg_bod_kg_mlvss_day"] == 0.20


def test_industrial_criteria_change_design_parameters():
    result = generate_design(make_project(wastewater_type="industrial"))
    biological = result["biological_treatment"]["biological"]
    secondary = result["secondary_treatment"]

    assert biological["mlss_mg_l"] == 3500
    assert biological["f_m_ratio_kg_bod_kg_mlvss_day"] == 0.15
    assert secondary["surface_overflow_rate_m3_m2_day"] == 20


def test_design_exposes_plant_wide_mass_balance():
    result = generate_design(make_project())
    balance = result["plant_mass_balance"]

    assert balance["flow_m3_day"] == 10000
    assert set(balance["parameters"]) == {"BOD", "TSS", "COD"}
    assert balance["parameters"]["BOD"]["final_concentration_mg_l"] == pytest.approx(20)
    assert balance["parameters"]["TSS"]["final_concentration_mg_l"] == pytest.approx(10)
    assert len(balance["assumptions"]) >= 4
