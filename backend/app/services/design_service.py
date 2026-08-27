from dataclasses import asdict, is_dataclass
from typing import Any

from app.calculations.design_engine import (
    generate_wwtp_design,
    design_to_dict,
)
from app.calculations.process_selection import select_treatment_process
from app.calculations.treatment_train import recommend_treatment_train
from app.calculations.flow import calculate_flow
from app.calculations.loads import calculate_wastewater_loads
from app.calculations.hydraulics import calculate_hydraulic_loads
from app.calculations.preliminary import design_screening, design_grit_chamber
from app.calculations.primary import design_primary_clarifier
from app.calculations.biological import design_biological_treatment
from app.calculations.aeration import design_aeration
from app.calculations.secondary import design_secondary_clarifier
from app.calculations.filtration import design_filtration
from app.calculations.disinfection import design_chlorination
from app.calculations.sludge import (
    calculate_sludge_production,
    design_sludge,
)
from app.calculations.pumps import design_pumps
from app.calculations.blower import design_blowers
from app.calculations.chemicals import design_chemicals
from app.calculations.energy import calculate_energy
from app.calculations.equipment_schedule import generate_equipment_schedule
from app.calculations.hydraulic_profile import create_hydraulic_profile
from app.calculations.mass_balance import calculate_mass_balance
from app.calculations.plant_mass_balance import calculate_plant_mass_balance
from app.calculations.final_effluent import calculate_final_effluent
from app.services.design_criteria import get_design_criteria
from app.services.engineering_checks import build_engineering_checks


def _serialize(value: Any) -> Any:
    """Convert dataclasses and nested objects into JSON-safe structures."""
    if is_dataclass(value):
        return asdict(value)

    if isinstance(value, list):
        return [_serialize(item) for item in value]

    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}

    return value


def _get(project, name, default=None):
    """Safely read a ProjectInput field."""
    return getattr(project, name, default)


def generate_design(project):
    """
    Main WWTP design orchestration service.

    Keeps the existing calculation modules independent while assembling
    their outputs into one complete engineering design response.
    """

    project_name = _get(project, "project_name", "WWTP Design")
    wastewater_type = _get(project, "wastewater_type", "municipal")

    average_flow = _get(
        project,
        "average_flow_m3_day",
        _get(project, "flow_m3_day", 0),
    )

    peak_flow = _get(
        project,
        "peak_flow_m3_day",
        average_flow * _get(project, "peak_factor", 2.5),
    )

    bod = _get(project, "influent_bod_mg_l", 250.0)
    cod = _get(project, "influent_cod_mg_l", 500.0)
    tss = _get(project, "influent_tss_mg_l", 300.0)
    ammonia = _get(project, "ammonia_mg_l", 30.0)

    target_bod = _get(project, "target_bod_mg_l", 20.0)
    target_tss = _get(project, "target_tss_mg_l", 10.0)
    nitrification = _get(
        project,
        "nitrification_required",
        False,
    )

    if average_flow <= 0:
        raise ValueError("Average flow must be greater than zero.")

    if peak_flow <= 0:
        peak_flow = average_flow * 2.5

    criteria = get_design_criteria(wastewater_type)

    # ---------------------------------------------------------
    # 1. Core design-engine calculation
    # ---------------------------------------------------------

    core_design = generate_wwtp_design(
        project_name=project_name,
        wastewater_type=wastewater_type,
        average_flow_m3_day=average_flow,
        peak_flow_m3_day=peak_flow,
        influent_bod_mg_l=bod,
        influent_cod_mg_l=cod,
        influent_tss_mg_l=tss,
        ammonia_mg_l=ammonia,
        target_bod_mg_l=target_bod,
        target_tss_mg_l=target_tss,
        nitrification_required=nitrification,
    )

    # ---------------------------------------------------------
    # 2. Flow
    # ---------------------------------------------------------

    average_mld = average_flow / 1000.0
    peak_factor = peak_flow / average_flow

    flow_design = calculate_flow(
        average_mld=average_mld,
        peak_factor=peak_factor,
    )

    # ---------------------------------------------------------
    # 3. Pollutant loads
    # ---------------------------------------------------------

    loads = calculate_wastewater_loads(
        flow_m3_day=average_flow,
        bod=bod,
        cod=cod,
        tss=tss,
        nh4_n=ammonia,
    )

    hydraulic_loads = calculate_hydraulic_loads(
        average_flow_m3_day=average_flow,
        peak_flow_m3_day=peak_flow,
        bod_mg_l=bod,
        cod_mg_l=cod,
        tss_mg_l=tss,
        ammonia_mg_l=ammonia,
    )

    # ---------------------------------------------------------
    # 4. Process selection
    # ---------------------------------------------------------

    process_selection = select_treatment_process(
        wastewater_type=wastewater_type,
        average_flow_m3_day=average_flow,
        influent_bod_mg_l=bod,
        influent_cod_mg_l=cod,
        influent_tss_mg_l=tss,
        ammonia_mg_l=ammonia,
        target_bod_mg_l=target_bod,
        target_tss_mg_l=target_tss,
        nitrification_required=nitrification,
    )

    treatment_train = recommend_treatment_train(
        wastewater_type=wastewater_type,
        bod_mg_l=bod,
        cod_mg_l=cod,
        tss_mg_l=tss,
        ammonia_mg_l=ammonia,
        nitrification_required=nitrification,
    )

    # ---------------------------------------------------------
    # 5. Preliminary treatment
    # ---------------------------------------------------------

    screening = design_screening(
        peak_flow_m3_day=peak_flow,
    )

    grit = design_grit_chamber(
        peak_flow_m3_day=peak_flow,
    )

    # ---------------------------------------------------------
    # 6. Primary clarification
    # ---------------------------------------------------------

    primary = design_primary_clarifier(
        average_flow_m3_day=average_flow,
        influent_bod_mg_l=bod,
        influent_tss_mg_l=tss,
    )

    # The biological reactor receives primary-clarifier effluent.
    # Carry that removal forward so organic loading, oxygen demand and
    # sludge production do not double-count the same BOD.
    primary_bod_removal = primary.bod_removal_percent / 100.0
    primary_tss_removal = primary.tss_removal_percent / 100.0
    post_primary_bod_mg_l = bod * (1.0 - primary_bod_removal)
    post_primary_tss_mg_l = tss * (1.0 - primary_tss_removal)

    # ---------------------------------------------------------
    # 7. Biological treatment
    # ---------------------------------------------------------

    biological = design_biological_treatment(
        design_flow_m3_day=average_flow,
        influent_bod_mg_l=post_primary_bod_mg_l,
        effluent_bod_mg_l=target_bod,
        mlss_mg_l=criteria["biological_process"]["mlss_mg_l"],
        f_m_ratio=criteria["biological_process"]["fm_ratio"],
    )

    aeration = design_aeration(
        average_flow_m3_day=average_flow,
        influent_bod_mg_l=post_primary_bod_mg_l,
        target_bod_mg_l=target_bod,
        ammonia_mg_l=ammonia,
        nitrification_required=nitrification,
        mlss_mg_l=criteria["biological_process"]["mlss_mg_l"],
        f_m_ratio=criteria["biological_process"]["fm_ratio"],
        srt_day=criteria["biological_process"]["srt_days"],
    )

    mlvss_fraction = criteria["biological_process"]["mlvss_to_mlss_ratio"]
    mlvss_mg_l = criteria["biological_process"]["mlss_mg_l"] * mlvss_fraction
    reactor_biomass_kg = aeration.aeration_tank_volume_m3 * mlvss_mg_l / 1000.0
    biological_feed_kg_day = average_flow * post_primary_bod_mg_l / 1000.0
    calculated_fm_ratio = biological_feed_kg_day / reactor_biomass_kg if reactor_biomass_kg > 0 else 0.0

    # ---------------------------------------------------------
    # 8. Secondary clarification
    # ---------------------------------------------------------

    secondary = design_secondary_clarifier(
        average_flow_m3_day=peak_flow,
        number_of_units=criteria["secondary_clarifier"]["number_of_units"],
        surface_overflow_rate_m3_m2_day=criteria["secondary_clarifier"]["surface_overflow_rate_m3_m2_day"],
        water_depth_m=criteria["secondary_clarifier"]["water_depth_m"],
    )
    secondary_dict = _serialize(secondary)
    secondary_dict["average_flow_detention_time_hr"] = secondary.total_volume_m3 / average_flow * 24.0
    secondary_dict["peak_surface_overflow_rate_m3_m2_day"] = peak_flow / secondary.required_surface_area_m2

    # ---------------------------------------------------------
    # 9. Tertiary filtration
    # ---------------------------------------------------------

    filtration = design_filtration(
        flow_m3_day=average_flow,
        filtration_rate_m3_m2_day=criteria["filtration"]["filtration_rate_m3_m2_day"],
        number_of_filters=criteria["filtration"]["number_of_filters"],
        filter_length_to_width_ratio=criteria["filtration"]["length_to_width_ratio"],
    )
    filtration_dict = _serialize(filtration)
    operating_area = filtration.required_filter_area_m2 / filtration.operating_filters
    filter_ratio = criteria["filtration"]["length_to_width_ratio"]
    operating_width = (operating_area / filter_ratio) ** 0.5
    operating_length = operating_width * filter_ratio
    filtration_dict["area_per_operating_filter_m2"] = operating_area
    filtration_dict["installed_area_m2"] = operating_area * filtration.number_of_filters
    filtration_dict["area_per_filter_m2"] = operating_area
    filtration_dict["filter_width_m"] = operating_width
    filtration_dict["filter_length_m"] = operating_length
    # ---------------------------------------------------------
    # 10. Disinfection
    # ---------------------------------------------------------

    chlorination = design_chlorination(
        peak_flow_m3_day=peak_flow,
        chlorine_dose_mg_l=criteria["disinfection"]["chlorine_dose_mg_l"],
        contact_time_min=criteria["disinfection"]["contact_time_min"],
        water_depth_m=criteria["disinfection"]["water_depth_m"],
    )

    # ---------------------------------------------------------
    # 11. Sludge
    # ---------------------------------------------------------

    primary_tss_removed = (
        tss
        * average_flow
        / 1000.0
        * primary_tss_removal
    )

    sludge_production = calculate_sludge_production(
        primary_tss_removed_kg_day=primary_tss_removed,
        biological_bod_load_kg_day=biological.bod_removed_kg_day,
        biological_yield=criteria["biological_process"]["biomass_yield_kg_kg_bod"],
    )

    sludge = design_sludge(
        flow_m3_day=average_flow,
        influent_tss_mg_l=tss,
        biological_solids_kg_day=sludge_production.secondary_sludge_kg_ds_day,
    )

    # ---------------------------------------------------------
    # 12. Pumps / blowers / chemicals
    # ---------------------------------------------------------

    pumps = design_pumps(
        flow_m3_day=peak_flow,
    )

    blowers = design_blowers(
        oxygen_demand_kg_day=aeration.design_oxygen_demand_kg_day,
    )

    chemicals = design_chemicals(
        flow_m3_day=average_flow,
    )

    # ---------------------------------------------------------
    # 13. Energy
    # ---------------------------------------------------------

    energy = calculate_energy(
        average_flow_m3_day=average_flow,
        aeration_power_kw=blowers.estimated_power_kw,
        pumping_power_kw=pumps.required_power_kw,
    )

    # ---------------------------------------------------------
    # 14. Equipment schedule
    # ---------------------------------------------------------

    equipment = generate_equipment_schedule(
        number_of_screens=screening.number_of_channels,
        number_of_grit_units=grit.number_of_units,
        number_of_primary_clarifiers=primary.number_of_units,
        number_of_aeration_tanks=aeration.number_of_aeration_tanks,
        number_of_secondary_clarifiers=secondary.number_of_units,
        number_of_filters=filtration.number_of_filters,
        number_of_blowers=3,
        number_of_pumps=3,
        capacities={
            "screening": f"{screening.channel_width_m:.2f} m channel width",
            "grit": f"{grit.volume_per_unit_m3:.1f} m³/unit",
            "primary": f"{primary.diameter_m:.1f} m dia/unit",
            "aeration": f"{aeration.aeration_tank_volume_m3 / aeration.number_of_aeration_tanks:.1f} m³/tank",
            "secondary": f"{secondary.diameter_m:.1f} m dia/unit",
            "filters": f"{filtration.area_per_filter_m2:.1f} m² nominal/filter",
            "blowers": f"{blowers.blower_capacity_m3_min:.1f} m³/min/blower",
            "pumps": f"{pumps.capacity_per_pump_m3_day:.0f} m³/day/pump",
        },
    )

    # ---------------------------------------------------------
    # 15. Hydraulic profile
    # ---------------------------------------------------------

    hydraulic_profile = create_hydraulic_profile(
        initial_water_level_m=100.0,
        process_stages=treatment_train.stages,
    )

    # ---------------------------------------------------------
    # 16. Mass balance
    # ---------------------------------------------------------

    mass_balance = calculate_mass_balance(
        parameter="BOD",
        influent_concentration_mg_l=bod,
        flow_m3_day=average_flow,
        removal_efficiency_percent=(
            max(0.0, min(100.0, (1.0 - target_bod / bod) * 100.0))
            if bod > 0
            else 0.0
        ),
    )

    plant_mass_balance = calculate_plant_mass_balance(
        flow_m3_day=average_flow,
        influent_bod_mg_l=bod,
        influent_cod_mg_l=cod,
        influent_tss_mg_l=tss,
        target_bod_mg_l=target_bod,
        target_tss_mg_l=target_tss,
    )

    # ---------------------------------------------------------
    # 17. Engineering checks
    # ---------------------------------------------------------

    design_basis = {
        "average_flow_m3_day": average_flow,
        "peak_flow_m3_day": peak_flow,
        "peak_factor": peak_factor,
        "influent_bod_mg_l": bod,
        "influent_cod_mg_l": cod,
        "influent_tss_mg_l": tss,
        "ammonia_mg_l": ammonia,
        "target_bod_mg_l": target_bod,
        "target_tss_mg_l": target_tss,
        "nitrification_required": nitrification,
        "post_primary_bod_mg_l": post_primary_bod_mg_l,
        "post_primary_tss_mg_l": post_primary_tss_mg_l,
    }

    engineering_checks = build_engineering_checks(
        design_basis=design_basis,
        criteria=criteria,
        primary=_serialize(primary),
        biological={
            "biological": {
                **_serialize(biological),
                "calculated_f_m_ratio": calculated_fm_ratio,
                "mlvss_mg_l": mlvss_mg_l,
                "reactor_biomass_kg": reactor_biomass_kg,
                "biological_feed_kg_day": biological_feed_kg_day,
            },
            "aeration": _serialize(aeration),
        },
        secondary=secondary_dict,
        filtration=filtration_dict,
        disinfection=_serialize(chlorination),
        hydraulic_profile=_serialize(hydraulic_profile),
    )

    # ---------------------------------------------------------
    # 18. Final effluent
    # ---------------------------------------------------------

    final_effluent = calculate_final_effluent(
        average_flow_m3_day=average_flow,
        influent_bod_mg_l=bod,
        influent_tss_mg_l=tss,
        target_bod_mg_l=target_bod,
        target_tss_mg_l=target_tss,
    )

    # ---------------------------------------------------------
    # FINAL API RESPONSE
    # ---------------------------------------------------------

    return {
        "project": {
            "name": project_name,
            "wastewater_type": wastewater_type,
        },

        "design_basis": design_basis,
        "design_criteria": criteria,
        "engineering_checks": engineering_checks,

        "core_design": _serialize(core_design),
        "flow": _serialize(flow_design),
        "loads": _serialize(loads),
        "hydraulic_loads": _serialize(hydraulic_loads),

        "process_selection": _serialize(process_selection),
        "treatment_train": _serialize(treatment_train),

        "preliminary_treatment": {
            "screening": _serialize(screening),
            "grit": _serialize(grit),
        },

        "primary_treatment": _serialize(primary),

        "biological_treatment": {
            "biological": {
                **_serialize(biological),
                "calculated_f_m_ratio": calculated_fm_ratio,
                "mlvss_mg_l": mlvss_mg_l,
                "reactor_biomass_kg": reactor_biomass_kg,
                "biological_feed_kg_day": biological_feed_kg_day,
                "influent_bod_mg_l_after_primary": post_primary_bod_mg_l,
            },
            "aeration": _serialize(aeration),
        },

        "secondary_treatment": secondary_dict,

        "tertiary_treatment": {
            "filtration": filtration_dict,
        },

        "disinfection": _serialize(chlorination),

        "sludge_management": {
            "production": _serialize(sludge_production),
            "design": _serialize(sludge),
        },

        "utilities": {
            "pumps": _serialize(pumps),
            "blowers": _serialize(blowers),
            "chemicals": _serialize(chemicals),
            "energy": _serialize(energy),
        },

        "equipment_schedule": _serialize(equipment),
        "hydraulic_profile": _serialize(hydraulic_profile),
        "mass_balance": _serialize(mass_balance),
        "plant_mass_balance": _serialize(plant_mass_balance),
        "final_effluent": _serialize(final_effluent),

        "metadata": {
            "engine": "WWTP Design Engine",
            "version": "1.2.0",
            "status": "preliminary engineering design",
            "scope": "Conceptual/preliminary engineering design and decision support; not construction-ready.",
            "capabilities": [
                "Design-basis validation",
                "Process selection and treatment-train generation",
                "Unit-level preliminary sizing",
                "Hydraulic profile and headloss",
                "Biological and aeration calculations",
                "Sludge and utilities calculations",
                "Equipment schedule",
                "Plant-wide mass balance",
                "Automated engineering checks",
            ],
        },
    }