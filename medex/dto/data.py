from datetime import datetime
from enum import Enum
from typing import List, Dict, Union

from pydantic import BaseModel


class PaginationInfo(BaseModel):
    offset: int
    limit: int


class SortDirection(Enum):
    ASC = 'asc'
    DESC = 'desc'


class SortItem(BaseModel):
    column: str
    direction: SortDirection


class SortOrder(BaseModel):
    items: List[SortItem]


class FilteredDataRequest(BaseModel):
    measurements: List[str]
    entities: List[str]
    pagination_info: PaginationInfo
    sort_order: SortOrder


class SingleDataItem(BaseModel):
    name_id: str
    measurement: str
    key: str
    value: str


class FilteredDataFlatResponse(BaseModel):
    data: List[SingleDataItem]


class MeasurementDataItem(BaseModel):
    name_id: str
    measurement: str
    data_by_entity_id: Dict[str, Union[str, float, datetime]]


class FilteredDataByMeasurementResponse(BaseModel):
    data: List[MeasurementDataItem]
