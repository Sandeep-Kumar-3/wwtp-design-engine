from dataclasses import dataclass


@dataclass
class ActivatedSludgeResult:
    flow_m3_day: float

    influent_bod_mg_l: float
    effluent_bod_mg_l: float

    influent_bod_load_kg_day: float
    effluent_bod_load_kg_day: float
    bod_removed_kg_day: float

    mlss_mg_l: float
    mlvss_mg_l: float
    fm_ratio: float

    reactor_volume_m3: float
    hrt_hours: float

    srt_days: float
    biomass_inventory_kg: float

    biomass_yield_kg_kg_bod: float
    biomass_production_kg_day: float

    endogenous_decay_fraction_per_day: float
    net_biomass_production_kg_day: float

    carbonaceous_oxygen_kg_day: float

    nitrification_required: bool
    ammonia_removed_kg_day: float
    nitrification_oxygen_kg_day: float

    total_oxygen_requirement_kg_day: float

    aeration_efficiency_kg_o2_per_kg_air: float
    air_requirement_kg_day: float

    blower_efficiency: float
    blower_power_kw: float


def design_activated_sludge(
    flow_m3_day: float,
    influent_bod_mg_l: float,
    effluent_bod_mg_l: float,
    mlss_mg_l: float,
    mlvss_to_mlss_ratio: float,
    fm_ratio: float,
    srt_days: float,
    biomass_yield_kg_kg_bod: float,
    endogenous_decay_rate_per_day: float,
    nitrification_required: bool = False,
    ammonia_removed_mg_l: float = 0.0,
    oxygen_per_kg_nh4_n: float = 4.57,
    aeration_efficiency_kg_o2_per_kg_air: float = 0.03,
    blower_efficiency: float = 0.65,
    air_pressure_kpa: float = 100.0,
) -> ActivatedSludgeResult:
    """
    Preliminary activated-sludge process design.

    This is a calculation framework. Design coefficients are supplied
    by the caller so that validated criteria can later be connected
    to the project's engineering knowledge base.
    """

    if flow_m3_day <= 0:
        raise ValueError("Flow must be greater than zero.")

    if influent_bod_mg_l < 0:
        raise ValueError("Influent BOD cannot be negative.")

    if effluent_bod_mg_l < 0:
        raise ValueError("Effluent BOD cannot be negative.")

    if effluent_bod_mg_l > influent_bod_mg_l:
        raise ValueError(
            "Effluent BOD cannot exceed influent BOD."
        )

    if mlss_mg_l <= 0:
        raise ValueError("MLSS must be greater than zero.")

    if not 0 < mlvss_to_mlss_ratio <= 1:
        raise ValueError(
            "MLVSS/MLSS ratio must be between 0 and 1."
        )

    if fm_ratio <= 0:
        raise ValueError("F/M ratio must be greater than zero.")

    if srt_days <= 0:
        raise ValueError("SRT must be greater than zero.")

    if biomass_yield_kg_kg_bod < 0:
        raise ValueError("Biomass yield cannot be negative.")

    if endogenous_decay_rate_per_day < 0:
        raise ValueError(
            "Endogenous decay rate cannot be negative."
        )

    if ammonia_removed_mg_l < 0:
        raise ValueError(
            "Ammonia removal cannot be negative."
        )

    if oxygen_per_kg_nh4_n < 0:
        raise ValueError(
            "Nitrification oxygen coefficient cannot be negative."
        )

    if aeration_efficiency_kg_o2_per_kg_air <= 0:
        raise ValueError(
            "Aeration efficiency must be greater than zero."
        )

    if not 0 < blower_efficiency <= 1:
        raise ValueError(
            "Blower efficiency must be between 0 and 1."
        )

    if air_pressure_kpa <= 0:
        raise ValueError(
            "Air pressure must be greater than zero."
        )

    # ---------------------------------------------------------
    # 1. BOD loads
    # ---------------------------------------------------------

    influent_bod_load_kg_day = (
        flow_m3_day * influent_bod_mg_l / 1000
    )

    effluent_bod_load_kg_day = (
        flow_m3_day * effluent_bod_mg_l / 1000
    )

    bod_removed_kg_day = (
        influent_bod_load_kg_day
        - effluent_bod_load_kg_day
    )

    # ---------------------------------------------------------
    # 2. MLSS / MLVSS
    # ---------------------------------------------------------

    mlvss_mg_l = (
        mlss_mg_l * mlvss_to_mlss_ratio
    )

    # ---------------------------------------------------------
    # 3. F/M reactor sizing
    #
    # F/M = substrate load / (reactor volume × MLVSS)
    #
    # With:
    #   S = kg BOD/day
    #   X = kg MLVSS/m3
    #
    # ---------------------------------------------------------

    mlvss_kg_m3 = mlvss_mg_l / 1000

    reactor_volume_m3 = (
        influent_bod_load_kg_day
        / (fm_ratio * mlvss_kg_m3)
    )

    hrt_hours = (
        reactor_volume_m3 / flow_m3_day * 24
    )

    # ---------------------------------------------------------
    # 4. Biomass inventory
    # ---------------------------------------------------------

    biomass_inventory_kg = (
        reactor_volume_m3 * mlvss_kg_m3
    )

    # ---------------------------------------------------------
    # 5. Biomass production
    # ---------------------------------------------------------

    biomass_production_kg_day = (
        biomass_yield_kg_kg_bod
        * bod_removed_kg_day
    )

    endogenous_decay_loss_kg_day = (
        endogenous_decay_rate_per_day
        * biomass_inventory_kg
    )

    net_biomass_production_kg_day = max(
        biomass_production_kg_day
        - endogenous_decay_loss_kg_day,
        0.0,
    )

    # ---------------------------------------------------------
    # 6. Carbonaceous oxygen requirement
    #
    # Simplified preliminary design relationship:
    # oxygen ≈ BOD removed - biomass synthesis credit
    # ---------------------------------------------------------

    carbonaceous_oxygen_kg_day = max(
        bod_removed_kg_day
        - biomass_production_kg_day,
        0.0,
    )

    # ---------------------------------------------------------
    # 7. Nitrification
    # ---------------------------------------------------------

    ammonia_removed_kg_day = (
        flow_m3_day
        * ammonia_removed_mg_l
        / 1000
    )

    if nitrification_required:

        nitrification_oxygen_kg_day = (
            ammonia_removed_kg_day
            * oxygen_per_kg_nh4_n
        )

    else:

        nitrification_oxygen_kg_day = 0.0

    # ---------------------------------------------------------
    # 8. Total oxygen
    # ---------------------------------------------------------

    total_oxygen_requirement_kg_day = (
        carbonaceous_oxygen_kg_day
        + nitrification_oxygen_kg_day
    )

    # ---------------------------------------------------------
    # 9. Air requirement
    #
    # kg air/day = kg O2/day ÷ kg O2/kg air
    # ---------------------------------------------------------

    air_requirement_kg_day = (
        total_oxygen_requirement_kg_day
        / aeration_efficiency_kg_o2_per_kg_air
    )

    # Approximate conversion:
    # air density ≈ 1.225 kg/m3 at standard conditions.
    air_density_kg_m3 = 1.225

    air_requirement_m3_day = (
        air_requirement_kg_day
        / air_density_kg_m3
    )

    # ---------------------------------------------------------
    # 10. Blower power
    #
    # Hydraulic/pneumatic power approximation:
    #
    # P = Q × ΔP / η
    #
    # where:
    # Q = m3/s
    # ΔP = Pa
    #
    # ---------------------------------------------------------

    air_flow_m3_s = air_requirement_m3_day / 86400

    pressure_pa = air_pressure_kpa * 1000

    blower_power_kw = (
        air_flow_m3_s
        * pressure_pa
        / blower_efficiency
        / 1000
    )

    return ActivatedSludgeResult(
        flow_m3_day=flow_m3_day,

        influent_bod_mg_l=influent_bod_mg_l,
        effluent_bod_mg_l=effluent_bod_mg_l,

        influent_bod_load_kg_day=influent_bod_load_kg_day,
        effluent_bod_load_kg_day=effluent_bod_load_kg_day,
        bod_removed_kg_day=bod_removed_kg_day,

        mlss_mg_l=mlss_mg_l,
        mlvss_mg_l=mlvss_mg_l,
        fm_ratio=fm_ratio,

        reactor_volume_m3=reactor_volume_m3,
        hrt_hours=hrt_hours,

        srt_days=srt_days,
        biomass_inventory_kg=biomass_inventory_kg,

        biomass_yield_kg_kg_bod=biomass_yield_kg_kg_bod,
        biomass_production_kg_day=biomass_production_kg_day,

        endogenous_decay_fraction_per_day=(
            endogenous_decay_rate_per_day
        ),

        net_biomass_production_kg_day=(
            net_biomass_production_kg_day
        ),

        carbonaceous_oxygen_kg_day=(
            carbonaceous_oxygen_kg_day
        ),

        nitrification_required=nitrification_required,
        ammonia_removed_kg_day=ammonia_removed_kg_day,
        nitrification_oxygen_kg_day=(
            nitrification_oxygen_kg_day
        ),

        total_oxygen_requirement_kg_day=(
            total_oxygen_requirement_kg_day
        ),

        aeration_efficiency_kg_o2_per_kg_air=(
            aeration_efficiency_kg_o2_per_kg_air
        ),

        air_requirement_kg_day=air_requirement_kg_day,

        blower_efficiency=blower_efficiency,
        blower_power_kw=blower_power_kw,
    )