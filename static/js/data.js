$(function () {


    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });
    $('#Plot').click(function(){
        // disable button
        $(this).html('<span class="spinner-border spinner-border0sm" role="status" aria-hidden="true"></span> Loading ...');

        });



    // handling select all choice
    //$('#entities').on("select2:select", function (e) {
    //       var data = e.params.data.text;
    //       if(data=='Select all'){
    //        $("#entities> option").prop("selected","selected");
    //        $('#entities> option[value="Select all"]').prop("selected", false);
    //        $("#entities ").trigger("change");
    //       }
    //  });


    $.fn.select2.amd.require(
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

		$("#entities").select2({
			ajax:{},
			allowClear:true,
			width:"element",
			multiple:true,
			dataAdapter:CustomData
		});
	});


    var column = JSON.parse($('#tab').attr('column').replace(/'/g, '"')); //"));
    $('#serverside_table').DataTable({
    bProcessing: true,
    bServerSide: true,
    scrollX: true,
    sPaginationType: "full_numbers",
    lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
    bjQueryUI: true,
    sAjaxSource: '/data/data1',
    columns: column
  });



});