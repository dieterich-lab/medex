from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class BasicStatsNumericalDataRequest(BaseModel):
    measurements: List[str]
    entities: List[str]


class BasicStatsCategoricalDataRequest(BaseModel):
    measurements: List[str]
    entities: List[str]


class BasicStatsDateRequest(BaseModel):
    measurements: List[str]
    entities: List[str]
