import pytest

from app.calculations.digestion import (
    design_anaerobic_digestion,
)


def test_digestion():

    result = design_anaerobic_digestion(
        sludge_flow_m3_day=25,
        solids_concentration_percent=4,
        volatile_solids_fraction=0.70,
        destruction_fraction=0.50,
        gas_yield_m3_kg_vs_destroyed=0.8,
        methane_fraction=0.65,
        digestion_srt_days=20,
    )

    total_solids = 25 * 1000 * 0.04
    vs = total_solids * 0.70
    destroyed = vs * 0.50

    assert result.volatile_solids_kg_day == pytest.approx(vs)

    assert result.volatile_solids_destroyed_kg_day == pytest.approx(
        destroyed
    )

    assert result.biogas_production_m3_day == pytest.approx(
        destroyed * 0.8
    )

    assert result.methane_production_m3_day == pytest.approx(
        destroyed * 0.8 * 0.65
    )

    assert result.digester_volume_m3 == pytest.approx(
        25 * 20
    )


def test_invalid_srt():

    with pytest.raises(ValueError):

        design_anaerobic_digestion(
            sludge_flow_m3_day=25,
            solids_concentration_percent=4,
            volatile_solids_fraction=0.70,
            destruction_fraction=0.50,
            gas_yield_m3_kg_vs_destroyed=0.8,
            methane_fraction=0.65,
            digestion_srt_days=0,
        )