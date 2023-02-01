from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class DateRange(BaseModel):
    from_date: date
    to_date: date


class HeatmapDataRequest(BaseModel):
    entities: List[str]
    date_range: Optional[DateRange]
