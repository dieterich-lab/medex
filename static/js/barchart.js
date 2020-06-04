$(function () {
    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

// pretify the select input for categorical entities
    $('#categorical_entities').select2();


    var barchart_data = $('#barchart').attr('data-plot-series').replace(/'/g, '"'); //");
    if (barchart_data.length != 0) {
        barchart_data = JSON.parse(barchart_data);
        // delete attribute
        Plotly.newPlot("barchart",
            barchart_data,
            {barmode: 'group'},);
    }



});