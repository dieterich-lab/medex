import {get_selected_items} from "../utility/misc.js";
import {handle_plot} from "../utility/plot.js";
import {configure_entity_selection} from "../utility/entity_selection.js";

function display_results() {
    handle_plot({
        decode_data: decode_data,
        get_query_parameters: get_query_parameters,
        plot_url: '/heatmap/json',
        download_url: '/heatmap/download',
        download_file_name: 'heatmap.svg',
    });
}

function decode_data(data) {
    Plotly.react('heatmap', data, {});
}

function get_query_parameters() {
    const entities = get_selected_items('heatmap_numerical_entities_select')
    validate_entities(entities);
    return new URLSearchParams({
        heatmap_data: JSON.stringify({
            entities: entities,
        })
    });
}

function validate_entities(entities) {
    if (entities.length < 2) {
        return 'Please select two or more numeric entities'
    }
}

async function init() {
    await configure_entity_selection(
        'heatmap_numerical_entities_select', window.selected_numerical_entities,
        true, false
    );
}

document.addEventListener('DOMContentLoaded', init);
window.display_results = display_results;
