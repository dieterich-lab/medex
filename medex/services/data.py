from typing import List, Optional

from sqlalchemy import union, select

from medex.services.filter import FilterService
from modules.models import TableCategorical, TableNumerical, TableDate


class DataService:
    def __init__(
            self,
            database_session,
            filter_service: FilterService,
            limit=None,
            offset=None
    ):
        self._database_session = database_session
        self._filter_service = filter_service

    def get_filtered_data_flat(
            self,
            measurements: List[str],
            entities: List[str],
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ):
        db = self._database_session
        sql_union = self._get_union_of_tables()
        sql_select = (
            select(sql_union.c)
            .where(sql_union.c.measurement == measurements)
            .where(sql_union.c.key == entities)
            .order_by(sql_union.c.name_id, sql_union.c.key)
        )
        query_with_filter = self._filter_service.apply_filter_to_complex_query(sql_select)
        if limit is not None and offset is not None:
            query_with_filter = query_with_filter \
                .limit(limit) \
                .offset(offset)
        result = db.execute(query_with_filter)

        return result

    @staticmethod
    def _get_union_of_tables():
        sql_union = union(
            select(TableCategorical.name_id, TableCategorical.case_id, TableCategorical.measurement,
                   TableCategorical.key, TableCategorical.value),
            select(TableNumerical.name_id, TableNumerical.case_id, TableNumerical.measurement,
                   TableNumerical.key, TableNumerical.value),
            select(TableDate.name_id, TableDate.case_id, TableDate.measurement, TableDate.key,
                   TableDate.value)
        ).subquery()

        return sql_union

    def get_filtered_data_by_measurement(self):
        pass
