from typing import Optional, Union

from sqlalchemy import delete, select, func
from sqlalchemy.dialects.mysql import insert

from medex.dto.filter import FilterStatus, CategoricalFilter, NumericalFilter
from modules.models import SessionFilteredNameIds, SessionNameIdsMatchingFilter, TableCategorical, TableNumerical


class FilterService:
    def __init__(self, database_session, session_id: str, filter_status: Optional[FilterStatus]):
        self._database_session = database_session
        self._session_id = session_id

        if filter_status is None:
            self._filter_status = FilterStatus(filters={})
        else:
            self._filter_status = filter_status

    def add_filter(self, entity: str, new_filter: Union[CategoricalFilter, NumericalFilter]):
        self._clean_up_filter_for_entity(entity)
        if isinstance(new_filter, CategoricalFilter):
            self._record_name_ids_for_categorical_filter(entity, new_filter)
        elif isinstance(new_filter, NumericalFilter):
            self._record_name_ids_for_numerical_filter(entity, new_filter)
        else:
            raise Exception('Unexpected Data Type')
        self._record_name_ids_for_all_filters()
        self._filter_status.filters[entity] = new_filter

    def _clean_up_filter_for_entity(self, entity):
        table = SessionNameIdsMatchingFilter
        if len(self._filter_status.filters) == 0:
            self.delete_all_filters()
        else:
            self._database_session.execute(
                delete(table)
                .where(table.c.session_id == self._session_id)
                .where(table.c.filter == entity)
            )

    def delete_all_filters(self):
        db = self._database_session
        for table in [SessionFilteredNameIds, SessionNameIdsMatchingFilter]:
            db.execute(
                delete(table)
                .where(table.c.session_id == self._session_id)
            )

    def _record_name_ids_for_categorical_filter(self, entity, new_filter: CategoricalFilter):
        data_table = TableCategorical
        name_ids_for_filter = (
            select(
                self._session_id, entity, data_table.c.name_id
            ).distinct()
            .where(data_table.c.key == entity)
            .where(data_table.c.value in new_filter.categories)
        )
        self._database_session.execute(
            insert(SessionNameIdsMatchingFilter).from_select(
                ['session_id', 'filter', 'name_id'],
                name_ids_for_filter
            )
        )

    def _record_name_ids_for_numerical_filter(self, entity, new_filter: NumericalFilter):
        data_table = TableNumerical
        name_ids_for_filter = (
            select(
                self._session_id, entity, data_table.c.name_id
            ).distinct()
            .where(data_table.c.key == entity)
            .where(data_table.c.value.between(new_filter.from_value, new_filter.to_value))
        )
        self._database_session.execute(
            insert(SessionNameIdsMatchingFilter).from_select(
                ['session_id', 'filter', 'name_id'],
                name_ids_for_filter
            )
        )

    def _record_name_ids_for_all_filters(self):
        db = self._database_session
        table = SessionNameIdsMatchingFilter
        db.execute(
            delete(SessionFilteredNameIds)
            .where(SessionFilteredNameIds.c.session_id == self._session_id)
        )

        name_ids_for_all_filters = (
            select(
                self._session_id, table.c.name_id, func.count(table.c.name_id)
            )
            .group_by(table.c.name_id)
        )
        db.execute(
            insert(SessionFilteredNameIds).from_select(
                ['session_id', 'name_id'],
                name_ids_for_all_filters
            )
        )
