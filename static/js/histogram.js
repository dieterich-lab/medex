$(function () {

    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

    // use plugin select2 for selector
    $("#numeric_entities").select2();
    $("#categorical_entities").select2();

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
        $cat.html('<option value="all">Select all</option>'+html)
    });



    //Plot histogram
    var histogram_data = $('#histogram_chart').attr('data-plot-series').replace(/'/g, '"'); //");
    var min_val = $('#histogram_chart').attr('data-min-val');
    var max_val = $('#histogram_chart').attr('data-max-val');
    var entity = $('#numeric_entitie').val();
    var count = $('#histogram_chart').attr('count');
    if (histogram_data.length != 0) {
        histogram_data = JSON.parse(histogram_data);
        // delete attribute
        $('#histogram_chart').removeAttr('data-plot-series');
        $('#histogram_chart').removeAttr('data-min-val');
        $('#histogram_chart').removeAttr('data-max-val');
        $('#histogram_chart').removeAttr('count');
        Plotly.newPlot("histogram_chart",
            histogram_data,
            {barmode: "overlay",
                xaxis: {
                    range: [min_val, max_val],
                    title: {
                        text: entity,
                    }
                },
                yaxis: {
                    title: {
                        text: "Number of Patients (Total count: " + count + ")",
                    }
                }
            },);
    }
});

// https://jsfiddle.net/2o8dgsnL/2/
//https://plot.ly/javascript/histograms/#overlaid-histgram