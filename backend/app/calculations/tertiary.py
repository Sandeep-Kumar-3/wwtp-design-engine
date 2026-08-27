from dataclasses import dataclass


@dataclass
class FiltrationDesign:
    number_of_filters: int
    design_flow_m3_day: float
    filtration_rate_m3_m2_day: float
    required_filter_area_m2: float
    area_per_filter_m2: float
    filter_length_m: float
    filter_width_m: float
    total_area_m2: float


def design_filtration(
    average_flow_m3_day: float,
    filtration_rate_m3_m2_day: float = 10.0,
    number_of_filters: int = 4,
    length_to_width_ratio: float = 1.5,
) -> FiltrationDesign:

    required_area = (
        average_flow_m3_day /
        filtration_rate_m3_m2_day
    )

    area_per_filter = (
        required_area /
        number_of_filters
    )

    width = (
        area_per_filter /
        length_to_width_ratio
    ) ** 0.5

    length = (
        width *
        length_to_width_ratio
    )

    return FiltrationDesign(
        number_of_filters=number_of_filters,
        design_flow_m3_day=average_flow_m3_day,
        filtration_rate_m3_m2_day=filtration_rate_m3_m2_day,
        required_filter_area_m2=required_area,
        area_per_filter_m2=area_per_filter,
        filter_length_m=length,
        filter_width_m=width,
        total_area_m2=required_area,
    )