import {http_fetch} from '../utility/http';
import {to_entities, Entity, EntityType, ShowMarker} from "../typia/entity.ts";
import {Cache} from "../utility/cache.ts";

const ALL_ENTITY_TYPES = [
    EntityType.NUMERICAL,
    EntityType.CATEGORICAL,
    EntityType.DATE,
];

class MyCache extends Cache<Entity[]> {
    get_raw_promise() {
        return http_fetch(
            'GET', '/entity/all',
            'loading entity data',
            false,
            false
        );
    }

    decode(raw: unknown) {
        return to_entities(raw)
    }
}

const my_cache = new MyCache();


async function get_entity_list(): Promise<readonly Entity[]> {
    return my_cache.get_data();
}

export {
    get_entity_list,
    type Entity, EntityType, ShowMarker, ALL_ENTITY_TYPES
};
