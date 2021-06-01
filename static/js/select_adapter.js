$(function () {


function matchCustom(params, data) {
    // If there are no search terms, return all of the data
    if ($.trim(params.term) === '') {
        return data;
    }
    // Do not display the item if there is no 'text' property
    if (typeof data.text === 'undefined') {
        return null;
    }
    // Match text of option
    if (stringMatch(params.term, data.text)) {
        return data;
    }
    // Match attribute "data-foo" of option
    if (stringMatch(params.term, $(data.element).attr('data-foo'))) {
        return data;
    }
    // Return `null` if the term should not be displayed
    return null;
}
function formatCustom(state) {
    return $(
        '<div><div>' + state.text + '</div><div class="foo">'
            + state.value
            + '</div></div>'
    );
    }

 $.fn.select2.amd.define('select2/data/CustomData',
	['select2/data/array', 'select2/utils'],
	function (ArrayData, Utils) {
		function CustomData($element, options) {
			CustomData.__super__.constructor.call(this, $element, options);
		}

		function contains(str1, str2) {
			return new RegExp(str2, "i").test(str1);
		}

		Utils.Extend(CustomData, ArrayData);

		CustomData.prototype.query = function (params, callback) {
			if (!("page" in params)) {
				params.page = 1;
			}
			var pageSize = 20;
			var results = this.$element.children().map(function(i, elem) {
				if (contains(elem.innerText, params.term)) {
					return {

						id:[elem.innerText].join(""),
						text:  elem.innerText ,
						value: elem.getAttribute('data')
					};
				}
				if (contains(elem.getAttribute('data'), params.term)) {
					return {

						id:[elem.innerText].join(""),
						text:  elem.innerText ,
						value: elem.getAttribute('data')
					};
				}
			});
			callback({
				results:results.slice((params.page - 1) * pageSize, params.page * pageSize),
				pagination:{
					more:results.length >= params.page * pageSize
				}
			});
		};


        return CustomData;
	});

	$("#entities").select2({
		ajax:{},
		allowClear:true,
		width:"element",
		multiple:true,
		dataAdapter:$.fn.select2.amd.require('select2/data/CustomData'),
		templateResult: formatCustom,
	});
		$("#numeric_entities_multiple").select2({
		ajax:{},
		allowClear:true,
		width:"element",
		multiple:true,
		dataAdapter:$.fn.select2.amd.require('select2/data/CustomData'),
		templateResult: formatCustom,
	});

	$(".axis").select2({
		ajax:{},
		allowClear:true,
		width:"element",
		dataAdapter: $.fn.select2.amd.require('select2/data/CustomData'),
		templateResult: formatCustom,
	});




});