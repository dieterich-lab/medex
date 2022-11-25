let entity_list = null;
let entities_by_key = null;

async function init() {
    await fetch('/entity/all', {method: 'GET'})
    .then(response => response.json())
    .then(new_entity_list => {
        entity_list = new_entity_list;
        entities_by_key = {};
        for (const entity of entity_list) {
            entities_by_key[entity[['key']]] = entity;
        }
    })
    .catch(error => {
        console.log(error)
    })
}

async function get_entity_list() {
    if ( entity_list === null ) {
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

export {get_entity_list, get_entity_by_key};
