import {handle_select_special_choices} from "../utility/misc.js";

let measurement_list_promise = null;
let measurement_list = null;
let measurement_display_name = null;

async function init() {
    if ( ! measurement_list_promise ) {
         measurement_list_promise = fetch('/measurement/', {method: 'GET'})
            .then(response => response.json())
            .then(async measurement_info => {
                const info = await measurement_info;
                measurement_display_name = info['display_name'];
                measurement_list = info['values'];
            })
            .catch(error => {
                console.log(error)
        })
    }
    await measurement_list_promise;
}

async function get_measurement_display_name() {
    await init();
    return measurement_display_name;
}

async function configure_single_measurement_select(id, parent_id, initial_value=null, allow_none=false) {
    const initial_values = initial_value === null ? [] : [initial_value];
    await render_select_html(id, parent_id, false, allow_none);
    add_select2_component(id, initial_values, allow_none);
}

async function render_select_html(id, parent_id, allow_multiple, allow_none) {
    const multiple = allow_multiple ? 'multiple' : '';
    const label = await get_measurement_display_name();
    const measurement_values = await get_measurement_list();
    const display = measurement_values.length > 1 ? 'block' : 'none';
    const options = await get_options(allow_multiple, allow_none);

    document.getElementById(parent_id).innerHTML = `
        <div class="form-group" style="display: ${ display }">
            <label for="${ id }">${ label }:</label>
            <select ${multiple} id="${ id }" style="width: 100%">
                ${ options }
            </select>
        </div>
    `;
}

async function get_options(allow_multiple, allow_none) {
    let options_as_list = [];
    if ( allow_multiple ) {
        options_as_list.push(`
               <option value="Select all">Select all</option>`);
    } else {
        if ( allow_none ) {
            options_as_list.push(`
               <option value="">None</option>`);
        } else {
            options_as_list.push(`
               <option value="" disabled selected>Search entity</option>`);
        }
    }
    const measurement_values = await get_measurement_list();
    options_as_list.push(...measurement_values.map((x) => {
			return `
        	    <option value="${x}">${x}</option>`
    }));
    return options_as_list.join('');
}

function add_select2_component(id, initial_values, allow_none) {
    let element = $(`#${id}`);
    const select2_properties = allow_none ? {} : {placeholder:"Search entity"};
    element.select2(select2_properties);
    element.on("select2:select", (e) => handle_select_special_choices(e, id));
    initial_values.forEach(
        x => $(`#${id} > option[value="${x}"]`).prop("selected", true)
    )
    $(`#${id} > option[value=""]`).prop("selected", false);
    element.trigger("change");
}

async function configure_multiple_measurement_select(id, parent_id, initial_values=null) {
    const cooked_initial_values = initial_values === null ? await get_measurement_list() : initial_values;
    await render_select_html(id, parent_id, true);
    add_select2_component(id, cooked_initial_values, false);
}

async function get_measurement_list() {
    await init();
    return measurement_list;
}

export {init, configure_single_measurement_select, configure_multiple_measurement_select};