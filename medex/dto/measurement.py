from typing import List

from pydantic import BaseModel


class MeasurementInfo(BaseModel):
    display_name: str
    values: List[str]
