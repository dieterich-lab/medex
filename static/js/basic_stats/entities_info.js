import {configure_multiple_measurement_select} from "../measurement";
import {configure_entity_selection} from "../entity_selection";

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

const Entities_info = [
    {
        'name': 'numerical',
        'table_columns': NUMERICAL_TABLE_COLUMNS,
    },
    {
        'name': 'categorical',
        'table_columns': DEFAULT_TABLE_COLUMNS,
    },
    {
        'name': 'date',
        'table_columns': DEFAULT_TABLE_COLUMNS,
    }
];


let init_promise = null;


async function do_init() {
    for( const descriptor of Entities_info ) {
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
}


async function init() {
    if (init_promise === null) {
        init_promise = await do_init()
    }
    return init_promise;
}

$('a[data-toggle="tab"]').on('shown.bs.tab', async (e) => {
    for( const descriptor of Entities_info ) {
        const name = descriptor.name;
        if ( e.target.hash === `#${ name }_tab` ) {
            await init();
        }
    }
});

function display_basic_stat(descriptor) {
    const name = descriptor.name;
    const measurements = get_selected_items(`basic_stats_measurement_${name}`);
    const entities = get_selected_items(`basic_stats_${name}_entities_select`);
    const ok = check_for_user_errors(descriptor, measurements, entities);
    if (ok) {
        create_datatable(descriptor, measurements, entities);
        const base_url = '/basic_stats/numerical_csv?';
        set_url_for_download(descriptor, measurements, entities);
    }
}

function get_selected_items(element_id) {
    const parent = document.getElementById(element_id);
    const children = Array.from(parent.childNodes);
    return children.filter((x) => x.selected).map((x) => x.value);
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
    if ($.fn.DataTable.isDataTable(query)) {
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
        columns: column,
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

export {init};