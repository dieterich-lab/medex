from typing import List, Optional

from medex.dto.data import SortOrder, SingleDataItem, MeasurementDataItem
from medex.services.data import DataService

DEFAULT_FILTERED_FLAT_DATA = [
    SingleDataItem(name_id='p1', measurement='baseline', key='cat1', value='ja'),
    SingleDataItem(name_id='p2', measurement='baseline', key='num1', value=120)
]

DEFAULT_FILTERED_BY_MEASUREMENT_DATA = [
    MeasurementDataItem(name_id='p1', measurement='baseline', data_by_entity_id={'cat1': 'ja', 'num1': 135}),
    MeasurementDataItem(name_id='p2', measurement='baseline', data_by_entity_id={'cat1': 'nein', 'num1': 128})
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
    ) -> List[SingleDataItem]:
        return DEFAULT_FILTERED_FLAT_DATA

    def get_filtered_data_by_measurement(
            self,
            measurements: List[str],
            entities: List[str],
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            sort_order: Optional[SortOrder] = None,
    ) -> List[MeasurementDataItem]:
        return DEFAULT_FILTERED_BY_MEASUREMENT_DATA
