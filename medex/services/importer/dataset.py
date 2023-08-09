from datetime import datetime
from typing import TextIO, Dict

from sqlalchemy import inspect, union, select, insert, text
from sqlalchemy.orm import Session

from medex.dto.entity import EntityType
from medex.services.entity import EntityService
from medex.services.importer.generic_importer import GenericImporter
from medex.database_schema import Base, NumericalValueTable, CategoricalValueTable, DateValueTable, PatientTable


class DatasetImporter(GenericImporter):
    def __init__(
            self,
            file_handle: TextIO,
            source_name: str,
            db_session: Session,
            entity_service: EntityService
    ):
        table_meta = inspect(NumericalValueTable)
        super().__init__(
            file_handle=file_handle,
            source_name=source_name,
            known_columns=[
                'patient_id', 'case_id', 'measurement', 'date', 'time',
                'key', 'value'
            ],
            required_columns=['patient_id', 'key', 'value'],
            db_session=db_session
        )
        self._entities_by_key = None
        self._entity_service = entity_service

    def parse_row(self, values: Dict[str, str]) -> (Dict[str, any], Base):
        cooked_values: Dict[str, any] = {**values}
        self._check_isolated_values(values)
        self._add_defaults(cooked_values)
        self._convert_date_time(cooked_values)
        entity_type = self._get_validated_entity_type(values)

        if entity_type == EntityType.NUMERICAL:
            return self._parse_numerical_row(cooked_values)
        elif entity_type == EntityType.CATEGORICAL:
            return cooked_values, CategoricalValueTable
        elif entity_type == EntityType.DATE:
            return self._parse_date_row(cooked_values)
        else:
            raise NotImplementedError(f"Not implemented: {entity_type.value}")

    def _check_isolated_values(self, values):
        if len(values['patient_id']) < 1:
            raise ValueError('Gote empty patient_id')
        if 'date' in values and not self._date_is_ok(values['date']):
            raise ValueError('Date column not in format YYYY-MM-DD')

    @staticmethod
    def _add_defaults(cooked_values):
        if 'measurement' not in cooked_values:
            cooked_values['measurement'] = '1'

    def _convert_date_time(self, cooked_values):
        if not self._is_valid(cooked_values, 'date'):
            final_date = None
        elif not self._is_valid(cooked_values, 'time'):
            final_date = datetime.strptime(cooked_values['date'], '%Y-%m-%d')
        else:
            combined = cooked_values['date'] + ' ' + cooked_values['time']
            final_date = datetime.strptime(combined, '%Y-%m-%d %H:%M:%S')
        if final_date is not None:
            cooked_values['date_time'] = final_date

        for key in ['date', 'time']:
            if key in cooked_values:
                del cooked_values[key]

    @staticmethod
    def _is_valid(data, key):
        return key in data and data[key] is not None and data[key] != ''

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
            key = cooked_values['key']
            raise ValueError(f"The 'value' column must be numeric for key '{key}'")
        return cooked_values, NumericalValueTable

    @staticmethod
    def _parse_date_row(cooked_values):
        try:
            cooked_values['value'] = datetime.strptime(cooked_values['value'], '%Y-%m-%d')
        except ValueError:
            raise ValueError("The 'value' column must be in the format YYYY-MM-DD for this key'")
        return cooked_values, DateValueTable

    @staticmethod
    def _date_is_ok(value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def populate_patient_table(self):
        all_patient_references = union(
            select(CategoricalValueTable.patient_id, CategoricalValueTable.case_id),
            select(NumericalValueTable.patient_id, NumericalValueTable.case_id),
            select(DateValueTable.patient_id, DateValueTable.case_id)
        ).subquery()

        all_patients = select(
            all_patient_references.c.patient_id, all_patient_references.c.case_id
        ).distinct()

        bug_insert = insert(PatientTable).from_select(['patient_id', 'case_id'], all_patients)
        self._db_session.execute(bug_insert)
        self._db_session.commit()

    def optimize_tables(self):
        for line in [
            'CLUSTER numerical_value USING idx_key_num',
            'CLUSTER categorical_value USING idx_key_cat',
            'CLUSTER date_value USING idx_key_date',
            'ANALYZE numerical_value',
            'ANALYZE categorical_value',
            'ANALYZE date_value',
        ]:
            self._db_session.execute(text(line))
            self._db_session.commit()
