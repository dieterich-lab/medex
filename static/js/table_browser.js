import {configure_entity_selection} from "./entity_selection.js";
import {configure_multiple_measurement_select} from "./measurement.js";

async function init() {
    await configure_multiple_measurement_select('measurement', 'measurement_div');
    await configure_entity_selection(
        'table_browser_entities_select', window.table_browser_data_selected_entities,
        true, false
    );
}

document.addEventListener("DOMContentLoaded", init);