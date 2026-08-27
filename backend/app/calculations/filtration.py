"""
Filtration design calculations for WWTP.

This module provides preliminary rapid filtration sizing.
It supports both m3/m2/day and m3/m2/hour filtration-rate inputs
for compatibility with the project's calculation and test modules.
"""

from dataclasses import dataclass


@dataclass
class FiltrationDesign:
    """Results of preliminary filtration design."""

    design_flow_m3_day: float

    filtration_rate_m3_m2_day: float
    filtration_rate_m3_m2_hr: float

    number_of_filters: int
    operating_filters: int
    standby_filters: int

    required_filter_area_m2: float
    total_area_m2: float
    area_per_filter_m2: float

    filter_width_m: float
    filter_length_m: float

    backwash_flow_m3_day: float
    backwash_flow_m3_hr: float


def design_filtration(
    flow_m3_day=None,
    filtration_rate_m3_m2_day=None,
    filtration_rate_m3_m2_hr=None,
    number_of_filters=1,
    filter_length_to_width_ratio=1.5,
    design_flow_m3_day=None,
):
    """
    Calculate preliminary filtration-unit dimensions.

    Parameters
    ----------
    flow_m3_day : float
        Design flow in m3/day.

    design_flow_m3_day : float
        Alternative name for design flow.

    filtration_rate_m3_m2_day : float
        Filtration rate in m3/m2/day.

    filtration_rate_m3_m2_hr : float
        Filtration rate in m3/m2/hour.

    number_of_filters : int
        Total number of filter units.

    filter_length_to_width_ratio : float
        Ratio of filter length to width.

    Returns
    -------
    FiltrationDesign
        Preliminary filtration design results.
    """

    # ---------------------------------------------------------
    # 1. FLOW
    # ---------------------------------------------------------

    if flow_m3_day is None:
        flow_m3_day = design_flow_m3_day

    if flow_m3_day is None:
        raise ValueError("Design flow must be provided.")

    if flow_m3_day <= 0:
        raise ValueError("Design flow must be greater than zero.")

    # ---------------------------------------------------------
    # 2. NUMBER OF FILTERS
    # ---------------------------------------------------------

    if number_of_filters <= 0:
        raise ValueError("Number of filters must be greater than zero.")

    if not isinstance(number_of_filters, int):
        raise ValueError("Number of filters must be an integer.")

    # ---------------------------------------------------------
    # 3. FILTRATION RATE
    # ---------------------------------------------------------

    if filtration_rate_m3_m2_day is None and filtration_rate_m3_m2_hr is None:
        raise ValueError("Filtration rate must be provided.")

    if (
        filtration_rate_m3_m2_day is not None
        and filtration_rate_m3_m2_hr is not None
    ):
        raise ValueError(
            "Provide either daily or hourly filtration rate, not both."
        )

    if filtration_rate_m3_m2_day is not None:

        if filtration_rate_m3_m2_day <= 0:
            raise ValueError(
                "Filtration rate must be greater than zero."
            )

        rate_day = float(filtration_rate_m3_m2_day)
        rate_hr = rate_day / 24.0

    else:

        if filtration_rate_m3_m2_hr <= 0:
            raise ValueError(
                "Filtration rate must be greater than zero."
            )

        rate_hr = float(filtration_rate_m3_m2_hr)
        rate_day = rate_hr * 24.0

    # ---------------------------------------------------------
    # 4. FILTER DIMENSION RATIO
    # ---------------------------------------------------------

    if filter_length_to_width_ratio <= 0:
        raise ValueError(
            "Filter length-to-width ratio must be greater than zero."
        )

    ratio = float(filter_length_to_width_ratio)

    # ---------------------------------------------------------
    # 5. REQUIRED FILTER AREA
    # ---------------------------------------------------------
    #
    # A = Q / filtration rate
    #
    # Q       = m3/day
    # rate    = m3/m2/day
    # A       = m2
    #
    # ---------------------------------------------------------

    required_filter_area_m2 = flow_m3_day / rate_day

    # ---------------------------------------------------------
    # 6. STANDBY / OPERATING FILTERS
    # ---------------------------------------------------------
    #
    # For more than one filter, keep one filter as standby.
    #
    # Example:
    # 5 total -> 4 operating + 1 standby
    #
    # For one filter:
    # 1 operating + 0 standby
    #
    # ---------------------------------------------------------

    if number_of_filters > 1:
        standby_filters = 1
    else:
        standby_filters = 0

    operating_filters = number_of_filters - standby_filters

    if operating_filters <= 0:
        raise ValueError(
            "At least one filter must remain operational."
        )

    # ---------------------------------------------------------
    # 7. AREA PER FILTER
    # ---------------------------------------------------------
    #
    # Design area is divided among operating filters.
    #
    # ---------------------------------------------------------

    area_per_filter_m2 = (
    required_filter_area_m2 / number_of_filters
    )


    # Total installed area is based on all physical filters.
    total_area_m2 = required_filter_area_m2

    # ---------------------------------------------------------
    # 8. FILTER WIDTH AND LENGTH
    # ---------------------------------------------------------
    #
    # L/W = ratio
    #
    # Area = L × W
    #
    # Therefore:
    #
    # W = sqrt(A / ratio)
    # L = ratio × W
    #
    # ---------------------------------------------------------

    filter_width_m = (
        area_per_filter_m2 / ratio
    ) ** 0.5

    filter_length_m = (
        filter_width_m * ratio
    )

    # ---------------------------------------------------------
    # 9. BACKWASH FLOW
    # ---------------------------------------------------------
    #
    # Preliminary allowance:
    # approximately 15% of design flow.
    #
    # This is a preliminary design estimate and should be
    # replaced by the selected filter manufacturer's/design
    # criteria in a detailed engineering design.
    #
    # ---------------------------------------------------------

    backwash_flow_m3_day = flow_m3_day * 0.15
    backwash_flow_m3_hr = backwash_flow_m3_day / 24.0

    # ---------------------------------------------------------
    # 10. RETURN RESULTS
    # ---------------------------------------------------------

    return FiltrationDesign(
        design_flow_m3_day=float(flow_m3_day),

        filtration_rate_m3_m2_day=rate_day,
        filtration_rate_m3_m2_hr=rate_hr,

        number_of_filters=number_of_filters,
        operating_filters=operating_filters,
        standby_filters=standby_filters,

        required_filter_area_m2=required_filter_area_m2,
        total_area_m2=total_area_m2,
        area_per_filter_m2=area_per_filter_m2,

        filter_width_m=filter_width_m,
        filter_length_m=filter_length_m,

        backwash_flow_m3_day=backwash_flow_m3_day,
        backwash_flow_m3_hr=backwash_flow_m3_hr,
    )