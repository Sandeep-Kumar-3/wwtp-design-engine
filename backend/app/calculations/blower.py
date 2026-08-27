from dataclasses import dataclass


@dataclass
class BlowerDesign:
    oxygen_demand_kg_day: float
    oxygen_transfer_efficiency: float
    air_oxygen_fraction: float
    required_air_kg_day: float
    required_air_m3_day: float
    required_air_m3_min: float
    number_of_blowers: int
    operating_blowers: int
    standby_blowers: int
    blower_capacity_m3_min: float
    pressure_kpa: float
    estimated_power_kw: float


def design_blowers(
    oxygen_demand_kg_day: float,
    oxygen_transfer_efficiency: float = 0.15,
    air_oxygen_fraction: float = 0.232,
    air_density_kg_m3: float = 1.225,
    number_of_blowers: int = 3,
    operating_blowers: int = 2,
    pressure_kpa: float = 60.0,
    blower_efficiency: float = 0.70,
) -> BlowerDesign:

    if oxygen_demand_kg_day < 0:
        raise ValueError(
            "Oxygen demand cannot be negative."
        )

    # A valid preliminary design can have no aeration duty when the
    # selected biological stage has no calculated oxygen demand (for
    # example, when upstream removal already meets the target). Return a
    # zero-duty equipment schedule rather than crashing the complete plant
    # design. The engineering-check layer can flag this condition for review.
    if oxygen_demand_kg_day == 0:
        return BlowerDesign(
            oxygen_demand_kg_day=0.0,
            oxygen_transfer_efficiency=oxygen_transfer_efficiency,
            air_oxygen_fraction=air_oxygen_fraction,
            required_air_kg_day=0.0,
            required_air_m3_day=0.0,
            required_air_m3_min=0.0,
            number_of_blowers=number_of_blowers,
            operating_blowers=operating_blowers,
            standby_blowers=max(0, number_of_blowers - operating_blowers),
            blower_capacity_m3_min=0.0,
            pressure_kpa=pressure_kpa,
            estimated_power_kw=0.0,
        )

    if not 0 < oxygen_transfer_efficiency <= 1:
        raise ValueError(
            "Oxygen transfer efficiency must be between 0 and 1."
        )

    if not 0 < air_oxygen_fraction <= 1:
        raise ValueError(
            "Air oxygen fraction must be between 0 and 1."
        )

    if air_density_kg_m3 <= 0:
        raise ValueError(
            "Air density must be greater than zero."
        )

    if number_of_blowers <= 0:
        raise ValueError(
            "Number of blowers must be greater than zero."
        )

    if operating_blowers <= 0:
        raise ValueError(
            "Operating blowers must be greater than zero."
        )

    if operating_blowers > number_of_blowers:
        raise ValueError(
            "Operating blowers cannot exceed total blowers."
        )

    if pressure_kpa <= 0:
        raise ValueError(
            "Pressure must be greater than zero."
        )

    if not 0 < blower_efficiency <= 1:
        raise ValueError(
            "Blower efficiency must be between 0 and 1."
        )

    # Oxygen actually transferred to wastewater
    required_air_oxygen_kg_day = (
        oxygen_demand_kg_day
        / oxygen_transfer_efficiency
    )

    # Oxygen represents approximately 23.2% of air by mass
    required_air_kg_day = (
        required_air_oxygen_kg_day
        / air_oxygen_fraction
    )

    required_air_m3_day = (
        required_air_kg_day
        / air_density_kg_m3
    )

    required_air_m3_min = (
        required_air_m3_day
        / 1440
    )

    blower_capacity = (
        required_air_m3_min
        / operating_blowers
    )

    # Approximate pneumatic power
    #
    # P = Q × ΔP / η
    #
    # Q in m3/s
    flow_m3_sec = (
        required_air_m3_min / 60
    )

    pressure_pa = (
        pressure_kpa * 1000
    )

    estimated_power_kw = (
        flow_m3_sec
        * pressure_pa
        / blower_efficiency
        / 1000
    )

    standby_blowers = (
        number_of_blowers
        - operating_blowers
    )

    return BlowerDesign(
        oxygen_demand_kg_day=oxygen_demand_kg_day,
        oxygen_transfer_efficiency=(
            oxygen_transfer_efficiency
        ),
        air_oxygen_fraction=air_oxygen_fraction,
        required_air_kg_day=required_air_kg_day,
        required_air_m3_day=required_air_m3_day,
        required_air_m3_min=required_air_m3_min,
        number_of_blowers=number_of_blowers,
        operating_blowers=operating_blowers,
        standby_blowers=standby_blowers,
        blower_capacity_m3_min=blower_capacity,
        pressure_kpa=pressure_kpa,
        estimated_power_kw=estimated_power_kw,
    )