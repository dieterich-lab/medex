function display_histogram_plot() {
    const result = get_query_parameters();
    let div = document.getElementById('error_histogram');
    if (!!result.error) {
        div.innerHTML = `
            <div class="alert alert-danger mt-2" role="alert">
                ${result.error}
                <span class="close" aria-label="Close"> &times;</span>
            </div>
        `;
    } else {
        const uri = '/plot/histogram/json?' + result.search_params;
        fetch(uri, {method: 'GET'})
        .then(response => response.json())
        .then(data => {
            div.innerHTML = ``;
            Plotly.react('histogram', data, {});
            get_svg_for_download();
        })
    }
}

function get_query_parameters() {
    const measurements = get_selected_measurements();
    const numerical_entity = document.getElementById('histogram_numerical_entities_select').value;
    const categorical_entity = document.getElementById('histogram_categorical_entities_select').value;
    const categories = get_categories();
    const number_of_bins = document.getElementById('number_of_bins').value;
    const date_dict = get_date_dict();
    const error = perform_error_handling(measurements, numerical_entity, categorical_entity, categories);
    const query_parameter_string = get_query_parameter_string(measurements, numerical_entity, categorical_entity, categories, number_of_bins, date_dict);
    return {
        search_params: query_parameter_string,
        error: error
    }
}

function get_svg_for_download() {
    const result = get_query_parameters();
    const base_uri = '/plot/histogram/download?';
    const uri = base_uri + result.search_params;
    let div = document.getElementById('histogram_svg_download');
    div.innerHTML = `
        <div class="card-body">
            <a href="${uri}" class="btn btn-outline-info" download="histogram.svg">Download</a>
        </div>
    `;
}

function get_selected_measurements() {
    const parent = document.getElementById('measurement');
    const children = Array.from(parent.childNodes);
    return children.filter((x) => x.selected).map((x) => x.value);
}

function get_categories() {
    const parent = document.getElementById('histogram_subcategory_entities');
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

function perform_error_handling(measurements, numerical_entity, categorical_entity, categories) {
    if (!measurements.length) {
        return "Please select one or more visits";
    } else if (!is_valid_entity(numerical_entity)) {
        return "Please select the numerical entity";
    } else if (!is_valid_entity(categorical_entity)) {
        return "Please select the group_by entity";
    } else if (!categories.length) {
        return "Please select one or more subcategories";
    } else {
        return null;
    }
}

function get_query_parameter_string(measurements, numerical_entity, categorical_entity, categories, number_of_bins, date_dict) {
    return new URLSearchParams({
        histogram_data: JSON.stringify({
            measurements: measurements,
            numerical_entity: numerical_entity,
            categorical_entity: categorical_entity,
            categories: categories,
            bins: number_of_bins,
            date_range: date_dict
        })
    });
}

function is_valid_entity(x){
    return (!!x && x !== '' && x !== 'Search Entity')
}
