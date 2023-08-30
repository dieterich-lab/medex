from typing import TextIO, Dict, Set

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from medex.dto.entity import EntityType
from medex.services.importer.generic_importer import GenericImporter
from medex.database_schema import Base, EntityTable


class EntityImporter(GenericImporter):
    ALLOWED_TYPES: Set[str] = set([x.value for x in EntityType])

    def __init__(self, file_handle: TextIO, source_name: str, db_session: Session):
        table_meta = inspect(EntityTable)
        known_columns = [x.key for x in table_meta.mapper.column_attrs]

        super().__init__(
            file_handle=file_handle,
            source_name=source_name,
            known_columns=known_columns,
            required_columns=['key', 'type'],
            db_session=db_session
        )

        self._column_list = None
        self._seen_keys = set()

    def parse_row(self, values: Dict[str, str]) -> (Dict[str, any], Base):
        key_value = values['key']
        if len(key_value) < 1:
            raise ValueError('Got empty string as key')
        if key_value in self._seen_keys:
            raise ValueError("Got duplicated key '{key_value}'")

        type_value = values['type']
        if type_value not in self.ALLOWED_TYPES:
            allowed = ', '.join(self.ALLOWED_TYPES)
            raise ValueError(f"Type column ({type_value}) is not in ({allowed})")

        self._seen_keys.add(key_value)
        return values, EntityTable
