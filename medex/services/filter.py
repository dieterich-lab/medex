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
        self._session_id = session_service.get_id()

        if filter_status is None:
            self._filter_status = FilterStatus(measurement=None, filtered_patient_count=None, filters={})
        else:
            self._filter_status = filter_status

    def add_filter(self, entity: str, new_filter: Union[CategoricalFilter, NumericalFilter]):
        self._session_service.touch()
        self._clean_up_filter_for_entity(entity)
        self._record_name_ids_for_filter(entity, new_filter)
        self._database_session.commit()
        self._filter_status.filters[entity] = new_filter
        self._record_name_ids_for_all_filters()
        self._database_session.commit()

    def _clean_up_filter_for_entity(self, entity):
        table = SessionNameIdsMatchingFilter
        if len(self._filter_status.filters) == 0:
            self.delete_all_filters()
        else:
            self._database_session.execute(
                delete(table)
                .where(table.session_id == self._session_id)
                .where(table.filter == entity)
            )

    def _record_name_ids_for_filter(self, entity, new_filter):
        if isinstance(new_filter, CategoricalFilter):
            data_table = TableCategorical
            entity_condition = data_table.value.in_(new_filter.categories)
        elif isinstance(new_filter, NumericalFilter):
            data_table = TableNumerical
            entity_condition = data_table.value.between(new_filter.from_value, new_filter.to_value)
        else:
            raise Exception('Unexpected Data Type')
        self._record_name_ids_for_entity(data_table, entity, entity_condition)

    def delete_all_filters(self):
        self._purge_filter_tables_for_session()
        self._filter_status.filters = {}
        self._filter_status.filtered_patient_count = None

    def _purge_filter_tables_for_session(self):
        db = self._database_session
        for table in [SessionFilteredNameIds, SessionNameIdsMatchingFilter]:
            db.execute(
                delete(table)
                .where(table.session_id == self._session_id)
            )
        self._database_session.commit()

    def _record_name_ids_for_entity(self, data_table, entity, entity_condition):
        name_ids_for_filter = (
            select(
                literal_column(f"'{self._session_id}'"),
                literal_column(f"'{entity}'"),
                data_table.name_id
            ).distinct()
            .where(
                self._get_filter_criteria(data_table, entity, entity_condition)
            )
        )
        self._database_session.execute(
            insert(SessionNameIdsMatchingFilter).from_select(
                ['session_id', 'filter', 'name_id'],
                name_ids_for_filter
            )
        )

    def _get_filter_criteria(self, data_table, entity, entity_condition):
        criteria = [
            data_table.key == entity,
            entity_condition,
        ]
        if self._filter_status.measurement is not None:
            criteria.append(data_table.measurement == self._filter_status.measurement)
        return and_(*criteria)

    def _record_name_ids_for_all_filters(self):
        self._reset_name_ids_for_all_filters()
        self._generate_name_ids_for_all_filters()
        self._update_patient_count()

    def _reset_name_ids_for_all_filters(self):
        self._database_session.execute(
            select(SessionFilteredNameIds)
            .where(SessionFilteredNameIds.session_id == self._session_id)
            .with_for_update()
        )
        self._database_session.execute(
            select(SessionFilteredNameIds)
            .where(SessionFilteredNameIds.session_id == self._session_id)
            .with_for_update()
        )
        self._database_session.execute(
            delete(SessionFilteredNameIds)
            .where(SessionFilteredNameIds.session_id == self._session_id)
        )

    def _generate_name_ids_for_all_filters(self):
        db = self._database_session
        table = SessionNameIdsMatchingFilter
        number_of_matching_filters = func.count(table.name_id).label('number_of_matching_filters')
        name_ids_for_all_filters = (
            select(
                literal_column(f"'{self._session_id}'"), table.name_id
            )
            .where(table.session_id == self._session_id)
            .group_by(table.name_id)
            .having(number_of_matching_filters == len(self._filter_status.filters))
        )
        db.execute(
            insert(SessionFilteredNameIds).from_select(
                ['session_id', 'name_id'],
                name_ids_for_all_filters
            )
        )

    def _update_patient_count(self):
        if len(self._filter_status.filters) == 0:
            self._filter_status.filtered_patient_count = None
            return
        table = SessionFilteredNameIds
        result = self._database_session.execute(
            select(func.count(table.name_id)).where(table.session_id == self._session_id)
        ).first()
        self._filter_status.filtered_patient_count = result[0]

    def delete_filter(self, entity: str):
        self._session_service.touch()
        self._clean_up_filter_for_entity(entity)
        del self._filter_status.filters[entity]
        self._record_name_ids_for_all_filters()
        self._database_session.commit()

    def apply_filter(self, table, query: Query) -> Query:
        if len(self._filter_status.filters) != 0:
            join_with_filtered_name_ids = join(
                table, SessionFilteredNameIds,
                and_(
                    table.name_id == SessionFilteredNameIds.name_id,
                    SessionFilteredNameIds.session_id == self._session_id
                )
            )
            query = query.select_from(join_with_filtered_name_ids)
        return query

    def dict(self):
        return self._filter_status.dict()

    def apply_filter_to_complex_query(self, query: Query) -> Query:
        if len(self._filter_status.filters) != 0:
            cte = query.cte('cte')
            join_with_filtered_name_ids = join(
                cte, SessionFilteredNameIds,
                and_(
                    cte.c.name_id == SessionFilteredNameIds.name_id,
                    SessionFilteredNameIds.session_id == self._session_id
                )
            )
            query = select(cte.c).select_from(join_with_filtered_name_ids)
        return query

    def set_measurement(self, new_measurement: Optional[str]):
        self._filter_status.measurement = new_measurement
        self._session_service.touch()
        self._purge_filter_tables_for_session()
        for entity, existing_filter in self._filter_status.filters.items():
            self._record_name_ids_for_filter(entity, existing_filter)
        self._record_name_ids_for_all_filters()
        self._database_session.commit()

    def get_measurement(self) -> Optional[str]:
        return self._filter_status.measurement
