import {configure_entity_selection} from "./entity_selection.js";
import {configure_multiple_measurement_select} from "./measurement.js";

async function init() {
    await configure_multiple_measurement_select('measurement_numeric', 'measurement_numeric_div');
    await configure_entity_selection(
        'basic_stats_numerical_entities_select', window.selected_numerical_entities,
        true, false
    );
}

document.addEventListener('DOMContentLoaded', init);
