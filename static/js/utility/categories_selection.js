import {handle_select_special_choices} from "./misc.js";
import {get_entity_by_key} from "../services/entity.js";

const CATEGORICAL_ENTITY_PLACEHOLDER = {
    key: 'x',
    categories: [],
};

function configure_category_selection(element_id, categorical_entity=null, entity_selection_id=null) {
    const cooked_entity = categorical_entity ? categorical_entity : CATEGORICAL_ENTITY_PLACEHOLDER;
    setup_category_selection(element_id, cooked_entity);
    if ( entity_selection_id ) {
        attach_on_change_handler_on_parent_element(element_id, entity_selection_id);
    }
}

function setup_category_selection(element_id, categorical_entity) {
    render_categories_select(element_id, categorical_entity);
    let cat_select = $(`#${element_id}`);
    cat_select.select2({
        placeholder:"Search entity",
    });
    cat_select.on("select2:select", (e) => handle_select_special_choices(e, element_id));
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

function attach_on_change_handler_on_parent_element(element_id, entity_selection_id) {
    document.getElementById(entity_selection_id).onchange = ( async () => {
        let element = document.getElementById(entity_selection_id);
        const entity_key = element.value;
        const categorical_entity = entity_key ? await get_entity_by_key(entity_key) : CATEGORICAL_ENTITY_PLACEHOLDER;
        configure_category_selection(element_id, categorical_entity)
    });
}

export {configure_category_selection};
