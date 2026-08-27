from dataclasses import dataclass
from typing import Optional


@dataclass
class PollutantLoad:
    parameter: str
    concentration_mg_l: float
    flow_m3_day: float
    load_kg_day: float


def calculate_load(
    concentration_mg_l: float,
    flow_m3_day: float,
) -> float:
    """
    Calculate pollutant mass loading.

    Formula:

        Load (kg/day) =
            Flow (m3/day) × Concentration (mg/L)
            --------------------------------------
                         1000

    because:
        1 mg/L = 0.001 kg/m3
    """

    if concentration_mg_l < 0:
        raise ValueError("Concentration cannot be negative.")

    if flow_m3_day <= 0:
        raise ValueError("Flow must be greater than zero.")

    return flow_m3_day * concentration_mg_l / 1000


def calculate_pollutant_load(
    parameter: str,
    concentration_mg_l: float,
    flow_m3_day: float,
) -> PollutantLoad:
    """
    Calculate and return a complete pollutant-load result.
    """

    load = calculate_load(
        concentration_mg_l=concentration_mg_l,
        flow_m3_day=flow_m3_day,
    )

    return PollutantLoad(
        parameter=parameter,
        concentration_mg_l=concentration_mg_l,
        flow_m3_day=flow_m3_day,
        load_kg_day=load,
    )


@dataclass
class WastewaterLoads:
    bod: Optional[PollutantLoad] = None
    cod: Optional[PollutantLoad] = None
    tss: Optional[PollutantLoad] = None
    tn: Optional[PollutantLoad] = None
    nh4_n: Optional[PollutantLoad] = None
    tp: Optional[PollutantLoad] = None
    oil_grease: Optional[PollutantLoad] = None


def calculate_wastewater_loads(
    flow_m3_day: float,
    bod: Optional[float] = None,
    cod: Optional[float] = None,
    tss: Optional[float] = None,
    tn: Optional[float] = None,
    nh4_n: Optional[float] = None,
    tp: Optional[float] = None,
    oil_grease: Optional[float] = None,
) -> WastewaterLoads:
    """
    Calculate loads for all supplied wastewater parameters.
    """

    parameters = {
        "bod": ("BOD", bod),
        "cod": ("COD", cod),
        "tss": ("TSS", tss),
        "tn": ("TN", tn),
        "nh4_n": ("NH4-N", nh4_n),
        "tp": ("TP", tp),
        "oil_grease": ("Oil & Grease", oil_grease),
    }

    results = {}

    for field_name, (display_name, concentration) in parameters.items():
        if concentration is not None:
            results[field_name] = calculate_pollutant_load(
                parameter=display_name,
                concentration_mg_l=concentration,
                flow_m3_day=flow_m3_day,
            )

    return WastewaterLoads(**results)