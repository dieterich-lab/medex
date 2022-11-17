from typing import Optional, Union

from sqlalchemy import delete, select, func, literal_column, join, and_
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Query

from medex.dto.filter import FilterStatus, CategoricalFilter, NumericalFilter
from medex.services.session import SessionService
from modules.models import SessionFilteredNameIds, SessionNameIdsMatchingFilter, TableCategorical, TableNumerical


class FilterService:
    def __init__(
            self,
            database_session,
            session_service: SessionService,
            filter_status: Optional[FilterStatus]
    ):
        self._database_session = database_session
        self._session_service = session_service

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
        self._database_session.commit()
        self._filter_status.filters[entity] = new_filter
        self._record_name_ids_for_all_filters()
        self._session_service.touch()
        self._database_session.commit()

    def _clean_up_filter_for_entity(self, entity):
        table = SessionNameIdsMatchingFilter
        if len(self._filter_status.filters) == 0:
            self.delete_all_filters()
        else:
            self._database_session.execute(
                delete(table)
                .where(table.session_id == self._session_service.get_id())
                .where(table.filter == entity)
            )

    def delete_all_filters(self):
        db = self._database_session
        for table in [SessionFilteredNameIds, SessionNameIdsMatchingFilter]:
            db.execute(
                delete(table)
                .where(table.session_id == self._session_service.get_id())
            )
        self._database_session.commit()
        self._filter_status.filters = {}

    def _record_name_ids_for_categorical_filter(self, entity, new_filter: CategoricalFilter):
        data_table = TableCategorical
        session_id = self._session_service.get_id()
        name_ids_for_filter = (
            select(
                literal_column(f"'{session_id}'"),
                literal_column(f"'{entity}'"),
                data_table.name_id
            ).distinct()
            .where(
                and_(
                    data_table.key == entity,
                    data_table.value.in_(new_filter.categories)
                )
            )
        )
        self._database_session.execute(
            insert(SessionNameIdsMatchingFilter).from_select(
                ['session_id', 'filter', 'name_id'],
                name_ids_for_filter
            )
        )

    def _record_name_ids_for_numerical_filter(self, entity, new_filter: NumericalFilter):
        data_table = TableNumerical
        session_id = self._session_service.get_id()
        name_ids_for_filter = (
            select(
                literal_column(f"'{session_id}'"),
                literal_column(f"'{entity}'"),
                data_table.name_id
            ).distinct()
            .where(data_table.key == entity)
            .where(data_table.value.between(new_filter.from_value, new_filter.to_value))
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
            .where(SessionFilteredNameIds.session_id == self._session_service.get_id())
        )

        number_of_matching_filters = func.count(table.name_id).label('number_of_matching_filters')
        session_id = self._session_service.get_id()
        name_ids_for_all_filters = (
            select(
                literal_column(f"'{session_id}'"), table.name_id
            )
            .group_by(table.name_id)
            .having(number_of_matching_filters == len(self._filter_status.filters))
        )
        db.execute(
            insert(SessionFilteredNameIds).from_select(
                ['session_id', 'name_id'],
                name_ids_for_all_filters
            )
        )

    def delete_filter(self, entity: str):
        self._clean_up_filter_for_entity(entity)
        del self._filter_status.filters[entity]
        self._record_name_ids_for_all_filters()
        self._session_service.touch()
        self._database_session.commit()

    def apply_filter(self, table, query: Query) -> Query:
        if len(self._filter_status.filters) != 0:
            join_with_filtered_name_ids = join(
                table, SessionFilteredNameIds,
                and_(
                    table.name_id == SessionFilteredNameIds.name_id,
                    SessionFilteredNameIds.session_id == self._session_service.get_id()
                )
            )
            query = query.select_from(join_with_filtered_name_ids)
        return query

    def dict(self):
        return self._filter_status.dict()

    def apply_filter_to_compex_query(self, query: Query) -> Query:
        if len(self._filter_status.filters) != 0:
            cte = query.cte('cte')
            join_with_filtered_name_ids = join(
                cte, SessionFilteredNameIds,
                and_(
                    cte.name_id == SessionFilteredNameIds.name_id,
                    SessionFilteredNameIds.session_id == self._session_service.get_id()
                )
            )
            query = select(cte.c).select_from(join_with_filtered_name_ids)
        return query
