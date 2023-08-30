from typing import Optional, Union

from sqlalchemy import delete, select, func, literal_column, join, and_
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Query

from medex.dto.filter import FilterStatus, CategoricalFilter, NumericalFilter
from medex.services.session import SessionService
from medex.database_schema import SessionFilteredPatientTable, SessionPatientsMatchingFilterTable,\
    CategoricalValueTable, NumericalValueTable


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
            self._filter_status = FilterStatus(filtered_patient_count=None, filters={})
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
        table = SessionPatientsMatchingFilterTable
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
            data_table = CategoricalValueTable
            entity_condition = [
                data_table.value.in_(new_filter.categories),
            ]
        elif isinstance(new_filter, NumericalFilter):
            data_table = NumericalValueTable
            entity_condition = [
                data_table.value.between(new_filter.from_value, new_filter.to_value),
            ]
        else:
            raise Exception('Unexpected Data Type')
        if new_filter.measurement is not None:
            entity_condition.append(data_table.measurement == new_filter.measurement)
        self._record_name_ids_for_entity(data_table, entity, entity_condition)

    def delete_all_filters(self):
        self._purge_filter_tables_for_session()
        self._filter_status.filters = {}
        self._filter_status.filtered_patient_count = None

    def _purge_filter_tables_for_session(self):
        db = self._database_session
        for table in [SessionFilteredPatientTable, SessionPatientsMatchingFilterTable]:
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
                data_table.patient_id
            ).distinct()
            .where(
                self._get_filter_criteria(data_table, entity, entity_condition)
            )
        )
        self._database_session.execute(
            insert(SessionPatientsMatchingFilterTable).from_select(
                ['session_id', 'filter', 'patient_id'],
                name_ids_for_filter
            )
        )

    @staticmethod
    def _get_filter_criteria(data_table, entity, entity_condition):
        criteria = [
            data_table.key == entity,
            *entity_condition
        ]
        return and_(*criteria)

    def _record_name_ids_for_all_filters(self):
        self._reset_name_ids_for_all_filters()
        self._generate_name_ids_for_all_filters()
        self._update_patient_count()

    def _reset_name_ids_for_all_filters(self):
        self._database_session.execute(
            select(SessionFilteredPatientTable)
            .where(SessionFilteredPatientTable.session_id == self._session_id)
            .with_for_update()
        )
        self._database_session.execute(
            delete(SessionFilteredPatientTable)
            .where(SessionFilteredPatientTable.session_id == self._session_id)
        )

    def _generate_name_ids_for_all_filters(self):
        db = self._database_session
        table = SessionPatientsMatchingFilterTable
        number_of_matching_filters = func.count(table.patient_id).label('number_of_matching_filters')
        name_ids_for_all_filters = (
            select(
                literal_column(f"'{self._session_id}'"), table.patient_id
            )
            .where(table.session_id == self._session_id)
            .group_by(table.patient_id)
            .having(number_of_matching_filters == len(self._filter_status.filters))
        )
        db.execute(
            insert(SessionFilteredPatientTable).from_select(
                ['session_id', 'patient_id'],
                name_ids_for_all_filters
            )
        )

    def _update_patient_count(self):
        if len(self._filter_status.filters) == 0:
            self._filter_status.filtered_patient_count = None
            return
        table = SessionFilteredPatientTable
        result = self._database_session.execute(
            select(func.count(table.patient_id)).where(table.session_id == self._session_id)
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
                table, SessionFilteredPatientTable,
                and_(
                    table.patient_id == SessionFilteredPatientTable.patient_id,
                    SessionFilteredPatientTable.session_id == self._session_id
                )
            )
            query = query.select_from(join_with_filtered_name_ids)
        return query

    def dict(self):
        return self._filter_status.dict()

    def apply_filter_to_complex_query(self, query: Query) -> Query:
        if len(self._filter_status.filters) != 0:
            cte = query.cte()
            join_with_filtered_name_ids = join(
                cte, SessionFilteredPatientTable,
                and_(
                    cte.c.patient_id == SessionFilteredPatientTable.patient_id,
                    SessionFilteredPatientTable.session_id == self._session_id
                )
            )
            query = select(cte.c).select_from(join_with_filtered_name_ids)
        return query

    def get_filtered_patient_count(self):
        return self._filter_status.filtered_patient_count
