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

export {handle_select_special_choices, show_collapsed};
