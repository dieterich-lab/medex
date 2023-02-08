from typing import Union, Optional

from flask_sqlalchemy.query import Query

from medex.dto.filter import FilterStatus, CategoricalFilter, NumericalFilter
from medex.services.filter import FilterService


DEFAULT_FILTER_STATUS = {
    'filtered_patient_count': 4711,
    'filters': {
        'diabetes': {'measurement': None, 'categories': ['nein']},
        'temperature': {'measurement': None, 'from_value': 39.0, 'to_value': 43.0}
    },
}


class FilterServiceMock(FilterService):
    def __init__(self):  # noqa
        self._filter_status = FilterStatus.parse_obj(DEFAULT_FILTER_STATUS)

    def add_filter(self, entity: str, new_filter: Union[CategoricalFilter, NumericalFilter]):
        self._filter_status.filters[entity] = new_filter

    def delete_all_filters(self):
        self._filter_status.filters = {}
        self._filter_status.filtered_patient_count = None

    def delete_filter(self, entity: str):
        del self._filter_status.filters[entity]

    def apply_filter(self, table, query: Query) -> Query:
        return query

    def apply_filter_to_complex_query(self, query: Query) -> Query:
        return query

    def set_measurement(self, new_measurement: Optional[str]):
        self._filter_status.measurement = new_measurement
