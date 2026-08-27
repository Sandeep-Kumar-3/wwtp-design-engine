import pytest

from app.calculations.ras_was import (
    calculate_ras_was,
)


def test_ras_was():

    result = calculate_ras_was(
        average_flow_m3_day=10000,
        ras_ratio=0.30,
        reactor_volume_m3=3645.833333,
        mlss_mg_l=3000,
        srt_days=10,
        was_concentration_mg_l=10000,
    )

    assert result.ras_flow_m3_day == pytest.approx(
        3000
    )

    expected_inventory = (
        3000
        * 3645.833333
        / 1000
    )

    assert result.solids_inventory_kg == pytest.approx(
        expected_inventory
    )

    expected_wasting = (
        expected_inventory / 10
    )

    assert result.wasting_solids_kg_day == pytest.approx(
        expected_wasting
    )

    expected_was_flow = (
        expected_wasting
        * 1000
        / 10000
    )

    assert result.was_flow_m3_day == pytest.approx(
        expected_was_flow
    )


def test_invalid_srt():

    with pytest.raises(ValueError):

        calculate_ras_was(
            average_flow_m3_day=10000,
            ras_ratio=0.30,
            reactor_volume_m3=3600,
            mlss_mg_l=3000,
            srt_days=0,
            was_concentration_mg_l=10000,
        )