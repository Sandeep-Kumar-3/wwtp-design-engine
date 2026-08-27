from dataclasses import dataclass


@dataclass
class SecondaryClarifierDesign:
    number_of_units: int

    design_flow_m3_day: float

    surface_overflow_rate_m3_m2_day: float

    required_surface_area_m2: float

    area_per_unit_m2: float

    water_depth_m: float

    volume_per_unit_m3: float

    total_volume_m3: float

    detention_time_hr: float

    diameter_m: float


def design_secondary_clarifier(
    average_flow_m3_day: float,
    number_of_units: int = 2,
    surface_overflow_rate_m3_m2_day: float = 25.0,
    water_depth_m: float = 3.5,
) -> SecondaryClarifierDesign:

    required_area = (
        average_flow_m3_day /
        surface_overflow_rate_m3_m2_day
    )

    area_per_unit = (
        required_area /
        number_of_units
    )

    total_volume = (
        required_area *
        water_depth_m
    )

    volume_per_unit = (
        total_volume /
        number_of_units
    )

    detention_time = (
        total_volume /
        average_flow_m3_day
    ) * 24

    diameter = (
        4 *
        area_per_unit /
        3.14159265359
    ) ** 0.5

    return SecondaryClarifierDesign(
        number_of_units=number_of_units,

        design_flow_m3_day=average_flow_m3_day,

        surface_overflow_rate_m3_m2_day=(
            surface_overflow_rate_m3_m2_day
        ),

        required_surface_area_m2=required_area,

        area_per_unit_m2=area_per_unit,

        water_depth_m=water_depth_m,

        volume_per_unit_m3=volume_per_unit,

        total_volume_m3=total_volume,

        detention_time_hr=detention_time,

        diameter_m=diameter,
    )