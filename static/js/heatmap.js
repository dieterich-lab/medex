import {configure_entity_selection} from "./entity_selection.js";

async function init() {
    await configure_entity_selection(
        'heatmap_numerical_entities_select', window.selected_numerical_entities,
        true, false
    );
}

document.addEventListener('DOMContentLoaded', init);