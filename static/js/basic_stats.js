$(function () {
    // export table as .xl file
    $('#export_excel').click(function() {
        // find closest parent with the class .card (accordion section)
        // and within the card find a table, which will be exported
        ($(this).closest('.card').find('.table')).table2excel({
            // todo: change the filename
        });
    });
    // export table as .csv file
    $('#export_csv').click(function() {
        // the same: find closest parent with the class .card (accordion section)
        // and within the card find a table, which will be exported
        ($(this).closest('.card').find('.table')).tableToCSV();
    });
    $('#Plot').click(function(){
        // disable button
        $(this).html('<span class="spinner-border spinner-border0sm" role="status" aria-hidden="true"></span> Loading ...');
        //$("#second").click();
        //document.getElementById("form2").submit();

    });
    $('#Plot2').click(function(){
        // disable button
        $(this).html('<span class="spinner-border spinner-border0sm" role="status" aria-hidden="true"></span> Loading ...');
        //        $("#second").click();
        //document.getElementById("form3").submit();

    });

    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

    $('#measurement').on("select2:select", function (e) {
           var data = e.params.data.text;
           if(data=='Select all'){
            $("#measurement> option").prop("selected","selected");
            $("#measurement").trigger("change");
           }
      });

    $('#measurement1').on("select2:select", function (e) {
           var data = e.params.data.text;
           if(data=='Select all'){
            $("#measurement1> option").prop("selected","selected");
            $("#measurement1").trigger("change");
           }
      });

    // use plugin select2 for selector
    $("#measurement").select2({
    placeholder:"Search entity"
    });
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

		$("#numeric_entities").select2({
			ajax:{},
			allowClear:true,
			width:"element",
			multiple:true,
			dataAdapter:CustomData
		});
	});
    $("#measurement1").select2({
    placeholder:"Search entity"
    });
    $("#categorical_entities").select2({
    placeholder:"Search entity"
    });

    //$("#Plot").click(function(){
    //    $("#second").click();
    //    document.getElementById("form2").submit();
    //});

    //    $("#Plot2").click(function(){
    //    $("#second").click();
    //    document.getElementById("form2").submit();
    //});
    submitForms = function(){
        document.getElementById("form1").submit();
        document.getElementById("form2").submit();
    }
});

