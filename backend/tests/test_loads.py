import pytest

from app.calculations.loads import (
    calculate_load,
    calculate_wastewater_loads,
)


def test_bod_load():

    result = calculate_load(
        concentration_mg_l=250,
        flow_m3_day=10000,
    )

    assert result == pytest.approx(2500)


def test_multiple_pollutant_loads():

    result = calculate_wastewater_loads(
        flow_m3_day=10000,
        bod=250,
        cod=500,
        tss=300,
        tn=40,
        nh4_n=30,
        tp=6,
    )

    assert result.bod.load_kg_day == pytest.approx(2500)
    assert result.cod.load_kg_day == pytest.approx(5000)
    assert result.tss.load_kg_day == pytest.approx(3000)
    assert result.tn.load_kg_day == pytest.approx(400)
    assert result.nh4_n.load_kg_day == pytest.approx(300)
    assert result.tp.load_kg_day == pytest.approx(60)


def test_negative_concentration_rejected():

    with pytest.raises(ValueError):
        calculate_load(
            concentration_mg_l=-10,
            flow_m3_day=10000,
        )


def test_zero_flow_rejected():

    with pytest.raises(ValueError):
        calculate_load(
            concentration_mg_l=250,
            flow_m3_day=0,
        )