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
        plot_url: '/barchart/json',
        download_url: '/barchart/download',
        download_file_name: 'barchart.svg',
    });
}

function decode_data(data) {
    Plotly.react('barchart', data, {});
}

function get_query_parameters() {
    const measurements = get_selected_measurements();
    const entity = document.getElementById('barchart_categorical_entities_select').value;
    const categories = get_selected_categories();
    validate_parameters(measurements, entity, categories);
    const plot_type = get_plot_type();
    return get_search_parameter_string(measurements, entity, categories, plot_type);
}

function get_plot_type() {
    const all_plot_types = document.querySelectorAll('input[name="plot_type"]');
    let plot_type;
    for (const selected_type of all_plot_types) {
        if (selected_type.checked) {
            plot_type = selected_type.value;
        }
    }
    return plot_type
}

function validate_parameters(measurements, entity, categories) {
    if ( !measurements.length ) {
        throw "Please select one or more measurements.";
    }
    if ( !is_valid_entity(entity) ) {
        throw "Please select the entity to group by.";
    }
    if ( !categories.length ) {
        throw "Please select one or more subcategories.";
    }
}

function get_search_parameter_string(measurements, entity, categories, plot_type) {
    return new URLSearchParams({
        barchart_data: JSON.stringify({
            measurements: measurements,
            key: entity,
            categories: categories,
            plot_type: plot_type,
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
        'barchart_categorical_entities_select', [],
        false, false
    );
    configure_category_selection('subcategory_entities', entity_placeholder);
    document.getElementById('barchart_categorical_entities_select').onchange = ( async () => {
        let element = document.getElementById('barchart_categorical_entities_select');
        const entity_key = element.value;
        const categorical_entity = entity_key ? await get_entity_by_key(entity_key) : entity_placeholder;
        configure_category_selection('subcategory_entities', categorical_entity)
    });
}

document.addEventListener("DOMContentLoaded", init);
window.display_results = display_results;
