from dataclasses import dataclass


@dataclass
class BiologicalDesign:
    design_flow_m3_day: float
    bod_load_kg_day: float
    bod_removal_target_percent: float
    bod_removed_kg_day: float
    aeration_volume_m3: float
    aeration_hydraulic_retention_time_hr: float
    mlss_mg_l: float
    f_m_ratio_kg_bod_kg_mlvss_day: float
    oxygen_requirement_kg_o2_day: float
    air_requirement_m3_day: float


def design_biological_treatment(
    design_flow_m3_day: float,
    influent_bod_mg_l: float,
    effluent_bod_mg_l: float = 20.0,
    mlss_mg_l: float = 3000.0,
    f_m_ratio: float = 0.25,
    aeration_hydraulic_retention_time_hr: float = 6.0,
    oxygen_per_kg_bod: float = 1.2,
    oxygen_transfer_efficiency: float = 0.15,
) -> BiologicalDesign:

    if design_flow_m3_day <= 0:
        raise ValueError("Design flow must be greater than zero.")

    if influent_bod_mg_l < 0:
        raise ValueError("Influent BOD cannot be negative.")

    if effluent_bod_mg_l < 0:
        raise ValueError("Effluent BOD cannot be negative.")

    if effluent_bod_mg_l > influent_bod_mg_l:
        raise ValueError(
            "Effluent BOD cannot exceed influent BOD."
        )

    if mlss_mg_l <= 0:
        raise ValueError("MLSS must be greater than zero.")

    if f_m_ratio <= 0:
        raise ValueError("F/M ratio must be greater than zero.")

    if aeration_hydraulic_retention_time_hr <= 0:
        raise ValueError("HRT must be greater than zero.")

    if oxygen_per_kg_bod <= 0:
        raise ValueError(
            "Oxygen requirement factor must be greater than zero."
        )

    if not 0 < oxygen_transfer_efficiency <= 1:
        raise ValueError(
            "Oxygen transfer efficiency must be between 0 and 1."
        )

    bod_load_kg_day = (
        design_flow_m3_day * influent_bod_mg_l / 1000
    )

    bod_removed_kg_day = (
        design_flow_m3_day
        * (influent_bod_mg_l - effluent_bod_mg_l)
        / 1000
    )

    if influent_bod_mg_l > 0:
        bod_removal_target_percent = (
            (influent_bod_mg_l - effluent_bod_mg_l)
            / influent_bod_mg_l
            * 100
        )
    else:
        bod_removal_target_percent = 0.0

    aeration_volume_m3 = (
        design_flow_m3_day
        * aeration_hydraulic_retention_time_hr
        / 24
    )

    oxygen_requirement_kg_day = (
        bod_removed_kg_day * oxygen_per_kg_bod
    )

    # Preliminary air estimate.
    # Oxygen in air ≈ 0.232 kg O2/kg air.
    oxygen_in_air_fraction = 0.232

    air_mass_kg_day = (
        oxygen_requirement_kg_day
        / (
            oxygen_in_air_fraction
            * oxygen_transfer_efficiency
        )
    )

    # Air density ≈ 1.225 kg/m3 at standard conditions.
    air_requirement_m3_day = (
        air_mass_kg_day / 1.225
    )

    return BiologicalDesign(
        design_flow_m3_day=design_flow_m3_day,
        bod_load_kg_day=bod_load_kg_day,
        bod_removal_target_percent=bod_removal_target_percent,
        bod_removed_kg_day=bod_removed_kg_day,
        aeration_volume_m3=aeration_volume_m3,
        aeration_hydraulic_retention_time_hr=(
            aeration_hydraulic_retention_time_hr
        ),
        mlss_mg_l=mlss_mg_l,
        f_m_ratio_kg_bod_kg_mlvss_day=f_m_ratio,
        oxygen_requirement_kg_o2_day=oxygen_requirement_kg_day,
        air_requirement_m3_day=air_requirement_m3_day,
    )
def design_biological_reactor(
    average_flow_m3_day: float,
    bod_load_kg_day: float,
    target_bod_mg_l: float = 20.0,
    nitrification_required: bool = False,
    number_of_reactors: int = 2,
    mlss_mg_l: float = 3000.0,
    mlvss_fraction: float = 0.8,
    fm_ratio: float = 0.25,
):
    """
    Compatibility wrapper for the central design service.

    Converts the BOD load supplied by the design service into
    an equivalent influent BOD concentration and uses the
    existing biological treatment calculation.
    """

    if average_flow_m3_day <= 0:
        raise ValueError(
            "Average flow must be greater than zero."
        )

    if bod_load_kg_day < 0:
        raise ValueError(
            "BOD load cannot be negative."
        )

    if number_of_reactors <= 0:
        raise ValueError(
            "Number of reactors must be greater than zero."
        )

    if not 0 < mlvss_fraction <= 1:
        raise ValueError(
            "MLVSS fraction must be between 0 and 1."
        )

    influent_bod_mg_l = (
        bod_load_kg_day
        * 1000
        / average_flow_m3_day
    )

    result = design_biological_treatment(
        design_flow_m3_day=average_flow_m3_day,
        influent_bod_mg_l=influent_bod_mg_l,
        effluent_bod_mg_l=target_bod_mg_l,
        mlss_mg_l=mlss_mg_l,
        f_m_ratio=fm_ratio,
    )

    # Add integration metadata without modifying the
    # existing BiologicalDesign dataclass.
    result_dict = result.__dict__.copy()

    result_dict.update({
        "nitrification_required": nitrification_required,
        "number_of_reactors": number_of_reactors,
        "mlss_mg_l": mlss_mg_l,
        "mlvss_fraction": mlvss_fraction,
        "mlvss_mg_l": mlss_mg_l * mlvss_fraction,
        "f_m_ratio": fm_ratio,
    })

    return result_dict