import {get_selected_categories, get_selected_measurements} from "../utility.js";

function display() {
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
        const uri = '/barchart/json?' + result.search_params;
        fetch(uri, {method: 'GET'})
        .then(response => response.json())
        .then(data => {
            div.innerHTML = ``;
            if (data.data.length === 0) {
                alert('No Matching Data Found to Display');
                console.log('No matching records available in the database');
            }
            else {
                Plotly.react('barchart', data, {});
                get_svg_download();
            }
        })
    }
}

function get_svg_download() {
    const result = get_search_parameters();
    const base_uri = '/barchart/download?';
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
    const categories = get_selected_categories();
    const plot_type = get_plot_type();
    const search_parameter_string = get_search_parameter_string(measurements, entity, categories, plot_type);
    const error = perform_error_handling(measurements, entity, categories)
    return {
        search_params: search_parameter_string,
        error: error
    }
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

export {display};
