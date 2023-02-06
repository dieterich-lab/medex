from pandas import DataFrame
from pydantic import json
from sqlalchemy import select, func, and_, label

from medex.services.filter import FilterService
from modules.models import TableNumerical, Patient


class BasicStatisticsService:
    def __init__(self, database_session, filter_service: FilterService):
        self._database_session = database_session
        self._filter_service = filter_service

    def get_basic_stats_for_numerical_entities(self, basis_stats_data) -> json:
        query_raw_data = self._get_raw_data_query(basis_stats_data)
        query_raw_data_with_filter = self._filter_service.apply_filter(TableNumerical, query_raw_data)
        query_select_stats = self._get_basic_statistics(query_raw_data_with_filter)
        df = self._get_dataframe(query_select_stats)
        df['measurement'] = df['measurement'].astype(str)
        df = df.set_index(['key', 'measurement'])
        result = df.to_json(orient='columns')
        return result

    @staticmethod
    def _get_raw_data_query(basis_stats_data):
        query_select = select(
            TableNumerical.key, TableNumerical.measurement, TableNumerical.name_id,
            func.avg(TableNumerical.value).label('value')
        ).where(
            and_(
                TableNumerical.key.in_(basis_stats_data.entities),
                TableNumerical.measurement.in_(basis_stats_data.measurements),
                TableNumerical.date.between(
                    basis_stats_data.date_range.from_date.strftime('%Y-%m-%d'),
                    basis_stats_data.date_range.to_date.strftime('%Y-%m-%d')
                )
            )
        ).group_by(TableNumerical.name_id, TableNumerical.key, TableNumerical.measurement)
        return query_select

    def _get_basic_statistics(self, query_raw_data_with_filter):
        query_select_stats = select(
            query_raw_data_with_filter.c.key,
            query_raw_data_with_filter.c.measurement,
            *self._get_aggregated_columns(query_raw_data_with_filter)
        )\
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
            label(
                'stderr',
                func.stddev(query_raw_data_with_filter.c.value).label('stddev') /
                func.sqrt(func.count(query_raw_data_with_filter.c.value))
            )
        ]
        return aggregated_columns

    def _get_dataframe(self, query_select_stats):
        rv = self._database_session.execute(query_select_stats)
        df = DataFrame(rv.all())
        total_patient_count = self._get_patient_count()
        df['count NaN'] = total_patient_count - df['count']
        df = df.round(decimals=2)
        return df

    def _get_patient_count(self):
        patient_count_sql = select(func.count(func.distinct(Patient.name_id)))
        patient_count_result = self._database_session.execute(patient_count_sql).scalar()
        return patient_count_result
