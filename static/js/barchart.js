$(function () {
    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

// pretify the select input for categorical entities
    var c_choices = new Choices('#categorical_entities', {
        allowSearch: true,
        removeItemButton: true,
    });

    // pretify the select input for numeric entities
    var n_choices = new Choices('#numeric_entities', {
        allowSearch: true,
        removeItemButton: true,
        shouldSort: false,
    });

    var barchart_data = $('#barchart').attr('data-plot-series').replace(/'/g, '"'); //");
    if (barchart_data.length != 0) {
        barchart_data = JSON.parse(barchart_data);
        // delete attribute
        Plotly.newPlot("barchart",
            barchart_data,
            {barmode: 'group'},);
    }



});