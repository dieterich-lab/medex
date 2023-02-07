function display_numerical_statistics_results() {
    const measurements = get_selected_measurements('measurement_numeric');
    const entities = get_selected_entities('basic_stats_numerical_entities_select');
    const date_dict = get_date_dict();
    const error = perform_error_handling(measurements, entities);
    const div = document.getElementById('error_basic_stats_numerical');
    if (error) {
        div.innerHTML = `
            <div class="alert alert-danger mt-2" role="alert">
                ${error}
                <span class="close" aria-label="Close"> &times;</span>
            </div>
        `;
    }
    else {
        div.innerHTML = ``;
        setup_numeric_datatable(measurements, entities, date_dict);
        const base_url = '/basic_stats/numerical_csv?';
        set_url_for_download(base_url, measurements, entities, date_dict, 'basic_stats_numeric_csv_download');
    }
}

function display_categorical_statistics_results() {
    const measurements = get_selected_measurements('measurement_categorical');
    const entities = get_selected_entities('basic_stats_categorical_entities_select');
    const date_dict = get_date_dict();
    const error = perform_error_handling(measurements, entities);
    const div = document.getElementById('error_basic_stats_categorical');
    if (error) {
        div.innerHTML = `
            <div class="alert alert-danger mt-2" role="alert">
                ${error}
                <span class="close" aria-label="Close"> &times;</span>
            </div>
        `;
    }
    else {
        div.innerHTML = ``;
        setup_categorical_datatable(measurements, entities, date_dict);
        const base_url = '/basic_stats/categorical_csv?';
        set_url_for_download(base_url, measurements, entities, date_dict, 'basic_stats_categorical_csv_download');
    }
}

function display_date_statistics_results() {
    const measurements = get_selected_measurements('measurement_date');
    const entities = get_selected_entities('basic_stats_date_entities_select');
    const date_dict = get_date_dict();
    const error = perform_error_handling(measurements, entities);
    const div = document.getElementById('error_basic_date');
    if (error) {
        div.innerHTML = `
            <div class="alert alert-danger mt-2" role="alert">
                ${error}
                <span class="close" aria-label="Close"> &times;</span>
            </div>
        `;
    }
    else {
        div.innerHTML = ``;
        setup_date_datatable(measurements, entities, date_dict);
        const base_url = '/basic_stats/date_csv?';
        set_url_for_download(base_url, measurements, entities, date_dict, 'basic_stats_date_csv_download');
    }
}

function get_selected_measurements(element_id) {
    const parent = document.getElementById(element_id);
    const children = Array.from(parent.childNodes);
    return children.filter((x) => x.selected).map((x) => x.value);
}


function get_selected_entities(element_id) {
    const parent = document.getElementById(element_id);
    const children = Array.from(parent.childNodes);
    return children.filter((x) => x.selected).map((x) => x.value);
}

function get_date_dict() {
    const date = document.getElementById('Date').value;
    const date_string = date.split(' - ');
    return {
        from_date: moment(date_string[0], 'MM/DD/YYYY').format('YYYY-MM-DD'),
        to_date: moment(date_string[1], 'MM/DD/YYYY').format('YYYY-MM-DD')
    }
}

function perform_error_handling(measurements, entities) {
    if (!measurements.length) {
        return "Please select one or more visits";
    } else if (!entities.length) {
        return "Please select one or more entities";
    } else {
        return null;
    }
}

function setup_numeric_datatable(measurements, entities, date_dict) {
    const url = '/basic_stats/numerical';
    const column = define_numerical_table_columns();
    const element = $('#numeric_table');
    if ($.fn.DataTable.isDataTable('#numeric_table')) {
        let table = element.DataTable();
        table.destroy();
        element.empty();
    }
    create_datatable(element, url, measurements, entities, date_dict, column);
}

function setup_categorical_datatable(measurements, entities, date_dict) {
    const url = '/basic_stats/categorical';
    const column = define_table_columns();
    const element = $('#categorical_table');
    if ($.fn.DataTable.isDataTable('#categorical_table')) {
        let table = element.DataTable();
        table.destroy();
        element.empty();
    }
    create_datatable(element, url, measurements, entities, date_dict, column);
}

function setup_date_datatable(measurements, entities, date_dict) {
    const url = '/basic_stats/date';
    const column = define_table_columns();
    const element = $('#date_table');
    if ($.fn.DataTable.isDataTable('#date_table')) {
        let table = element.DataTable();
        table.destroy();
        element.empty();
    }
    create_datatable(element, url, measurements, entities, date_dict, column);
}

function define_numerical_table_columns() {
    return [
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
}

function define_table_columns() {
    return [
        {data: 'key', title: 'Entity'},
        {data:'measurement', title: 'Visit'},
        {data: 'count', title: 'Counts'},
        {data: 'count NaN', title: 'Counts NaN'},
    ];
}

function create_datatable(element, url, measurements, entities, date_dict, column) {
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
                    date_range: date_dict
                });
            },
        },
        columns: column,
        sDom: 'lrtip',
    });
}

function set_url_for_download(base_url, measurements, entities, date_dict, element_id) {
    const search_params = new URLSearchParams({
        basic_stats_data: JSON.stringify({
            measurements: measurements,
            entities: entities,
            date_range: date_dict
        })
    });
    const url = base_url + search_params;

    let div = document.getElementById(element_id);
    div.innerHTML = `
        <div class="card-body">
            <a href="${url}" class="btn btn-outline-info">Download</a>
        </div>
    `;
}