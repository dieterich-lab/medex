from typing import List, Optional

from medex.dto.data import SortOrder
from medex.services.data import DataService

DEFAULT_FILTERED_FLAT_DATA = [
    {'patient_id': 'p1', 'measurement': 'baseline', 'key': 'cat1', 'value': 'ja', 'total': 2},
    {'patient_id': 'p2', 'measurement': 'baseline', 'key': 'num1', 'value': '120', 'total': 2},
]

DEFAULT_FILTERED_BY_MEASUREMENT_DATA = [
    {'patient_id': 'p1', 'measurement': 'baseline', 'cat1': 'ja', 'num1': '135', 'total': 3},
    {'patient_id': 'p2', 'measurement': 'baseline', 'cat1': 'nein', 'num1': '128', 'total': 3}
]


class DataServiceMock(DataService):
    def __init__(self):  # noqa
        pass

    def get_filtered_data_flat(
            self,
            measurements: List[str],
            entities: List[str],
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            sort_order: Optional[SortOrder] = None,
    ) -> (List[dict], int):
        return DEFAULT_FILTERED_FLAT_DATA, 2

    def get_filtered_data_by_measurement(
            self,
            measurements: List[str],
            entities: List[str],
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            sort_order: Optional[SortOrder] = None,
    ) -> (List[dict], int):
        return DEFAULT_FILTERED_BY_MEASUREMENT_DATA, 3
