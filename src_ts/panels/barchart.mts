import {Plot, Plotly, setup_plot} from "../utility/plot.mjs";
import {get_selected_categories, get_selected_measurements} from "../utility/misc.mjs";
import {UserError} from "../utility/error.mjs";
import {get_input_value_by_id, get_radio_input_by_name} from "../utility/dom.mjs";
import {configure_multiple_measurement_select, get_measurement_display_name} from "../services/measurement.mjs";
import {configure_entity_selection, is_valid_entity} from "../utility/entity_selection.mjs";
import {configure_category_selection} from "../utility/categories_selection.mjs";
import {switch_nav_item} from "../utility/nav.mjs";
import {EntityType} from "../services/entity.mjs";

interface BarchartData {
    data: Object[]
}

class Barchart extends Plot<BarchartData> {
    get_name() {
        return 'barchart';
    }

    decode_data(data) {
        return Plotly.react('plot_div', data, {});
    }

    get_query_parameters() {
        const measurements = get_selected_measurements();
        const entity = get_input_value_by_id('barchart_categorical_entities_select')
        const categories = get_selected_categories();
        this.validate_parameters(measurements, entity, categories);
        const plot_type = get_radio_input_by_name('plot_type');
        return this.get_search_parameter_string(measurements, entity, categories, plot_type);
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

    is_empty(data) {
            return data.data.length === 0;
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

async function init() {
    switch_nav_item('barchart');
    await configure_multiple_measurement_select('measurement', 'measurement_div');
    await configure_entity_selection(
        'barchart_categorical_entities_select', [],
        false, false, [EntityType.CATEGORICAL]
    );
    configure_category_selection(
        'subcategory_entities',
        null,
        'barchart_categorical_entities_select'
    );
}

setup_plot(new Barchart(), init);
