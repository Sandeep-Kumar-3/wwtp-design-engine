from dataclasses import dataclass


@dataclass
class RASWASResult:
    average_flow_m3_day: float
    ras_ratio: float
    ras_flow_m3_day: float

    reactor_volume_m3: float
    mlss_mg_l: float
    solids_inventory_kg: float

    srt_days: float
    wasting_solids_kg_day: float
    was_flow_m3_day: float

    was_concentration_mg_l: float


def calculate_ras_was(
    average_flow_m3_day: float,
    ras_ratio: float,
    reactor_volume_m3: float,
    mlss_mg_l: float,
    srt_days: float,
    was_concentration_mg_l: float,
) -> RASWASResult:

    if average_flow_m3_day <= 0:
        raise ValueError("Flow must be greater than zero.")

    if ras_ratio < 0:
        raise ValueError("RAS ratio cannot be negative.")

    if reactor_volume_m3 <= 0:
        raise ValueError(
            "Reactor volume must be greater than zero."
        )

    if mlss_mg_l <= 0:
        raise ValueError("MLSS must be greater than zero.")

    if srt_days <= 0:
        raise ValueError("SRT must be greater than zero.")

    if was_concentration_mg_l <= 0:
        raise ValueError(
            "WAS concentration must be greater than zero."
        )

    # RAS flow

    ras_flow_m3_day = (
        average_flow_m3_day * ras_ratio
    )

    # Solids inventory in aeration tank.
    #
    # mg/L × m3 × 1000 L/m3
    # / 1,000,000 mg/kg
    #
    # = MLSS(mg/L) × volume(m3) / 1000

    solids_inventory_kg = (
        mlss_mg_l
        * reactor_volume_m3
        / 1000
    )

    # Simplified SRT-based wasting requirement.

    wasting_solids_kg_day = (
        solids_inventory_kg
        / srt_days
    )

    # WAS flow from solids concentration.

    was_flow_m3_day = (
        wasting_solids_kg_day
        * 1000
        / was_concentration_mg_l
    )

    return RASWASResult(
        average_flow_m3_day=average_flow_m3_day,
        ras_ratio=ras_ratio,
        ras_flow_m3_day=ras_flow_m3_day,
        reactor_volume_m3=reactor_volume_m3,
        mlss_mg_l=mlss_mg_l,
        solids_inventory_kg=solids_inventory_kg,
        srt_days=srt_days,
        wasting_solids_kg_day=wasting_solids_kg_day,
        was_flow_m3_day=was_flow_m3_day,
        was_concentration_mg_l=was_concentration_mg_l,
    )