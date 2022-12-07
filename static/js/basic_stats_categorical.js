import {configure_entity_selection} from "./entity_selection.js";

async function init() {
    await configure_entity_selection(
        'basic_stats_categorical_entities_select', window.basic_stats_selected_categorical_entities,
        true, false
    );
}

document.addEventListener('DOMContentLoaded', init);