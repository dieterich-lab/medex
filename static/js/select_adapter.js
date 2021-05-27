$(function () {


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
						text:elem.innerText
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
		dataAdapter: $.fn.select2.amd.require('select2/data/CustomData')
	});
		$("#numeric_entities_multiple").select2({
		ajax:{},
		allowClear:true,
		width:"element",
		multiple:true,
		dataAdapter:$.fn.select2.amd.require('select2/data/CustomData')
	});

	$(".axis").select2({
		ajax:{},
		allowClear:true,
		width:"element",
		dataAdapter: $.fn.select2.amd.require('select2/data/CustomData')
	});




});