import {get_selected_measurements, get_selected_items} from "../utility/misc.js";
import {handle_plot} from "../utility/plot.js";
import {configure_multiple_measurement_select} from "../services/measurement.js";
import {configure_entity_selection} from "../utility/entity_selection.js";
import {configure_category_selection} from "../utility/categories_selection.js";
import {get_entity_by_key} from "../services/entity.js";

function display_results() {
    handle_plot({
        decode_data: decode_data,
        get_query_parameters: get_query_parameters,
        plot_url: '/histogram/json',
        download_url: '/histogram/download',
        download_file_name: 'histogram.svg',
    });
}

function decode_data(data) {
    Plotly.react('histogram', data, {});
}

function get_query_parameters() {
    const measurements = get_selected_measurements();
    const numerical_entity = document.getElementById('histogram_numerical_entities_select').value;
    const categorical_entity = document.getElementById('histogram_categorical_entities_select').value;
    const categories = get_selected_items('histogram_subcategory_entities');
    const number_of_bins = document.getElementById('number_of_bins').value;
    validate_parameters(measurements, numerical_entity, categorical_entity, categories);
    return get_query_parameter_string(measurements, numerical_entity, categorical_entity, categories, number_of_bins);
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

function get_query_parameter_string(measurements, numerical_entity, categorical_entity, categories, number_of_bins) {
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
        'histogram_numerical_entities_select', window.selected_numerical_entities,
        false, false
    );
    await configure_entity_selection(
        'histogram_categorical_entities_select', [],
        false, false
    );
    configure_category_selection('histogram_subcategory_entities', entity_placeholder);
    document.getElementById('histogram_categorical_entities_select').onchange = ( async () => {
        let element = document.getElementById('histogram_categorical_entities_select');
        const entity_key = element.value;
        const categorical_entity = entity_key ? await get_entity_by_key(entity_key) : entity_placeholder;
        configure_category_selection('histogram_subcategory_entities', categorical_entity)
    });
}

document.addEventListener("DOMContentLoaded", init);
window.display_results = display_results;
