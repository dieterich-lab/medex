from typing import List, Union, Dict, Optional

from pydantic import BaseModel


class GenericFilter(BaseModel):
    measurement: Optional[str]


class CategoricalFilter(GenericFilter):
    categories: List[str]


class AddCategoricalFilterRequest(CategoricalFilter):
    entity: str


class NumericalFilter(GenericFilter):
    from_value: float
    to_value: float


class AddNumericalFilterRequest(NumericalFilter):
    entity: str


class FilterStatus(BaseModel):
    filtered_patient_count: Optional[int]
    filters: Dict[str, Union[CategoricalFilter, NumericalFilter]]


class DeleteFilterRequest(BaseModel):
    entity: str


class SetMeasurementRequest(BaseModel):
    measurement: Optional[str]
