import json
from typing import List, Optional

from sqlalchemy import union, select, and_, desc, literal_column, func, case, cast, String, Date, Float
from sqlalchemy.orm import query

from medex.dto.data import SortOrder, SingleDataItem, MeasurementDataItem
from medex.services.filter import FilterService
from modules.models import TableCategorical, TableNumerical, TableDate


class DataService:
    def __init__(
            self,
            database_session,
            filter_service: FilterService,
    ):
        self._database_session = database_session
        self._filter_service = filter_service

    def get_filtered_data_flat(
            self,
            measurements: List[str],
            entities: List[str],
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            sort_order: Optional[SortOrder] = None,
    ) -> List[SingleDataItem]:
        query_select = self._get_union_of_tables(entities, measurements)
        query_select = self._get_ordered_data(query_select, sort_order)
        query_with_filter = self._filter_service.apply_filter_to_complex_query(query_select)

        if limit is not None and offset is not None:
            query_with_filter = query_with_filter \
                .limit(limit) \
                .offset(offset)

        result = self._database_session.execute(query_with_filter).all()

        return result

    def get_filtered_data_by_measurement(
            self,
            measurements: List[str],
            entities: List[str],
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            sort_order: Optional[SortOrder] = None
    ) -> List[MeasurementDataItem]:
        query_select = self._get_union_of_tables_postgres(entities, measurements)
        query_select = self._get_entities_as_columns(query_select, entities)
        query_select_with_order = self._get_ordered_data(query_select, sort_order)
        query_with_filter = self._filter_service.apply_filter_to_complex_query(query_select_with_order)

        if limit is not None and offset is not None:
            query_with_filter = query_with_filter \
                .limit(limit) \
                .offset(offset)
        result = self._database_session.execute(query_with_filter).all()
        return result

    def _get_entities_as_columns(self, query_select, entities) -> query:
        query_group_by = (
            select(query_select.c.name_id, query_select.c.measurement, query_select.c.key,
                   func.string_agg(query_select.c.value, literal_column("';'")).label('value'))
            .group_by(query_select.c.name_id, query_select.c.measurement, query_select.c.key)
        )

        case_when = []
        for entity in entities:
            case_when.append(self._get_valid_case_for_entity(entity, query_group_by))

        query_select = (
            select(query_group_by.c.name_id, query_group_by.c.measurement, *case_when)
            .group_by(query_group_by.c.name_id, query_group_by.c.measurement)
        )

        return query_select

    def _get_valid_case_for_entity(self, entity, query_group_by):
        db = self._database_session
        entity_list_numeric = db.execute(select(TableNumerical.key).distinct()).all()
        entity_list_numeric = [i[0] for i in entity_list_numeric]
        entity_list_date = db.execute(select(TableDate.key).distinct()).all()
        entity_list_date = [i[0] for i in entity_list_date]
        if entity in entity_list_numeric:
            return func.min(case([(query_group_by.c.key == entity, cast(query_group_by.c.value, Float))])).label(entity)
        elif entity in entity_list_date:
            return func.min(case([(query_group_by.c.key == entity, cast(query_group_by.c.value, Date))])).label(entity)
        else:
            return func.min(case([(query_group_by.c.key == entity, query_group_by.c.value)])).label(entity)

    @staticmethod
    def _get_union_of_tables(entities, measurements) -> query:
        list_query_tables = [
            select(table.name_id, table.measurement, table.key, table.value)
            for table in [TableCategorical, TableNumerical, TableDate]
        ]
        query_union = union(*list_query_tables)
        query_select = (
            select(query_union.c)
            .where(
                and_(query_union.c.measurement.in_(measurements),
                     query_union.c.key.in_(entities))
            )
        )

        return query_select

    @staticmethod
    def _get_union_of_tables_postgres(entities, measurements) -> query:
        list_query_tables = [
            select(table.name_id, table.measurement, table.key, cast(table.value, String))
            for table in [TableCategorical, TableNumerical, TableDate]
        ]
        query_union = union(*list_query_tables)
        query_select = (
            select(query_union.c)
            .where(
                and_(query_union.c.measurement.in_(measurements),
                     query_union.c.key.in_(entities))
            )
        )

        return query_select

    def _get_ordered_data(self, query_select, sort_order) -> query:
        if sort_order is not None:
            sort_columns = self._get_sort_order_as_columns(sort_order)
            query_select = query_select.order_by(*sort_columns)
        return query_select

    @staticmethod
    def _get_sort_order_as_columns(sort_order) -> query:
        sort_columns = [
            desc(item.column) if item.direction.value == 'desc' else item.column
            for idx, item in enumerate(sort_order.items)
        ]
        return sort_columns
