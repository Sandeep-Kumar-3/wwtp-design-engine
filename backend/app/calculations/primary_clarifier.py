from dataclasses import dataclass
import math


@dataclass
class PrimaryClarifierResult:
    average_flow_m3_day: float
    peak_flow_m3_day: float
    number_of_units: int
    surface_overflow_rate_m3_m2_day: float
    required_area_m2: float
    area_per_unit_m2: float
    diameter_m: float
    detention_time_h: float
    total_volume_m3: float
    volume_per_unit_m3: float
    water_depth_m: float
    weir_loading_m3_m_day: float
    total_weir_length_m: float


def design_primary_clarifier(
    average_flow_m3_day: float,
    peak_flow_m3_day: float,
    number_of_units: int,
    surface_overflow_rate_m3_m2_day: float,
    detention_time_h: float,
    weir_loading_m3_m_day: float,
) -> PrimaryClarifierResult:
    """
    Preliminary circular primary clarifier design.

    The hydraulic criteria are supplied explicitly and
    should later be selected from the engineering
    knowledge base.
    """

    if average_flow_m3_day <= 0:
        raise ValueError(
            "Average flow must be greater than zero."
        )

    if peak_flow_m3_day <= 0:
        raise ValueError(
            "Peak flow must be greater than zero."
        )

    if number_of_units <= 0:
        raise ValueError(
            "Number of units must be greater than zero."
        )

    if surface_overflow_rate_m3_m2_day <= 0:
        raise ValueError(
            "Surface overflow rate must be greater than zero."
        )

    if detention_time_h <= 0:
        raise ValueError(
            "Detention time must be greater than zero."
        )

    if weir_loading_m3_m_day <= 0:
        raise ValueError(
            "Weir loading must be greater than zero."
        )

    # Size based on average-flow surface overflow rate.
    required_area_m2 = (
        average_flow_m3_day
        / surface_overflow_rate_m3_m2_day
    )

    area_per_unit_m2 = (
        required_area_m2 / number_of_units
    )

    diameter_m = math.sqrt(
        4 * area_per_unit_m2 / math.pi
    )

    total_volume_m3 = (
        average_flow_m3_day
        * detention_time_h
        / 24
    )

    volume_per_unit_m3 = (
        total_volume_m3 / number_of_units
    )

    water_depth_m = (
        volume_per_unit_m3 / area_per_unit_m2
    )

    # Total weir length required from the selected
    # weir-loading criterion.
    total_weir_length_m = (
        average_flow_m3_day
        / weir_loading_m3_m_day
    )

    weir_loading_check = (
        average_flow_m3_day
        / total_weir_length_m
    )

    return PrimaryClarifierResult(
        average_flow_m3_day=average_flow_m3_day,
        peak_flow_m3_day=peak_flow_m3_day,
        number_of_units=number_of_units,
        surface_overflow_rate_m3_m2_day=(
            surface_overflow_rate_m3_m2_day
        ),
        required_area_m2=required_area_m2,
        area_per_unit_m2=area_per_unit_m2,
        diameter_m=diameter_m,
        detention_time_h=detention_time_h,
        total_volume_m3=total_volume_m3,
        volume_per_unit_m3=volume_per_unit_m3,
        water_depth_m=water_depth_m,
        weir_loading_m3_m_day=weir_loading_check,
        total_weir_length_m=total_weir_length_m,
    )