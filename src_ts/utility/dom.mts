
function set_input_element_by_id(id: string, value: string) {
    (document.getElementById(id) as HTMLInputElement).value = value;
}

function get_input_value_by_id(id: string): string {
    return (document.getElementById(id) as HTMLInputElement).value;
}

function get_input_number_by_id(id: string): number {
    return parseFloat(
        get_input_value_by_id(id)
    );
}

function get_input_elements_by_query(query: string): HTMLInputElement[] {
     return Array.from(document.querySelectorAll(query));
}

function get_radio_input_by_name(name: string): string {
    const all_elements = get_input_elements_by_query(`input[name="${name}"]`);
    for ( const element of all_elements) {
        if ( element.checked ) {
            return element.value
        }
    }
}

function get_selected_child_values_by_id(id: string): string[] {
    const parent = document.getElementById(id);
    const children = Array.from(parent.childNodes) as HTMLOptionElement[];
    return children
        .filter(x => x.selected)
        .map((x) => x.value);
}

function is_checked_by_id(id: string): boolean {
    return (document.getElementById(id) as HTMLInputElement).checked;
}

export {
    set_input_element_by_id, get_input_value_by_id, get_input_number_by_id,
    get_radio_input_by_name, get_selected_child_values_by_id, is_checked_by_id
};
