from flask_sqlalchemy.session import Session

from medex.database_schema import Patient, TableNumerical, TableCategorical, TableDate, NameType
from medex.dto.database_info import DatabaseInfo
from medex.dto.entity import EntityType


class DatabaseInfoService:
    def __init__(self, database_session: Session):
        self._database_session = database_session
        self._cache = None

    def get(self) -> DatabaseInfo:
        if self._cache is None:
            self._cache = DatabaseInfo(
                number_of_patients=self._get_count(Patient.name_id),
                number_of_numerical_entities=self._get_entity_count_by_type(EntityType.NUMERICAL),
                number_of_categorical_entities=self._get_entity_count_by_type(EntityType.CATEGORICAL),
                number_of_date_entities=self._get_entity_count_by_type(EntityType.DATE),
                number_of_numerical_data_items=self._get_count(TableNumerical.name_id),
                number_of_categorical_data_items=self._get_count(TableCategorical.name_id),
                number_of_date_data_items=self._get_count(TableDate.name_id),
            )
        return self._cache.copy(deep=True)

    def _get_count(self, column):
        return self._database_session.query(column).count()

    def _get_entity_count_by_type(self, entity_type):
        return self._database_session.query(NameType.key).where(NameType.type == entity_type.value).count()
