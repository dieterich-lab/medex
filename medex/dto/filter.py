from typing import List, Union, Dict

from pydantic import BaseModel


class CategoricalFilter(BaseModel):
    categories: List[str]


class AddCategoricalFilterRequest(CategoricalFilter):
    entity: str


class NumericalFilter(BaseModel):
    from_value: float
    to_value: float
    min: float
    max: float


class AddNumericalFilterRequest(NumericalFilter):
    entity: str


class FilterStatus(BaseModel):
    filters: Dict[str, Union[CategoricalFilter, NumericalFilter]]


class DeleteFilterRequest(BaseModel):
    entity: str
