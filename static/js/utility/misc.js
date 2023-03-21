import {report_error, clear_error, UserError, HTTPError} from "./error.js";

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
        const annotation = `Failed on ${method} ${uri}:`;
        handle_fetch_error(error, annotation);

    });
}

function handle_fetch_error(error, annotation) {
    if ( error instanceof UserError ) {
        report_error(error);
        return;
    }
    if ( 'status' in error && 'statusText' in error ) {
        report_error(new HTTPError(`${annotation} ${error.status} ${error.statusText}`));
        return;
    }
    if ( error instanceof Error ) {
        error.message = `${annotation} ${error.message}`;
        report_error(error);
        return;
    }
    report_error(`${annotation} ${error}`);
}

const DOWNLOAD_DIV_ID = 'download_div';

function create_download_link(uri, file_name) {
    let div = document.getElementById(DOWNLOAD_DIV_ID);
    div.innerHTML = `
        <div class="card-body">
            <a href="${uri}" class="btn btn-outline-info" download="${file_name}">Download</a>
        </div>
    `;
}

function remove_download_link() {
    let div = document.getElementById(DOWNLOAD_DIV_ID);
    div.innerHTML = '';
}

export {
    handle_select_special_choices, show_collapsed,
    get_selected_items, get_selected_measurements, get_selected_categories,
    process_fetch,
    create_download_link, remove_download_link, DOWNLOAD_DIV_ID
};
