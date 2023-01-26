from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class DateRange(BaseModel):
    from_date: date
    to_date: date


class HistogramDataRequest(BaseModel):
    measurements: List[str]
    numerical_entity: str
    categorical_entity: str
    categories: List[str]
    bins: Optional[int]
    date_range: Optional[DateRange]
