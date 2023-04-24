import {EntityType, get_entity_list} from "../services/entity.mjs";
import {configure_selection} from "./selection.mjs";


const SEARCH_ENTITY_PLACEHOLDER = 'Search Entity';

async function configure_entity_selection(
	element_id: string, selected_entity_ids: string[], multiple_allowed: boolean, allow_select_all: boolean,
	entity_types: EntityType[]
) {
	await render_select_entity_box(element_id, selected_entity_ids, multiple_allowed, entity_types);
	configure_selection(element_id, selected_entity_ids, {
		allowClear: allow_select_all,
		width: "100%",
		multiple: multiple_allowed,
	});
}

async function render_select_entity_box(element_id, selected_entities, multiple_allowed, entity_types) {
    let select_box = document.getElementById(element_id);
    const all_entities = await get_entity_list();
	const prefix = multiple_allowed ? '': `<option>${SEARCH_ENTITY_PLACEHOLDER}</option>`;
	const options_html = all_entities
		.filter((x) => entity_types.includes(x.type))
		.map((x) => {
			const selected_marker = selected_entities.includes(x.key) ? ' selected' : '';
			return `
        	<option value="${x.key}"${selected_marker} data-html="${format_entity(x)}">${x.key}</option>`
		});
    select_box.innerHTML = prefix + options_html.join('') + '\n';
}

function is_valid_entity(name){
	return (!!name && name !== '' && name !== SEARCH_ENTITY_PLACEHOLDER)
}

async function format_entities_for_slim_selelect(entity_types) {
	const all_entities = await get_entity_list();
	return all_entities
		.filter((x) => entity_types.includes(x.type))
		.map((x) => {
			return {
				text: x.key,
				value: x.key,
				html: format_entity(x)
			}
		})
}

function format_entity(entity) {
	if ( !entity ) {
		return `<div>(not loaded yet)</div>`;
	}
	if ( entity.description ) {
		return `
			<div>${entity.key}</div>
			&nbsp;&nbsp;&nbsp;<div class=&quot;description&quot;>${entity.description}</div>`;
	} else {
		return entity.key;
	}
}

export {configure_entity_selection, is_valid_entity};
