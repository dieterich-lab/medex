from typing import List

from pydantic import BaseModel


class BoxplotDataRequest(BaseModel):
    measurements: List[str]
    numerical_entity: str
    categorical_entity: str
    categories: List[str]
    plot_type: str
