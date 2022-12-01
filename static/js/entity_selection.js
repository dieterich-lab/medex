import {get_entity_by_key, get_entity_list} from "./entity";


function formatCustom(state) {
	const entity = get_entity_by_key(state.value);
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
	if ( ! entity['type'] in valid_entity_types ) {
		return false;
	}
	return contains(entity['key'], search_string)
		|| contains(entity['description'], search_string);
}

$.fn.select2.amd.define('select2/data/CustomData',
	['select2/data/array', 'select2/utils'],
	function (ArrayData, Utils) {
		function CustomData($element, options) {
			CustomData.__super__.constructor.call(this, $element, options);
		}

		Utils.Extend(CustomData, ArrayData);

		CustomData.prototype.query = function (params, callback) {
			params.page = params.page || 1;
			const page_size = 20;
			const entity_list = get_entity_list();
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
			});

			const first_index = (params.page - 1) * page_size;
			const next_page_index = params.page * page_size;
			const more_pages = results.length >= params.page * page_size;
			const result_page = results.slice(first_index, next_page_index);
			callback({
				results: result_page,
				pagination: {more: more_pages}
			});
		};

        return CustomData;
});

function configure_entity_selection(element_id, multiple_allowed, allow_select_all) {
	let select2_parameters = {
		ajax:{},
		allowClear: allow_select_all,
		width: "element",
		multiple: multiple_allowed,
		dataAdapter:$.fn.select2.amd.require('select2/data/CustomData'),
		templateResult: formatCustom,
	};

	$(`#${element_id}`).select2(select2_parameters);
}




export {configure_entity_selection};