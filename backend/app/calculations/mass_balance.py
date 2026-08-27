from dataclasses import dataclass


@dataclass
class MassBalanceResult:
    parameter: str
    influent_concentration_mg_l: float
    influent_load_kg_day: float
    removal_efficiency_percent: float
    removed_load_kg_day: float
    effluent_load_kg_day: float
    effluent_concentration_mg_l: float


def calculate_mass_balance(
    parameter: str,
    influent_concentration_mg_l: float,
    flow_m3_day: float,
    removal_efficiency_percent: float,
) -> MassBalanceResult:

    if influent_concentration_mg_l < 0:
        raise ValueError(
            "Influent concentration cannot be negative."
        )

    if flow_m3_day <= 0:
        raise ValueError(
            "Flow must be greater than zero."
        )

    if not 0 <= removal_efficiency_percent <= 100:
        raise ValueError(
            "Removal efficiency must be between 0 and 100%."
        )

    influent_load_kg_day = (
        flow_m3_day * influent_concentration_mg_l / 1000
    )

    removed_load_kg_day = (
        influent_load_kg_day
        * removal_efficiency_percent
        / 100
    )

    effluent_load_kg_day = (
        influent_load_kg_day
        - removed_load_kg_day
    )

    effluent_concentration_mg_l = (
        effluent_load_kg_day * 1000 / flow_m3_day
    )

    return MassBalanceResult(
        parameter=parameter,
        influent_concentration_mg_l=influent_concentration_mg_l,
        influent_load_kg_day=influent_load_kg_day,
        removal_efficiency_percent=removal_efficiency_percent,
        removed_load_kg_day=removed_load_kg_day,
        effluent_load_kg_day=effluent_load_kg_day,
        effluent_concentration_mg_l=effluent_concentration_mg_l,
    )