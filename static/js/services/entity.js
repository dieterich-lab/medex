import {http_fetch} from "../utility/http.js";

let entity_list_promise = null;
let entity_list = null;
let entities_by_key = null;

async function init() {
    if ( ! entity_list_promise ) {
        entity_list_promise = http_fetch(
            'GET', '/entity/all',
            load_data, null, false
        );
    }
    await entity_list_promise;
}

async function load_data(new_entity_list) {
    entity_list = await new_entity_list;
    entities_by_key = {};
    for (const entity of entity_list) {
        entities_by_key[entity[['key']]] = entity;
    }
}

async function get_entity_list() {
    if ( entity_list == null ) {
        await init();
    }
    return entity_list;
}

async function get_entity_by_key(entity_key) {
    if ( entities_by_key == null ) {
        await init();
    }
    return entities_by_key[entity_key];
}

// The try_* functions work around limitations of the old bootstrap 4.X code,
// which can't handle async function/promises. It should be removed once we
// move to HTML5 and/or a bootstrap version based on it.

function try_get_entity_list() {
    if ( entity_list == null ) {
        return null;
    }
    return entity_list;
}


function try_get_entity_by_key(entity_key) {
    if ( entities_by_key == null ) {
        return null;
    }
    return entities_by_key[entity_key];
}


export {get_entity_list, get_entity_by_key, try_get_entity_list, try_get_entity_by_key};
