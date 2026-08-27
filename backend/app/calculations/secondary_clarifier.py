from dataclasses import dataclass
import math


@dataclass
class SecondaryClarifierResult:
    average_flow_m3_day: float
    peak_flow_m3_day: float

    number_of_units: int

    hydraulic_area_m2: float
    solids_area_m2: float
    required_area_m2: float
    area_per_unit_m2: float

    diameter_m: float

    water_depth_m: float
    total_volume_m3: float
    volume_per_unit_m3: float

    detention_time_h: float

    total_weir_length_m: float
    weir_loading_m3_m_day: float

    solids_loading_kg_m2_day: float


def design_secondary_clarifier(
    average_flow_m3_day: float,
    peak_flow_m3_day: float,
    mlss_mg_l: float,
    ras_flow_m3_day: float,
    number_of_units: int,
    surface_overflow_rate_m3_m2_day: float,
    solids_loading_rate_kg_m2_day: float,
    water_depth_m: float,
    weir_loading_m3_m_day: float,
) -> SecondaryClarifierResult:

    if average_flow_m3_day <= 0:
        raise ValueError("Average flow must be greater than zero.")

    if peak_flow_m3_day <= 0:
        raise ValueError("Peak flow must be greater than zero.")

    if mlss_mg_l <= 0:
        raise ValueError("MLSS must be greater than zero.")

    if ras_flow_m3_day < 0:
        raise ValueError("RAS flow cannot be negative.")

    if number_of_units <= 0:
        raise ValueError("Number of units must be greater than zero.")

    if surface_overflow_rate_m3_m2_day <= 0:
        raise ValueError("SOR must be greater than zero.")

    if solids_loading_rate_kg_m2_day <= 0:
        raise ValueError("Solids loading rate must be greater than zero.")

    if water_depth_m <= 0:
        raise ValueError("Water depth must be greater than zero.")

    if weir_loading_m3_m_day <= 0:
        raise ValueError("Weir loading must be greater than zero.")

    # Hydraulic area based on peak flow.
    hydraulic_area_m2 = (
        peak_flow_m3_day
        / surface_overflow_rate_m3_m2_day
    )

    # Simplified solids-loading check.
    #
    # Solids entering clarifier are approximated as
    # MLSS concentration × (Q + RAS).

    solids_load_kg_day = (
        mlss_mg_l
        / 1000
        * (average_flow_m3_day + ras_flow_m3_day)
    )

    solids_area_m2 = (
        solids_load_kg_day
        / solids_loading_rate_kg_m2_day
    )

    required_area_m2 = max(
        hydraulic_area_m2,
        solids_area_m2,
    )

    area_per_unit_m2 = (
        required_area_m2 / number_of_units
    )

    diameter_m = math.sqrt(
        4 * area_per_unit_m2 / math.pi
    )

    total_volume_m3 = (
        required_area_m2 * water_depth_m
    )

    volume_per_unit_m3 = (
        total_volume_m3 / number_of_units
    )

    detention_time_h = (
        total_volume_m3
        / average_flow_m3_day
        * 24
    )

    total_weir_length_m = (
        average_flow_m3_day
        / weir_loading_m3_m_day
    )

    actual_weir_loading = (
        average_flow_m3_day
        / total_weir_length_m
    )

    actual_solids_loading = (
        solids_load_kg_day
        / required_area_m2
    )

    return SecondaryClarifierResult(
        average_flow_m3_day=average_flow_m3_day,
        peak_flow_m3_day=peak_flow_m3_day,
        number_of_units=number_of_units,
        hydraulic_area_m2=hydraulic_area_m2,
        solids_area_m2=solids_area_m2,
        required_area_m2=required_area_m2,
        area_per_unit_m2=area_per_unit_m2,
        diameter_m=diameter_m,
        water_depth_m=water_depth_m,
        total_volume_m3=total_volume_m3,
        volume_per_unit_m3=volume_per_unit_m3,
        detention_time_h=detention_time_h,
        total_weir_length_m=total_weir_length_m,
        weir_loading_m3_m_day=actual_weir_loading,
        solids_loading_kg_m2_day=actual_solids_loading,
    )