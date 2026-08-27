from dataclasses import dataclass


@dataclass
class PrimaryClarifierDesign:
    number_of_units: int
    design_flow_m3_day: float
    surface_overflow_rate_m3_m2_day: float
    required_surface_area_m2: float
    area_per_unit_m2: float
    water_depth_m: float
    detention_time_hr: float
    volume_per_unit_m3: float
    diameter_m: float
    bod_removal_percent: float
    tss_removal_percent: float
    bod_removed_kg_day: float
    tss_removed_kg_day: float


def design_primary_clarifier(
    average_flow_m3_day: float,
    influent_bod_mg_l: float,
    influent_tss_mg_l: float,
    number_of_units: int = 2,
    surface_overflow_rate_m3_m2_day: float = 30.0,
    water_depth_m: float = 3.0,
    detention_time_hr: float = 2.0,
    bod_removal_percent: float = 30.0,
    tss_removal_percent: float = 60.0,
) -> PrimaryClarifierDesign:

    required_area = (
        average_flow_m3_day /
        surface_overflow_rate_m3_m2_day
    )

    area_per_unit = (
        required_area / number_of_units
    )

    volume_per_unit = (
        average_flow_m3_day *
        detention_time_hr / 24 /
        number_of_units
    )

    diameter = (
        4 * area_per_unit / 3.14159265359
    ) ** 0.5

    bod_load = (
        average_flow_m3_day *
        influent_bod_mg_l / 1000
    )

    tss_load = (
        average_flow_m3_day *
        influent_tss_mg_l / 1000
    )

    return PrimaryClarifierDesign(
        number_of_units=number_of_units,
        design_flow_m3_day=average_flow_m3_day,
        surface_overflow_rate_m3_m2_day=surface_overflow_rate_m3_m2_day,
        required_surface_area_m2=required_area,
        area_per_unit_m2=area_per_unit,
        water_depth_m=water_depth_m,
        detention_time_hr=detention_time_hr,
        volume_per_unit_m3=volume_per_unit,
        diameter_m=diameter,
        bod_removal_percent=bod_removal_percent,
        tss_removal_percent=tss_removal_percent,
        bod_removed_kg_day=(
            bod_load * bod_removal_percent / 100
        ),
        tss_removed_kg_day=(
            tss_load * tss_removal_percent / 100
        ),
    )