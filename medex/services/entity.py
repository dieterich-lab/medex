from typing import List, Dict, Optional

from sqlalchemy import select, inspect, func
from sqlalchemy.orm import Session

from medex.database_schema import EntityTable, CategoricalValueTable, NumericalValueTable, DateValueTable
from medex.dto.entity import Entity, EntityType


class EntityService:
    ENTITY_COLUMNS = inspect(EntityTable).mapper.column_attrs

    def __init__(self, database_session: Session):
        self._db = database_session
        self._dict_cache: Optional[Dict[str, Entity]] = None
        self._list_cache = None

    def _fill_cache(self):
        if self._dict_cache is None:
            print('Setting up entities cache ...')
            categories_by_entity = self._get_categories_by_entity()
            min_max_by_entity = self._get_min_max_by_entity()
            rv = self._db.execute(
                select(*self.ENTITY_COLUMNS)
            )
            raw_result = [
                self._get_entity_from_row(x, categories_by_entity, min_max_by_entity)
                for x in rv.all()
            ]
            sorted_list = sorted(raw_result, key=lambda x: x.key)
            self._dict_cache = {v.key: v for v in sorted_list}
            self._list_cache = list(self._dict_cache.values())
            print('Done setting up entities cache.')

    def get_all(self) -> List[Entity]:
        self._fill_cache()
        return self._list_cache

    def get_all_as_dict(self) -> List[Dict[str, any]]:
        self._fill_cache()
        result = [
            x.dict()
            for x in self.get_all()
        ]
        for entity in result:
            entity['type'] = entity['type'].value
        return result

    def _get_categories_by_entity(self):
        rv = self._db.execute(
            select(CategoricalValueTable.key, CategoricalValueTable.value).distinct()
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
                NumericalValueTable.key,
                func.min(NumericalValueTable.value).label('min_value'),
                func.max(NumericalValueTable.value).label('max_value'),
            )
            .group_by(NumericalValueTable.key)
        )
        return {
            x.key: (x.min_value, x.max_value)
            for x in rv.all()
        }

    def _get_entity_from_row(self, row, categories_by_entity, min_max_by_entity) -> Entity:
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
        self._dict_cache = None

    def get_entity_by_key(self, entity_key: str) -> Entity:
        self._fill_cache()
        return self._dict_cache[entity_key]

    @staticmethod
    def get_database_table_for_entity(entity: Entity):
        if entity.type == EntityType.NUMERICAL:
            return NumericalValueTable
        elif entity.type == EntityType.CATEGORICAL:
            return CategoricalValueTable
        else:
            return DateValueTable
