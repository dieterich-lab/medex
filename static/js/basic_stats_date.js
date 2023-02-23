import {configure_entity_selection} from "./entity_selection.js";
import {configure_multiple_measurement_select} from "./measurement.js";

async function init() {
    await configure_multiple_measurement_select('measurement_date', 'measurement_date_div');
    await configure_entity_selection(
        'basic_stats_date_entities_select', window.basic_stats_selected_date_entities,
        true, false
    );
}

$('a[data-toggle="tab"]').on('shown.bs.tab', async (e) => {
    if ( e.target.hash === '#date_tab' ) {
        await init();
    }
});

document.addEventListener('DOMContentLoaded', init);