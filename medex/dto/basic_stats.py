from typing import List

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
