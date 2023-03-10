from typing import List

from pydantic import BaseModel


class BarChartDataRequest(BaseModel):
    measurements: List[str]
    key: str
    categories: List[str]
    plot_type: str
