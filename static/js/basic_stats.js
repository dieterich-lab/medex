import {configure_multiple_measurement_select} from "./measurement.js";
import {configure_entity_selection} from "./entity_selection.js";
import {get_database_info} from "./database_info.js";
import {get_selected_items} from "./utility.js";

const DEFAULT_TABLE_COLUMNS = [
    {data: 'key', title: 'Entity'},
    {data: 'measurement', title: 'Visit'},
    {data: 'count', title: 'Counts'},
    {data: 'count NaN', title: 'Counts NaN'},
];

const NUMERICAL_TABLE_COLUMNS = [
    {data: 'key', title: 'Entity'},
    {data: 'measurement', title: 'Visit'},
    {data: 'count', title: 'Counts'},
    {data: 'count NaN', title: 'Counts NaN'},
    {data: 'min', title: 'Min'},
    {data: 'max', title: 'Max'},
    {data: 'mean', title: 'Mean'},
    {data: 'median', title: 'Median'},
    {data: 'stddev', title: 'Std. Deviation'},
    {data: 'stderr', title: 'Std. Error'},
];

const NUMERICAL_DESCRIPTOR = {
    'name': 'numerical',
    'table_columns': NUMERICAL_TABLE_COLUMNS,
};

const CATEGORICAL_DESCRIPTOR = {
    'name': 'categorical',
    'table_columns': DEFAULT_TABLE_COLUMNS,
};

const DATE_DESCRIPTOR = {
    'name': 'date',
    'table_columns': DEFAULT_TABLE_COLUMNS,
};

const ALL_ENTITY_DESCRIPTORS = [
    NUMERICAL_DESCRIPTOR,
    CATEGORICAL_DESCRIPTOR,
    DATE_DESCRIPTOR,
];


let init_promise = null;


async function do_init() {
    for( const descriptor of ALL_ENTITY_DESCRIPTORS ) {
        const name = descriptor.name;
        await configure_multiple_measurement_select(
            `basic_stats_measurement_${name}`,
            `basic_stats_measurement_${name}_div`
        );
        await configure_entity_selection(
            `basic_stats_${name}_entities_select`, [],
            true, false
        );
    }
    await show_database_info();
}


async function init() {
    if (init_promise === null) {
        init_promise = await do_init()
    }
    return init_promise;
}

async function show_database_info() {
    const info = await get_database_info();
    let element = document.getElementById('database_tab_table_id');
    element.innerHTML = `
        <tr><td>Number of patients:</td><td>${ info.number_of_patients }</td></tr>
        <tr><td>Number of numerical entities:</td><td>${ info.number_of_numerical_entities }</td></tr>
        <tr><td>Number of numerical data items:</td><td>${ info.number_of_numerical_data_items }</td></tr>
        <tr><td>Number of categorical entities:</td><td>${ info.number_of_categorical_entities }</td></tr>
        <tr><td>Number of categorical data items:</td><td>${ info.number_of_categorical_data_items }</td></tr>
        <tr><td>Number of date entities:</td><td>${ info.number_of_date_entities }</td></tr>
        <tr><td>Number of date data items:</td><td>${ info.number_of_date_data_items }</td></tr>
    `;
}

function display_results(descriptor) {
    const name = descriptor.name;
    const measurements = get_selected_items(`basic_stats_measurement_${name}`);
    const entities = get_selected_items(`basic_stats_${name}_entities_select`);
    const ok = check_for_user_errors(descriptor, measurements, entities);
    if ( ok ) {
        create_datatable(descriptor, measurements, entities);
        const base_url = '/basic_stats/numerical_csv?';
        set_url_for_download(descriptor, measurements, entities);
    }
}

function check_for_user_errors(descriptor, measurements, entities) {
    let error = null;
    if (!measurements.length) {
        error = "Please select one or more visits";
    } else if (!entities.length) {
        error = "Please select one or more entities";
    }
    handle_error(descriptor, error);
    return error === null;
}

function handle_error(descriptor, error) {
    const name = descriptor.name;
    let div = document.getElementById(`basic_stats_error_${ name }`);
    if ( error ) {
        div.innerHTML = `
        <div class="alert alert-danger mt-2" role="alert">
            ${error}
            <span class="close" aria-label="Close"> &times;</span>
        </div>
        `;
    } else {
        div.innerHTML = '';
    }
}

function create_datatable(descriptor, measurements, entities) {
    const name = descriptor.name;
    const url = `/basic_stats/${ name }`;
    const query = `#${ name }_table`;
    let element = $(query);
    if ( $.fn.DataTable.isDataTable(query) ) {
        let table = element.DataTable();
        table.destroy();
        element.empty();
    }
    element.DataTable({
        processing: true,
        serverSide: true,
        info: false,
        paging: false,
        ordering: false,
        ajax: {
            url: url,
            data: function (raw_data) {
                raw_data.basic_stats_data = JSON.stringify({
                    measurements: measurements,
                    entities: entities,
                });
            },
        },
        columns: descriptor.table_columns,
        sDom: 'lrtip',
    });
}

function set_url_for_download(descriptor, measurements, entities) {
    const name = descriptor.name;
    const search_params = new URLSearchParams({
        basic_stats_data: JSON.stringify({
            measurements: measurements,
            entities: entities,
        })
    });
    const url = `/basic_stats/${ name }_csv? ${ search_params }`;
    let div = document.getElementById(`basic_stats_${ name }_csv_download`);
    div.innerHTML = `
        <div class="card-body">
            <a href="${ url }" class="btn btn-outline-info">Download</a>
        </div>
    `;
}

function display_numerical_results() {
    display_results(NUMERICAL_DESCRIPTOR);
}

function display_categorical_results() {
    display_results(CATEGORICAL_DESCRIPTOR);
}

function display_date_results() {
    display_results(DATE_DESCRIPTOR);
}

export {init, display_numerical_results, display_categorical_results, display_date_results};