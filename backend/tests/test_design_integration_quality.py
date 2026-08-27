import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.design_service import generate_design
from app.schemas.project import ProjectInput


CLIENT = TestClient(app)


BASE = {
    "project_name": "Integrated Municipal WWTP",
    "wastewater_type": "municipal",
    "average_flow_m3_day": 10000,
    "peak_flow_m3_day": 25000,
    "influent_bod_mg_l": 250,
    "influent_cod_mg_l": 500,
    "influent_tss_mg_l": 300,
    "target_bod_mg_l": 20,
    "target_tss_mg_l": 10,
    "ammonia_mg_l": 30,
    "nitrification_required": True,
}


def test_api_health_and_design_endpoint():
    assert CLIENT.get("/health").json() == {"status": "healthy"}
    response = CLIENT.post("/api/design", json=BASE)
    assert response.status_code == 200
    payload = response.json()
    assert payload["metadata"]["version"] == "1.2.0"
    assert payload["metadata"]["status"] == "preliminary engineering design"


def test_bod_is_not_double_counted_after_primary_treatment():
    result = generate_design(ProjectInput(**BASE))
    primary = result["primary_treatment"]
    biological = result["biological_treatment"]["biological"]

    assert biological["influent_bod_mg_l_after_primary"] == pytest.approx(175.0)
    assert biological["bod_load_kg_day"] == pytest.approx(1750.0)
    assert primary["bod_removed_kg_day"] + biological["bod_removed_kg_day"] + 200 == pytest.approx(2500.0)


def test_secondary_clarifier_uses_peak_hydraulic_basis():
    result = generate_design(ProjectInput(**BASE))
    secondary = result["secondary_treatment"]
    assert secondary["peak_surface_overflow_rate_m3_m2_day"] <= 35
    assert secondary["average_flow_detention_time_hr"] > 0


def test_filter_standby_area_is_explicit():
    result = generate_design(ProjectInput(**BASE))
    filtration = result["tertiary_treatment"]["filtration"]
    assert filtration["operating_filters"] == 4
    assert filtration["area_per_operating_filter_m2"] == pytest.approx(250.0)
    assert filtration["installed_area_m2"] == pytest.approx(1250.0)


def test_equipment_schedule_matches_design_counts():
    result = generate_design(ProjectInput(**BASE))
    equipment = {item["equipment"]: item for item in result["equipment_schedule"]}
    assert equipment["Mechanical Screen"]["quantity"] == result["preliminary_treatment"]["screening"]["number_of_channels"]
    assert equipment["Pressure/Gravity Filter"]["quantity"] == result["tertiary_treatment"]["filtration"]["number_of_filters"]


def test_invalid_cross_field_design_basis_is_rejected():
    bad = dict(BASE)
    bad["peak_flow_m3_day"] = 5000
    response = CLIENT.post("/api/design", json=bad)
    assert response.status_code == 422


def test_cod_below_bod_is_rejected():
    bad = dict(BASE)
    bad["influent_cod_mg_l"] = 100
    response = CLIENT.post("/api/design", json=bad)
    assert response.status_code == 422
