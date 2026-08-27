from dataclasses import dataclass


@dataclass
class DigestionResult:
    volatile_solids_kg_day: float
    destruction_fraction: float

    volatile_solids_destroyed_kg_day: float
    volatile_solids_remaining_kg_day: float

    gas_yield_m3_kg_vs_destroyed: float
    biogas_production_m3_day: float

    methane_fraction: float
    methane_production_m3_day: float

    digestion_srt_days: float
    digester_volume_m3: float


def design_anaerobic_digestion(
    sludge_flow_m3_day: float,
    solids_concentration_percent: float,
    volatile_solids_fraction: float,
    destruction_fraction: float,
    gas_yield_m3_kg_vs_destroyed: float,
    methane_fraction: float,
    digestion_srt_days: float,
) -> DigestionResult:

    if sludge_flow_m3_day <= 0:
        raise ValueError("Sludge flow must be greater than zero.")

    if not 0 < solids_concentration_percent < 100:
        raise ValueError(
            "Solids concentration must be between 0 and 100%."
        )

    if not 0 <= volatile_solids_fraction <= 1:
        raise ValueError(
            "VS fraction must be between 0 and 1."
        )

    if not 0 <= destruction_fraction <= 1:
        raise ValueError(
            "Destruction fraction must be between 0 and 1."
        )

    if gas_yield_m3_kg_vs_destroyed < 0:
        raise ValueError(
            "Gas yield cannot be negative."
        )

    if not 0 <= methane_fraction <= 1:
        raise ValueError(
            "Methane fraction must be between 0 and 1."
        )

    if digestion_srt_days <= 0:
        raise ValueError(
            "Digestion SRT must be greater than zero."
        )

    total_solids_kg_day = (
        sludge_flow_m3_day
        * 1000
        * solids_concentration_percent
        / 100
    )

    volatile_solids_kg_day = (
        total_solids_kg_day
        * volatile_solids_fraction
    )

    volatile_solids_destroyed_kg_day = (
        volatile_solids_kg_day
        * destruction_fraction
    )

    volatile_solids_remaining_kg_day = (
        volatile_solids_kg_day
        - volatile_solids_destroyed_kg_day
    )

    biogas_production_m3_day = (
        volatile_solids_destroyed_kg_day
        * gas_yield_m3_kg_vs_destroyed
    )

    methane_production_m3_day = (
        biogas_production_m3_day
        * methane_fraction
    )

    digester_volume_m3 = (
        sludge_flow_m3_day
        * digestion_srt_days
    )

    return DigestionResult(
        volatile_solids_kg_day=volatile_solids_kg_day,
        destruction_fraction=destruction_fraction,
        volatile_solids_destroyed_kg_day=(
            volatile_solids_destroyed_kg_day
        ),
        volatile_solids_remaining_kg_day=(
            volatile_solids_remaining_kg_day
        ),
        gas_yield_m3_kg_vs_destroyed=(
            gas_yield_m3_kg_vs_destroyed
        ),
        biogas_production_m3_day=biogas_production_m3_day,
        methane_fraction=methane_fraction,
        methane_production_m3_day=(
            methane_production_m3_day
        ),
        digestion_srt_days=digestion_srt_days,
        digester_volume_m3=digester_volume_m3,
    )