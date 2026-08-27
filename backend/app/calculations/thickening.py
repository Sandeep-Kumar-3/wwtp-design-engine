from dataclasses import dataclass


@dataclass
class ThickeningResult:
    sludge_flow_m3_day: float

    influent_solids_kg_day: float
    influent_solids_concentration_percent: float

    target_solids_concentration_percent: float

    thickened_sludge_flow_m3_day: float
    water_removed_m3_day: float


def design_thickening(
    sludge_flow_m3_day: float,
    influent_solids_concentration_percent: float,
    target_solids_concentration_percent: float,
) -> ThickeningResult:

    if sludge_flow_m3_day <= 0:
        raise ValueError(
            "Sludge flow must be greater than zero."
        )

    if not 0 < influent_solids_concentration_percent < 100:
        raise ValueError(
            "Influent solids concentration must be between 0 and 100%."
        )

    if not 0 < target_solids_concentration_percent < 100:
        raise ValueError(
            "Target solids concentration must be between 0 and 100%."
        )

    if (
        target_solids_concentration_percent
        <= influent_solids_concentration_percent
    ):
        raise ValueError(
            "Target solids concentration must exceed influent concentration."
        )

    # Approximate density = 1000 kg/m3.
    #
    # Solids fraction × sludge volume × density

    influent_solids_kg_day = (
        sludge_flow_m3_day
        * 1000
        * influent_solids_concentration_percent
        / 100
    )

    thickened_sludge_flow_m3_day = (
        influent_solids_kg_day
        /
        (
            1000
            * target_solids_concentration_percent
            / 100
        )
    )

    water_removed_m3_day = (
        sludge_flow_m3_day
        - thickened_sludge_flow_m3_day
    )

    return ThickeningResult(
        sludge_flow_m3_day=sludge_flow_m3_day,
        influent_solids_kg_day=influent_solids_kg_day,
        influent_solids_concentration_percent=(
            influent_solids_concentration_percent
        ),
        target_solids_concentration_percent=(
            target_solids_concentration_percent
        ),
        thickened_sludge_flow_m3_day=(
            thickened_sludge_flow_m3_day
        ),
        water_removed_m3_day=water_removed_m3_day,
    )