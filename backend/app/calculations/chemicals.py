from dataclasses import dataclass


@dataclass
class ChemicalDesign:
    chlorine_dose_mg_l: float
    chlorine_required_kg_day: float
    chlorine_annual_kg: float

    alum_dose_mg_l: float
    alum_required_kg_day: float
    alum_annual_kg: float

    polymer_dose_mg_l: float
    polymer_required_kg_day: float
    polymer_annual_kg: float


def design_chemicals(
    flow_m3_day: float,
    chlorine_dose_mg_l: float = 5.0,
    alum_dose_mg_l: float = 0.0,
    polymer_dose_mg_l: float = 0.0,
) -> ChemicalDesign:

    if flow_m3_day <= 0:
        raise ValueError("Flow must be greater than zero.")

    doses = [
        chlorine_dose_mg_l,
        alum_dose_mg_l,
        polymer_dose_mg_l,
    ]

    if any(dose < 0 for dose in doses):
        raise ValueError("Chemical dose cannot be negative.")

    chlorine = (
        flow_m3_day
        * chlorine_dose_mg_l
        / 1000
    )

    alum = (
        flow_m3_day
        * alum_dose_mg_l
        / 1000
    )

    polymer = (
        flow_m3_day
        * polymer_dose_mg_l
        / 1000
    )

    return ChemicalDesign(
        chlorine_dose_mg_l=chlorine_dose_mg_l,
        chlorine_required_kg_day=chlorine,
        chlorine_annual_kg=chlorine * 365,

        alum_dose_mg_l=alum_dose_mg_l,
        alum_required_kg_day=alum,
        alum_annual_kg=alum * 365,

        polymer_dose_mg_l=polymer_dose_mg_l,
        polymer_required_kg_day=polymer,
        polymer_annual_kg=polymer * 365,
    )