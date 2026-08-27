from dataclasses import dataclass


@dataclass
class ScreeningResult:
    design_flow_m3_s: float
    number_of_channels: int
    flow_per_channel_m3_s: float
    channel_area_m2: float
    channel_width_m: float
    water_depth_m: float
    approach_velocity_m_s: float
    bar_spacing_m: float
    gross_screen_area_m2: float
    open_area_ratio: float
    net_open_area_m2: float


def design_screen(
    peak_flow_m3_day: float,
    number_of_channels: int,
    approach_velocity_m_s: float,
    water_depth_m: float,
    bar_spacing_m: float,
    open_area_ratio: float = 0.60,
) -> ScreeningResult:
    """
    Preliminary hydraulic sizing of a bar screen channel.

    The design criteria are explicitly supplied by the caller.
    They should later come from the engineering knowledge base.
    """

    if peak_flow_m3_day <= 0:
        raise ValueError("Peak flow must be greater than zero.")

    if number_of_channels <= 0:
        raise ValueError("Number of channels must be greater than zero.")

    if approach_velocity_m_s <= 0:
        raise ValueError("Approach velocity must be greater than zero.")

    if water_depth_m <= 0:
        raise ValueError("Water depth must be greater than zero.")

    if bar_spacing_m <= 0:
        raise ValueError("Bar spacing must be greater than zero.")

    if not 0 < open_area_ratio <= 1:
        raise ValueError("Open area ratio must be between 0 and 1.")

    design_flow_m3_s = peak_flow_m3_day / 86400

    flow_per_channel_m3_s = (
        design_flow_m3_s / number_of_channels
    )

    channel_area_m2 = (
        flow_per_channel_m3_s / approach_velocity_m_s
    )

    channel_width_m = channel_area_m2 / water_depth_m

    gross_screen_area_m2 = channel_width_m * water_depth_m

    net_open_area_m2 = (
        gross_screen_area_m2 * open_area_ratio
    )

    return ScreeningResult(
        design_flow_m3_s=design_flow_m3_s,
        number_of_channels=number_of_channels,
        flow_per_channel_m3_s=flow_per_channel_m3_s,
        channel_area_m2=channel_area_m2,
        channel_width_m=channel_width_m,
        water_depth_m=water_depth_m,
        approach_velocity_m_s=approach_velocity_m_s,
        bar_spacing_m=bar_spacing_m,
        gross_screen_area_m2=gross_screen_area_m2,
        open_area_ratio=open_area_ratio,
        net_open_area_m2=net_open_area_m2,
    )