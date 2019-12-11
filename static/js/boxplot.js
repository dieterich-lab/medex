$(function () {
    var boxplot_data = $('#boxplot_chart').attr('data-plot-series').replace(/'/g, '"'); //");
    var min_val = $('#boxplot_chart').attr('data-min-val');
    var max_val = $('#boxplot_chart').attr('data-max-val');
    var entity = $('#entity').val();
    if (boxplot_data.length != 0) {
        boxplot_data = JSON.parse(boxplot_data);
        // delete attribute
        $('#boxplot_chart').removeAttr('data-plot-series');
        $('#boxplot_chart').removeAttr('data-min-val');
        $('#hboxplot_chart').removeAttr('data-max-val');
        Plotly.newPlot("boxplot_chart",
            boxplot_data,
            {barmode: "overlay",
            yaxis: {
                range: [min_val, max_val],
                title: {
                    text: entity,
                }
              }
            },
        );
    }
});

// https://jsfiddle.net/2o8dgsnL/2/
//https://plot.ly/javascript/histograms/#overlaid-histgram
