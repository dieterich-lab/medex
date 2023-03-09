from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class HistogramDataRequest(BaseModel):
    measurements: List[str]
    numerical_entity: str
    categorical_entity: str
    categories: List[str]
    bins: Optional[int]
