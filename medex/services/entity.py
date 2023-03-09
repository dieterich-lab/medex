from typing import List, Dict

from sqlalchemy import select, inspect, func
from sqlalchemy.orm import Session

from medex.database_schema import NameType, TableCategorical, TableNumerical
from medex.dto.entity import Entity, EntityType


class EntityService:
    ENTITY_COLUMNS = inspect(NameType).mapper.column_attrs

    def __init__(self, database_session: Session):
        self._db = database_session
        self._cache = None

    def get_all(self) -> List[Entity]:
        if self._cache is None:
            categories_by_entity = self._get_categories_by_entity()
            min_max_by_entity = self._get_min_max_by_entity()
            rv = self._db.execute(
                select(*self.ENTITY_COLUMNS)
            )
            raw_result = [
                self._get_entity_from_row(x, categories_by_entity, min_max_by_entity)
                for x in rv.all()
            ]
            self._cache = sorted(raw_result, key=lambda x: x.key)
        return self._cache

    def get_all_as_dict(self) -> List[Dict[str, any]]:
        result = [
            x.dict()
            for x in self.get_all()
        ]
        for entity in result:
            entity['type'] = entity['type'].value
        return result

    def _get_categories_by_entity(self):
        rv = self._db.execute(
            select(TableCategorical.key, TableCategorical.value).distinct()
        )
        result = {}
        for row in rv.all():
            entity_key = row.key
            entity_value = row.value
            if entity_key in result:
                result[entity_key].append(entity_value)
            else:
                result[entity_key] = [entity_value]
        for entity_key in result:
            result[entity_key] = sorted(result[entity_key])
        return result

    def _get_min_max_by_entity(self):
        rv = self._db.execute(
            select(
                TableNumerical.key,
                func.min(TableNumerical.value).label('min_value'),
                func.max(TableNumerical.value).label('max_value'),
            )
            .group_by(TableNumerical.key)
        )
        return {
            x.key: (x.min_value, x.max_value)
            for x in rv.all()
        }

    def _get_entity_from_row(self, row, categories_by_entity, min_max_by_entity):
        raw_entity = {
            col.key: getattr(row, col.key)
            for col in self.ENTITY_COLUMNS
        }

        entity_key = raw_entity['key']
        if raw_entity['type'] == EntityType.CATEGORICAL.value:
            if entity_key in categories_by_entity:
                raw_entity['categories'] = categories_by_entity[entity_key]
            else:
                raw_entity['categories'] = []
        elif raw_entity['type'] == EntityType.NUMERICAL.value:
            if entity_key in min_max_by_entity:
                raw_entity['min'], raw_entity['max'] = min_max_by_entity[entity_key]
            else:
                raw_entity['min'], raw_entity['max'] = 0.0, 1.0

        return Entity.parse_obj(raw_entity)

    def refresh(self):
        self._cache = None
