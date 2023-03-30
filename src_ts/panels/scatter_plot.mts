import {get_selected_categories} from "../utility/misc.mjs";
import {Plot, Plotly, setup_plot} from "../utility/plot.mjs";
import {configure_single_measurement_select, get_measurement_display_name} from "../services/measurement.mjs";
import {configure_entity_selection, is_valid_entity} from "../utility/entity_selection.mjs";
import {configure_category_selection} from "../utility/categories_selection.mjs";
import {UserError} from "../utility/error.mjs";
import {switch_nav_item} from "../utility/nav.mjs";
import {get_input_value_by_id, is_checked_by_id} from "../utility/dom.mjs";


class ScatterPlot extends Plot {

    get_name() {
        return 'scatter_plot';
    }

    decode_data(data) {
        return Plotly.react('plot_div', data, {});
    }

    get_query_parameters() {
        const measurement_x_axis = get_input_value_by_id('scatter_plot_x_measurement');
        const entity_x_axis = get_input_value_by_id('scatter_plot_x_axis_numerical_entities_select');
        const measurement_y_axis = get_input_value_by_id('scatter_plot_y_measurement');
        const entity_y_axis = get_input_value_by_id('scatter_plot_y_axis_numerical_entities_select');
        const scale = this.get_scale_type();
        const add_group_by = this.get_group_by_data();
        this.perform_error_handling(entity_x_axis, entity_y_axis, add_group_by, measurement_x_axis, measurement_y_axis);
        return this.get_parameter_string(
            measurement_x_axis, entity_x_axis, measurement_y_axis, entity_y_axis, scale, add_group_by
        );
    }

    get_scale_type() {
        return {
            log_x: is_checked_by_id('log_x'),
            log_y: is_checked_by_id('log_y'),
        };
    }

    get_group_by_data() {
        let add_group_by;
        if ( is_checked_by_id('add_group_by') ) {
            add_group_by = {
                key: get_input_value_by_id('scatter_plot_categorical_entities_select'),
                categories: get_selected_categories()
            };
        }
        return add_group_by;
    }

    perform_error_handling(entity_x_axis, entity_y_axis, add_group_by, measurement_x_axis, measurement_y_axis) {
        const group_by = is_checked_by_id('add_group_by');
        if (!is_valid_entity(entity_x_axis)) {
            throw new UserError("Please select x_axis");
        }
        if (!is_valid_entity(entity_y_axis)) {
            throw new UserError("Please select y_axis");
        }
        if (entity_x_axis === entity_y_axis && measurement_x_axis === measurement_y_axis) {
            const name = get_measurement_display_name();
            throw new UserError(`You can't compare same entity for the same ${name}`);
        }
        if (group_by && !is_valid_entity(add_group_by.key)) {
            throw new UserError("Please select 'group by' entity");
        }
        if (group_by && !add_group_by.categories.length) {
            throw new UserError("Please select subcategory");
        }
    }

    get_parameter_string(measurement_x_axis, entity_x_axis, measurement_y_axis, entity_y_axis, scale, add_group_by) {
        return new URLSearchParams({
            scatter_plot_data: JSON.stringify({
                measurement_x_axis: measurement_x_axis,
                entity_x_axis: entity_x_axis,
                measurement_y_axis: measurement_y_axis,
                entity_y_axis: entity_y_axis,
                scale: scale,
                add_group_by: add_group_by
            })
        });
    }
}

async function init() {
    switch_nav_item('scatter_plot');
    await configure_single_measurement_select('scatter_plot_x_measurement', 'scatter_plot_x_measurement_div');
    await configure_single_measurement_select('scatter_plot_y_measurement', 'scatter_plot_y_measurement_div');
    await configure_entity_selection(
        'scatter_plot_x_axis_numerical_entities_select', [],
        false, false
    );
    await configure_entity_selection(
        'scatter_plot_y_axis_numerical_entities_select', [],
        false, false
    );
    await configure_entity_selection(
        'scatter_plot_categorical_entities_select', [],
        false, false
    );
    configure_category_selection(
        'subcategory_entities',
        null,
        'scatter_plot_categorical_entities_select',
    );
    configure_add_group_by_switch();
}

function configure_add_group_by_switch() {
    const element = document.getElementById('add_group_by') as HTMLInputElement;
    element.onchange = () => {
        let add_group_element = document.getElementById('add_group');
        if( element.checked ) {
            add_group_element.classList.remove('d-none');
        } else {
            add_group_element.classList.add('d-none');
        }
    };
}

setup_plot(new ScatterPlot(), init);
