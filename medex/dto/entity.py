from typing import Optional, List

from pydantic import BaseModel, root_validator
from enum import Enum


class EntityType(Enum):
    NUMERICAL = 'Double'
    CATEGORICAL = 'String'
    DATE = 'Date'


class Entity(BaseModel):
    key: str
    type: EntityType
    synonym: Optional[str]
    description: Optional[str]
    unit: Optional[str]
    show: Optional[str]
    categories: Optional[List[str]]
    min: Optional[float]
    max: Optional[float]

    @classmethod
    @root_validator
    def check_categories(cls, values):
        entity_type = values.get('type')
        categories = values.get('categories')
        if entity_type == EntityType.CATEGORICAL:
            if categories is None:
                raise ValueError('categorical entities need categories')
        else:
            if categories is not None:
                raise ValueError('only categorical entities can have categories')

    @classmethod
    @root_validator
    def check_min_max(cls, values):
        entity_type = values.get('type')
        min_value = values.get('min')
        max_value = values.get('max')
        if entity_type == EntityType.NUMERICAL:
            if min_value is None or max_value is None:
                raise ValueError('numerical entities need a min/max range')
        else:
            if min_value is not None or max_value is not None:
                raise ValueError('only numerical entities can have a min/max range')
