from dataclasses import dataclass


@dataclass
class ClarifierDesign:
    design_flow_m3_day: float
    surface_overflow_rate_m3_m2_day: float
    required_surface_area_m2: float
    number_of_clarifiers: int
    area_per_clarifier_m2: float
    diameter_per_clarifier_m: float
    side_water_depth_m: float
    total_volume_m3: float
    hydraulic_retention_time_hr: float


def design_secondary_clarifier(
    design_flow_m3_day: float,
    surface_overflow_rate_m3_m2_day: float = 25.0,
    number_of_clarifiers: int = 2,
    side_water_depth_m: float = 3.0,
) -> ClarifierDesign:

    if design_flow_m3_day <= 0:
        raise ValueError("Design flow must be greater than zero.")

    if surface_overflow_rate_m3_m2_day <= 0:
        raise ValueError(
            "Surface overflow rate must be greater than zero."
        )

    if number_of_clarifiers <= 0:
        raise ValueError(
            "Number of clarifiers must be greater than zero."
        )

    if side_water_depth_m <= 0:
        raise ValueError(
            "Side water depth must be greater than zero."
        )

    required_surface_area_m2 = (
        design_flow_m3_day
        / surface_overflow_rate_m3_m2_day
    )

    area_per_clarifier_m2 = (
        required_surface_area_m2 / number_of_clarifiers
    )

    diameter_per_clarifier_m = (
        4 * area_per_clarifier_m2 / 3.141592653589793
    ) ** 0.5

    total_volume_m3 = (
        required_surface_area_m2
        * side_water_depth_m
    )

    hydraulic_retention_time_hr = (
        total_volume_m3
        / design_flow_m3_day
        * 24
    )

    return ClarifierDesign(
        design_flow_m3_day=design_flow_m3_day,
        surface_overflow_rate_m3_m2_day=(
            surface_overflow_rate_m3_m2_day
        ),
        required_surface_area_m2=required_surface_area_m2,
        number_of_clarifiers=number_of_clarifiers,
        area_per_clarifier_m2=area_per_clarifier_m2,
        diameter_per_clarifier_m=diameter_per_clarifier_m,
        side_water_depth_m=side_water_depth_m,
        total_volume_m3=total_volume_m3,
        hydraulic_retention_time_hr=(
            hydraulic_retention_time_hr
        ),
    )