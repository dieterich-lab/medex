from flask_sqlalchemy.session import Session

from medex.database_schema import PatientTable, NumericalValueTable, CategoricalValueTable, DateValueTable, EntityTable
from medex.dto.database_info import DatabaseInfo
from medex.dto.entity import EntityType


class DatabaseInfoService:
    def __init__(self, database_session: Session):
        self._database_session = database_session
        self._cache = None

    def get(self) -> DatabaseInfo:
        if self._cache is None:
            self._cache = DatabaseInfo(
                number_of_patients=self._get_count(PatientTable.patient_id),
                number_of_numerical_entities=self._get_entity_count_by_type(EntityType.NUMERICAL),
                number_of_categorical_entities=self._get_entity_count_by_type(EntityType.CATEGORICAL),
                number_of_date_entities=self._get_entity_count_by_type(EntityType.DATE),
                number_of_numerical_data_items=self._get_count(NumericalValueTable.patient_id),
                number_of_categorical_data_items=self._get_count(CategoricalValueTable.patient_id),
                number_of_date_data_items=self._get_count(DateValueTable.patient_id),
            )
        return self._cache.copy(deep=True)

    def _get_count(self, column):
        return self._database_session.query(column).count()

    def _get_entity_count_by_type(self, entity_type):
        return self._database_session.query(EntityTable.key).where(EntityTable.type == entity_type.value).count()
