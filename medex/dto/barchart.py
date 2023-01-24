from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class DateRange(BaseModel):
    from_date: date
    to_date: date


class BarChartDataRequest(BaseModel):
    measurements: List[str]
    key: str
    categories: List[str]
    plot_type: str
    date_range: Optional[DateRange]
