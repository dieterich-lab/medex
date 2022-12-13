import {try_get_entity_list, get_entity_list, try_get_entity_by_key} from "./entity.js";


function format_entity(state) {
	const entity = try_get_entity_by_key(state.value);
	if ( !entity ) {
		return `<div>(not loaded yet)</div>`;
	}
    return $(
		`<div>
			 <div>${entity.key}</div>
			 <div class="description">${entity.description}</div>
		 </div>`
    );
}

function contains(text, search_string) {
	return text.toLowerCase().includes(search_string.toLowerCase());
}

function is_valid_entity(entity, valid_entity_types, search_string) {
	if ( ! valid_entity_types.includes(entity['type']) ) {
		return false;
	}
	if ( !search_string ) {
		return true;
	}
	return contains(entity['key'], search_string)
		|| contains(entity['description'], search_string);
}

$.fn.select2.amd.define('select2/data/EntityData',
	['select2/data/array', 'select2/utils'],
	function (ArrayData, Utils) {
		function EntityData($element, options) {
			EntityData.__super__.constructor.call(this, $element, options);
		}

		Utils.Extend(EntityData, ArrayData);

		EntityData.prototype.query = function (params, callback) {
			params.page = params.page || 1;
			const page_size = 20;
			const entity_list = try_get_entity_list();
			const entity_types = this.$element.attr('data-entity-types').split(',');
			const results = entity_list.map( (x) => {
				if (is_valid_entity(x, entity_types, params.term)) {
					return {
						id: x['key'],
						text: x['key'],
						value: x['key'],
					}
				} else {
					return null;
				}
			}).filter( (x) => x != null);

			const first_index = (params.page - 1) * page_size;
			const next_page_index = params.page * page_size;
			const more_pages = results.length >= params.page * page_size;
			const result_page = results.slice(first_index, next_page_index);
			callback({
				results: result_page,
				pagination: {more: more_pages}
			});
		};

        return EntityData;
});

async function configure_entity_selection(element_id, selected_entity_ids, multiple_allowed, allow_select_all) {
	if ( ! document.getElementById(element_id) ) {
		return;
	}
	await render_select_entity_box(element_id, selected_entity_ids);
	const select2_parameters = {
		ajax:{},
		allowClear: allow_select_all,
		width: "100%",
		multiple: multiple_allowed,
		dataAdapter:$.fn.select2.amd.require('select2/data/EntityData'),
		templateResult: format_entity,
	};
	$(`#${element_id}`).select2(select2_parameters);
}

async function render_select_entity_box(element_id, selected_entities, multiple_allowed) {
    let select_box = document.getElementById(element_id);
    const all_entities = await get_entity_list();
	const entity_types = select_box.getAttribute('data-entity-types').split(',');
	const prefix = multiple_allowed ? '': '<option>Search Entity</option>';
	const options_html = all_entities
		.filter((x) => entity_types.includes(x.type))
		.map((x) => {
			const selected_marker = selected_entities.includes(x.key) ? ' selected' : '';
			return `
        	<option value="${x.key}"${selected_marker}>${get_entity_display_name(x)}</option>`
		});
    select_box.innerHTML = prefix + options_html.join('') + '\n';
}

function get_entity_display_name(entity) {
    if ( entity.description ) {
        return `${entity.key} <div class="description">${entity.description}</div>`;
    } else {
        return entity.key;
    }
}

export {configure_entity_selection};
