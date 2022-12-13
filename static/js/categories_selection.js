import {handle_select_all_choices} from "./utility.js";

function configure_category_selection(element_id, categorical_entity) {
    render_categories_select(element_id, categorical_entity);
    let cat_select = $(`#${element_id}`);
    cat_select.select2({
        placeholder:"Search entity",
    });
    cat_select.on("select2:select", (e) => handle_select_all_choices(e, element_id));
}

function render_categories_select(element_id, categorical_entity) {
    let select_categories = document.getElementById(element_id);
    select_categories.innerHTML = `
        <option value="Select all">Select all</option>`
        + categorical_entity.categories.map( x => `
        <option value="${x}">${x}</option>`
    ) + '\n';
    $(`#${element_id}`).trigger("change");
}

export {configure_category_selection};
