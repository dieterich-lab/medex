$(function () {
    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });
    $('#Plot').click(function(){
        // disable button
        $(this).html('<span class="spinner-border spinner-border0sm" role="status" aria-hidden="true"></span> Loading ...');

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

    //Plot
    var heatmap_data = JSON.parse($('#heatmap').attr('data-plot-series').replace(/'/g, '"')); //"));
    if (heatmap_data.length != 0) {
        // delete attribute
        Plotly.newPlot('heatmap',
            heatmap_data,
            {height: 1000,
            margin: {
                    l: 270,
                    r: 100,
                    b: 200,
                  },
            font: {size: 16},
            title: 'Heatmap shows Pearson correlation ',annotations: [
            {
              text: 'Rows with missing values have been removed ',
                xref: 'paper',
                yref: 'paper',
                x: 0.15,
                xanchor: 'right',
                y: 1,
                yanchor: 'bottom',
                showarrow: false
            },

          ]},);
            }

    //$("#Plot").click(function(){
    //    $("#second").click();
    //    document.getElementById("form2").submit();
    //});
});