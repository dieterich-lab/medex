from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class HeatmapDataRequest(BaseModel):
    entities: List[str]
