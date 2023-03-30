import {get_entity_list, try_get_entity_by_key} from "../services/entity.mjs";
import {configure_selection} from "./selection.mjs";


const SEARCH_ENTITY_PLACEHOLDER = 'Search Entity';


function format_entity(state) {
	if ( !( 'id' in state ) || state.id == SEARCH_ENTITY_PLACEHOLDER ) {
		return null;
	}
	const entity = try_get_entity_by_key(state.id);
	if ( !entity ) {
		return `<div>(not loaded yet)</div>`;
	}
	if ( entity.description === null ) {
		return $(
			`<div>
				 <div>${entity.key}</div>
			 </div>`
		);
	} else {
		return $(
			`<div>
				 <div>${entity.key}</div>
				 <div class="description">${entity.description}</div>
			 </div>`
		);
	}
}

async function configure_entity_selection(element_id, selected_entity_ids, multiple_allowed, allow_select_all) {
	await render_select_entity_box(element_id, selected_entity_ids, multiple_allowed);
	configure_selection(element_id, selected_entity_ids, {
		allowClear: allow_select_all,
		width: "100%",
		multiple: multiple_allowed,
		templateResult: format_entity,
	});
}

async function render_select_entity_box(element_id, selected_entities, multiple_allowed) {
    let select_box = document.getElementById(element_id);
    const all_entities = await get_entity_list();
	const entity_types = select_box.getAttribute('data-entity-types').split(',');
	const prefix = multiple_allowed ? '': `<option>${SEARCH_ENTITY_PLACEHOLDER}</option>`;
	const options_html = all_entities
		.filter((x) => entity_types.includes(x.type))
		.map((x) => {
			const selected_marker = selected_entities.includes(x.key) ? ' selected' : '';
			return `
        	<option value="${x.key}"${selected_marker}>${x.key}</option>`
		});
    select_box.innerHTML = prefix + options_html.join('') + '\n';
}

function is_valid_entity(name){
	return (!!name && name !== '' && name !== SEARCH_ENTITY_PLACEHOLDER)
}

export {configure_entity_selection, is_valid_entity};
