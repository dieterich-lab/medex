import {get_selected_measurements, get_selected_items} from "../utility/misc.js";
import {Plot} from "../utility/plot.js";
import {configure_multiple_measurement_select} from "../services/measurement.js";
import {configure_entity_selection, is_valid_entity} from "../utility/entity_selection.js";
import {configure_category_selection} from "../utility/categories_selection.js";
import {UserError} from "../utility/error.js";

class Histogram extends Plot {
    get_name() {
        return 'histogram';
    }

    decode_data(data) {
        Plotly.react('plot_div', data, {});
    }

    get_query_parameters() {
        const measurements = get_selected_measurements();
        const numerical_entity = document.getElementById('histogram_numerical_entities_select').value;
        const categorical_entity = document.getElementById('histogram_categorical_entities_select').value;
        const categories = get_selected_items('histogram_subcategory_entities');
        const number_of_bins = document.getElementById('number_of_bins').value;
        this.validate_parameters(measurements, numerical_entity, categorical_entity, categories);
        return this.get_query_parameter_string(
            measurements, numerical_entity, categorical_entity, categories, number_of_bins
        );
    }

    validate_parameters(measurements, numerical_entity, categorical_entity, categories) {
        if (!measurements.length) {
            throw new UserError("Please select one or more visits");
        }
        if (!is_valid_entity(numerical_entity)) {
            throw new UserError("Please select the numerical entity");
        }
        if (!is_valid_entity(categorical_entity)) {
            throw new UserError("Please select the group_by entity");
        }
        if (!categories.length) {
            throw new UserError("Please select one or more subcategories");
        }
    }

    get_query_parameter_string(measurements, numerical_entity, categorical_entity, categories, number_of_bins) {
        return new URLSearchParams({
            histogram_data: JSON.stringify({
                measurements: measurements,
                numerical_entity: numerical_entity,
                categorical_entity: categorical_entity,
                categories: categories,
                bins: number_of_bins,
            })
        });
    }
}

function display_results() {
    let plot = new Histogram();
    plot.handle_plot();
}

async function init() {
    await configure_multiple_measurement_select('measurement', 'measurement_div');
    await configure_entity_selection(
        'histogram_numerical_entities_select', window.selected_numerical_entities,
        false, false
    );
    await configure_entity_selection(
        'histogram_categorical_entities_select', [],
        false, false
    );
    configure_category_selection(
        'histogram_subcategory_entities',
        null,
        'histogram_categorical_entities_select'
    );
}

document.addEventListener("DOMContentLoaded", init);
window.display_results = display_results;
