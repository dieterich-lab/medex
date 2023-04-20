import {Plot, Plotly, setup_plot} from "../utility/plot.mjs";
import {get_selected_items} from "../utility/misc.mjs";
import {configure_entity_selection} from "../utility/entity_selection.mjs";
import {UserError} from "../utility/error.mjs";
import {switch_nav_item} from "../utility/nav.mjs";

interface HeatmapData {
    data: Object[]
}

class Heatmap extends Plot<HeatmapData> {
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

    is_empty(data) {
        return data.data.length === 0;
    }
}

async function init() {
    switch_nav_item('heatmap');
    await configure_entity_selection(
        'heatmap_numerical_entities_select', [],
        true, false
    );
}

setup_plot(new Heatmap(), init);
