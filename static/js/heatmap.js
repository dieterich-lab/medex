$(function () {
    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });


// pretify the select input for categorical entities
    $("#numeric_entities").select2();

    var heatmap_data = JSON.parse($('#heatmap').attr('data-plot-series').replace(/'/g, '"')); //"));
    if (heatmap_data.length != 0) {
        // delete attribute
        Plotly.newPlot('heatmap',
            heatmap_data,
            {title: 'Heatmap'},);
    }
});