from dataclasses import dataclass


@dataclass
class AerationDesign:
    average_flow_m3_day: float
    influent_bod_mg_l: float
    bod_removed_kg_day: float
    bod_load_kg_day: float
    oxygen_for_bod_kg_day: float
    oxygen_for_nitrification_kg_day: float
    total_oxygen_demand_kg_day: float
    safety_factor: float
    design_oxygen_demand_kg_day: float
    aeration_tank_volume_m3: float
    mlss_mg_l: float
    f_m_ratio: float
    srt_day: float
    number_of_aeration_tanks: int


def design_aeration(
    average_flow_m3_day: float,
    influent_bod_mg_l: float,
    target_bod_mg_l: float = 20.0,
    ammonia_mg_l: float = 25.0,
    nitrification_required: bool = False,
    mlss_mg_l: float = 3000.0,
    f_m_ratio: float = 0.25,
    srt_day: float = 10.0,
    bod_oxygen_factor: float = 1.42,
    nitrification_oxygen_factor: float = 4.57,
    safety_factor: float = 1.15,
    number_of_aeration_tanks: int = 2,
) -> AerationDesign:

    if average_flow_m3_day <= 0:
        raise ValueError("Flow must be greater than zero.")

    if influent_bod_mg_l < 0:
        raise ValueError("Influent BOD cannot be negative.")

    if target_bod_mg_l < 0:
        raise ValueError("Target BOD cannot be negative.")

    if ammonia_mg_l < 0:
        raise ValueError("Ammonia cannot be negative.")

    if mlss_mg_l <= 0:
        raise ValueError("MLSS must be greater than zero.")

    if f_m_ratio <= 0:
        raise ValueError("F/M ratio must be greater than zero.")

    if srt_day <= 0:
        raise ValueError("SRT must be greater than zero.")

    if safety_factor < 1:
        raise ValueError("Safety factor should be at least 1.")

    if number_of_aeration_tanks <= 0:
        raise ValueError(
            "Number of aeration tanks must be greater than zero."
        )

    # BOD load entering biological treatment
    bod_load = (
        average_flow_m3_day
        * influent_bod_mg_l
        / 1000
    )

    # Remaining BOD in final effluent
    final_bod_load = (
        average_flow_m3_day
        * target_bod_mg_l
        / 1000
    )

    bod_removed = max(
        bod_load - final_bod_load,
        0
    )

    # Oxygen required for carbonaceous oxidation
    oxygen_for_bod = (
        bod_removed
        * bod_oxygen_factor
    )

    # Nitrification oxygen demand
    if nitrification_required:
        ammonia_load = (
            average_flow_m3_day
            * ammonia_mg_l
            / 1000
        )

        oxygen_for_nitrification = (
            ammonia_load
            * nitrification_oxygen_factor
        )
    else:
        oxygen_for_nitrification = 0.0

    total_oxygen = (
        oxygen_for_bod
        + oxygen_for_nitrification
    )

    design_oxygen = (
        total_oxygen
        * safety_factor
    )

    # F/M relationship:
    #
    # F/M = BOD load / (MLSS × reactor volume)
    #
    # MLSS converted from mg/L to kg/m3
    mlss_kg_m3 = mlss_mg_l / 1000

    aeration_volume = (
        bod_load
        / (
            f_m_ratio
            * mlss_kg_m3
        )
    )

    return AerationDesign(
        average_flow_m3_day=average_flow_m3_day,
        influent_bod_mg_l=influent_bod_mg_l,
        bod_removed_kg_day=bod_removed,
        bod_load_kg_day=bod_load,
        oxygen_for_bod_kg_day=oxygen_for_bod,
        oxygen_for_nitrification_kg_day=(
            oxygen_for_nitrification
        ),
        total_oxygen_demand_kg_day=total_oxygen,
        safety_factor=safety_factor,
        design_oxygen_demand_kg_day=design_oxygen,
        aeration_tank_volume_m3=aeration_volume,
        mlss_mg_l=mlss_mg_l,
        f_m_ratio=f_m_ratio,
        srt_day=srt_day,
        number_of_aeration_tanks=number_of_aeration_tanks,
    )