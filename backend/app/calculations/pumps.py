from dataclasses import dataclass


@dataclass
class PumpDesign:
    flow_m3_day: float
    flow_m3_sec: float
    total_dynamic_head_m: float
    pump_efficiency: float
    required_power_kw: float
    number_of_pumps: int
    operating_pumps: int
    standby_pumps: int
    capacity_per_pump_m3_day: float


def design_pumps(
    flow_m3_day: float,
    static_head_m: float = 5.0,
    friction_head_m: float = 3.0,
    minor_loss_head_m: float = 1.0,
    pump_efficiency: float = 0.75,
    number_of_pumps: int = 3,
    operating_pumps: int = 2,
    capacity_factor: float = 1.10,
) -> PumpDesign:

    if flow_m3_day <= 0:
        raise ValueError(
            "Flow must be greater than zero."
        )

    if static_head_m < 0:
        raise ValueError(
            "Static head cannot be negative."
        )

    if friction_head_m < 0:
        raise ValueError(
            "Friction head cannot be negative."
        )

    if minor_loss_head_m < 0:
        raise ValueError(
            "Minor-loss head cannot be negative."
        )

    if not 0 < pump_efficiency <= 1:
        raise ValueError(
            "Pump efficiency must be between 0 and 1."
        )

    if number_of_pumps <= 0:
        raise ValueError(
            "Number of pumps must be greater than zero."
        )

    if operating_pumps <= 0:
        raise ValueError(
            "Operating pumps must be greater than zero."
        )

    if operating_pumps > number_of_pumps:
        raise ValueError(
            "Operating pumps cannot exceed total pumps."
        )

    if capacity_factor <= 0:
        raise ValueError(
            "Capacity factor must be greater than zero."
        )

    total_head = (
        static_head_m
        + friction_head_m
        + minor_loss_head_m
    )

    design_flow = (
        flow_m3_day
        * capacity_factor
    )

    flow_m3_sec = (
        design_flow
        / 86400
    )

    # Hydraulic power:
    #
    # P = ρgQH / η
    #
    power_w = (
        1000
        * 9.81
        * flow_m3_sec
        * total_head
        / pump_efficiency
    )

    power_kw = power_w / 1000

    capacity_per_pump = (
        design_flow
        / operating_pumps
    )

    standby_pumps = (
        number_of_pumps
        - operating_pumps
    )

    return PumpDesign(
        flow_m3_day=design_flow,
        flow_m3_sec=flow_m3_sec,
        total_dynamic_head_m=total_head,
        pump_efficiency=pump_efficiency,
        required_power_kw=power_kw,
        number_of_pumps=number_of_pumps,
        operating_pumps=operating_pumps,
        standby_pumps=standby_pumps,
        capacity_per_pump_m3_day=capacity_per_pump,
    )