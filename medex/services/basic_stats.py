from typing import List
from pandas import DataFrame
from sqlalchemy import select, func, and_
from medex.services.filter import FilterService
from medex.database_schema import TableNumerical, Patient, TableCategorical, TableDate


class BasicStatisticsService:
    def __init__(self, database_session, filter_service: FilterService):
        self._database_session = database_session
        self._filter_service = filter_service

    def get_basic_stats_for_numerical_entities(self, basis_stats_data) -> List[dict]:
        query_raw_data = self._get_raw_data_query(basis_stats_data)
        query_raw_data_with_filter = self._filter_service.apply_filter(TableNumerical, query_raw_data)
        query_select_stats = self._get_basic_statistics(query_raw_data_with_filter)
        df = self._get_dataframe(query_select_stats)
        result_dict = df.to_dict(orient='records')
        return result_dict

    def get_basic_stats_for_categorical_entities(self, basic_stats_data) -> List[dict]:
        query_select = self._select_raw_data(TableCategorical, basic_stats_data)
        query_with_filter = self._filter_service.apply_filter(TableCategorical, query_select)
        result_dict = self._get_dataframe_to_dict(query_with_filter)
        return result_dict

    def get_basic_stats_for_date_entities(self, basic_stats_data) -> List[dict]:
        query_select = self._select_raw_data(TableDate, basic_stats_data)
        query_with_filter = self._filter_service.apply_filter(TableDate, query_select)
        result_dict = self._get_dataframe_to_dict(query_with_filter)
        return result_dict

    def _get_dataframe_to_dict(self, query_with_filter):
        query_statistics = self._get_statistics(query_with_filter)
        rv = self._database_session.execute(query_statistics)
        df = DataFrame(rv.all())
        if not df.empty:
            n = self._get_patient_count()
            df['count NaN'] = n - df['count']
        result_dict = df.to_dict(orient='records')
        return result_dict

    @staticmethod
    def _select_raw_data(table, basic_stats_data):
        query_select = select(
            table.key, table.measurement, table.name_id
        ).where(
            and_(
                table.key.in_(basic_stats_data.entities), table.measurement.in_(basic_stats_data.measurements),
            )
        ).group_by(table.name_id, table.key, table.measurement)
        return query_select

    @staticmethod
    def _get_statistics(query_with_filter):
        query_statistics = select(
            query_with_filter.c.key, query_with_filter.c.measurement,
            func.count(query_with_filter.c.name_id).label('count')
        ) \
            .group_by(query_with_filter.c.key, query_with_filter.c.measurement) \
            .order_by(query_with_filter.c.key, query_with_filter.c.measurement)
        return query_statistics

    @staticmethod
    def _get_raw_data_query(basic_stats_data):
        query_select = select(
            TableNumerical.key, TableNumerical.measurement, TableNumerical.name_id,
            func.avg(TableNumerical.value).label('value')
        ).where(
            and_(
                TableNumerical.key.in_(basic_stats_data.entities),
                TableNumerical.measurement.in_(basic_stats_data.measurements),
            )
        ).group_by(TableNumerical.name_id, TableNumerical.key, TableNumerical.measurement)
        return query_select

    def _get_basic_statistics(self, query_raw_data_with_filter):
        query_select_stats = select(
            query_raw_data_with_filter.c.key,
            query_raw_data_with_filter.c.measurement,
            *self._get_aggregated_columns(query_raw_data_with_filter)
        ) \
            .group_by(query_raw_data_with_filter.c.key, query_raw_data_with_filter.c.measurement) \
            .order_by(query_raw_data_with_filter.c.key, query_raw_data_with_filter.c.measurement)
        return query_select_stats

    @staticmethod
    def _get_aggregated_columns(query_raw_data_with_filter):
        aggregated_columns = [
            func.count(query_raw_data_with_filter.c.name_id).label('count'),
            func.min(query_raw_data_with_filter.c.value).label('min'),
            func.max(query_raw_data_with_filter.c.value).label('max'),
            func.avg(query_raw_data_with_filter.c.value).label('mean'),
            func.percentile_cont(0.5).within_group(query_raw_data_with_filter.c.value).label('median'),
            func.stddev(query_raw_data_with_filter.c.value).label('stddev'),
            (
                    func.stddev(query_raw_data_with_filter.c.value).label('stddev') /
                    func.sqrt(func.count(query_raw_data_with_filter.c.value))
            ).label('stderr')
        ]
        return aggregated_columns

    def _get_dataframe(self, query_select_stats):
        rv = self._database_session.execute(query_select_stats)
        df = DataFrame(rv.all())
        if not df.empty:
            total_patient_count = self._get_patient_count()
            df['count NaN'] = total_patient_count - df['count']
            df[['min', 'max', 'mean', 'median', 'stddev', 'stderr']] = df[
                ['min', 'max', 'mean', 'median', 'stddev', 'stderr']
            ].astype(float).round(decimals=2)
        return df

    def _get_patient_count(self):
        patient_count_sql = select(func.count(func.distinct(Patient.name_id)))
        patient_count_result = self._database_session.execute(patient_count_sql).scalar()
        return patient_count_result
