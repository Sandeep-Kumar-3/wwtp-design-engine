from dataclasses import dataclass


# ============================================================
# SLUDGE PRODUCTION
# ============================================================

@dataclass
class SludgeProduction:
    primary_sludge_kg_ds_day: float
    secondary_sludge_kg_ds_day: float
    total_sludge_kg_ds_day: float


def calculate_sludge_production(
    primary_tss_removed_kg_day: float,
    biological_bod_load_kg_day: float,
    biological_yield: float = 0.5,
) -> SludgeProduction:

    if primary_tss_removed_kg_day < 0:
        raise ValueError("Primary TSS removed cannot be negative.")

    if biological_bod_load_kg_day < 0:
        raise ValueError("Biological BOD load cannot be negative.")

    if biological_yield < 0:
        raise ValueError("Biological yield cannot be negative.")

    secondary_sludge = (
        biological_bod_load_kg_day * biological_yield
    )

    total_sludge = (
        primary_tss_removed_kg_day
        + secondary_sludge
    )

    return SludgeProduction(
        primary_sludge_kg_ds_day=primary_tss_removed_kg_day,
        secondary_sludge_kg_ds_day=secondary_sludge,
        total_sludge_kg_ds_day=total_sludge,
    )


# ============================================================
# RAS / WAS
# ============================================================

@dataclass
class RASWASDesign:
    average_flow_m3_day: float
    secondary_sludge_kg_ds_day: float
    ras_flow_m3_day: float
    was_flow_m3_day: float
    ras_recycle_ratio: float


def design_ras_was(
    average_flow_m3_day: float,
    secondary_sludge_kg_ds_day: float,
    ras_recycle_ratio: float = 0.5,
    sludge_concentration_kg_m3: float = 8.0,
) -> RASWASDesign:

    if average_flow_m3_day <= 0:
        raise ValueError("Average flow must be greater than zero.")

    if secondary_sludge_kg_ds_day < 0:
        raise ValueError("Secondary sludge cannot be negative.")

    if ras_recycle_ratio < 0:
        raise ValueError("RAS recycle ratio cannot be negative.")

    if sludge_concentration_kg_m3 <= 0:
        raise ValueError("Sludge concentration must be positive.")

    ras_flow = average_flow_m3_day * ras_recycle_ratio

    was_flow = (
        secondary_sludge_kg_ds_day
        / sludge_concentration_kg_m3
    )

    return RASWASDesign(
        average_flow_m3_day=average_flow_m3_day,
        secondary_sludge_kg_ds_day=secondary_sludge_kg_ds_day,
        ras_flow_m3_day=ras_flow,
        was_flow_m3_day=was_flow,
        ras_recycle_ratio=ras_recycle_ratio,
    )


# ============================================================
# SLUDGE THICKENER
# ============================================================

@dataclass
class SludgeThickenerDesign:
    total_sludge_kg_ds_day: float
    solids_loading_rate_kg_m2_day: float
    required_area_m2: float
    number_of_units: int
    area_per_unit_m2: float


def design_sludge_thickener(
    total_sludge_kg_ds_day: float,
    solids_loading_rate_kg_m2_day: float = 50.0,
    number_of_units: int = 2,
) -> SludgeThickenerDesign:

    if total_sludge_kg_ds_day < 0:
        raise ValueError("Total sludge cannot be negative.")

    if solids_loading_rate_kg_m2_day <= 0:
        raise ValueError("Solids loading rate must be positive.")

    if number_of_units <= 0:
        raise ValueError("Number of units must be positive.")

    area = (
        total_sludge_kg_ds_day
        / solids_loading_rate_kg_m2_day
    )

    return SludgeThickenerDesign(
        total_sludge_kg_ds_day=total_sludge_kg_ds_day,
        solids_loading_rate_kg_m2_day=solids_loading_rate_kg_m2_day,
        required_area_m2=area,
        number_of_units=number_of_units,
        area_per_unit_m2=area / number_of_units,
    )


# ============================================================
# ANAEROBIC DIGESTER
# ============================================================

@dataclass
class AnaerobicDigesterDesign:
    total_sludge_kg_ds_day: float
    solids_retention_time_day: float
    required_volume_m3: float
    number_of_units: int
    volume_per_unit_m3: float


def design_anaerobic_digester(
    total_sludge_kg_ds_day: float,
    solids_retention_time_day: float = 20.0,
    sludge_concentration_kg_m3: float = 40.0,
    number_of_units: int = 2,
) -> AnaerobicDigesterDesign:

    if total_sludge_kg_ds_day < 0:
        raise ValueError("Total sludge cannot be negative.")

    if solids_retention_time_day <= 0:
        raise ValueError("Retention time must be positive.")

    if sludge_concentration_kg_m3 <= 0:
        raise ValueError("Sludge concentration must be positive.")

    if number_of_units <= 0:
        raise ValueError("Number of units must be positive.")

    sludge_flow = (
        total_sludge_kg_ds_day
        / sludge_concentration_kg_m3
    )

    volume = (
        sludge_flow
        * solids_retention_time_day
    )

    return AnaerobicDigesterDesign(
        total_sludge_kg_ds_day=total_sludge_kg_ds_day,
        solids_retention_time_day=solids_retention_time_day,
        required_volume_m3=volume,
        number_of_units=number_of_units,
        volume_per_unit_m3=volume / number_of_units,
    )


# ============================================================
# DEWATERING
# ============================================================

@dataclass
class DewateringDesign:
    dry_solids_kg_day: float
    cake_solids_percent: float
    cake_flow_kg_day: float
    cake_flow_m3_day: float


def design_dewatering(
    dry_solids_kg_day: float,
    cake_solids_percent: float = 20.0,
) -> DewateringDesign:

    if dry_solids_kg_day < 0:
        raise ValueError("Dry solids cannot be negative.")

    if not 0 < cake_solids_percent <= 100:
        raise ValueError(
            "Cake solids percentage must be between 0 and 100."
        )

    fraction = cake_solids_percent / 100.0

    cake_flow_kg_day = dry_solids_kg_day / fraction

    cake_flow_m3_day = cake_flow_kg_day / 1000.0

    return DewateringDesign(
        dry_solids_kg_day=dry_solids_kg_day,
        cake_solids_percent=cake_solids_percent,
        cake_flow_kg_day=cake_flow_kg_day,
        cake_flow_m3_day=cake_flow_m3_day,
    )


# ============================================================
# EXISTING GENERAL SLUDGE DESIGN
# ============================================================

@dataclass
class SludgeDesign:
    primary_solids_kg_day: float
    biological_solids_kg_day: float
    total_dry_solids_kg_day: float
    sludge_concentration_kg_m3: float
    raw_sludge_flow_m3_day: float
    thickened_sludge_concentration_kg_m3: float
    thickened_sludge_flow_m3_day: float
    dewatered_solids_percent: float
    dewatered_cake_flow_kg_day: float
    dewatered_cake_flow_m3_day: float


def design_sludge(
    flow_m3_day: float,
    influent_tss_mg_l: float,
    tss_removal_efficiency: float = 0.60,
    biological_solids_kg_day: float = 500.0,
    raw_sludge_concentration_kg_m3: float = 25.0,
    thickened_sludge_concentration_kg_m3: float = 50.0,
    dewatered_solids_percent: float = 20.0,
) -> SludgeDesign:

    if flow_m3_day <= 0:
        raise ValueError("Flow must be greater than zero.")

    if influent_tss_mg_l < 0:
        raise ValueError("Influent TSS cannot be negative.")

    if not 0 <= tss_removal_efficiency <= 1:
        raise ValueError(
            "TSS removal efficiency must be between 0 and 1."
        )

    if biological_solids_kg_day < 0:
        raise ValueError(
            "Biological solids cannot be negative."
        )

    if raw_sludge_concentration_kg_m3 <= 0:
        raise ValueError(
            "Raw sludge concentration must be positive."
        )

    if thickened_sludge_concentration_kg_m3 <= 0:
        raise ValueError(
            "Thickened sludge concentration must be positive."
        )

    if not 0 < dewatered_solids_percent <= 100:
        raise ValueError(
            "Dewatered solids percentage must be between 0 and 100."
        )

    tss_load = flow_m3_day * influent_tss_mg_l / 1000

    primary_solids = tss_load * tss_removal_efficiency

    total_dry_solids = (
        primary_solids + biological_solids_kg_day
    )

    raw_sludge_flow = (
        total_dry_solids / raw_sludge_concentration_kg_m3
    )

    thickened_sludge_flow = (
        total_dry_solids
        / thickened_sludge_concentration_kg_m3
    )

    cake_fraction = dewatered_solids_percent / 100

    cake_flow_kg_day = total_dry_solids / cake_fraction

    cake_flow_m3_day = cake_flow_kg_day / 1000

    return SludgeDesign(
        primary_solids_kg_day=primary_solids,
        biological_solids_kg_day=biological_solids_kg_day,
        total_dry_solids_kg_day=total_dry_solids,
        sludge_concentration_kg_m3=raw_sludge_concentration_kg_m3,
        raw_sludge_flow_m3_day=raw_sludge_flow,
        thickened_sludge_concentration_kg_m3=(
            thickened_sludge_concentration_kg_m3
        ),
        thickened_sludge_flow_m3_day=thickened_sludge_flow,
        dewatered_solids_percent=dewatered_solids_percent,
        dewatered_cake_flow_kg_day=cake_flow_kg_day,
        dewatered_cake_flow_m3_day=cake_flow_m3_day,
    )