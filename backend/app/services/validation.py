from typing import List


def validate_project(project) -> List[str]:

    errors = []

    if project.average_flow_m3_day <= 0:
        errors.append(
            "Average flow must be greater than zero."
        )

    if project.peak_flow_m3_day <= 0:
        errors.append(
            "Peak flow must be greater than zero."
        )

    if (
        project.peak_flow_m3_day
        < project.average_flow_m3_day
    ):
        errors.append(
            "Peak flow cannot be lower than average flow."
        )

    if project.influent_bod_mg_l < 0:
        errors.append(
            "Influent BOD cannot be negative."
        )

    if project.influent_cod_mg_l < 0:
        errors.append(
            "Influent COD cannot be negative."
        )

    if project.influent_tss_mg_l < 0:
        errors.append(
            "Influent TSS cannot be negative."
        )

    if project.ammonia_mg_l < 0:
        errors.append(
            "Ammonia cannot be negative."
        )

    if (
        project.influent_cod_mg_l
        < project.influent_bod_mg_l
    ):
        errors.append(
            "COD should normally be greater than "
            "or equal to BOD. Verify the input."
        )

    if (
        project.target_bod_mg_l
        > project.influent_bod_mg_l
    ):
        errors.append(
            "Target BOD is higher than influent BOD."
        )

    if (
        project.target_tss_mg_l
        > project.influent_tss_mg_l
    ):
        errors.append(
            "Target TSS is higher than influent TSS."
        )

    return errors