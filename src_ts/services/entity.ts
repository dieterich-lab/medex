import {http_fetch} from '../utility/http';
import {assertEquals} from 'typia';

enum EntityType {
    NUMERICAL = 'Double',
    CATEGORICAL = 'String',
    DATE = 'Date',
}

const ALL_ENTITY_TYPES = [
    EntityType.NUMERICAL,
    EntityType.CATEGORICAL,
    EntityType.DATE,
];

enum ShowMarker {
    SHOW = '+',
    DONT_SHOW = '',
}

class NoSuchEntity extends Error {}

interface Entity {
    key: string,
    type: EntityType,
    synonym: string | null,
    description: string | null,
    unit: string | null,
    show: ShowMarker | null,
    categories: string[] | null,
    min: number | null,
    max: number | null,
}

let untyped_entity_list_promise = http_fetch(
    'GET', '/entity/all',
    'loading entity data',
    false,
    false
);
let entity_list_promise = async_assert_equals(untyped_entity_list_promise);
let entities_by_key_promise = get_entities_by_key_promise();


async function async_assert_equals(raw: Promise<any>): Promise<Entity[]> {
    return assertEquals<Entity[]>(await raw);
}

async function get_entity_list(): Promise<Entity[]> {
    const entity_list = await entity_list_promise;
    if ( ! entity_list ) {
        throw new Error('Failed to load entity list!');
    }
    return entity_list;
}

function get_entities_by_key_promise(): Promise<Map<string, Entity>> {
    return new Promise(async (resolve) => {
        const entity_list = await get_entity_list();
        let entities_by_key = new Map<string, Entity>();
        for (const entity of entity_list) {
            entities_by_key.set(entity.key, entity);
        }
        resolve(entities_by_key);
    });
}

async function get_entity_by_key(entity_key: string): Promise<Entity> {
    const entities_by_key = await entities_by_key_promise;
    const result = entities_by_key.get(entity_key);
    if ( result ) {
        return result;
    } else {
        throw new NoSuchEntity(`No entity with key '{entity_key}'`);
    }
}

export {
    get_entity_list, get_entity_by_key,
    Entity, EntityType, ALL_ENTITY_TYPES, ShowMarker
};
