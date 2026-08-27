from dataclasses import dataclass


@dataclass
class ScreeningDesign:

    number_of_channels: int

    design_flow_m3_day: float

    design_flow_m3_sec: float

    approach_velocity_m_sec: float

    required_open_area_m2: float

    gross_screen_area_m2: float

    channel_width_m: float

    water_depth_m: float

    channel_length_m: float


def design_screening(
    peak_flow_m3_day: float,
    approach_velocity_m_sec: float = 0.8,
    water_depth_m: float = 1.0,
    screen_opening_ratio: float = 0.60,
) -> ScreeningDesign:

    q = peak_flow_m3_day / 86400

    number_of_channels = 2

    channel_flow = q / number_of_channels

    open_area = (
        channel_flow /
        approach_velocity_m_sec
    )

    gross_area = (
        open_area /
        screen_opening_ratio
    )

    channel_width = (
        gross_area /
        water_depth_m
    )

    channel_width = max(
        0.6,
        round(channel_width, 2)
    )

    channel_length = 5.0

    return ScreeningDesign(

        number_of_channels=number_of_channels,

        design_flow_m3_day=peak_flow_m3_day,

        design_flow_m3_sec=q,

        approach_velocity_m_sec=(
            approach_velocity_m_sec
        ),

        required_open_area_m2=open_area,

        gross_screen_area_m2=gross_area,

        channel_width_m=channel_width,

        water_depth_m=water_depth_m,

        channel_length_m=channel_length,
    )


@dataclass
class GritDesign:

    number_of_units: int

    design_flow_m3_day: float

    detention_time_min: float

    total_volume_m3: float

    volume_per_unit_m3: float

    water_depth_m: float

    length_m: float

    width_m: float


def design_grit_chamber(
    peak_flow_m3_day: float,
    detention_time_min: float = 3.0,
    water_depth_m: float = 1.0,
    length_to_width_ratio: float = 3.0,
) -> GritDesign:

    number_of_units = 2

    q = peak_flow_m3_day / 1440

    total_volume = (
        q * detention_time_min
    )

    volume_per_unit = (
        total_volume /
        number_of_units
    )

    width = (
        (
            volume_per_unit /
            (
                water_depth_m *
                length_to_width_ratio
            )
        ) ** 0.5
    )

    length = (
        width *
        length_to_width_ratio
    )

    return GritDesign(

        number_of_units=number_of_units,

        design_flow_m3_day=peak_flow_m3_day,

        detention_time_min=detention_time_min,

        total_volume_m3=total_volume,

        volume_per_unit_m3=volume_per_unit,

        water_depth_m=water_depth_m,

        length_m=length,

        width_m=width,
    )