import {configure_multiple_measurement_select} from "../services/measurement.mjs";
import {configure_entity_selection} from "../utility/entity_selection.mjs";
import {get_database_info} from "../services/database_info.mjs";
import {get_selected_items, show_collapsed} from "../utility/misc.mjs";
import {switch_nav_item} from "../utility/nav.mjs";
import Datatable from 'datatables.net-dt';
import 'datatables.net-dt/css/jquery.dataTables.min.css';
import {EntityType} from "../services/entity.mjs";
import {clear_error, report_error} from "../utility/error.mjs";

declare global {
    interface Window {
        display_numerical_results: () => void;
        display_categorical_results: () => void;
        display_date_results: () => void;
        clear_errors: () => void;
    }
}

interface BasicStatsData {
    basic_stats_data: string
}

interface TabDescriptor {
    name: string,
    entity_type: EntityType,
    table_columns: ColumnDescriptor[],
}

interface ColumnDescriptor {
    data: string,
    title: string,
}

const DEFAULT_TABLE_COLUMNS: ColumnDescriptor[] = [
    {data: 'key', title: 'Entity'},
    {data: 'measurement', title: 'Visit'},
    {data: 'count', title: 'Counts'},
    {data: 'count NaN', title: 'Counts NaN'},
];

const NUMERICAL_TABLE_COLUMNS:ColumnDescriptor[] = [
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

const NUMERICAL_DESCRIPTOR: TabDescriptor = {
    'name': 'numerical',
    'entity_type': EntityType.NUMERICAL,
    'table_columns': NUMERICAL_TABLE_COLUMNS,
};

const CATEGORICAL_DESCRIPTOR: TabDescriptor = {
    'name': 'categorical',
    'entity_type': EntityType.CATEGORICAL,
    'table_columns': DEFAULT_TABLE_COLUMNS,
};

const DATE_DESCRIPTOR: TabDescriptor = {
    'name': 'date',
    'entity_type': EntityType.DATE,
    'table_columns': DEFAULT_TABLE_COLUMNS,
};

const ALL_DESCRIPTORS: TabDescriptor[] = [
    NUMERICAL_DESCRIPTOR,
    CATEGORICAL_DESCRIPTOR,
    DATE_DESCRIPTOR,
];


let init_promise = null;

let datatable = null;


async function do_init() {
    switch_nav_item('basic_stats');
    for( const descriptor of ALL_DESCRIPTORS ) {
        const name = descriptor.name;
        const entity_type = descriptor.entity_type;
        await configure_multiple_measurement_select(
            `basic_stats_measurement_${name}`,
            `basic_stats_measurement_${name}_div`
        );
        await configure_entity_selection(
            `basic_stats_${name}_entities_select`, [],
            true, false, [entity_type]
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
    clear_error();
    const name = descriptor.name;
    const measurements = get_selected_items(`basic_stats_measurement_${name}`);
    const entities = get_selected_items(`basic_stats_${name}_entities_select`);
    const ok = check_user_input(descriptor, measurements, entities);
    if ( ok ) {
        create_datatable(descriptor, measurements, entities);
        set_url_for_download(descriptor, measurements, entities);
        show_collapsed(`${name}_results`);
    }
}

function check_user_input(descriptor, measurements, entities) {
    if (!measurements.length) {
        report_error("Please select one or more visits");
        return false;
    }
    if (!entities.length) {
        report_error("Please select one or more entities");
        return false;
    }
    return true;
}

function create_datatable(descriptor, measurements, entities) {
    const name = descriptor.name;
    const url = `/basic_stats/${ name }`;
    const query = `#${ name }_table`;
    if ( datatable ) {
        datatable.destroy();
    }
    datatable = new Datatable(query,{
        processing: true,
        serverSide: true,
        info: false,
        paging: false,
        ordering: false,
        ajax: {
            url: url,
            data: function (raw_data: BasicStatsData) {
                raw_data.basic_stats_data = JSON.stringify({
                    measurements: measurements,
                    entities: entities,
                });
            },
        },
        columns: descriptor.table_columns,
        dom: 'lrtip',
    })
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

document.addEventListener("DOMContentLoaded", init);
window.display_numerical_results = display_numerical_results;
window.display_categorical_results = display_categorical_results;
window.display_date_results = display_date_results;
window.clear_errors = clear_error;
