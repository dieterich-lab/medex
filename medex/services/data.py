from collections import namedtuple
from typing import List, Optional

from sqlalchemy import union, select, and_, desc, func, cast, String
from sqlalchemy.orm import query, aliased

from medex.dto.data import SortOrder
from medex.services.entity import EntityService
from medex.services.filter import FilterService
from medex.database_schema import TableCategorical, TableNumerical, TableDate


PartialQuery = namedtuple('PartialQuery', 'table entity_key')


class DataService:
    def __init__(
            self,
            database_session,
            filter_service: FilterService,
            entity_service: EntityService,
    ):
        self._database_session = database_session
        self._filter_service = filter_service
        self._entity_service = entity_service

    def get_filtered_data_flat(
            self,
            measurements: List[str],
            entities: List[str],
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            sort_order: Optional[SortOrder] = None,
    ) -> (List[dict], int):
        query_select = self._get_union_of_tables(entities, measurements)
        return self._do_query_with_extras(query_select, limit, offset, sort_order)

    def _do_query_with_extras(self, query_select, limit, offset, sort_order):
        query_with_filter = self._filter_service.apply_filter_to_complex_query(query_select)
        query_with_total = self._get_query_with_total(query_with_filter.subquery())
        query_ordered = self._get_ordered_data(query_with_total, sort_order)
        query_with_limit = self._get_query_with_limit(limit, offset, query_ordered)
        result_dict, total = self._get_all_results(query_with_limit)
        return result_dict, total

    def get_filtered_data_by_measurement(
            self,
            measurements: List[str],
            entities: List[str],
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            sort_order: Optional[SortOrder] = None
    ) -> (List[dict], int):
        relevant_patients_query = self._relevant_patients_query(entities, measurements)
        partial_queries = [self._get_partial_query(x) for x in entities]
        base_query = self._join_partial_queries(relevant_patients_query, partial_queries)
        return self._do_query_with_extras(base_query, limit, offset, sort_order)

    @staticmethod
    def _relevant_patients_query(entities: List[str], measurements: List[str]):
        list_query_tables = [
            select(table.name_id, table.measurement, table.key)
            for table in [TableCategorical, TableNumerical, TableDate]
        ]
        query_union = union(*list_query_tables).subquery()
        query_select_union = (
            select(
                query_union.exported_columns.name_id,
                query_union.exported_columns.measurement,
            )
            .where(
                and_(query_union.exported_columns.measurement.in_(measurements),
                     query_union.exported_columns.key.in_(entities))
            )
        )
        return query_select_union

    def _get_partial_query(self, entity_key) -> PartialQuery:
        entity = self._entity_service.get_entity_by_key(entity_key)
        return PartialQuery(
            table=self._entity_service.get_database_table_for_entity(entity),
            entity_key=entity_key
        )

    @staticmethod
    def _join_partial_queries(base_query, partial_queries: List[PartialQuery]):
        select_items = [
            base_query.exported_columns.name_id,
            base_query.exported_columns.measurement,
        ]
        tables = []
        for item in partial_queries:
            join_table = aliased(item.table)
            select_items.append(join_table.value.label(item.entity_key))
            tables.append(join_table)

        q = select(*select_items).distinct()
        for i in range(0, len(partial_queries)):
            q = q.outerjoin(
                tables[i],
                and_(
                    tables[i].key == partial_queries[i].entity_key,
                    base_query.exported_columns.name_id == tables[i].name_id,
                    base_query.exported_columns.measurement == tables[i].measurement,
                ),
            )
        return q

    @staticmethod
    def _get_union_of_tables(entities, measurements) -> query:
        list_query_tables = [
            select(table.name_id, table.measurement, table.key, cast(table.value, String))
            for table in [TableCategorical, TableNumerical, TableDate]
        ]
        query_union = union(*list_query_tables).subquery()
        query_select_union = (
            select(query_union)
            .where(
                and_(query_union.exported_columns.measurement.in_(measurements),
                     query_union.exported_columns.key.in_(entities))
            )
        )

        return query_select_union

    @staticmethod
    def _get_ordered_data(query_select, sort_order) -> query:
        if sort_order is not None:
            sort_columns = [
                desc(item.column) if item.direction.value == 'desc' else item.column
                for idx, item in enumerate(sort_order.items)
            ]
            return query_select.order_by(*sort_columns)
        return query_select

    @staticmethod
    def _get_query_with_limit(limit, offset, query_with_filter):
        if limit is not None and offset is not None:
            query_with_filter = query_with_filter \
                .limit(limit) \
                .offset(offset)
        return query_with_filter

    @staticmethod
    def _get_query_with_total(query_with_filter):
        total_count = func.count(query_with_filter.exported_columns.name_id).over().label('total')
        query_with_total = select(*query_with_filter.exported_columns, total_count)
        return query_with_total

    def _get_all_results(self, query_with_limit):
        all_results = self._database_session.execute(query_with_limit).all()
        total = 0
        if len(all_results) > 0:
            total = all_results[0].total
        result_dict = [
            {
                k: self._get_sanitized_value(k, v)
                for k, v in row._asdict().items()  # noqa - workaround
            }
            for row in all_results
        ]
        return result_dict, total

    @staticmethod
    def _get_sanitized_value(key, value):
        if value is None or key == 'total':
            return value
        else:
            return str(value)
