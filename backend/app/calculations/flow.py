from dataclasses import dataclass


@dataclass
class FlowResult:
    average_mld: float
    average_m3_day: float
    average_m3_hour: float
    average_m3_sec: float
    peak_mld: float
    peak_m3_day: float
    peak_m3_hour: float
    peak_m3_sec: float


def calculate_flow(
    average_mld: float,
    peak_factor: float = 2.5,
) -> FlowResult:
    """
    Convert average wastewater flow from MLD into
    m³/day, m³/hour and m³/second, and calculate
    peak flow using a peak factor.

    1 MLD = 1,000 m³/day
    """

    if average_mld <= 0:
        raise ValueError("Average flow must be greater than zero.")

    if peak_factor < 1:
        raise ValueError("Peak factor must be >= 1.")

    average_m3_day = average_mld * 1000
    average_m3_hour = average_m3_day / 24
    average_m3_sec = average_m3_day / 86400

    peak_mld = average_mld * peak_factor
    peak_m3_day = peak_mld * 1000
    peak_m3_hour = peak_m3_day / 24
    peak_m3_sec = peak_m3_day / 86400

    return FlowResult(
        average_mld=average_mld,
        average_m3_day=average_m3_day,
        average_m3_hour=average_m3_hour,
        average_m3_sec=average_m3_sec,
        peak_mld=peak_mld,
        peak_m3_day=peak_m3_day,
        peak_m3_hour=peak_m3_hour,
        peak_m3_sec=peak_m3_sec,
    )