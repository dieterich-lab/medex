import {get_entity_by_key} from '../services/entity.js';
import {configure_single_measurement_select} from '../services/measurement.js';
import {configure_entity_selection} from "../utility/entity_selection.js";
import {configure_category_selection} from "../utility/categories_selection.js";

async function init() {
    refresh_filter_panel();
    await configure_single_measurement_select('filter_measurement', 'filter_measurement_div', null,true);
    await configure_entity_selection('selected_filter', [], false, false);
    setup_measurement_filter_select();
}

function setup_measurement_filter_select() {
    let filter_measurement_select = $("#filter_measurement");
    filter_measurement_select.change(() => {
        set_filter_measurement(filter_measurement_select.val());
    });
}

async function get_selected_entity() {
    const entity_key = document.getElementById('selected_filter').value;
    return await get_entity_by_key(entity_key);
}

function get_numerical_filter_range_slider() {
    return $('#numerical_filter_panel_range_slider').data("ionRangeSlider");
}

async function select_filter() {
    const entity = await get_selected_entity();
    if ( entity.type === 'String' ) {
        display_categorical_filter_settings(entity);
    } else if ( entity.type === 'Double' ) {
        display_numerical_filter_settings(entity);
    } else {
        hide_specific_filter_panels();
    }
}

function display_categorical_filter_settings(entity) {
    configure_category_selection('categorical_filter_panel_categories', entity);
    document.getElementById('numerical_filter_panel').style.display = 'none';
    document.getElementById('categorical_filter_panel').style.display = 'block';
}

function display_numerical_filter_settings(entity) {
    // ToDo: Purge jquery.ionRangeSlider
    $('#numerical_filter_panel_range_slider').ionRangeSlider({
        type: "double",
        skin: "big",
        grid: true,
        grid_num: 4,
        min: entity.min,
        max: entity.max,
        step: 0.001,
        onStart: update_numerical_filter_settings,
        onChange: update_numerical_filter_settings
    });
    document.getElementById('numerical_filter_settings_from_field').value = entity.min;
    document.getElementById('numerical_filter_settings_to_field').value = entity.max;
    get_numerical_filter_range_slider().update({from: entity.min, to: entity.max, min: entity.min, max: entity.max});
    document.getElementById('categorical_filter_panel').style.display = 'none';
    document.getElementById('numerical_filter_panel').style.display = 'block';
}

function update_numerical_filter_settings(data) {
    document.getElementById('numerical_filter_settings_from_field').value = data.from;
    document.getElementById('numerical_filter_settings_to_field').value = data.to;
}

function hide_specific_filter_panels() {
    document.getElementById('numerical_filter_panel').style.display = 'none';
    document.getElementById('categorical_filter_panel').style.display = 'none';
}

async function set_numerical_filter_from() {
    let new_value = parseFloat(document.getElementById('numerical_filter_settings_from_field').value);
    let to_value = parseFloat(document.getElementById('numerical_filter_settings_to_field').value);
    const entity = await get_selected_entity();
    if ( new_value < entity.min ) {
        new_value = entity.min;
    }
    if ( new_value > to_value ) {
        new_value = to_value;
    }
    const update_value = {from: new_value};
    get_numerical_filter_range_slider().update(update_value);
}

async function set_numerical_filter_to() {
    let new_value = parseFloat(document.getElementById('numerical_filter_settings_to_field').value);
    let from_value = parseFloat(document.getElementById('numerical_filter_settings_from_field').value);
    const entity = await get_selected_entity();
    if ( new_value > entity.max ) {
        new_value = entity.max;
    }
    if ( new_value < from_value ) {
        new_value = from_value;
    }
    get_numerical_filter_range_slider().update({to: new_value});
}

function clear_all_filters() {
    fetch('/filter/all', {
        method: 'DELETE',
    }).then(() => {
        refresh_filter_panel();
    }).catch(error => {
        console.log(error);
        refresh_filter_panel();
    });
}

function refresh_filter_panel() {
    fetch('/filter/all', {method: 'GET'})
    .then(response => response.json())
    .then(data => render_all_filters(data))
    .catch(error => {
        console.log(error)
    })
}

async function render_all_filters(data) {
    clear_filter_panel();
    const filters = data['filters'];
    const filter_entities_sorted = Object.keys(filters).sort();
    filter_entities_sorted.forEach(entity_key => {
        const filter = filters[entity_key];
        if ('categories' in filter) {
            render_categorical_filter(entity_key, filter);
        } else {
            render_numerical_filter(entity_key, filter);
        }
    })
    update_filtered_patient_count(data['filtered_patient_count']);
}

function clear_filter_panel() {
    let div = document.getElementById('active_filters');
    let child = div.lastElementChild;
    while (child) {
        div.removeChild(child);
        child = div.lastElementChild;
    }
}

function render_categorical_filter(entity_key, filter) {
    const measurement = filter['measurement'];
    const categories = filter['categories'].join(', ');
    render_filter(entity_key, measurement, `${categories}`);
}

function render_filter(entity_key, measurement, inner_html) {
    let div = document.getElementById('active_filters');
    let child = document.createElement('div');
    child.setAttribute('class', 'card');
    let span_entity = `${entity_key} (${measurement})`;
    if (!measurement) {
        span_entity = `${entity_key}`;
    }
    child.innerHTML = `
        <div class="card-body" style="display: flex; justify-content: space-between">
            <span> ${span_entity}:&nbsp;&nbsp;&nbsp;&#32; ${inner_html}</span>
            <button type="button" style="word-wrap: normal; white-space: normal; text-align: right; height: min-content"
             class="btn btn-outline-info btn-sm" id="remove_filter_${entity_key}"
            >
             Delete
            </button>
        </div>
    `;
    div.appendChild(child);
    let remover = document.getElementById(`remove_filter_${entity_key}`);
    remover.addEventListener('click', () => { remove_filter(entity_key) }, false);
}

function remove_filter(entity_key) {
    fetch('/filter/delete', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({'entity': entity_key}),
    }).then(() => {
        refresh_filter_panel();
    }).catch(error => {
        console.log(error);
        refresh_filter_panel();
    })
}

async function render_numerical_filter(entity_key, filter) {
    const measurement = filter.measurement;
    render_filter(entity_key, measurement, `${filter.from_value}&nbsp;-&nbsp;${filter.to_value}`);
}

function update_filtered_patient_count(filtered_patient_count) {
    let span = document.getElementById('filtered_patient_count');
    if (filtered_patient_count === null) {
        span.innerHTML = '';
    } else {
        span.innerHTML = ` (${filtered_patient_count} patients)`;
    }
}

async function add_or_update_categorical_filter() {
    let measurement = document.getElementById('filter_measurement').value;
    if (!measurement) {
        measurement = null;
    }
    const entity = await get_selected_entity();
    const categories = get_selected_categories();

    fetch('/filter/add_categorical', {
        method: 'POST',
        headers:{
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({'entity': entity['key'], 'measurement': measurement, 'categories': categories}),
    }).then(() => {
        refresh_filter_panel();
    }).catch(error => {
        console.log(error)
        refresh_filter_panel();
    })
}
function get_selected_categories() {
    const parent = document.getElementById('categorical_filter_panel_categories');
    const children = Array.from(parent.childNodes);
    return children.filter((x) => x.selected).map((x) => x.value);
}

async function add_or_update_numerical_filter() {
    let measurement = document.getElementById('filter_measurement').value;
    if (!measurement) {
        measurement = null;
    }
    const entity = await get_selected_entity();
    const from_to = document.getElementById("numerical_filter_panel_range_slider").value.split(';');
    const request_json = {
        'entity': entity['key'],
        'measurement': measurement,
        'from_value': parseFloat(from_to[0]),
        'to_value': parseFloat(from_to[1]),
    };

    fetch('/filter/add_numerical', {
        method: 'POST',
        headers:{
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(request_json),
    }).then(() => {
        refresh_filter_panel();
    }).catch(error => {
        console.log(error);
        refresh_filter_panel();
    })
}

let present_filter_measurement = null;

function set_filter_measurement(new_measurement) {
    if ( new_measurement === present_filter_measurement ) {
        return;
    }
    present_filter_measurement = new_measurement;
    refresh_filter_panel();
}

window.patient_filter = {
    select_filter: select_filter,
    add_or_update_categorical_filter: add_or_update_categorical_filter,
    set_numerical_filter_from: set_numerical_filter_from,
    set_numerical_filter_to: set_numerical_filter_to,
    clear_all_filters: clear_all_filters,
    add_or_update_numerical_filter: add_or_update_numerical_filter,
    set_filter_measurement: set_filter_measurement,
};

document.addEventListener("DOMContentLoaded", init);
