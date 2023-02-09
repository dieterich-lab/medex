from datetime import datetime
from typing import TextIO, Dict, List

from sqlalchemy import inspect, union, select, insert, text
from sqlalchemy.orm import Session

from medex.dto.entity import Entity, EntityType
from medex.services.entity import EntityService
from medex.services.importer.generic_importer import GenericImporter
from modules.models import Base, TableNumerical, TableCategorical, TableDate, Patient


class DatasetImporter(GenericImporter):
    def __init__(
            self,
            file_handle: TextIO,
            source_name: str,
            db_session: Session,
            entity_service: EntityService
    ):
        table_meta = inspect(TableNumerical)
        known_columns = [x.key for x in table_meta.mapper.column_attrs]
        super().__init__(
            file_handle=file_handle,
            source_name=source_name,
            known_columns=known_columns,
            required_columns=['name_id', 'key', 'value'],
            db_session=db_session
        )
        self._entities_by_key = None
        self._entity_service = entity_service

    def parse_row(self, values: Dict[str, str]) -> (Dict[str, any], Base):
        cooked_values: Dict[str, any] = {**values}
        self._check_isolated_values(values)
        entity_type = self._get_validated_entity_type(values)

        if entity_type == EntityType.NUMERICAL:
            return self._parse_numerical_row(cooked_values)
        elif entity_type == EntityType.CATEGORICAL:
            return cooked_values, TableCategorical
        elif entity_type == EntityType.DATE:
            return self._parse_date_row(cooked_values)
        else:
            raise NotImplemented(f"Not implemented: {entity_type.value}")

    def _check_isolated_values(self, values):
        if len(values['name_id']) < 1:
            raise ValueError('Gote empty name_id')
        if 'date' in values and not self._date_is_ok(values['date']):
            raise ValueError(f"Date column not in format YYYY-MM-DD")

    def _get_validated_entity_type(self, values):
        entity_key = values['key']
        if entity_key not in self._get_entities_by_key():
            raise ValueError(f"Unknown key '{entity_key}'")
        return self._entities_by_key[values['key']].type

    def _get_entities_by_key(self):
        if self._entities_by_key is None:
            self._entity_service.refresh()
            entities = self._entity_service.get_all()
            self._entities_by_key = {
                x.key: x
                for x in entities
            }
        return self._entities_by_key

    @staticmethod
    def _parse_numerical_row(cooked_values):
        try:
            cooked_values['value'] = float(cooked_values['value'])
        except ValueError:
            raise ValueError(f"The 'value' column must be numeric for this key'")
        return cooked_values, TableNumerical

    @staticmethod
    def _parse_date_row(cooked_values):
        try:
            cooked_values['value'] = datetime.strptime(cooked_values['value'], '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"The 'value' column must be in the format YYYY-MM-DD for this key'")
        return cooked_values, TableDate

    @staticmethod
    def _date_is_ok(value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def populate_patient_table(self):
        all_patient_references = union(
            select(TableCategorical.name_id, TableCategorical.case_id),
            select(TableNumerical.name_id, TableNumerical.case_id),
            select(TableDate.name_id, TableDate.case_id)
        ).subquery()

        all_patients = select(
            all_patient_references.c.name_id, all_patient_references.c.case_id
        ).distinct()

        bug_insert = insert(Patient).from_select(['name_id', 'case_id'], all_patients)
        self._db_session.execute(bug_insert)
        self._db_session.commit()

    def optimize_tables(self):
        for line in [
            'CLUSTER examination_date USING idx_key_date',
            'CLUSTER examination_numerical USING idx_key_num',
            'CLUSTER examination_categorical USING idx_key_cat',
            'ANALYZE examination_numerical',
            'ANALYZE examination_categorical',
            'ANALYZE examination_date',
        ]:
            self._db_session.execute(text(line))
            self._db_session.commit()
