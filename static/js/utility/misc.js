import {report_error, clear_error} from "./error.js";

function handle_select_special_choices(event, element_id) {
    const selected_item = event.params.data.text;
    if (selected_item === 'Select all') {
        $(`#${element_id}> option`).prop("selected", "selected");
        $(`#${element_id}> option[value="Select all"]`).prop("selected", false);
        $(`#${element_id}> option[value=""]`).prop("selected", false);
        $(`#${element_id}`).trigger("change");
    }
    if (selected_item === 'Select none') {
        $(`#${element_id}> option`).prop("selected", false);
        $(`#${element_id}> option[value=""]`).prop("selected", true);
        $(`#${element_id}`).trigger("change");
    }
}

function show_collapsed(element_id) {
    let element = document.getElementById(element_id);
    const old_classes = element.getAttribute('class').split(' ');
    if ( ! old_classes.includes('show') ) {
        const new_classes = old_classes + ['show'];
        element.setAttribute('class', new_classes);
    }
}

function get_selected_items(element_id) {
    const parent = document.getElementById(element_id);
    const children = Array.from(parent.childNodes);
    return children.filter((x) => x.selected).map((x) => x.value);
}

function get_selected_categories() {
    return get_selected_items('subcategory_entities');
}

function get_selected_measurements() {
    return get_selected_items('measurement');
}

function process_fetch(method, uri, process_data) {
    fetch(uri, {'method': method}).then(response => {
        if ( response.ok ) {
            return response.json();
        } else {
            return Promise.reject(response);
        }
    })
    .then(data => {
        clear_error();
        process_data(data);
    })
    .catch(error => {
        const message = ( 'status' in error && 'statusText' in error ) ? `${error.status} ${error.statusText}` : error;
        report_error(`Failed on ${method} ${uri}: ${message}`);
    });
}

function create_download_link(uri, file_name) {
    let div = document.getElementById('download_div');
    div.innerHTML = `
        <div class="card-body">
            <a href="${uri}" class="btn btn-outline-info" download="${file_name}">Download</a>
        </div>
    `;
}

export {
    handle_select_special_choices, show_collapsed,
    get_selected_items, get_selected_measurements, get_selected_categories,
    process_fetch,
    create_download_link
};
