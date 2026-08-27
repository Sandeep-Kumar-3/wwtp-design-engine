from dataclasses import dataclass


@dataclass
class HydraulicUnit:
    name: str
    water_depth_m: float
    freeboard_m: float
    total_depth_m: float
    headloss_m: float
    invert_elevation_m: float
    water_level_m: float


@dataclass
class HydraulicProfile:
    units: list
    total_headloss_m: float
    final_water_level_m: float


def create_hydraulic_profile(
    initial_water_level_m: float = 100.0,
    process_stages=None,
) -> HydraulicProfile:

    unit_data = [
        ("Inlet Chamber", 2.0, 0.5, 0.20),
        ("Screening", 1.5, 0.5, 0.15),
        ("Grit Chamber", 2.0, 0.5, 0.20),
        ("Primary Clarifier", 3.0, 0.5, 0.30),
        ("Aeration Tank", 4.5, 0.5, 0.40),
        ("Secondary Clarifier", 3.5, 0.5, 0.30),
        ("Tertiary Filtration", 2.0, 0.5, 0.40),
        ("Disinfection", 2.0, 0.5, 0.15),
        ("Final Outlet", 1.5, 0.5, 0.10),
    ]

    if process_stages:
        defaults = {
            "Inlet Works": (2.0, 0.5, 0.20),
            "Screening": (1.5, 0.5, 0.15),
            "Grit Removal": (2.0, 0.5, 0.20),
            "Equalization": (4.0, 0.5, 0.15),
            "Primary Clarifier": (3.0, 0.5, 0.30),
            "Primary Physico-Chemical Treatment": (3.0, 0.5, 0.25),
            "Biological Treatment": (4.5, 0.5, 0.40),
            "Activated Sludge": (4.5, 0.5, 0.40),
            "Activated Sludge with Nitrification": (4.5, 0.5, 0.40),
            "Nitrification": (4.5, 0.5, 0.25),
            "Secondary Clarifier": (3.5, 0.5, 0.30),
            "Tertiary Filtration": (2.0, 0.5, 0.40),
            "Disinfection": (2.0, 0.5, 0.15),
            "Treated Effluent": (1.5, 0.5, 0.10),
            "Sludge Treatment and Dewatering": (1.5, 0.5, 0.15),
        }
        mapped = []
        for stage in process_stages:
            name = getattr(stage, "unit", None) or str(stage)
            mapped.append((name, *defaults.get(name, (2.0, 0.5, 0.20))))
        unit_data = mapped

    units = []
    current_level = initial_water_level_m
    total_headloss = 0.0

    for name, depth, freeboard, headloss in unit_data:

        current_level -= headloss
        total_headloss += headloss

        units.append(
            HydraulicUnit(
                name=name,
                water_depth_m=depth,
                freeboard_m=freeboard,
                total_depth_m=depth + freeboard,
                headloss_m=headloss,
                invert_elevation_m=current_level - depth,
                water_level_m=current_level,
            )
        )

    return HydraulicProfile(
        units=units,
        total_headloss_m=total_headloss,
        final_water_level_m=current_level,
    )