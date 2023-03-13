import {get_selected_categories, get_selected_measurements} from "../utility.js";

function display() {
    const result = get_query_parameters();
    let div = document.getElementById('error_boxplot');
    if (!!result.error) {
        div.innerHTML = `
            <div class="alert alert-danger mt-2" role="alert">
                ${result.error}
                <span class="close" aria-label="Close"> &times;</span>
            </div>
        `;
    } else {
        const uri = '/boxplot/json?' + result.search_params;
        fetch(uri, {method: 'GET'})
        .then(response => response.json())
        .then(data => {
            div.innerHTML = ``;
            if (data.image_json.data.length === 0) {
                alert('No Matching Data Found to Display');
                console.log('No matching records available in the database');
            }
            else {
                Plotly.react('boxplot_table', data.table_json, {});
                Plotly.react('boxplot', data.image_json, {});
                get_svg_for_download();
            }
        })
    }
}

function get_query_parameters() {
    const measurements = get_selected_measurements();
    const numerical_entity = document.getElementById('boxplot_numerical_entities_select').value;
    const categorical_entity = document.getElementById('boxplot_categorical_entities_select').value;
    const categories = get_selected_categories();
    const plot_type = get_plot_type();
    const query_parameter_string = get_parameter_string(measurements, numerical_entity, categorical_entity, categories, plot_type);
    const error = perform_error_handling(measurements, numerical_entity, categorical_entity, categories);
    return {
        search_params: query_parameter_string,
        error: error
    }
}

function get_svg_for_download() {
    const result = get_query_parameters();
    const base_uri = '/boxplot/download?';
    const uri = base_uri + result.search_params;
    let div = document.getElementById('boxplot_svg_download');
    div.innerHTML = `
        <div class="card-body">
            <a href="${uri}" class="btn btn-outline-info" download="boxplot.svg">Download</a>
        </div>
    `;
}

function get_plot_type() {
    const all_plot_types = document.querySelectorAll('input[name="plot_type_boxplot"]');
    let plot_type;
    for (const selected_type of all_plot_types) {
        if (selected_type.checked) {
            plot_type = selected_type.value;
        }
    }
    return plot_type
}

function get_parameter_string(measurements, numerical_entity, categorical_entity, categories, plot_type) {
    return new URLSearchParams({
        boxplot_data: JSON.stringify({
            measurements: measurements,
            numerical_entity: numerical_entity,
            categorical_entity: categorical_entity,
            categories: categories,
            plot_type: plot_type,
        })
    });
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

function is_valid_entity(x){
    return (!!x && x !== '' && x !== 'Search Entity')
}

export{display};
