$(function() {

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

    if ($('#cluster').length != 0) {
        var x_axis = $('#cluster').attr('data-plot-x');
        var y_axis = $('#cluster').attr('data-plot-y');
        var plot_series = $('#cluster').attr('data-plot-series').replace(/'/g, '"'); //")
        // clean up
        plot_series = JSON.parse(plot_series);
        Plotly.newPlot("cluster",
            plot_series,
            {
        title: 'Compare values of <b>' + x_axis + '</b> and <b>' + y_axis + '</b>',
        xaxis: {
            title: {
                    text: x_axis,
                    }
                },
        yaxis: {
            title: {
                text: y_axis,
                    }
                }
        },);

    }

});