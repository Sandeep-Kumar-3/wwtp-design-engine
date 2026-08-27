from dataclasses import dataclass


@dataclass
class GritChamberResult:
    peak_flow_m3_s: float
    number_of_units: int
    detention_time_s: float
    volume_per_unit_m3: float
    total_volume_m3: float
    water_depth_m: float
    width_m: float
    length_m: float
    horizontal_velocity_m_s: float


def design_grit_chamber(
    peak_flow_m3_day: float,
    number_of_units: int,
    detention_time_s: float,
    horizontal_velocity_m_s: float,
    water_depth_m: float,
) -> GritChamberResult:
    """
    Preliminary hydraulic sizing of a grit chamber.

    Criteria are supplied explicitly and will later be
    retrieved from the engineering knowledge base.
    """

    if peak_flow_m3_day <= 0:
        raise ValueError("Peak flow must be greater than zero.")

    if number_of_units <= 0:
        raise ValueError("Number of units must be greater than zero.")

    if detention_time_s <= 0:
        raise ValueError("Detention time must be greater than zero.")

    if horizontal_velocity_m_s <= 0:
        raise ValueError(
            "Horizontal velocity must be greater than zero."
        )

    if water_depth_m <= 0:
        raise ValueError("Water depth must be greater than zero.")

    peak_flow_m3_s = peak_flow_m3_day / 86400

    flow_per_unit_m3_s = (
        peak_flow_m3_s / number_of_units
    )

    volume_per_unit_m3 = (
        flow_per_unit_m3_s * detention_time_s
    )

    total_volume_m3 = (
        volume_per_unit_m3 * number_of_units
    )

    # From:
    #
    # Q = A × v
    #
    # A = width × depth

    cross_sectional_area_m2 = (
        flow_per_unit_m3_s / horizontal_velocity_m_s
    )

    width_m = (
        cross_sectional_area_m2 / water_depth_m
    )

    # From:
    #
    # V = L × W × D

    length_m = (
        volume_per_unit_m3
        / (width_m * water_depth_m)
    )

    return GritChamberResult(
        peak_flow_m3_s=peak_flow_m3_s,
        number_of_units=number_of_units,
        detention_time_s=detention_time_s,
        volume_per_unit_m3=volume_per_unit_m3,
        total_volume_m3=total_volume_m3,
        water_depth_m=water_depth_m,
        width_m=width_m,
        length_m=length_m,
        horizontal_velocity_m_s=horizontal_velocity_m_s,
    )