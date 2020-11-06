$(function () {
    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });


    // use plugin select2 for selector
    $("#visit").select2();
    $("#numeric_entities").select2({
    placeholder:"Search entity"
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
            font: {size: 18},
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
});