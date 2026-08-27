from typing import Dict, Any


def recommend_treatment_process(
    wastewater_type: str,
    average_flow_m3_day: float,
    bod_mg_l: float,
    cod_mg_l: float,
    tss_mg_l: float,
    ammonia_mg_l: float,
    nitrification_required: bool,
) -> Dict[str, Any]:

    wastewater_type = wastewater_type.lower()

    processes = [
        {
            "stage": 1,
            "unit": "Preliminary Treatment",
            "processes": [
                "Coarse Screening",
                "Fine Screening",
                "Grit Removal",
            ],
            "reason": (
                "Removal of large solids, rags and grit "
                "to protect downstream equipment."
            ),
        }
    ]

    # Industrial wastewater generally benefits
    # from flow/equalization control.

    if wastewater_type == "industrial":

        processes.append(
            {
                "stage": 2,
                "unit": "Equalization",
                "processes": [
                    "Equalization Tank"
                ],
                "reason": (
                    "Industrial wastewater can have significant "
                    "flow and pollutant concentration variations."
                ),
            }
        )

        # High-strength wastewater.

        if cod_mg_l > 1000 or bod_mg_l > 500:

            processes.append(
                {
                    "stage": 3,
                    "unit": "Physico-Chemical Pretreatment",
                    "processes": [
                        "pH Adjustment",
                        "Coagulation",
                        "Flocculation",
                        "Primary Clarification",
                    ],
                    "reason": (
                        "High-strength industrial wastewater "
                        "may require pretreatment before biological treatment."
                    ),
                }
            )

    else:

        processes.append(
            {
                "stage": 2,
                "unit": "Primary Treatment",
                "processes": [
                    "Primary Clarification"
                ],
                "reason": (
                    "Removal of settleable solids and "
                    "a portion of organic load."
                ),
            }
        )

    # Biological treatment

    biological_process = "Activated Sludge"

    if nitrification_required or ammonia_mg_l > 20:
        biological_process = (
            "Activated Sludge with Nitrification"
        )

    processes.append(
        {
            "stage": len(processes) + 1,
            "unit": "Biological Treatment",
            "processes": [
                biological_process
            ],
            "reason": (
                "Biological treatment is required to "
                "reduce biodegradable organic matter."
            ),
        }
    )

    # Secondary clarification

    processes.append(
        {
            "stage": len(processes) + 1,
            "unit": "Secondary Treatment",
            "processes": [
                "Secondary Clarification",
                "RAS",
                "WAS",
            ],
            "reason": (
                "Separates biological solids from treated wastewater "
                "and returns activated sludge to the biological reactor."
            ),
        }
    )

    # Tertiary

    processes.append(
        {
            "stage": len(processes) + 1,
            "unit": "Tertiary Treatment",
            "processes": [
                "Tertiary Filtration"
            ],
            "reason": (
                "Polishing treatment for suspended solids "
                "and improved final effluent quality."
            ),
        }
    )

    # Disinfection

    processes.append(
        {
            "stage": len(processes) + 1,
            "unit": "Disinfection",
            "processes": [
                "Chlorination"
            ],
            "reason": (
                "Reduction of pathogenic microorganisms "
                "before final discharge or reuse."
            ),
        }
    )

    # Sludge

    processes.append(
        {
            "stage": len(processes) + 1,
            "unit": "Sludge Treatment",
            "processes": [
                "Sludge Thickening",
                "Anaerobic Digestion",
                "Sludge Dewatering",
            ],
            "reason": (
                "Reduction and stabilization of generated sludge."
            ),
        }
    )

    return {
        "treatment_train": processes,
        "design_notes": [
            "Final process selection must be validated against "
            "site-specific wastewater characterization.",
            "Industrial wastewater may require pilot testing.",
            "Applicable discharge/reuse standards must be verified "
            "for the project location.",
        ],
    }