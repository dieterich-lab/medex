$(function() {
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
        $('#table').tableToCSV();
    });


    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });





    // pretify the select input for numerical and categorical entities
    $("#visit").select2();
    $("#numeric_entities").select2({
    placeholder:"Search entity"
    });
    $("#categorical_entities").select2({
    placeholder:"Search entity"
    });

    //Plot data
    if ($('#cluster').length != 0) {
        var x_axis = $('#cluster').attr('data-plot-x');
        var y_axis = $('#cluster').attr('data-plot-y');
        var plot_series = $('#cluster').attr('data-plot-series').replace(/'/g, '"'); //")
        plot_series = JSON.parse(plot_series);
        Plotly.newPlot("cluster",
            plot_series,
            {
        title: 'Compare values of <b>' + x_axis +  '</b>',
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