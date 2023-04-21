import {Plot, Plotly, setup_plot} from "../utility/plot.mjs";
import {get_selected_categories, get_selected_measurements} from "../utility/misc.mjs";
import {UserError} from "../utility/error.mjs";
import {configure_multiple_measurement_select, get_measurement_display_name} from "../services/measurement.mjs";
import {configure_entity_selection, is_valid_entity} from "../utility/entity_selection.mjs";
import {configure_category_selection} from "../utility/categories_selection.mjs";
import {switch_nav_item} from "../utility/nav.mjs";
import {get_input_value_by_id, get_radio_input_by_name} from "../utility/dom.mjs";

interface BoxplotData {
    table_json: Object[]
    image_json: Object[]
}


class Boxplot extends Plot<BoxplotData> {
    get_name() {
        return 'boxplot';
    }

    decode_data(data) {
        Plotly.react('boxplot_table', data.table_json, {});
        Plotly.react('boxplot', data.image_json, {});
    }

    get_plot_divs() {
        return ['boxplot_table', 'boxplot'];
    }

    get_query_parameters() {
        const measurements = get_selected_measurements();
        const numerical_entity = get_input_value_by_id('boxplot_numerical_entities_select');
        const categorical_entity = get_input_value_by_id('boxplot_categorical_entities_select');
        const categories = get_selected_categories();
        const plot_type = get_radio_input_by_name('plot_type_boxplot');
        this.validate_parameters(measurements, numerical_entity, categorical_entity, categories);
        return this.get_parameter_string(measurements, numerical_entity, categorical_entity, categories, plot_type);
    }

    get_parameter_string(measurements, numerical_entity, categorical_entity, categories, plot_type) {
        return new URLSearchParams({
            boxplot_data: JSON.stringify({
                measurements: measurements,
                numerical_entity: numerical_entity,
                categorical_entity: categorical_entity,
                categories: categories,
                plot_type: plot_type,
            })
        });
    }

    validate_parameters(measurements, numerical_entity, categorical_entity, categories) {
        if ( !measurements.length ) {
            const name = get_measurement_display_name(true);
            throw new UserError(`Please select one or more ${name}`);
        }
        if ( !is_valid_entity(numerical_entity) ) {
            throw new UserError("Please select the numerical entity");
        }
        if ( !is_valid_entity(categorical_entity) ) {
            throw new UserError("Please select the group_by entity");
        }
        if ( !categories.length ) {
            throw new UserError("Please select one or more subcategories");
        }
    }

    is_empty(data) {
        return data.image_json.data.length === 0;
    }
}

async function init() {
    switch_nav_item('boxplot');
    await configure_multiple_measurement_select('measurement', 'measurement_div');
    await configure_entity_selection(
        'boxplot_numerical_entities_select', [],
        false, false
    );
    await configure_entity_selection(
        'boxplot_categorical_entities_select', [],
        false, false
    );
    configure_category_selection(
        'subcategory_entities',
        null,
        'boxplot_categorical_entities_select'
    );
}

setup_plot(new Boxplot(), init);
