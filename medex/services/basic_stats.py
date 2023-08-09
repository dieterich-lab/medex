from math import isnan
from typing import List
from sqlalchemy import select, func, and_
from medex.services.filter import FilterService
from medex.database_schema import TableNumerical, TableCategorical, TableDate, Patient


class BasicStatisticsService:
    BASE_COLUMNS = ['key', 'measurement', 'count']
    NUMERICAL_COLUMNS = BASE_COLUMNS + ['min', 'max', 'mean', 'median', 'stddev', 'stderr']

    def __init__(self, database_session, filter_service: FilterService):
        self._database_session = database_session
        self._filter_service = filter_service

    def get_basic_stats_for_numerical_entities(self, basic_stats_data) -> List[dict]:
        return self._get_generic_data_as_dicts(basic_stats_data, TableNumerical, self.NUMERICAL_COLUMNS, True)

    def _get_generic_data_as_dicts(self, basic_stats_data, table, columns, is_numerical) -> List[dict]:
        if is_numerical:
            extra_columns = self._get_extra_numerical_columns()
        else:
            extra_columns = []
        base_query = self._get_base_query(table, basic_stats_data, extra_columns)
        filtered_query = self._filter_service.apply_filter(table, base_query)
        grouped_query = self._get_grouped_query(table, filtered_query)
        return self._get_query_as_dicts(grouped_query, columns)

    @staticmethod
    def _get_base_query(table, basic_stats_data, extra_columns):
        query = select(
            table.key, table.measurement, func.count(table.name_id).label('count'),
            *extra_columns
        ).where(
            and_(
                table.key.in_(basic_stats_data.entities), table.measurement.in_(basic_stats_data.measurements),
            )
        )
        return query

    @staticmethod
    def _get_extra_numerical_columns():
        return [
            func.min(TableNumerical.value).label('min'),
            func.max(TableNumerical.value).label('max'),
            func.avg(TableNumerical.value).label('mean'),
            func.percentile_cont(0.5).within_group(TableNumerical.value).label('median'),
            func.stddev(TableNumerical.value).label('stddev'),
            (
                    func.stddev(TableNumerical.value) /
                    func.sqrt(func.count(TableNumerical.value))
            ).label('stderr')
        ]

    @staticmethod
    def _get_grouped_query(table, query):
        group_query = query \
            .group_by(table.key, table.measurement) \
            .order_by(table.key, table.measurement)
        return group_query

    def get_basic_stats_for_categorical_entities(self, basic_stats_data) -> List[dict]:
        return self._get_generic_data_as_dicts(basic_stats_data, TableCategorical, self.BASE_COLUMNS, False)

    def get_basic_stats_for_date_entities(self, basic_stats_data) -> List[dict]:
        return self._get_generic_data_as_dicts(basic_stats_data, TableDate, self.BASE_COLUMNS, False)

    def _get_query_as_dicts(self, query, columns):
        results = []
        patient_count = self._get_patient_count()
        for row in self._database_session.execute(query):
            new_item = {
                k: self._sanitize_value(getattr(row, k))
                for k in columns
            }
            new_item['count NaN'] = patient_count - new_item['count']
            results.append(new_item)
        return results

    def _get_patient_count(self):
        filtered_patients = self._filter_service.get_filtered_patient_count()
        if filtered_patients is None:
            query = select(func.count(func.distinct(Patient.name_id)))
            return self._database_session.execute(query).scalar()
        else:
            return filtered_patients

    @staticmethod
    def _sanitize_value(value):
        if isinstance(value, float) and isnan(value):
            return 'NaN'
        else:
            return value
