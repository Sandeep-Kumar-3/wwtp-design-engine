from dataclasses import dataclass


@dataclass
class TreatmentStage:
    sequence: int
    unit: str
    purpose: str
    required: bool
    design_basis: str


@dataclass
class TreatmentTrain:
    process_type: str
    stages: list
    explanation: str


def recommend_treatment_train(
    wastewater_type: str,
    bod_mg_l: float,
    cod_mg_l: float,
    tss_mg_l: float,
    ammonia_mg_l: float,
    nitrification_required: bool = False,
) -> TreatmentTrain:

    wastewater_type = wastewater_type.lower().strip()

    if wastewater_type not in {
        "municipal",
        "industrial",
    }:
        raise ValueError(
            "Wastewater type must be municipal or industrial."
        )

    if min(
        bod_mg_l,
        cod_mg_l,
        tss_mg_l,
        ammonia_mg_l,
    ) < 0:
        raise ValueError(
            "Water quality parameters cannot be negative."
        )

    stages = []

    sequence = 1

    stages.append(
        TreatmentStage(
            sequence,
            "Inlet Works",
            "Flow measurement and preliminary control",
            True,
            "Design flow",
        )
    )

    sequence += 1

    stages.append(
        TreatmentStage(
            sequence,
            "Screening",
            "Removal of coarse floating and suspended material",
            True,
            "Influent characteristics",
        )
    )

    sequence += 1

    stages.append(
        TreatmentStage(
            sequence,
            "Grit Removal",
            "Removal of sand, grit and dense inorganic particles",
            True,
            "Municipal/industrial influent",
        )
    )

    sequence += 1

    if wastewater_type == "industrial":

        stages.append(
            TreatmentStage(
                sequence,
                "Equalization",
                "Flow and pollutant load balancing",
                True,
                "Industrial wastewater variability",
            )
        )

        sequence += 1

        if cod_mg_l > 1000:
            stages.append(
                TreatmentStage(
                    sequence,
                    "Primary Physico-Chemical Treatment",
                    "Reduction of high particulate/chemical loads",
                    True,
                    "High COD",
                )
            )
            sequence += 1

    if wastewater_type == "municipal" or bod_mg_l > 100:

        stages.append(
            TreatmentStage(
                sequence,
                "Primary Clarification",
                "Removal of settleable solids and part of organic load",
                True,
                "BOD/TSS loading",
            )
        )

        sequence += 1

    stages.append(
        TreatmentStage(
            sequence,
            "Biological Treatment",
            "Biological oxidation of biodegradable organic matter",
            True,
            "BOD/COD",
        )
    )

    sequence += 1

    if nitrification_required or ammonia_mg_l > 15:

        stages.append(
            TreatmentStage(
                sequence,
                "Nitrification",
                "Biological oxidation of ammonia",
                True,
                "Ammonia concentration/target",
            )
        )

        sequence += 1

    stages.append(
        TreatmentStage(
            sequence,
            "Secondary Clarification",
            "Separation of biological solids",
            True,
            "Activated sludge process",
        )
    )

    sequence += 1

    if tss_mg_l > 20:

        stages.append(
            TreatmentStage(
                sequence,
                "Tertiary Filtration",
                "Final suspended solids polishing",
                True,
                "TSS target",
            )
        )

        sequence += 1

    stages.append(
        TreatmentStage(
            sequence,
            "Disinfection",
            "Pathogen reduction",
            True,
            "Reuse/discharge requirements",
        )
    )

    sequence += 1

    stages.append(
        TreatmentStage(
            sequence,
            "Treated Effluent",
            "Final discharge/reuse stream",
            True,
            "Final effluent requirements",
        )
    )

    explanation = (
        "The treatment train is automatically selected from "
        "wastewater type, organic loading, suspended solids, "
        "ammonia concentration and nitrification requirements."
    )

    return TreatmentTrain(
        process_type=(
            "Industrial treatment train"
            if wastewater_type == "industrial"
            else "Municipal treatment train"
        ),
        stages=stages,
        explanation=explanation,
    )