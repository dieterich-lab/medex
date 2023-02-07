from typing import List

from medex.services.basic_stats import BasicStatisticsService

DEFAULT_DATA_NUMERICAL = [
    {"key": "blood pressure", "measurement": "baseline", "count": 2, "min": 129.0, "max": 138.0, "mean": 133.5,
     "median": 133.5, "stddev": 6.3639610307, "stderr": 4.5, "count NaN": 1},
    {"key": "blood pressure", "measurement": "follow up1", "count": 1, "min": 135.0, "max": 135.0, "mean": 135.0,
     "median": 135.0, "stddev": None, "stderr": None, "count NaN": 2},
    {"key": "temperature", "measurement": "baseline", "count": 1, "min": 38.5, "max": 38.5, "mean": 38.5,
     "median": 38.5, "stddev": None, "stderr": None, "count NaN": 2},
    {"key": "temperature", "measurement": "follow up1", "count": 1, "min": 41.5, "max": 41.5, "mean": 41.5,
     "median": 41.5, "stddev": None, "stderr": None, "count NaN": 2}
]

DEFAULT_DATA_CATEGORICAL = [
    {'key': 'biopsy', 'measurement': 'baseline', 'count': 1, 'count NaN': 2},
    {'key': 'diabetes', 'measurement': 'baseline', 'count': 2, 'count NaN': 1},
    {'key': 'diabetes', 'measurement': 'follow up1', 'count': 1, 'count NaN': 2}
]


class BasicStatisticsServiceMock(BasicStatisticsService):
    def __init__(self):  # noqa
        pass

    def get_basic_stats_for_numerical_entities(self, basis_stats_data) -> List[dict]:
        return DEFAULT_DATA_NUMERICAL

    def get_basic_stats_for_categorical_entities(self, basic_stats_data) -> List[dict]:
        return DEFAULT_DATA_CATEGORICAL

    def get_basic_stats_for_date_entities(self, basic_stats_data) -> List[dict]:
        return [{}]
