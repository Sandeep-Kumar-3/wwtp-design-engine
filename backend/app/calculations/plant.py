from dataclasses import dataclass

from app.calculations.flow import calculate_flow
from app.calculations.loads import calculate_wastewater_loads
from app.calculations.mass_balance import calculate_mass_balance


@dataclass
class PlantDesignBasis:
    flow: object
    loads: object
    primary_treatment: dict


def calculate_design_basis(
    average_flow_mld: float,
    peak_factor: float,
    bod_mg_l: float,
    cod_mg_l: float,
    tss_mg_l: float,
):
    """
    First integrated wastewater-treatment calculation.

    Current model:

    User input
        ↓
    Flow calculation
        ↓
    Pollutant loading
        ↓
    Preliminary primary-treatment mass balance
    """

    flow = calculate_flow(
        average_mld=average_flow_mld,
        peak_factor=peak_factor,
    )

    loads = calculate_wastewater_loads(
        flow_m3_day=flow.average_m3_day,
        bod=bod_mg_l,
        cod=cod_mg_l,
        tss=tss_mg_l,
    )

    primary_bod = calculate_mass_balance(
        parameter="BOD",
        influent_concentration_mg_l=bod_mg_l,
        flow_m3_day=flow.average_m3_day,
        removal_efficiency_percent=30,
    )

    primary_tss = calculate_mass_balance(
        parameter="TSS",
        influent_concentration_mg_l=tss_mg_l,
        flow_m3_day=flow.average_m3_day,
        removal_efficiency_percent=60,
    )

    return PlantDesignBasis(
        flow=flow,
        loads=loads,
        primary_treatment={
            "bod": primary_bod,
            "tss": primary_tss,
        },
    )