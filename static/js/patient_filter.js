import {get_entity_list, get_entity_by_key} from './entity.js';
import {configure_entity_selection} from "./entity_selection";

async function init() {
    refresh_filter_panel();
    await render_select_filter_box();
    setup_measurement_filter_select();
    setup_categorical_filter_panel_categories();
}

async function render_select_filter_box() {
    let select_box = document.getElementById('selected_filter');
    const all_entities = await get_entity_list();
    const html = '<option>Search entity</option>'
        + all_entities.map((x) => `
        <option value="${x.key}">${get_entity_display_name(x)}</option>`).join('')
        + '\n';
    select_box.innerHTML = html;
}

function get_entity_display_name(entity) {
    if ( entity.description ) {
        return `${entity.key} <div class="description">${entity.description}</div>`;
    } else {
        return entity.key;
    }
}

function setup_categorical_filter_panel_categories() {
    // ToDo: Purge Jquery
    let cat_select = $("#categorical_filter_panel_categories");
    cat_select.select2({
        placeholder:"Search entity"
    });
    cat_select.on("select2:select", handle_select_categories);
}

function setup_measurement_filter_select() {
    let filter_measurement_select = $("#filter_measurement");
    filter_measurement_select.select2({
        placeholder: "Search entity"
    });
    filter_measurement_select.change(() => {
        set_filter_measurement(filter_measurement_select.val());
    });
}

function handle_select_categories(event) {
    const selected_item = event.params.data.text;
    if ( selected_item === 'Select all') {
        $("#categorical_filter_panel_categories> option").prop("selected","selected");
        $('#categorical_filter_panel_categories> option[value="Select all"]').prop("selected", false);
        $("#categorical_filter_panel_categories").trigger("change");
    }
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
    let select_categories = document.getElementById('categorical_filter_panel_categories');
    select_categories.innerHTML = `
        <option value="Select all" id="categorical_filter_panel_select_all_categories">Select all</option>`
        + entity.categories.map( x => `
        <option value="${x}">${x}</option>`
    ) + '\n';
    $("#categorical_filter_panel_categories").trigger("change");
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
    }).then(response => {
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
    const categories = filter['categories'].join(', ');
    render_filter(entity_key, `${categories}`);
}

function render_filter(entity_key, inner_html) {
    let div = document.getElementById('active_filters');
    let child = document.createElement('div');
    child.setAttribute('class', 'card');
    child.innerHTML = `
        <div class="card-body" style="display: flex; justify-content: space-between">
            <span>${entity_key}:&nbsp;&nbsp;&nbsp;&#32; ${inner_html}</span>
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
    }).then(response => {
        refresh_filter_panel();
    }).catch(error => {
        console.log(error);
        refresh_filter_panel();
    })
}

async function render_numerical_filter(entity_key, filter) {
    const entity = await get_entity_by_key(entity_key);
    const slider_id = `active_filter_${entity_key}`;
    render_filter(entity_key, `${filter.from_value}&nbsp;-&nbsp;${filter.to_value}`);
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
    const entity = await get_selected_entity();
    const categories = get_selected_categories();

    fetch('/filter/add_categorical', {
        method: 'POST',
        headers:{
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({'entity': entity['key'], 'categories': categories}),
    }).then(response => {
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
    const entity = await get_selected_entity();
    const from_to = document.getElementById("numerical_filter_panel_range_slider").value.split(';');
    const request_json = {
        'entity': entity['key'],
        'from_value': parseFloat(from_to[0]),
        'to_value': parseFloat(from_to[1]),
    };

    fetch('/filter/add_numerical', {
        method: 'POST',
        headers:{
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(request_json),
    }).then(response => {
        refresh_filter_panel();
    }).catch(error => {
        console.log(error);
        refresh_filter_panel();
    })
}

function set_filter_measurement(new_measurement) {
    fetch('/filter/set_measurement', {
        method: 'POST',
        headers:{
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({'measurement': new_measurement}),
    }).then(response => {
        refresh_filter_panel();
    }).catch(error => {
        console.log(error);
        refresh_filter_panel();
    });
}

$(function () {
    function cd(start, end) {
        $('#Date span').html(start.format('YYYY-MM-DD') + ' - ' + end.format('YYYY-MM-DD'));
    }
    $('#Date').daterangepicker({
        startDate: start,
        endDate: end,
    },cd);

    cd(start,end);

    // Still needed? What is this good for?
    //
    // $(".range").ionRangeSlider({
    //     type: "double",
    //     skin: "big",
    //     grid: true,
    //     grid_num: 4,
    //     step: 0.001,
    //     to_fixed:true,//block the top
    //     from_fixed:true//block the from
    // });
});

export {
    init, select_filter, add_or_update_categorical_filter, set_numerical_filter_from, set_numerical_filter_to,
    clear_all_filters, add_or_update_numerical_filter
};
