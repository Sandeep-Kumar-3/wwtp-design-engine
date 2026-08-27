import pytest

from app.calculations.activated_sludge import (
    design_activated_sludge,
)


def test_activated_sludge_design():

    result = design_activated_sludge(
        flow_m3_day=10000,

        influent_bod_mg_l=175,
        effluent_bod_mg_l=20,

        mlss_mg_l=3000,
        mlvss_to_mlss_ratio=0.80,

        fm_ratio=0.20,
        srt_days=10,

        biomass_yield_kg_kg_bod=0.50,
        endogenous_decay_rate_per_day=0.06,

        nitrification_required=False,

        aeration_efficiency_kg_o2_per_kg_air=0.03,
        blower_efficiency=0.65,
        air_pressure_kpa=100,
    )

    # BOD load

    assert result.influent_bod_load_kg_day == pytest.approx(
        1750
    )

    assert result.effluent_bod_load_kg_day == pytest.approx(
        200
    )

    assert result.bod_removed_kg_day == pytest.approx(
        1550
    )

    # MLVSS

    assert result.mlvss_mg_l == pytest.approx(
        2400
    )

    # Reactor volume

    expected_volume = (
        1750
        / (0.20 * 2.4)
    )

    assert result.reactor_volume_m3 == pytest.approx(
        expected_volume
    )

    # HRT

    assert result.hrt_hours == pytest.approx(
        expected_volume / 10000 * 24
    )

    # Biomass

    assert result.biomass_inventory_kg == pytest.approx(
        expected_volume * 2.4
    )

    # Oxygen should be positive

    assert result.total_oxygen_requirement_kg_day > 0

    # Air should be positive

    assert result.air_requirement_kg_day > 0

    # Blower power should be positive

    assert result.blower_power_kw > 0


def test_nitrification_adds_oxygen_requirement():

    without_nitrification = design_activated_sludge(
        flow_m3_day=10000,
        influent_bod_mg_l=175,
        effluent_bod_mg_l=20,
        mlss_mg_l=3000,
        mlvss_to_mlss_ratio=0.80,
        fm_ratio=0.20,
        srt_days=10,
        biomass_yield_kg_kg_bod=0.50,
        endogenous_decay_rate_per_day=0.06,
        nitrification_required=False,
    )

    with_nitrification = design_activated_sludge(
        flow_m3_day=10000,
        influent_bod_mg_l=175,
        effluent_bod_mg_l=20,
        mlss_mg_l=3000,
        mlvss_to_mlss_ratio=0.80,
        fm_ratio=0.20,
        srt_days=10,
        biomass_yield_kg_kg_bod=0.50,
        endogenous_decay_rate_per_day=0.06,
        nitrification_required=True,
        ammonia_removed_mg_l=20,
    )

    assert (
        with_nitrification.total_oxygen_requirement_kg_day
        >
        without_nitrification.total_oxygen_requirement_kg_day
    )


def test_invalid_fm_ratio():

    with pytest.raises(ValueError):

        design_activated_sludge(
            flow_m3_day=10000,
            influent_bod_mg_l=175,
            effluent_bod_mg_l=20,
            mlss_mg_l=3000,
            mlvss_to_mlss_ratio=0.80,
            fm_ratio=0,
            srt_days=10,
            biomass_yield_kg_kg_bod=0.50,
            endogenous_decay_rate_per_day=0.06,
        )