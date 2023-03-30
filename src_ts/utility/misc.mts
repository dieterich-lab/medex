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
    if ( ! element.classList.contains('show') ) {
        element.classList.add('show');
    }
}

function get_selected_items(element_id) {
    const parent = document.getElementById(element_id);
    const children = Array.from(parent.childNodes) as HTMLOptionElement[];
    return children.filter((x) => x.selected).map((x) => x.value);
}

function get_selected_categories() {
    return get_selected_items('subcategory_entities');
}

function get_selected_measurements() {
    return get_selected_items('measurement');
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
    create_download_link, remove_download_link, DOWNLOAD_DIV_ID
};
