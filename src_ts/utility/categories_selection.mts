import $ from 'jquery';
import {get_entity_by_key} from "../services/entity.mjs";
import {get_input_value_by_id} from "./dom.mjs";
import {configure_selection, get_select_box_by_element_id} from "./selection.mjs";

const CATEGORICAL_ENTITY_PLACEHOLDER = {
    key: 'x',
    categories: [],
};

function configure_category_selection(element_id, categorical_entity=null, entity_selection_id=null) {
    const cooked_entity = categorical_entity ? categorical_entity : CATEGORICAL_ENTITY_PLACEHOLDER;
    render_categories_select(element_id, cooked_entity);
    configure_selection(element_id);
    if ( entity_selection_id ) {
        attach_on_change_handler_on_parent_element(element_id, entity_selection_id);
    }
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
        const entity_key = get_input_value_by_id(entity_selection_id);
        const categorical_entity = entity_key ? await get_entity_by_key(entity_key) : CATEGORICAL_ENTITY_PLACEHOLDER;
        let old_select_box = get_select_box_by_element_id(element_id);
        if ( old_select_box ) {
            old_select_box.destroy();
        }
        configure_category_selection(element_id, categorical_entity)
    });
}

export {configure_category_selection};
