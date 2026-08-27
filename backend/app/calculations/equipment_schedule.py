from dataclasses import dataclass


@dataclass
class EquipmentItem:
    equipment_id: str
    process: str
    equipment: str
    quantity: int
    duty: str
    capacity: str
    remarks: str


def generate_equipment_schedule(
    number_of_screens: int = 2,
    number_of_grit_units: int = 2,
    number_of_primary_clarifiers: int = 2,
    number_of_aeration_tanks: int = 2,
    number_of_secondary_clarifiers: int = 2,
    number_of_filters: int = 4,
    number_of_blowers: int = 3,
    number_of_pumps: int = 3,
    capacities: dict | None = None,
) -> list:

    capacities = capacities or {}

    return [

        EquipmentItem(
            "SCR-01",
            "Preliminary",
            "Mechanical Screen",
            number_of_screens,
            "Duty/Standby",
            capacities.get("screening", "Preliminary sizing"),
            "Fine/coarse screening",
        ),

        EquipmentItem(
            "GR-01",
            "Preliminary",
            "Grit Chamber",
            number_of_grit_units,
            "Parallel",
            capacities.get("grit", "Preliminary sizing"),
            "Grit removal",
        ),

        EquipmentItem(
            "PC-01",
            "Primary",
            "Primary Clarifier",
            number_of_primary_clarifiers,
            "Parallel",
            capacities.get("primary", "Preliminary sizing"),
            "Primary solids removal",
        ),

        EquipmentItem(
            "AT-01",
            "Biological",
            "Aeration Tank",
            number_of_aeration_tanks,
            "Parallel",
            capacities.get("aeration", "Preliminary sizing"),
            "Biological treatment",
        ),

        EquipmentItem(
            "SC-01",
            "Secondary",
            "Secondary Clarifier",
            number_of_secondary_clarifiers,
            "Parallel",
            capacities.get("secondary", "Preliminary sizing"),
            "Biomass separation",
        ),

        EquipmentItem(
            "F-01",
            "Tertiary",
            "Pressure/Gravity Filter",
            number_of_filters,
            "Duty/Standby",
            capacities.get("filters", "Preliminary sizing"),
            "Polishing filtration",
        ),

        EquipmentItem(
            "BL-01",
            "Aeration",
            "Air Blower",
            number_of_blowers,
            "Duty + Standby",
            capacities.get("blowers", "Preliminary sizing"),
            "Aeration air supply",
        ),

        EquipmentItem(
            "P-01",
            "Hydraulics",
            "Process Pump",
            number_of_pumps,
            "Duty + Standby",
            capacities.get("pumps", "Preliminary sizing"),
            "Water/sludge pumping",
        ),
    ]