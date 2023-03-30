import {configure_entity_selection} from "../utility/entity_selection.mjs";
import {configure_multiple_measurement_select} from "../services/measurement.mjs";
import {get_selected_items, get_selected_measurements, show_collapsed} from "../utility/misc.mjs";
import {switch_nav_item} from "../utility/nav.mjs";
import {get_radio_input_by_name} from '../utility/dom.mjs';
import Datatable from 'datatables.net-dt';
import 'datatables.net-dt/css/jquery.dataTables.min.css';

let datatable = null;

declare global {
    interface Window {
        display_results: () => void;
    }
}

interface FilteredDataParameters {
    table_data: string
}

async function init() {
    switch_nav_item('table_browser');
    await configure_multiple_measurement_select('measurement', 'measurement_div');
    await configure_entity_selection(
        'table_browser_entities_select', [],
        true, false
    );
}

document.addEventListener("DOMContentLoaded", init);

function display_results() {
    const table_type = get_radio_input_by_name('what_table');
    const measurements = get_selected_measurements();
    const entities = get_selected_items('table_browser_entities_select');
    create_datatable(table_type, measurements, entities);
    set_url_for_download(table_type, measurements, entities);
    show_collapsed('results');
}

function create_datatable(selected_table, measurements, entities) {
    const url = selected_table === 'long' ? '/filtered_data/flat' : '/filtered_data/by_measurement';
    const column = define_table_columns(selected_table);
    if ( datatable ) {
        datatable.destroy();
    }

    datatable = new Datatable(
        '#serverside_table',
        {
            destroy: true,
            processing: true,
            serverSide: true,
            ajax: {
                url: url,
                data: function (raw_data: FilteredDataParameters) {
                    raw_data.table_data = JSON.stringify({
                        measurements: measurements,
                        entities: entities,
                    });
                },
            },
            columns: column,
            dom: 'lrtip',
            scrollX: true,
            pagingType: 'full_numbers',
            lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
        }
    );
}

function define_table_columns(selected_table) {
    let column = [
        {data: 'name_id', title: 'name_id'},
        {data: 'measurement', title: 'measurement'},
    ]
    if (selected_table === 'long') {
        column = column.concat([
            {data: 'key', title: 'key'},
            {data: 'value', title: 'value'},
        ]);
    } else if (selected_table === 'short') {
        const entities = get_selected_items('table_browser_entities_select');
        const entity_columns = entities.map((x) => {
            return {data: `${x}`, title: `${x}`};
        });
        column = column.concat(entity_columns);
    }
    return column;
}

function set_url_for_download(selected_table, measurements, entities) {
    const base_url = selected_table === 'long' ? '/filtered_data/flat_csv?' : '/filtered_data/by_measurement_csv?';
    const search_params = new URLSearchParams({
        data: JSON.stringify({
            measurements: measurements,
            entities: entities,
        })
    });
    const url = base_url + search_params;

    let div = document.getElementById('csv_download');
    div.innerHTML = `
        <div class="card-body">
            <a href="${url}" class="btn btn-outline-info">Download</a>
        </div>
    `;
}

document.addEventListener("DOMContentLoaded", init);
window.display_results = display_results;
