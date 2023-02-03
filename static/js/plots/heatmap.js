function display_heatmap_plot() {
    const result = get_query_parameter_string()
    let div = document.getElementById('error_heatmap');
    if (!!result.error) {
        div.innerHTML = `
            <div class="alert alert-danger mt-2" role="alert">
                ${result.error}
                <span class="close" aria-label="Close"> &times;</span>
            </div>
        `;
    } else {
        const uri = '/plot/heatmap/json?' + result.search_params;
        fetch(uri, {method: 'GET'})
        .then(response => response.json())
        .then(data => {
            div.innerHTML = ``;
            Plotly.react('heatmap', data, {});
            get_svg_download();
        })
    }
}

function get_svg_download() {
    const result = get_query_parameter_string();
    const base_uri = '/plot/heatmap/download?';
    const uri = base_uri + result.search_params;
    let div = document.getElementById('heatmap_svg_download');
    div.innerHTML = `
        <div class="card-body">
            <a href="${uri}" class="btn btn-outline-info" download="heatmap.svg">Download</a>
        </div>
    `;
}

function get_query_parameter_string() {
    const entities = get_entities_list()
    const date_dict = get_date_dict();
    const query_string = new URLSearchParams({
        heatmap_data: JSON.stringify({
            entities: entities,
            date_range: date_dict
        })
    });
    const error = perform_error_handling(entities)
    return {
        search_params: query_string,
        error: error
    }
}

function get_entities_list() {
    const parent = document.getElementById('heatmap_numerical_entities_select');
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

function perform_error_handling(entities) {
    if (entities.length < 2) {
        return 'Please select two or more numeric entities'
    }
}