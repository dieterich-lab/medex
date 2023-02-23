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

export {handle_select_special_choices};