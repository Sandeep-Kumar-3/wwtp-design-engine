from typing import Dict, Any


MUNICIPAL_CRITERIA: Dict[str, Any] = {
    "biological_process": {
        "process": "Activated Sludge Process",
        "mlss_mg_l": 3000,
        "mlvss_to_mlss_ratio": 0.80,
        "fm_ratio": 0.20,
        "srt_days": 10,
        "biomass_yield_kg_kg_bod": 0.50,
        "endogenous_decay_rate_per_day": 0.06,
    },

    "secondary_clarifier": {
        "number_of_units": 2,
        "surface_overflow_rate_m3_m2_day": 25,
        "solids_loading_rate_kg_m2_day": 100,
        "water_depth_m": 3.5,
        "weir_loading_m3_m_day": 250,
    },

    "ras_was": {
        "ras_ratio": 0.30,
        "srt_days": 10,
        "was_concentration_mg_l": 10000,
    },

    "filtration": {
        "filtration_rate_m3_m2_day": 10,
        "number_of_filters": 5,
        "length_to_width_ratio": 1.5,
    },

    "disinfection": {
        "method": "chlorination",
        "chlorine_dose_mg_l": 5,
        "contact_time_min": 30,
        "water_depth_m": 2,
    },

    "sludge_thickening": {
        "influent_solids_percent": 1,
        "target_solids_percent": 4,
    },

    "digestion": {
        "solids_concentration_percent": 4,
        "volatile_solids_fraction": 0.70,
        "destruction_fraction": 0.50,
        "gas_yield_m3_kg_vs_destroyed": 0.8,
        "methane_fraction": 0.65,
        "digestion_srt_days": 20,
    },
}


INDUSTRIAL_CRITERIA: Dict[str, Any] = {
    "biological_process": {
        "process": "Activated Sludge Process",
        "mlss_mg_l": 3500,
        "mlvss_to_mlss_ratio": 0.80,
        "fm_ratio": 0.15,
        "srt_days": 15,
        "biomass_yield_kg_kg_bod": 0.50,
        "endogenous_decay_rate_per_day": 0.06,
    },

    "secondary_clarifier": {
        "number_of_units": 2,
        "surface_overflow_rate_m3_m2_day": 20,
        "solids_loading_rate_kg_m2_day": 90,
        "water_depth_m": 3.5,
        "weir_loading_m3_m_day": 200,
    },

    "ras_was": {
        "ras_ratio": 0.40,
        "srt_days": 15,
        "was_concentration_mg_l": 12000,
    },

    "filtration": {
        "filtration_rate_m3_m2_day": 8,
        "number_of_filters": 5,
        "length_to_width_ratio": 1.5,
    },

    "disinfection": {
        "method": "chlorination",
        "chlorine_dose_mg_l": 5,
        "contact_time_min": 30,
        "water_depth_m": 2,
    },

    "sludge_thickening": {
        "influent_solids_percent": 1.5,
        "target_solids_percent": 5,
    },

    "digestion": {
        "solids_concentration_percent": 5,
        "volatile_solids_fraction": 0.70,
        "destruction_fraction": 0.50,
        "gas_yield_m3_kg_vs_destroyed": 0.8,
        "methane_fraction": 0.65,
        "digestion_srt_days": 20,
    },
}


def get_design_criteria(
    wastewater_type: str,
) -> Dict[str, Any]:

    wastewater_type = wastewater_type.lower()

    if wastewater_type == "municipal":
        return MUNICIPAL_CRITERIA

    if wastewater_type == "industrial":
        return INDUSTRIAL_CRITERIA

    raise ValueError(
        f"Unsupported wastewater type: {wastewater_type}"
    )