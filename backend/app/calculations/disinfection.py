from dataclasses import dataclass


@dataclass
class ChlorinationDesign:
    design_flow_m3_day: float
    chlorine_dose_mg_l: float
    chlorine_demand_mg_l: float
    chlorine_residual_mg_l: float
    chlorine_required_kg_day: float
    contact_time_min: float
    contact_tank_volume_m3: float
    contact_volume_m3: float
    tank_area_m2: float
    water_depth_m: float
    tank_length_m: float
    tank_width_m: float


@dataclass
class UVDesign:
    design_flow_m3_day: float
    uv_dose_mj_cm2: float
    required_uv_power_kw: float
    number_of_uv_units: int


def design_chlorination(
    flow_m3_day=None,
    chlorine_dose_mg_l=5.0,
    contact_time_min=30.0,
    water_depth_m=2.0,
    tank_length_to_width_ratio=3.0,
    peak_flow_m3_day=None,
    chlorine_demand_mg_l=3.0,
    chlorine_residual_mg_l=1.0,
):
    """
    Chlorination contact tank design.

    Supports both:
        flow_m3_day
    and:
        peak_flow_m3_day

    This keeps compatibility with older tests and the new
    design service.
    """

    # Support both parameter names
    if flow_m3_day is None:
        flow_m3_day = peak_flow_m3_day

    if flow_m3_day is None:
        raise ValueError("Flow must be provided.")

    if flow_m3_day <= 0:
        raise ValueError("Flow must be greater than zero.")

    if chlorine_dose_mg_l < 0:
        raise ValueError(
            "Chlorine dose cannot be negative."
        )

    if contact_time_min <= 0:
        raise ValueError(
            "Contact time must be greater than zero."
        )

    if water_depth_m <= 0:
        raise ValueError(
            "Water depth must be greater than zero."
        )

    if tank_length_to_width_ratio <= 0:
        raise ValueError(
            "Tank length-to-width ratio must be greater than zero."
        )

    if chlorine_demand_mg_l < 0:
        raise ValueError(
            "Chlorine demand cannot be negative."
        )

    if chlorine_residual_mg_l < 0:
        raise ValueError(
            "Chlorine residual cannot be negative."
        )

    # Chlorine requirement
    chlorine_required_kg_day = (
        flow_m3_day
        * chlorine_dose_mg_l
        / 1000
    )

    # Flow in m3/min
    flow_m3_min = flow_m3_day / 1440

    # Contact tank volume
    contact_tank_volume_m3 = (
        flow_m3_min
        * contact_time_min
    )

    # Plan area
    tank_plan_area = (
        contact_tank_volume_m3
        / water_depth_m
    )

    # L = ratio × W
    tank_width_m = (
        tank_plan_area
        / tank_length_to_width_ratio
    ) ** 0.5

    tank_length_m = (
        tank_width_m
        * tank_length_to_width_ratio
    )

    return ChlorinationDesign(
        design_flow_m3_day=flow_m3_day,
        chlorine_dose_mg_l=chlorine_dose_mg_l,
        chlorine_demand_mg_l=chlorine_demand_mg_l,
        chlorine_residual_mg_l=chlorine_residual_mg_l,
        chlorine_required_kg_day=chlorine_required_kg_day,
        contact_time_min=contact_time_min,
        contact_tank_volume_m3=contact_tank_volume_m3,
        contact_volume_m3=contact_tank_volume_m3,
        tank_area_m2=tank_plan_area,
        water_depth_m=water_depth_m,
        tank_length_m=tank_length_m,
        tank_width_m=tank_width_m,
    )


def design_uv(
    peak_flow_m3_day,
    uv_dose_mj_cm2=40.0,
    power_factor_kw_per_m3_day=0.00025,
    number_of_uv_units=2,
):
    """
    Preliminary UV disinfection design.
    """

    if peak_flow_m3_day <= 0:
        raise ValueError(
            "Flow must be greater than zero."
        )

    if uv_dose_mj_cm2 <= 0:
        raise ValueError(
            "UV dose must be greater than zero."
        )

    if power_factor_kw_per_m3_day <= 0:
        raise ValueError(
            "Power factor must be greater than zero."
        )

    if number_of_uv_units <= 0:
        raise ValueError(
            "Number of UV units must be greater than zero."
        )

    power = (
        peak_flow_m3_day
        * power_factor_kw_per_m3_day
    )

    return UVDesign(
        design_flow_m3_day=peak_flow_m3_day,
        uv_dose_mj_cm2=uv_dose_mj_cm2,
        required_uv_power_kw=power,
        number_of_uv_units=number_of_uv_units,
    )