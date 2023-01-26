function display_scatter_plot() {
    const result = get_search_params();
    let div = document.getElementById('error_scatter_plot');
    if (!!result.error) {
        div.innerHTML = `
            <div class="alert alert-danger mt-2" role="alert">
                ${result.error}
                <span class="close" aria-label="Close"> &times;</span>
            </div>
        `;
    } else {
        const uri = '/plot/scatter_plot/json?' + result.search_params;
        fetch(uri, {method: 'GET'})
        .then(response => response.json())
        .then(data => {
            div.innerHTML = ``;
            Plotly.react('scatter_plot', data, {});
            get_svg_download();
        })
    }
}

function get_svg_download() {
    const result = get_search_params();
    const base_uri = '/plot/scatter_plot/download?';
    const uri = base_uri + result.search_params;
    let div = document.getElementById('svg_download');
    div.innerHTML = `
        <div class="card-body">
            <a href="${uri}" class="btn btn-outline-info" download="scatter_plot.svg">Download</a>
        </div>
    `;
}

function get_search_params() {
    const measurement_x_axis = document.getElementById('x_measurement').value;
    const entity_x_axis = document.getElementById('scatter_plot_x_axis_numerical_entities_select').value;
    const measurement_y_axis = document.getElementById('y_measurement').value;
    const entity_y_axis = document.getElementById('scatter_plot_y_axis_numerical_entities_select').value;
    const date_dict = get_date_dict();
    const scale = get_scale_type();
    const add_group_by = get_group_by_data();
    const error = perform_error_handling(entity_x_axis, entity_y_axis, add_group_by, measurement_x_axis, measurement_y_axis);
    const search_parameter_string = get_parameter_string(measurement_x_axis, entity_x_axis, measurement_y_axis, entity_y_axis,
                                                        date_dict, scale, add_group_by);
    return {
        search_params: search_parameter_string,
        error: error
    }
}

function get_date_dict() {
    const date = document.getElementById('Date').value;
    const date_string = date.split(' - ');
    return {
        from_date: moment(date_string[0], 'MM/DD/YYYY').format('YYYY-MM-DD'),
        to_date: moment(date_string[1], 'MM/DD/YYYY').format('YYYY-MM-DD')
    }
}

function get_scale_type() {
    return {
        log_x: !!document.querySelector('input[name="log_x"]').checked,
        log_y: !!document.querySelector('input[name="log_y"]').checked
    };
}

function get_group_by_data() {
    let add_group_by;
    if (document.querySelector('input[name="add_group_by"]').checked) {
        add_group_by = {
            key: document.getElementById('scatter_plot_categorical_entities_select').value,
            categories: get_categories()
        };
    }
    return add_group_by;
}

function get_categories() {
    const parent = document.getElementById('subcategory_entities');
    const children = Array.from(parent.childNodes);
    return children.filter((x) => x.selected).map((x) => x.value);
}

function perform_error_handling(entity_x_axis, entity_y_axis, add_group_by, measurement_x_axis, measurement_y_axis) {
    let group_by = !!document.querySelector('input[name="add_group_by"]').checked;
    if (!is_valid_entity(entity_x_axis)) {
        return "Please select x_axis";
    } else if (!is_valid_entity(entity_y_axis)) {
        return "Please select y_axis";
    } else if (entity_x_axis === entity_y_axis && measurement_x_axis === measurement_y_axis) {
        return "You can't compare same entity for the same visit";
    } else if (group_by && !is_valid_entity(add_group_by.key)) {
        return "Please select 'group by' entity";
    } else if (group_by && !add_group_by.categories.length) {
        return "Please select subcategory";
    } else {
        return null;
    }
}

function get_parameter_string(measurement_x_axis, entity_x_axis, measurement_y_axis, entity_y_axis, date_dict, scale, add_group_by) {
    return new URLSearchParams({
        scatter_plot_data: JSON.stringify({
            measurement_x_axis: measurement_x_axis,
            entity_x_axis: entity_x_axis,
            measurement_y_axis: measurement_y_axis,
            entity_y_axis: entity_y_axis,
            date_range: date_dict,
            scale: scale,
            add_group_by: add_group_by
        })
    });
}


function is_valid_entity(x){
    return (!!x && x !== '' && x !== 'Search Entity')
}
