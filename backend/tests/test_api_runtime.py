from fastapi.testclient import TestClient

from app.main import app


CLIENT = TestClient(app)

DEFAULT_PAYLOAD = {
    "project_name": "Municipal WWTP Design",
    "wastewater_type": "municipal",
    "average_flow_m3_day": 10000,
    "peak_flow_m3_day": 25000,
    "influent_bod_mg_l": 250,
    "influent_cod_mg_l": 500,
    "influent_tss_mg_l": 300,
    "ammonia_mg_l": 30,
    "target_bod_mg_l": 20,
    "target_tss_mg_l": 10,
    "nitrification_required": True,
}


def test_design_endpoint_returns_complete_response():
    response = CLIENT.post("/api/design", json=DEFAULT_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert "treatment_train" in body
    assert "hydraulic_profile" in body
    assert "mass_balance" in body
    assert "engineering_checks" in body
    assert "equipment_schedule" in body


def test_frontend_preflight_is_accepted_on_any_local_dev_port():
    response = CLIENT.options(
        "/api/design",
        headers={
            "Origin": "http://localhost:5174",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5174"


def test_design_handles_zero_oxygen_duty_without_crashing():
    payload = {**DEFAULT_PAYLOAD, "target_bod_mg_l": 175, "nitrification_required": False}
    response = CLIENT.post("/api/design", json=payload)
    assert response.status_code == 200
    assert response.json()["utilities"]["blowers"]["required_air_m3_day"] == 0.0
