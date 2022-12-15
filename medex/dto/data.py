from typing import List, Dict

from pydantic import BaseModel


class FilteredDataRequest(BaseModel):
    measurements: List[str]
    entities: List[str]


class PaginationInfo(BaseModel):
    offset: int
    limit: int


class SingleDataItem(BaseModel):
    name_id: str
    measurement: str
    key: str
    value: str


class FilteredDataFlatResponse(BaseModel):
    pagination_info: PaginationInfo
    data: List[SingleDataItem]


class MeasurementDataItem(BaseModel):
    name_id: str
    measurement: str
    data_by_entity_id: Dict[str, any]


class FilteredDataByMeasurementResponse(BaseModel):
    pagination_info: PaginationInfo
    data: List[MeasurementDataItem]
