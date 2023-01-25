import {configure_entity_selection} from "./entity_selection.js";
import {configure_category_selection} from "./categories_selection.js";
import {get_entity_by_key} from "./entity.js";

const entity_placeholder = {
    key: 'x',
    categories: [],
};

async function init() {
    await configure_entity_selection(
        'scatter_plot_x_axis_numerical_entities_select', window.selected_numerical_entities,
        false, false
    );
    await configure_entity_selection(
        'scatter_plot_y_axis_numerical_entities_select', window.selected_numerical_entities,
        false, false
    );
    await configure_entity_selection(
        'scatter_plot_categorical_entities_select', [],
        false, false
    );
    configure_category_selection('subcategory_entities', entity_placeholder);
    document.getElementById('scatter_plot_categorical_entities_select').onchange = (async () => {
        let element = document.getElementById('scatter_plot_categorical_entities_select');
        const entity_key = element.value;
        const categorical_entity = entity_key ? await get_entity_by_key(entity_key) : entity_placeholder;
        configure_category_selection('subcategory_entities', categorical_entity)
    });
}

document.addEventListener("DOMContentLoaded", init);