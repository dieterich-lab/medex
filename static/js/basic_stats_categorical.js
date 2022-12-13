import {configure_entity_selection} from "./entity_selection.js";

async function init() {
    await configure_entity_selection(
        'basic_stats_categorical_entities_select', [],
        true, false
    );
}

$('a[data-toggle="tab"]').on('shown.bs.tab', async (e) => {
    if ( e.target.hash === '#categorical_tab' ) {
        await init();
    }
});

export {init};