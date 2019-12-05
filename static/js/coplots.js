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

    // they all have to be of the same length
    var chart_containers = [];
    var titles = [];
    var y_axis_text = [];
    var x_axis_text = [];
    var plot_series = [];
    var how_to_plot = $('#coplot').attr('data-how-to-plot');
    $('#coplot').removeAttr('data-how-to-plot');
    // for single_plot
    if (how_to_plot == "single_plot") {
        // initializing constants and removing attributes from html elements
        var PLOT_SERIES = $('#coplot').attr('data-plot-series').replace(/'/g, '"'); //");
        if (PLOT_SERIES.length != 0) {
            PLOT_SERIES = JSON.parse(PLOT_SERIES);
            // removing attributes
            $('#coplot').removeAttr('data-plot-series');

            var x_axis = $('#x_axis').val();
            var y_axis = $('#y_axis').val();
            var cat1 = $('#category1').val();
            var cat2 = $('#category2').val();

            chart_containers.push('coplot');
            titles.push('Comparison of:<b>' + x_axis + '</b> and <b>' + y_axis + '</b>');
            x_axis_text.push(x_axis);
            y_axis_text.push(y_axis);
            plot_series.push(PLOT_SERIES);
        }
    } else { // for multiple plots
        var how_to_plot = $('input:radio:checked').val();
        if (how_to_plot == 'multiple_plots') {
            var x_axis = $('#x_axis').val();
            var y_axis = $('#y_axis').val();
            var cat1 = $('#category1').val();
            var cat2 = $('#category2').val();
            var cat1_values = $('#coplot').attr('data-cat1-values').replace(/'/g, '"'); //");
            var cat2_values = $('#coplot').attr('data-cat2-values').replace(/'/g, '"'); //");
            cat1_values = JSON.parse(cat1_values);
            cat2_values = JSON.parse(cat2_values);
            var PLOT_SERIES = $('#coplot').attr('data-plot-series').replace(/'/g, '"'); //");
            PLOT_SERIES = JSON.parse(PLOT_SERIES);
            for (i=0; i<cat1_values.length; i++) {
                var val1 = cat1_values[i];
                for (j=0; j<cat2_values.length; j++) {
                    var val2 = cat2_values[j];
                    chart_containers.push(val1 + "_" + val2);
                    titles.push("Comparison of <b>" + val1 + "</b> and <b>" + val2 + "</b>");
                    x_axis_text.push(x_axis);
                    y_axis_text.push(y_axis);
                    var key = val1 + "_" + val2;
                    var series = PLOT_SERIES[key];
                    plot_series.push([series]);
                }
            }
            var chart_width = $('.coplot').width();
            chart_width = chart_width / cat2_values.length;
        }
    }
    var x_min = parseFloat($('#coplot').attr('data-x-min'));
    var x_max = parseFloat($('#coplot').attr('data-x-max'));
    var y_min = parseFloat($('#coplot').attr('data-y-min'));
    var y_max = parseFloat($('#coplot').attr('data-y-max'));

    for(i=0; i<chart_containers.length; i++) {
        // initializing plot(s)
        var chart = Highcharts.chart(chart_containers[i], {
            chart: {
                type: 'scatter',
                zoomType: 'xy',
                height: 400,
            },
            title: {
                text: titles[i]
            },
            xAxis: {
                title: {
                    text: x_axis_text[i],
                },
                min: x_min,
                max: x_max,
            },
            yAxis: {
                title: {
                    text: y_axis_text[i],
                },
                min: y_min,
                max: y_max,
            },
            legend: {
                labelFormatter: function () {
                    return "<b>" + $('#category1').val() + "</b>: " + this.options.cat1 +
                    '<br><b>' + $('#category2').val() + '</b>: ' + this.options.cat2;
                }
            },
            plotOptions: {
                scatter: {
                    marker: {
                        radius: 5,
                        states: {
                            hover: {
                                enabled: true,
                                lineColor: 'rgb(100,100,100)'
                            }
                        }
                    },
                    states: {
                        hover: {
                            marker: {
                                enabled: false
                            }
                        }
                    },
                    tooltip: {
                        pointFormat: '<b>' + x_axis + ' :</b> {point.x}<br><b>' +
                                    '<br><b>' + y_axis + ' : </b> {point.y}' +
                                    '<br><b>' + cat1 + '</b> {point.cat1}' +
                                    '<br><b>' + cat2 + '</b> {point.cat2}' +
                                    '<br><b>patient_id:</b> {point.patient_id}' +
                                    '<br><b>group size:</b> {point.series.options.series_length}',
                    }
                }
            },
            series: plot_series[i]
        });
        if (how_to_plot == "multiple_plots") {
            chart.setSize(chart_width, 400, doAnimation=false);
        }
    }


});