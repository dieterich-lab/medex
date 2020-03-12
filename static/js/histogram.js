$(function () {
    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

    var histogram_data = $('#histogram_chart').attr('data-plot-series').replace(/'/g, '"'); //");
    var min_val = $('#histogram_chart').attr('data-min-val');
    var max_val = $('#histogram_chart').attr('data-max-val');
    var entity = $('#entity').val();
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