import SlimSelect from 'slim-select';
import '../../node_modules/slim-select/dist/slimselect.css';

const SEARCH_ENTITY_PLACEHOLDER = 'Search Entity';
const SELECT_ALL = 'Select all';
const SELECT_NONE = 'Select none';

const SPECIAL_OPTIONS = [
    SEARCH_ENTITY_PLACEHOLDER,
    SELECT_ALL,
    SELECT_NONE,
    ''
]

const DEFAULT_SETTINGS = {
    placeholder: SEARCH_ENTITY_PLACEHOLDER,
};

interface HTMLElementWithOptionalSlimSelect extends HTMLHtmlElement{
    slim?: SlimSelect,
}

function configure_selection(id: string, initial_values: string[]|null = [], settings: object = DEFAULT_SETTINGS) {
    const all_normal_values = get_all_normal_values(id);
    let select_box = new SlimSelect({
        select: `#${id}`,
        events: {
            afterChange: (new_values) => handle_select_special_choices(select_box, id, new_values, all_normal_values)
        }
    });
    select_box.setSelected(initial_values);
    return select_box;
}

function get_all_normal_values(id: string): string[] {
    let values = [];
    with_children(id, (option) => {
        if ( ! (SPECIAL_OPTIONS.includes(option.value))) {
            values.push(option.value)
        }
    });
    return values;
}

function with_children(id, handler: (HTMLOptionElement) => void) {
    let element = document.getElementById(id);
    for ( let option  of Array.from(element.children) as HTMLOptionElement[] ) {
        handler(option);
    }
}

function handle_select_special_choices(select_box, element_id, new_options, all_normal_values) {
    const selected_values = get_selected_values(element_id);
    if ( selected_values.includes(SELECT_ALL) ) {
        select_box.setSelected(all_normal_values);
    }
    if ( selected_values.includes(SELECT_NONE)) {
        select_box.setSelected([]);
    }
}

function get_selected_values(id) {
    let values = [];
    with_children(id, (option) => {
        if ( option.selected ) {
            values.push(option.value)
        }
    });
    return values;
}

function get_select_box_by_element_id(id): SlimSelect|null {
    const element = document.getElementById(id) as HTMLElementWithOptionalSlimSelect;
    return element?.slim;
}

export {configure_selection, get_select_box_by_element_id, SEARCH_ENTITY_PLACEHOLDER, DEFAULT_SETTINGS};