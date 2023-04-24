import {Entity, EntityType, get_entity_list} from "../services/entity.mjs";
import {configure_selection} from "./selection.mjs";


const SEARCH_ENTITY_PLACEHOLDER = 'Search Entity';

interface DataItem {
	text: string,
	value: string,
	html: string,
}

async function configure_entity_selection(
	element_id: string, selected_entity_ids: string[], multiple_allowed: boolean, allow_select_all: boolean,
	entity_types: EntityType[]
) {
	await render_select_entity_box(element_id, selected_entity_ids, multiple_allowed, entity_types);
	const settings = {
		allowClear: allow_select_all,
		width: "100%",
		multiple: multiple_allowed
	};
	const events = {
		search: (search_string, custome_data) => custom_search(search_string, custome_data, entity_types)
	};
	configure_selection(element_id, selected_entity_ids, settings, events);
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
        	<option value="${x.key}"${selected_marker} data-html="${format_entity(x, true)}">${x.key}</option>`
		});
    select_box.innerHTML = prefix + options_html.join('') + '\n';
}

function is_valid_entity(name){
	return (!!name && name !== '' && name !== SEARCH_ENTITY_PLACEHOLDER)
}

function get_data_item_from_entity(entity: Entity, quote_quotes: boolean): DataItem {
	return {
		text: entity.key,
		value: entity.key,
		html: format_entity(entity, quote_quotes),
	}
}

function format_entity(entity, quote_quotes: boolean) {
	const quote = quote_quotes ? '&quot;' : '"';
	if ( !entity ) {
		return `<div>(not loaded yet)</div>`;
	}
	if ( entity.description ) {
		return `
			<div class=${quote}option_container=${quote}>
			${entity.key}
			&nbsp;&nbsp;&nbsp;<span class=${quote}option_description${quote}>${entity.description}</span>
			</div>`;
	} else {
		return entity.key;
	}
}

async function custom_search(
	search_sting: string, current_data: DataItem[], entity_types: EntityType[]
): Promise<DataItem[]> {
	const already_selected_entities = current_data.map((item) => item.value);
	const all_entities = await get_entity_list();
	const lower_case_search_string = search_sting.toLowerCase();
	return all_entities
		.filter((x) => entity_types.includes(x.type))
		.filter((x) => !already_selected_entities.includes(x.key))
		.filter((x) => matches_entity(lower_case_search_string, x))
		.map((x) => get_data_item_from_entity(x, false));
}

function matches_entity(search_string: string, entity: Entity): boolean {
	return entity.key.toLowerCase().includes(search_string)
		|| entity.description.toLowerCase().includes(search_string);
}

export {configure_entity_selection, is_valid_entity};
