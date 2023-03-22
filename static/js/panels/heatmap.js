import {get_selected_items} from "../utility/misc.js";
import {Plot} from "../utility/plot.js";
import {configure_entity_selection} from "../utility/entity_selection.js";
import {UserError} from "../utility/error.js";
import {switch_nav_item} from "../utility/nav.js";

class HeatMap extends Plot {
    get_name() {
        return 'heatmap';
    }

    decode_data(data) {
        Plotly.react('plot_div', data, {});
    }

    get_query_parameters() {
        const entities = get_selected_items('heatmap_numerical_entities_select')
        this.validate_entities(entities);
        return new URLSearchParams({
            heatmap_data: JSON.stringify({
                entities: entities,
            })
        });
    }

    validate_entities(entities) {
        if (entities.length < 2) {
            throw new UserError('Please select two or more numeric entities');
        }
    }
}

function display_results() {
    let plot = new HeatMap();
    plot.handle_plot();
}

async function init() {
    switch_nav_item('heatmap');
    await configure_entity_selection(
        'heatmap_numerical_entities_select', window.selected_numerical_entities,
        true, false
    );
}

document.addEventListener('DOMContentLoaded', init);
window.display_results = display_results;
