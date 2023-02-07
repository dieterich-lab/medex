from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class DateRange(BaseModel):
    from_date: date
    to_date: date


class BasicStatsNumericalDataRequest(BaseModel):
    measurements: List[str]
    entities: List[str]
    date_range: Optional[DateRange]


class BasicStatsCategoricalDataRequest(BaseModel):
    measurements: List[str]
    entities: List[str]
    date_range: Optional[DateRange]


class BasicStatsDateRequest(BaseModel):
    measurements: List[str]
    entities: List[str]
    date_range: Optional[DateRange]
