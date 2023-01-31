from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class DateRange(BaseModel):
    from_date: date
    to_date: date


class BoxplotDataRequest(BaseModel):
    measurements: List[str]
    numerical_entity: str
    categorical_entity: str
    categories: List[str]
    plot_type: str
    date_range: Optional[DateRange]
