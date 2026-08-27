"""
Central WWTP Design Engine

Combines wastewater characteristics, pollutant loads and
treatment-process selection into one preliminary WWTP design.

This is a preliminary engineering decision-support system.
Final design requires site-specific data, applicable standards,
hydraulic profiles and detailed engineering review.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

from .process_selection import select_treatment_process


# ============================================================
# RESULT DATA STRUCTURES
# ============================================================

@dataclass
class PollutantLoad:
    parameter: str
    concentration_mg_l: float
    load_kg_day: float


@dataclass
class DesignSummary:
    project_name: str
    wastewater_type: str

    average_flow_m3_day: float
    peak_flow_m3_day: float
    peak_factor: float

    influent_bod_mg_l: float
    influent_cod_mg_l: float
    influent_tss_mg_l: float
    ammonia_mg_l: float

    target_bod_mg_l: float
    target_tss_mg_l: float

    nitrification_required: bool

    pollutant_loads: List[PollutantLoad]

    treatment_level: str
    biological_process: str

    process_flow: List[str]
    process_reasons: List[str]

    design_basis: Dict[str, Any]


# ============================================================
# VALIDATION
# ============================================================

def _validate_non_negative(value: float, name: str) -> None:
    if value < 0:
        raise ValueError(f"{name} cannot be negative.")


def _validate_input(
    average_flow_m3_day: float,
    peak_flow_m3_day: float,
    influent_bod_mg_l: float,
    influent_cod_mg_l: float,
    influent_tss_mg_l: float,
    ammonia_mg_l: float,
    target_bod_mg_l: float,
    target_tss_mg_l: float,
) -> None:

    if average_flow_m3_day <= 0:
        raise ValueError(
            "Average flow must be greater than zero."
        )

    if peak_flow_m3_day <= 0:
        raise ValueError(
            "Peak flow must be greater than zero."
        )

    if peak_flow_m3_day < average_flow_m3_day:
        raise ValueError(
            "Peak flow cannot be less than average flow."
        )

    _validate_non_negative(
        influent_bod_mg_l,
        "Influent BOD",
    )

    _validate_non_negative(
        influent_cod_mg_l,
        "Influent COD",
    )

    _validate_non_negative(
        influent_tss_mg_l,
        "Influent TSS",
    )

    _validate_non_negative(
        ammonia_mg_l,
        "Ammonia",
    )

    _validate_non_negative(
        target_bod_mg_l,
        "Target BOD",
    )

    _validate_non_negative(
        target_tss_mg_l,
        "Target TSS",
    )


# ============================================================
# POLLUTANT LOAD
# ============================================================

def calculate_load_kg_day(
    flow_m3_day: float,
    concentration_mg_l: float,
) -> float:
    """
    Calculate pollutant load.

    Load (kg/day) =
        Q (m3/day) × C (mg/L) / 1000

    because:

        1 m3 = 1000 L
        1 kg = 1,000,000 mg
    """

    return flow_m3_day * concentration_mg_l / 1000.0


def calculate_pollutant_loads(
    average_flow_m3_day: float,
    influent_bod_mg_l: float,
    influent_cod_mg_l: float,
    influent_tss_mg_l: float,
    ammonia_mg_l: float,
) -> List[PollutantLoad]:

    return [
        PollutantLoad(
            parameter="BOD",
            concentration_mg_l=influent_bod_mg_l,
            load_kg_day=calculate_load_kg_day(
                average_flow_m3_day,
                influent_bod_mg_l,
            ),
        ),
        PollutantLoad(
            parameter="COD",
            concentration_mg_l=influent_cod_mg_l,
            load_kg_day=calculate_load_kg_day(
                average_flow_m3_day,
                influent_cod_mg_l,
            ),
        ),
        PollutantLoad(
            parameter="TSS",
            concentration_mg_l=influent_tss_mg_l,
            load_kg_day=calculate_load_kg_day(
                average_flow_m3_day,
                influent_tss_mg_l,
            ),
        ),
        PollutantLoad(
            parameter="Ammonia",
            concentration_mg_l=ammonia_mg_l,
            load_kg_day=calculate_load_kg_day(
                average_flow_m3_day,
                ammonia_mg_l,
            ),
        ),
    ]


# ============================================================
# PEAK FACTOR
# ============================================================

def calculate_peak_factor(
    average_flow_m3_day: float,
    peak_flow_m3_day: float,
) -> float:

    if average_flow_m3_day <= 0:
        raise ValueError(
            "Average flow must be greater than zero."
        )

    return peak_flow_m3_day / average_flow_m3_day


# ============================================================
# CENTRAL DESIGN FUNCTION
# ============================================================

def generate_wwtp_design(
    project_name: str,
    wastewater_type: str,
    average_flow_m3_day: float,
    peak_flow_m3_day: float,
    influent_bod_mg_l: float,
    influent_cod_mg_l: float,
    influent_tss_mg_l: float,
    ammonia_mg_l: float,
    target_bod_mg_l: float = 20,
    target_tss_mg_l: float = 10,
    nitrification_required: bool = False,
) -> DesignSummary:
    """
    Generate a complete preliminary WWTP design basis.
    """

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    _validate_input(
        average_flow_m3_day=average_flow_m3_day,
        peak_flow_m3_day=peak_flow_m3_day,
        influent_bod_mg_l=influent_bod_mg_l,
        influent_cod_mg_l=influent_cod_mg_l,
        influent_tss_mg_l=influent_tss_mg_l,
        ammonia_mg_l=ammonia_mg_l,
        target_bod_mg_l=target_bod_mg_l,
        target_tss_mg_l=target_tss_mg_l,
    )

    # --------------------------------------------------------
    # PEAK FACTOR
    # --------------------------------------------------------

    peak_factor = calculate_peak_factor(
        average_flow_m3_day,
        peak_flow_m3_day,
    )

    # --------------------------------------------------------
    # POLLUTANT LOADS
    # --------------------------------------------------------

    pollutant_loads = calculate_pollutant_loads(
        average_flow_m3_day=average_flow_m3_day,
        influent_bod_mg_l=influent_bod_mg_l,
        influent_cod_mg_l=influent_cod_mg_l,
        influent_tss_mg_l=influent_tss_mg_l,
        ammonia_mg_l=ammonia_mg_l,
    )

    # --------------------------------------------------------
    # PROCESS SELECTION
    # --------------------------------------------------------

    process = select_treatment_process(
        wastewater_type=wastewater_type,
        average_flow_m3_day=average_flow_m3_day,
        influent_bod_mg_l=influent_bod_mg_l,
        influent_cod_mg_l=influent_cod_mg_l,
        influent_tss_mg_l=influent_tss_mg_l,
        ammonia_mg_l=ammonia_mg_l,
        target_bod_mg_l=target_bod_mg_l,
        target_tss_mg_l=target_tss_mg_l,
        nitrification_required=nitrification_required,
    )

    # --------------------------------------------------------
    # DESIGN BASIS
    # --------------------------------------------------------

    design_basis = {
        "flow_basis": {
            "average_flow_m3_day": average_flow_m3_day,
            "peak_flow_m3_day": peak_flow_m3_day,
            "peak_factor": peak_factor,
        },

        "influent_quality": {
            "BOD_mg_L": influent_bod_mg_l,
            "COD_mg_L": influent_cod_mg_l,
            "TSS_mg_L": influent_tss_mg_l,
            "ammonia_mg_L": ammonia_mg_l,
        },

        "effluent_targets": {
            "BOD_mg_L": target_bod_mg_l,
            "TSS_mg_L": target_tss_mg_l,
        },

        "nitrification_required": nitrification_required,

        "pollutant_loads_kg_day": {
            load.parameter: load.load_kg_day
            for load in pollutant_loads
        },
    }

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    return DesignSummary(
        project_name=project_name,
        wastewater_type=wastewater_type,

        average_flow_m3_day=average_flow_m3_day,
        peak_flow_m3_day=peak_flow_m3_day,
        peak_factor=peak_factor,

        influent_bod_mg_l=influent_bod_mg_l,
        influent_cod_mg_l=influent_cod_mg_l,
        influent_tss_mg_l=influent_tss_mg_l,
        ammonia_mg_l=ammonia_mg_l,

        target_bod_mg_l=target_bod_mg_l,
        target_tss_mg_l=target_tss_mg_l,

        nitrification_required=nitrification_required,

        pollutant_loads=pollutant_loads,

        treatment_level=process.treatment_level,
        biological_process=process.biological_process,

        process_flow=process.process_flow,
        process_reasons=process.reasons,

        design_basis=design_basis,
    )


# ============================================================
# SERIALIZATION HELPER
# ============================================================

def design_to_dict(
    design: DesignSummary,
) -> Dict[str, Any]:
    """
    Convert design result into JSON-compatible dictionary.
    """

    result = asdict(design)

    return result