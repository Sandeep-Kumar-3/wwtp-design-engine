from dataclasses import asdict, dataclass
from typing import Dict, List


@dataclass
class StreamPoint:
    stage: str
    parameter: str
    concentration_mg_l: float
    load_kg_day: float
    removal_from_previous_percent: float


@dataclass
class ParameterBalance:
    parameter: str
    influent_concentration_mg_l: float
    final_concentration_mg_l: float
    influent_load_kg_day: float
    final_load_kg_day: float
    overall_removal_percent: float
    streams: List[StreamPoint]


@dataclass
class PlantMassBalance:
    flow_m3_day: float
    parameters: Dict[str, ParameterBalance]
    assumptions: List[str]


def _load(flow_m3_day: float, concentration_mg_l: float) -> float:
    return flow_m3_day * concentration_mg_l / 1000.0


def _stage(
    flow: float,
    parameter: str,
    previous: float,
    removal_percent: float,
    stage_name: str,
) -> StreamPoint:
    removal = max(0.0, min(100.0, removal_percent))
    concentration = previous * (1.0 - removal / 100.0)
    return StreamPoint(
        stage=stage_name,
        parameter=parameter,
        concentration_mg_l=concentration,
        load_kg_day=_load(flow, concentration),
        removal_from_previous_percent=removal,
    )


def _balance(
    flow: float,
    parameter: str,
    influent: float,
    removals: List[tuple[str, float]],
) -> ParameterBalance:
    current = max(0.0, influent)
    streams = [
        StreamPoint(
            stage="Influent",
            parameter=parameter,
            concentration_mg_l=current,
            load_kg_day=_load(flow, current),
            removal_from_previous_percent=0.0,
        )
    ]
    for stage_name, removal in removals:
        point = _stage(flow, parameter, current, removal, stage_name)
        streams.append(point)
        current = point.concentration_mg_l

    influent_load = _load(flow, influent)
    final_load = _load(flow, current)
    overall = ((influent - current) / influent * 100.0) if influent > 0 else 0.0
    return ParameterBalance(
        parameter=parameter,
        influent_concentration_mg_l=influent,
        final_concentration_mg_l=current,
        influent_load_kg_day=influent_load,
        final_load_kg_day=final_load,
        overall_removal_percent=overall,
        streams=streams,
    )


def calculate_plant_mass_balance(
    flow_m3_day: float,
    influent_bod_mg_l: float,
    influent_cod_mg_l: float,
    influent_tss_mg_l: float,
    target_bod_mg_l: float,
    target_tss_mg_l: float,
) -> PlantMassBalance:
    """Create a preliminary plant-wide pollutant balance.

    This is a process-design accounting model, not a process-performance
    guarantee. Unit removals are explicit preliminary assumptions and are
    returned with the balance so they can be replaced by project data.
    """
    if flow_m3_day <= 0:
        raise ValueError("Flow must be greater than zero.")
    values = [
        influent_bod_mg_l,
        influent_cod_mg_l,
        influent_tss_mg_l,
        target_bod_mg_l,
        target_tss_mg_l,
    ]
    if any(value < 0 for value in values):
        raise ValueError("Mass-balance concentrations cannot be negative.")

    # Preliminary accounting assumptions. Final concentrations for BOD/TSS
    # are constrained to the requested targets where those targets are lower.
    primary_bod = 30.0
    primary_tss = 60.0
    primary_cod = 25.0
    secondary_tss = 85.0

    bod_after_primary = influent_bod_mg_l * (1 - primary_bod / 100)
    bod_bio_removal = (
        max(0.0, min(100.0, (1 - target_bod_mg_l / bod_after_primary) * 100))
        if bod_after_primary > 0
        else 0.0
    )
    tss_after_primary = influent_tss_mg_l * (1 - primary_tss / 100)
    tss_after_secondary = tss_after_primary * (1 - secondary_tss / 100)
    tss_filter_removal = (
        max(0.0, min(100.0, (1 - target_tss_mg_l / tss_after_secondary) * 100))
        if tss_after_secondary > 0
        else 0.0
    )

    # COD has no user-specified final criterion in the current design basis;
    # keep a transparent preliminary biological polishing assumption.
    cod_bio = 65.0

    parameters = {
        "BOD": _balance(
            flow_m3_day,
            "BOD",
            influent_bod_mg_l,
            [
                ("Primary Clarifier", primary_bod),
                ("Biological Treatment", bod_bio_removal),
            ],
        ),
        "TSS": _balance(
            flow_m3_day,
            "TSS",
            influent_tss_mg_l,
            [
                ("Primary Clarifier", primary_tss),
                ("Secondary Clarifier", secondary_tss),
                ("Tertiary Filtration", tss_filter_removal),
            ],
        ),
        "COD": _balance(
            flow_m3_day,
            "COD",
            influent_cod_mg_l,
            [
                ("Primary Clarifier", primary_cod),
                ("Biological Treatment", cod_bio),
            ],
        ),
    }

    assumptions = [
        "Primary BOD removal assumed at 30% for preliminary accounting.",
        "Primary TSS removal assumed at 60% for preliminary accounting.",
        "Secondary TSS removal assumed at 85% before tertiary polishing.",
        "COD biological removal assumed at 65% because no COD effluent target is currently entered.",
        "BOD and TSS final concentrations are constrained to the user-entered targets where applicable.",
        "Replace assumed removals with project-specific jar tests, pilot data, or validated design criteria for final design.",
    ]

    return PlantMassBalance(
        flow_m3_day=flow_m3_day,
        parameters=parameters,
        assumptions=assumptions,
    )
