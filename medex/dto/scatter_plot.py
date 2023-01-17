from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class GroupByCategoricalEntity(BaseModel):
    key: str
    categories: List[str]


class ScaleScatterPlot(BaseModel):
    log_x: bool
    log_y: bool


class DateRange(BaseModel):
    from_date: date
    to_date: date


class ScatterPlotDataRequest(BaseModel):
    measurement_x_axis: str
    key_x_axis: str
    measurement_y_axis: str
    key_y_axis: str
    scale: Optional[ScaleScatterPlot]
    add_group_by: Optional[GroupByCategoricalEntity]
    date_range: Optional[DateRange]
