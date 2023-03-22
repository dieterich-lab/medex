import {get_selected_categories, get_selected_measurements} from "../utility/misc.js";
import {UserError} from "../utility/error.js";
import {Plot} from "../utility/plot.js";
import {configure_multiple_measurement_select, get_measurement_display_name} from "../services/measurement.js";
import {configure_entity_selection, is_valid_entity} from "../utility/entity_selection.js";
import {configure_category_selection} from "../utility/categories_selection.js";
import {switch_nav_item} from "../utility/nav.js";


class BarChart extends Plot {
    get_name() {
        return 'barchart';
    }

    decode_data(data) {
        Plotly.react('plot_div', data, {});
    }

    get_query_parameters() {
        const measurements = get_selected_measurements();
        const entity = document.getElementById('barchart_categorical_entities_select').value;
        const categories = get_selected_categories();
        this.validate_parameters(measurements, entity, categories);
        const plot_type = this.get_plot_type();
        return this.get_search_parameter_string(measurements, entity, categories, plot_type);
    }

    get_plot_type() {
        const all_plot_types = document.querySelectorAll('input[name="plot_type"]');
        let plot_type;
        for (const selected_type of all_plot_types) {
            if (selected_type.checked) {
                plot_type = selected_type.value;
            }
        }
        return plot_type
    }

    validate_parameters(measurements, entity, categories) {
        if ( !measurements.length ) {
            const name = get_measurement_display_name(true);
            throw new UserError(`Please select one or more ${name}.`);
        }
        if ( !is_valid_entity(entity) ) {
            throw new UserError("Please select the entity to group by.");
        }
        if ( !categories.length ) {
            throw new UserError("Please select one or more subcategories.");
        }
    }

    get_search_parameter_string(measurements, entity, categories, plot_type) {
        return new URLSearchParams({
            barchart_data: JSON.stringify({
                measurements: measurements,
                key: entity,
                categories: categories,
                plot_type: plot_type,
            })
        });
    }
}

function display_results() {
    let plot = new BarChart();
    plot.handle_plot();
}

async function init() {
    switch_nav_item('barchart');
    await configure_multiple_measurement_select('measurement', 'measurement_div');
    await configure_entity_selection(
        'barchart_categorical_entities_select', [],
        false, false
    );
    configure_category_selection(
        'subcategory_entities',
        null,
        'barchart_categorical_entities_select'
    );
}

document.addEventListener("DOMContentLoaded", init);
window.display_results = display_results;
