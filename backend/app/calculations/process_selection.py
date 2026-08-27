"""
WWTP Treatment Process Selection Engine

Automatically recommends a preliminary treatment train based on:
- wastewater type
- flow
- BOD
- COD
- TSS
- ammonia
- required nitrification
- target BOD
- target TSS

This is a preliminary engineering decision-support model.
Final process selection requires detailed site-specific engineering.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class TreatmentUnit:
    """Represents one treatment unit in the recommended process."""

    stage: int
    unit: str
    purpose: str
    required: bool


@dataclass
class ProcessSelection:
    """Complete preliminary treatment-process recommendation."""

    wastewater_type: str
    treatment_level: str
    nitrification_required: bool

    units: List[TreatmentUnit]

    process_flow: List[str]
    biological_process: str

    reasons: List[str]


def select_treatment_process(
    wastewater_type: str,
    average_flow_m3_day: float,
    influent_bod_mg_l: float,
    influent_cod_mg_l: float,
    influent_tss_mg_l: float,
    ammonia_mg_l: float,
    target_bod_mg_l: float = 20,
    target_tss_mg_l: float = 10,
    nitrification_required: bool = False,
) -> ProcessSelection:
    """
    Select a preliminary WWTP treatment train.

    Parameters
    ----------
    wastewater_type:
        municipal, industrial, domestic, etc.

    average_flow_m3_day:
        Average wastewater flow.

    influent_bod_mg_l:
        Influent BOD concentration.

    influent_cod_mg_l:
        Influent COD concentration.

    influent_tss_mg_l:
        Influent TSS concentration.

    ammonia_mg_l:
        Influent ammonia concentration.

    target_bod_mg_l:
        Required final BOD.

    target_tss_mg_l:
        Required final TSS.

    nitrification_required:
        Whether nitrification is explicitly required.
    """

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    if average_flow_m3_day <= 0:
        raise ValueError("Average flow must be greater than zero.")

    if influent_bod_mg_l < 0:
        raise ValueError("Influent BOD cannot be negative.")

    if influent_cod_mg_l < 0:
        raise ValueError("Influent COD cannot be negative.")

    if influent_tss_mg_l < 0:
        raise ValueError("Influent TSS cannot be negative.")

    if ammonia_mg_l < 0:
        raise ValueError("Ammonia cannot be negative.")

    if target_bod_mg_l < 0:
        raise ValueError("Target BOD cannot be negative.")

    if target_tss_mg_l < 0:
        raise ValueError("Target TSS cannot be negative.")

    wastewater_type = wastewater_type.lower().strip()

    # ---------------------------------------------------------
    # BASIC PROCESS
    # ---------------------------------------------------------

    units = []
    reasons = []

    def add_unit(stage, unit, purpose):
        units.append(
            TreatmentUnit(
                stage=stage,
                unit=unit,
                purpose=purpose,
                required=True,
            )
        )

    # ---------------------------------------------------------
    # 1. PRELIMINARY TREATMENT
    # ---------------------------------------------------------

    add_unit(
        1,
        "Screening",
        "Removal of coarse solids, plastics, rags and large debris.",
    )

    add_unit(
        2,
        "Grit Removal",
        "Removal of sand, grit and other dense inorganic particles.",
    )

    reasons.append(
        "Preliminary treatment is required to protect downstream equipment."
    )

    # ---------------------------------------------------------
    # 2. EQUALIZATION
    # ---------------------------------------------------------

    # Industrial wastewater generally has greater flow/load variation.
    if wastewater_type in {
        "industrial",
        "industrial wastewater",
        "mixed industrial",
    }:
        add_unit(
            3,
            "Equalization Tank",
            "Reduces flow and pollutant-load fluctuations before biological treatment.",
        )

        reasons.append(
            "Equalization is recommended because industrial wastewater "
            "can have significant flow and load variability."
        )

        next_stage = 4

    else:
        next_stage = 3

    # ---------------------------------------------------------
    # 3. PRIMARY TREATMENT
    # ---------------------------------------------------------

    # Primary clarification becomes particularly useful when
    # particulate loading is significant.
    high_tss = influent_tss_mg_l >= 200
    high_bod = influent_bod_mg_l >= 200

    if high_tss or high_bod or wastewater_type == "municipal":

        add_unit(
            next_stage,
            "Primary Clarifier",
            "Settling of primary suspended solids and removal of a portion of organic load.",
        )

        reasons.append(
            "Primary clarification is recommended because of the "
            "influent solids/organic loading."
        )

        next_stage += 1

    # ---------------------------------------------------------
    # 4. BIOLOGICAL PROCESS
    # ---------------------------------------------------------

    # Calculate BOD/COD ratio when possible.
    if influent_cod_mg_l > 0:
        bod_cod_ratio = influent_bod_mg_l / influent_cod_mg_l
    else:
        bod_cod_ratio = 0

    # Industrial wastewater with poor biodegradability may require
    # specialized treatment.
    if wastewater_type in {
        "industrial",
        "industrial wastewater",
        "mixed industrial",
    } and bod_cod_ratio < 0.3:

        biological_process = "Physico-chemical + Biological Treatment"

        reasons.append(
            "Low BOD/COD ratio indicates potentially lower biodegradability; "
            "additional physico-chemical treatment may be required."
        )

    elif nitrification_required or ammonia_mg_l >= 20:

        biological_process = "Activated Sludge with Nitrification"

        reasons.append(
            "Nitrification is included because ammonia removal is required "
            "or ammonia concentration is significant."
        )

    else:

        biological_process = "Activated Sludge"

        reasons.append(
            "Conventional biological treatment is recommended for "
            "biodegradable organic matter removal."
        )

    add_unit(
        next_stage,
        biological_process,
        "Biological removal of dissolved and biodegradable organic matter.",
    )

    next_stage += 1

    # ---------------------------------------------------------
    # 5. SECONDARY CLARIFIER
    # ---------------------------------------------------------

    add_unit(
        next_stage,
        "Secondary Clarifier",
        "Separates biological solids from treated wastewater.",
    )

    next_stage += 1

    # ---------------------------------------------------------
    # 6. TERTIARY FILTRATION
    # ---------------------------------------------------------

    # Filtration is recommended when a low TSS target is specified.
    if target_tss_mg_l <= 10 or influent_tss_mg_l >= 250:

        add_unit(
            next_stage,
            "Tertiary Filtration",
            "Polishing treatment for removal of residual suspended solids.",
        )

        reasons.append(
            "Tertiary filtration is recommended to achieve the low "
            "target suspended-solids concentration."
        )

        next_stage += 1

    # ---------------------------------------------------------
    # 7. DISINFECTION
    # ---------------------------------------------------------

    add_unit(
        next_stage,
        "Disinfection",
        "Inactivation of pathogenic microorganisms before discharge or reuse.",
    )

    next_stage += 1

    reasons.append(
        "Disinfection is included as the final pathogen-control barrier."
    )

    # ---------------------------------------------------------
    # 8. SLUDGE TREATMENT
    # ---------------------------------------------------------

    add_unit(
        next_stage,
        "Sludge Treatment and Dewatering",
        "Thickening, stabilization and dewatering of generated sludge.",
    )

    # ---------------------------------------------------------
    # TREATMENT LEVEL
    # ---------------------------------------------------------

    has_tertiary = any(
        unit.unit == "Tertiary Filtration"
        for unit in units
    )

    if has_tertiary:
        treatment_level = "Secondary + Tertiary Treatment"
    else:
        treatment_level = "Secondary Treatment"

    # ---------------------------------------------------------
    # PROCESS FLOW
    # ---------------------------------------------------------

    process_flow = [unit.unit for unit in units]

    return ProcessSelection(
        wastewater_type=wastewater_type,
        treatment_level=treatment_level,
        nitrification_required=nitrification_required,
        units=units,
        process_flow=process_flow,
        biological_process=biological_process,
        reasons=reasons,
    )