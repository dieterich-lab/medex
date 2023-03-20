import {get_selected_categories, get_selected_measurements} from "../utility/misc.js";
import {handle_plot} from "../utility/plot.js";
import {configure_multiple_measurement_select} from "../services/measurement.js";
import {configure_entity_selection} from "../utility/entity_selection.js";
import {configure_category_selection} from "../utility/categories_selection.js";
import {get_entity_by_key} from "../services/entity.js";

function display_results() {
    handle_plot({
        decode_data: decode_data,
        get_query_parameters: get_query_parameters,
        plot_url: '/boxplot/json',
        download_url: '/boxplot/download',
        download_file_name: 'boxplot.svg',
    });
}

function decode_data(data) {
    Plotly.react('boxplot_table', data.table_json, {});
    Plotly.react('boxplot', data.image_json, {});
}

function get_query_parameters() {
    const measurements = get_selected_measurements();
    const numerical_entity = document.getElementById('boxplot_numerical_entities_select').value;
    const categorical_entity = document.getElementById('boxplot_categorical_entities_select').value;
    const categories = get_selected_categories();
    const plot_type = get_plot_type();
    validate_parameters(measurements, numerical_entity, categorical_entity, categories);
    return get_parameter_string(measurements, numerical_entity, categorical_entity, categories, plot_type);

}

function get_plot_type() {
    const all_plot_types = document.querySelectorAll('input[name="plot_type_boxplot"]');
    let plot_type;
    for (const selected_type of all_plot_types) {
        if (selected_type.checked) {
            plot_type = selected_type.value;
        }
    }
    return plot_type
}

function get_parameter_string(measurements, numerical_entity, categorical_entity, categories, plot_type) {
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

function validate_parameters(measurements, numerical_entity, categorical_entity, categories) {
    if (!measurements.length) {
        throw "Please select one or more visits";
    }
    if (!is_valid_entity(numerical_entity)) {
        throw "Please select the numerical entity";
    }
    if (!is_valid_entity(categorical_entity)) {
        throw "Please select the group_by entity";
    }
    if (!categories.length) {
        throw "Please select one or more subcategories";
    }
}

function is_valid_entity(x){
    return (!!x && x !== '' && x !== 'Search Entity')
}

const entity_placeholder = {
    key: 'x',
    categories: [],
};

async function init() {
    await configure_multiple_measurement_select('measurement', 'measurement_div');
    await configure_entity_selection(
        'boxplot_numerical_entities_select', window.selected_numerical_entities,
        false, false
    );
    await configure_entity_selection(
        'boxplot_categorical_entities_select', [],
        false, false
    );
    configure_category_selection('subcategory_entities', entity_placeholder);
    document.getElementById('boxplot_categorical_entities_select').onchange = ( async () => {
        let element = document.getElementById('boxplot_categorical_entities_select');
        const entity_key = element.value;
        const categorical_entity = entity_key ? await get_entity_by_key(entity_key) : entity_placeholder;
        configure_category_selection('subcategory_entities', categorical_entity)
    });
}

document.addEventListener("DOMContentLoaded", init);
window.display_results = display_results;