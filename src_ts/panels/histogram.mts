import {Plot, Plotly, setup_plot} from "../utility/plot.mjs";
import {get_selected_measurements, get_selected_items} from "../utility/misc.mjs";
import {configure_multiple_measurement_select, get_measurement_display_name} from "../services/measurement.mjs";
import {configure_entity_selection, is_valid_entity} from "../utility/entity_selection.mjs";
import {configure_category_selection} from "../utility/categories_selection.mjs";
import {UserError} from "../utility/error.mjs";
import {switch_nav_item} from "../utility/nav.mjs";
import {get_input_value_by_id} from "../utility/dom.mjs";

class Histogram extends Plot {
    get_name() {
        return 'histogram';
    }

    decode_data(data) {
        Plotly.react('plot_div', data, {});
    }

    get_query_parameters() {
        const measurements = get_selected_measurements();
        const numerical_entity = get_input_value_by_id('histogram_numerical_entities_select');
        const categorical_entity = get_input_value_by_id('histogram_categorical_entities_select');
        const categories = get_selected_items('histogram_subcategory_entities');
        const number_of_bins = get_input_value_by_id('number_of_bins');
        this.validate_parameters(measurements, numerical_entity, categorical_entity, categories);
        return this.get_query_parameter_string(
            measurements, numerical_entity, categorical_entity, categories, number_of_bins
        );
    }

    validate_parameters(measurements, numerical_entity, categorical_entity, categories) {
        if (!measurements.length) {
            const name = get_measurement_display_name(true);
            throw new UserError(`Please select one or more ${name}`);
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

async function init() {
    switch_nav_item('histogram');
    await configure_multiple_measurement_select('measurement', 'measurement_div');
    await configure_entity_selection(
        'histogram_numerical_entities_select', [],
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

setup_plot(new Histogram(), init);
