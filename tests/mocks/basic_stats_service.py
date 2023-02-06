from medex.services.basic_stats import BasicStatisticsService

DEFAULT_DATA = {'count': {"('blood pressure', 'baseline')": 2}, 'min': {"('blood pressure', 'baseline')": 65},
                'max': {"('blood pressure', 'baseline')": 128},
                'mean': {"('blood pressure', 'baseline')": 96.5}, 'median': {"('blood pressure', 'baseline')": 95},
                'stddev': {"('blood pressure', 'baseline')": 25},
                'stderr': {"('blood pressure', 'baseline')": 0}, 'count_nan': {"('blood pressure', 'baseline')": 0}}


class BasicStatisticsServiceMock(BasicStatisticsService):
    def __init__(self):  # noqa
        pass

    def get_basic_stats_for_numerical_entities(self, basis_stats_data):
        return DEFAULT_DATA
