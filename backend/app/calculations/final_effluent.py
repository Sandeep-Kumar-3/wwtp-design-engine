from dataclasses import dataclass


@dataclass
class FinalEffluentQuality:
    influent_bod_mg_l: float
    influent_tss_mg_l: float
    target_bod_mg_l: float
    target_tss_mg_l: float

    bod_removal_percent: float
    tss_removal_percent: float

    bod_load_kg_day: float
    tss_load_kg_day: float


def calculate_final_effluent(
    average_flow_m3_day: float,
    influent_bod_mg_l: float,
    influent_tss_mg_l: float,
    target_bod_mg_l: float,
    target_tss_mg_l: float,
) -> FinalEffluentQuality:

    if influent_bod_mg_l > 0:
        bod_removal = (
            1 -
            target_bod_mg_l /
            influent_bod_mg_l
        ) * 100
    else:
        bod_removal = 0

    if influent_tss_mg_l > 0:
        tss_removal = (
            1 -
            target_tss_mg_l /
            influent_tss_mg_l
        ) * 100
    else:
        tss_removal = 0

    bod_load = (
        average_flow_m3_day
        * target_bod_mg_l
        / 1000
    )

    tss_load = (
        average_flow_m3_day
        * target_tss_mg_l
        / 1000
    )

    return FinalEffluentQuality(
        influent_bod_mg_l=influent_bod_mg_l,
        influent_tss_mg_l=influent_tss_mg_l,
        target_bod_mg_l=target_bod_mg_l,
        target_tss_mg_l=target_tss_mg_l,
        bod_removal_percent=bod_removal,
        tss_removal_percent=tss_removal,
        bod_load_kg_day=bod_load,
        tss_load_kg_day=tss_load,
    )