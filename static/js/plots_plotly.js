$(function () {

    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });


    // use plugin select2 for selector

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

		$("#x_axis").select2({
			ajax:{},
			allowClear:true,
			width:"element",
			dataAdapter:CustomData
		});
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

		$("#y_axis").select2({
			ajax:{},
			allowClear:true,
			width:"element",
			dataAdapter:CustomData
		});
	});
    $("#x_measurement").select2({
    placeholder:"Search entity"
    });
    $("#y_measurement").select2({
    placeholder:"Search entity"
    });
    $("#categorical_entities").select2({
    placeholder:"Search entity"
    });

    $('#Plot').click(function(){
        // disable button
        $(this).html('<span class="spinner-border spinner-border0sm" role="status" aria-hidden="true"></span> Loading ...');

        });
    // apply filters for add group by
    $(document).on('change', '#add_group_by', function() {
        if(this.checked == false) {
          $('#add_group').addClass('d-none');
        } else {
            $('#add_group').removeClass('d-none');
        }
    });

    // hide choice scale for x and y axis
    $("#log2").hide();

    // show choice for log scale for x and y axis if we choose log
    $(document).on('change', '#log', function() {
        if(this.checked == false) {
          $("#log2").hide();
        } else {
            $("#log2").show();
        }
    });
    // hide choice scale for x and y axis if we choose linear
    $(document).on('change', '#linear', function() {
        if(this.checked == false) {
          $("#log2").show();
        } else {
            $("#log2").hide();
        }
    });

    // initiate value for subcategory selector
    var $cat = $('#subcategory_entities').select2({
    placeholder:"Search entity"
    });

    // handling select all choice
    $('#subcategory_entities').on("select2:select", function (e) {
           var data = e.params.data.text;
           if(data=='Select all'){
            $("#subcategory_entities> option").prop("selected","selected");
            $("#subcategory_entities").trigger("change");
           }
      });
    //change subcategories if category change
    $('#categorical_entities').change(function () {
        var entity =$(this).val(), values = cat[entity] || [];

        var html = $.map(values, function(value){
            return '<option value="' + value + '">' + value + '</option>'
        }).join('');
        $cat.html('<option value="Select all">Select all</option>'+html)
    });

    //$("#Plot").click(function(){
    //    $("#second").click();
    //    document.getElementById("form2").submit();
    //});

});

