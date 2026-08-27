from dataclasses import dataclass


@dataclass
class EnergyDesign:
    aeration_power_kw: float
    pumping_power_kw: float
    uv_power_kw: float
    other_power_kw: float
    total_power_kw: float
    daily_energy_kwh: float
    annual_energy_kwh: float
    specific_energy_kwh_m3: float


def calculate_energy(
    average_flow_m3_day: float,
    aeration_power_kw: float = 0.0,
    pumping_power_kw: float = 0.0,
    uv_power_kw: float = 0.0,
    other_power_kw: float = 0.0,
    operating_hours_day: float = 24.0,
) -> EnergyDesign:

    if average_flow_m3_day <= 0:
        raise ValueError("Flow must be greater than zero.")

    powers = [
        aeration_power_kw,
        pumping_power_kw,
        uv_power_kw,
        other_power_kw,
    ]

    if any(power < 0 for power in powers):
        raise ValueError("Power cannot be negative.")

    if operating_hours_day <= 0 or operating_hours_day > 24:
        raise ValueError(
            "Operating hours must be between 0 and 24."
        )

    total_power = sum(powers)

    daily_energy = (
        total_power
        * operating_hours_day
    )

    annual_energy = daily_energy * 365

    specific_energy = (
        daily_energy /
        average_flow_m3_day
    )

    return EnergyDesign(
        aeration_power_kw=aeration_power_kw,
        pumping_power_kw=pumping_power_kw,
        uv_power_kw=uv_power_kw,
        other_power_kw=other_power_kw,
        total_power_kw=total_power,
        daily_energy_kwh=daily_energy,
        annual_energy_kwh=annual_energy,
        specific_energy_kwh_m3=specific_energy,
    )