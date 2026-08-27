from typing import Literal
from pydantic import BaseModel, Field, model_validator


class ProjectInput(BaseModel):
    project_name: str = Field(min_length=1, max_length=200)
    wastewater_type: Literal["municipal", "industrial"]
    average_flow_m3_day: float = Field(gt=0)
    peak_flow_m3_day: float = Field(gt=0)
    influent_bod_mg_l: float = Field(ge=0)
    influent_cod_mg_l: float = Field(ge=0)
    influent_tss_mg_l: float = Field(ge=0)
    target_bod_mg_l: float = Field(ge=0)
    target_tss_mg_l: float = Field(ge=0)
    ammonia_mg_l: float = Field(ge=0, default=0)
    nitrification_required: bool = False

    @model_validator(mode="after")
    def validate_design_basis(self):
        if self.peak_flow_m3_day < self.average_flow_m3_day:
            raise ValueError("Peak flow must be greater than or equal to average flow.")
        if self.influent_cod_mg_l < self.influent_bod_mg_l:
            raise ValueError("Influent COD should be greater than or equal to BOD.")
        if self.target_bod_mg_l > self.influent_bod_mg_l:
            raise ValueError("Target BOD cannot exceed influent BOD.")
        if self.target_tss_mg_l > self.influent_tss_mg_l:
            raise ValueError("Target TSS cannot exceed influent TSS.")
        if self.nitrification_required and self.ammonia_mg_l <= 0:
            raise ValueError("Ammonia concentration must be greater than zero when nitrification is required.")
        return self
