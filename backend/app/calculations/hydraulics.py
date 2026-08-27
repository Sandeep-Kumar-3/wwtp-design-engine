from dataclasses import dataclass


@dataclass
class HydraulicLoads:
    average_flow_m3_day: float
    peak_flow_m3_day: float

    average_flow_m3_hour: float
    peak_flow_m3_hour: float

    average_flow_m3_sec: float
    peak_flow_m3_sec: float

    peak_factor: float

    bod_load_kg_day: float
    cod_load_kg_day: float
    tss_load_kg_day: float
    ammonia_load_kg_day: float


def calculate_hydraulic_loads(
    average_flow_m3_day: float,
    peak_flow_m3_day: float,
    bod_mg_l: float,
    cod_mg_l: float,
    tss_mg_l: float,
    ammonia_mg_l: float,
) -> HydraulicLoads:

    if average_flow_m3_day <= 0:
        raise ValueError(
            "Average flow must be greater than zero."
        )

    if peak_flow_m3_day < average_flow_m3_day:
        raise ValueError(
            "Peak flow cannot be lower than average flow."
        )

    peak_factor = (
        peak_flow_m3_day /
        average_flow_m3_day
    )

    return HydraulicLoads(

        average_flow_m3_day=average_flow_m3_day,

        peak_flow_m3_day=peak_flow_m3_day,

        average_flow_m3_hour=(
            average_flow_m3_day / 24
        ),

        peak_flow_m3_hour=(
            peak_flow_m3_day / 24
        ),

        average_flow_m3_sec=(
            average_flow_m3_day / 86400
        ),

        peak_flow_m3_sec=(
            peak_flow_m3_day / 86400
        ),

        peak_factor=peak_factor,

        bod_load_kg_day=(
            average_flow_m3_day *
            bod_mg_l /
            1000
        ),

        cod_load_kg_day=(
            average_flow_m3_day *
            cod_mg_l /
            1000
        ),

        tss_load_kg_day=(
            average_flow_m3_day *
            tss_mg_l /
            1000
        ),

        ammonia_load_kg_day=(
            average_flow_m3_day *
            ammonia_mg_l /
            1000
        ),
    )