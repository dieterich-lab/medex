from typing import Optional, List

from pydantic import BaseModel, model_validator
from enum import Enum


class EntityType(Enum):
    NUMERICAL = 'Double'
    CATEGORICAL = 'String'
    DATE = 'Date'


class Entity(BaseModel):
    key: str
    type: EntityType
    synonym: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    show: Optional[str] = None
    categories: Optional[List[str]] = None
    min: Optional[float] = None
    max: Optional[float] = None

    @classmethod
    @model_validator(mode='after')
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
    @model_validator(mode='after')
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
