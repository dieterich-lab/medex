from typing import List

from pydantic import BaseModel


class HeatmapDataRequest(BaseModel):
    entities: List[str]
