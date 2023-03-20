import {get_selected_categories} from "../utility/misc.js";
import {handle_plot} from "../utility/plot.js";
import {configure_single_measurement_select} from "../services/measurement.js";
import {configure_entity_selection} from "../utility/entity_selection.js";
import {configure_category_selection} from "../utility/categories_selection.js";
import {get_entity_by_key} from "../services/entity.js";

function display_results() {
    handle_plot({
        decode_data: decode_data,
        get_query_parameters: get_query_parameters,
        plot_url: '/scatter_plot/json',
        download_url: '/scatter_plot/download',
        download_file_name: 'scatter_plot.svg',
    });
}

function decode_data(data) {
    Plotly.react('scatter_plot', data, {});
}

function get_query_parameters() {
    const measurement_x_axis = document.getElementById('scatter_plot_x_measurement').value;
    const entity_x_axis = document.getElementById('scatter_plot_x_axis_numerical_entities_select').value;
    const measurement_y_axis = document.getElementById('scatter_plot_y_measurement').value;
    const entity_y_axis = document.getElementById('scatter_plot_y_axis_numerical_entities_select').value;
    const scale = get_scale_type();
    const add_group_by = get_group_by_data();
    perform_error_handling(entity_x_axis, entity_y_axis, add_group_by, measurement_x_axis, measurement_y_axis);
    return get_parameter_string(
        measurement_x_axis, entity_x_axis, measurement_y_axis, entity_y_axis, scale, add_group_by
    );
}

function get_scale_type() {
    return {
        log_x: !!document.querySelector('input[name="log_x"]').checked,
        log_y: !!document.querySelector('input[name="log_y"]').checked
    };
}

function get_group_by_data() {
    let add_group_by;
    if (document.querySelector('input[name="add_group_by"]').checked) {
        add_group_by = {
            key: document.getElementById('scatter_plot_categorical_entities_select').value,
            categories: get_selected_categories()
        };
    }
    return add_group_by;
}

function perform_error_handling(entity_x_axis, entity_y_axis, add_group_by, measurement_x_axis, measurement_y_axis) {
    const group_by = !!document.querySelector('input[name="add_group_by"]').checked;
    if ( !is_valid_entity(entity_x_axis) ) {
        throw "Please select x_axis";
    }
    if (!is_valid_entity(entity_y_axis)) {
        throw "Please select y_axis";
    }
    if ( entity_x_axis === entity_y_axis && measurement_x_axis === measurement_y_axis ) {
        throw "You can't compare same entity for the same visit";
    }
    if (group_by && !is_valid_entity(add_group_by.key)) {
        throw "Please select 'group by' entity";
    }
    if (group_by && !add_group_by.categories.length) {
        throw "Please select subcategory";
    }
}

function get_parameter_string(measurement_x_axis, entity_x_axis, measurement_y_axis, entity_y_axis, scale, add_group_by) {
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


function is_valid_entity(entity){
    return (!!entity && entity !== '' && entity !== 'Search Entity')
}

$(function () {
    // apply filters for add group by
    $(document).on('change', '#add_group_by', function() {
        if(this.checked === false) {
          $('#add_group').addClass('d-none');
        } else {
            $('#add_group').removeClass('d-none');
        }
    });
});

const entity_placeholder = {
    key: 'x',
    categories: [],
};

async function init() {
    await configure_single_measurement_select('scatter_plot_x_measurement', 'scatter_plot_x_measurement_div');
    await configure_single_measurement_select('scatter_plot_y_measurement', 'scatter_plot_y_measurement_div');
    await configure_entity_selection(
        'scatter_plot_x_axis_numerical_entities_select', window.selected_numerical_entities,
        false, false
    );
    await configure_entity_selection(
        'scatter_plot_y_axis_numerical_entities_select', window.selected_numerical_entities,
        false, false
    );
    await configure_entity_selection(
        'scatter_plot_categorical_entities_select', [],
        false, false
    );
    configure_category_selection('subcategory_entities', entity_placeholder);
    document.getElementById('scatter_plot_categorical_entities_select').onchange = (async () => {
        let element = document.getElementById('scatter_plot_categorical_entities_select');
        const entity_key = element.value;
        const categorical_entity = entity_key ? await get_entity_by_key(entity_key) : entity_placeholder;
        configure_category_selection('subcategory_entities', categorical_entity)
    });
}

document.addEventListener("DOMContentLoaded", init);
window.display_results = display_results;
