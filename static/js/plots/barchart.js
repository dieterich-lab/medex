function display_barchart() {
    const result = get_search_parameters();
    let div = document.getElementById('error_barchart');
    if (!!result.error) {
        div.innerHTML = `
            <div class="alert alert-danger mt-2" role="alert">
                ${result.error}
                <span class="close" aria-label="Close"> &times;</span>
            </div>
        `;
    } else {
        const uri = '/plot/barchart/json?' + result.search_params;
        fetch(uri, {method: 'GET'})
        .then(response => response.json())
        .then(data => {
            div.innerHTML = ``;
            Plotly.react('barchart', data, {});
            get_svg_download();
        })
    }
}

function get_svg_download() {
    const result = get_search_parameters();
    const base_uri = '/plot/barchart/download?';
    const uri = base_uri + result.search_params;
    let div = document.getElementById('barchart_svg_download');
    div.innerHTML = `
        <div class="card-body">
            <a href="${uri}" class="btn btn-outline-info" download="barchart.svg">Download</a>
        </div>
    `;
}

function get_search_parameters() {
    const measurements = get_selected_measurements();
    const entity = document.getElementById('barchart_categorical_entities_select').value;
    const categories = get_categories();
    const plot_type = get_plot_type();
    const date_dict = get_date_dict();
    const search_parameter_string = get_search_parameter_string(measurements, entity, categories, date_dict, plot_type);
    const error = perform_error_handling(measurements, entity, categories)
    return {
        search_params: search_parameter_string,
        error: error
    }
}

function get_selected_measurements() {
    const parent = document.getElementById('measurement');
    const children = Array.from(parent.childNodes);
    return children.filter((x) => x.selected).map((x) => x.value);
}

function get_categories() {
    const parent = document.getElementById('subcategory_entities');
    const children = Array.from(parent.childNodes);
    return children.filter((x) => x.selected).map((x) => x.value);
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

function get_date_dict() {
    const date = document.getElementById('Date').value;
    const date_string = date.split(' - ');
    return {
        from_date: moment(date_string[0], 'MM/DD/YYYY').format('YYYY-MM-DD'),
        to_date: moment(date_string[1], 'MM/DD/YYYY').format('YYYY-MM-DD')
    }
}

function perform_error_handling(measurements, entity, categories) {
    if (!measurements.length) {
        return "Please select one or more visits";
    } else if (!is_valid_entity(entity)) {
        return "Please select the group_by entity";
    } else if (!categories.length) {
        return "Please select one or more subcategories";
    } else {
        return null;
    }
}
function get_search_parameter_string(measurements, entity, categories, date_dict, plot_type) {
    return new URLSearchParams({
        barchart_data: JSON.stringify({
            measurements: measurements,
            key: entity,
            categories: categories,
            plot_type: plot_type,
            date_range: date_dict
        })
    });
}

function is_valid_entity(x){
    return (!!x && x !== '' && x !== 'Search Entity')
}

