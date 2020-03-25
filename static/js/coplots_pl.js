$(document).ready(function() {

    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

    // apply filters
    $(document).on('change', '#select_scale', function() {
        if(this.checked) {
          $('#scale_values').removeClass('d-none');
        } else {
            $('#scale_values').addClass('d-none');
        }
    });


    var how_to_plot = $('#coplot').attr('data-how-to-plot');
    $('#coplot').removeAttr('data-how-to-plot');
    // for single_plot

    if (how_to_plot == "single_plot") {
        // initializing constants and removing attributes from html elements
        var x_axis = $('#coplot').attr('data-plot-x');
        var y_axis = $('#coplot').attr('data-plot-y');
        var PLOT_SERIES = $('#coplot').attr('data-plot-series2').replace(/'/g, '"'); //");
        if (PLOT_SERIES.length != 0) {
            PLOT_SERIES = JSON.parse(PLOT_SERIES);
            // removing attributes
            Plotly.newPlot('coplot',
            PLOT_SERIES,
            {
            title: 'Compare values of <b>' + x_axis + '</b> and <b>' + y_axis + '</b>',
                    'xaxis': {
                        'title': {
                                'text': x_axis,
                                }
                            },
                    'yaxis': {
                        'title': {
                            'text': y_axis,
                                }
                        },
            },);
            }
    } else { // for multiple plots
        var PLOT_SERIES = $('#coplot').attr('data-plot-series').replace(/'/g, '"'); //");
        var layout = $('#coplot').attr('data-layout').replace(/'/g, '"'); //");
        if (PLOT_SERIES.length != 0) {
            PLOT_SERIES = JSON.parse(PLOT_SERIES);
            layout = JSON.parse(layout);
            Plotly.newPlot('coplot',
            PLOT_SERIES,layout);
            }
        }
});