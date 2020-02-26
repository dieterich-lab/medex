$(function () {

    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

    var chart_containers = [];
    var plot_series = [];
    var x_axis_text = [];
    var y_axis_text = [];
    var titles = [];
    var check_add_group_by = [];
    // scatter plot
    if ($('#scatter_plot_n').length != 0) {
        if (check_add_group_by = $('input:checkbox:checked').val()) {
            var PLOT_SERIES = $('#scatter_plot_n').attr('data-plot-series').replace(/'/g, '"');
            if (PLOT_SERIES.length != 0) {
                PLOT_SERIES = JSON.parse(PLOT_SERIES);
                $('#scatter_plot_n').removeAttr('data-plot-series');

                var x_axis = $('#x_axis').val();
                var y_axis = $('#y_axis').val();
                var cat = $('#category').val();

                chart_containers.push('scatter_plot_n')
                titles.push('Comparison of:<b>' + x_axis + '</b> and <b>' + y_axis + '</b>')
                x_axis_text.push(x_axis);
                y_axis_text.push(y_axis);
                plot_series.push(PLOT_SERIES);
            }

                for(i=0; i<chart_containers.length; i++) {
                    // initializing plot(s)
                    Highcharts.chart(chart_containers[i], {
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
                            
                        },
                        yAxis: {
                            title: {
                                text: y_axis_text[i],
                            },
                            
                        },
                        legend: {
                            labelFormatter: function () {
                                return "<b>" + cat + "</b>: " + this.options.cat;
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
                                                '<br><b>' + cat + '</b> {point.cat}' +
                                                '<br><b>patient_id:</b> {point.patient_id}' +
                                                '<br><b>group size:</b> {point.series.options.series_length}',
                                }
                            }
                        },
                        series: plot_series[i],
                        // series: [{
                        //     regression: true,
                        //     regressionSettings: {
                        //         type: 'linear',
                        //         color: 'black',
                        //         name: 'Linear regression: r: %r (%eq)', // show equation and r
                        //     },
                        //     data: plot_series[i],
                        //     name: 'Patients',
                        //     // disable max length of data-series
                        //     turboThreshold: 0,
                        // }],
                    });
                }
                
        } else {
            var x_axis = $('#scatter_plot_n').attr('data-plot-x');
        var y_axis = $('#scatter_plot_n').attr('data-plot-y');
        var plot_data = $('#scatter_plot_n').attr('data-plot-series').replace(/'/g, '"'); //");
        Highcharts.chart('scatter_plot_n', {
            chart: {
                type: 'scatter',
                zoomType: 'xy'
            },
            title: {
                text: 'Compare values of <b>' + x_axis + '</b> and <b>' + y_axis + '</b>',
            },
            xAxis: {
                title: {
                    enabled: true,
                    text: x_axis,
                },
//                startOnTick: true,
//                endOnTick: true,
//                showLastLabel: true
            },
            yAxis: {
                title: {
                    enabled: true,
                    text: y_axis,
                }
            },
            plotOptions: {
                scatter: {
                    tooltip: {
                        headerFormat: '',
                        pointFormat: '<b>Patient: </b>{point.patient_id}<br>' + x_axis + ': {point.x}<br>' + y_axis +': {point.y}',
                    }
                }
            },
            series:  [{
                regression: true,
                regressionSettings: {
                    type: 'linear',
                    color: 'black',
                    name: 'Linear regression: r: %r (%eq)', // show equation and r
                },
                data: JSON.parse(plot_data),
                name: 'Patients',
                // disable max length of data-series
                turboThreshold: 0,
            }],
        });
        }
        
    }

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



    // build bar chart for categorical entities
    if ($('#cluster_chart_c').length != 0) {
        var plot_series = $('#cluster_chart_c').attr('data-plot-series').replace(/'/g, '"'); //");
        var plot_categories = $('#cluster_chart_c').attr('data-plot-categories').replace(/'/g, '"'); //");
        plot_series = JSON.parse(plot_series);
        plot_categories = JSON.parse(plot_categories);

        Highcharts.chart('cluster_chart_c', {
            chart: {
                type: 'column'
            },
            title: {
                text: 'Grouped categorical values'
            },
            xAxis: {
                categories: plot_categories,
                crosshair: true
            },
            yAxis: {
                min: 0,
                title: {
                    text: 'Number of patients'
                }
            },
            tooltip: {
                headerFormat: '<span style="font-size:14px"><b>{point.key}</b></span><table>',
                footerFormat: '</table>',
                pointFormatter: function() {
                    if (this.y != 0) {
                        return '<tr><td style="color:' + this.series.color +';padding:0">'+ this.series.name+': </td>' +
                    '<td style="padding:0"><b>' + this.y +'</b></td></tr>';
                    }
                },
                shared: true,
                useHTML: true
            },
            plotOptions: {
                column: {
                    pointPadding: 0.2,
                    borderWidth: 0
                },
            },
            series: {
                dataLabels: {
                  enabled: true,
                  formatter: function() {
                    if (this.y > 0) {
                      return this.y;
                    }
                  }
                }
            },
            series: plot_series,
        });
    };

    // hide/show controls when plot type is selected
    $(document).on('change', 'select#plot_type', function() {
        var plot_type = $(this).val();
        if (plot_type == 'scatter_plot_n') {
            $('#scatter_plot_controls').removeClass('d-none');
            $('#heat_map_controls').addClass('d-none');
        };
        if (plot_type == 'heat_map_n') {
            $('#heat_map_controls').removeClass('d-none');
            $('#scatter_plot_controls').addClass('d-none');
        };
        if (plot_type == 'select_plot') {
            $('#scatter_plot_controls').addClass('d-none');
            $('#heat_map_controls').addClass('d-none');
        }
    });

    // // apply filters for separate regression
    // $(document).on('change', '#add_separate_regression', function() {
    //     if(this.checked) {
    //       $('#add_separate_regression').removeClass('d-none');
    //     } else {
    //         $('#add_separate_regression').addClass('d-none');
    //     }
    // });

    // apply filter 
    $(document).on('change', '#add_group_by', function() {
        if(this.checked) {
          $('#add_group').removeClass('d-none');
        } else {
            $('#add_group').addClass('d-none');
        }
    });

    // add entity to the list when selected in select input
    $('#numeric_entities').on('addItem', function(event) {
        // there are problems if selector containing dots. So, we get rid of the dots
        var entity_id = event.detail.value; // with dots
        var entity = entity_id.split('__').join('.'); // replace dots with underscore

        // request of min_max_values
        $.post('/plots/get_min_max/' + entity, function(data, status) {
            if (status != 'success') {
                // instead of slider using custom number fields
                // append new element
                $('#selected_entities').append(
                    '<li class="list-group-item" id="' + entity_id + '">' +
                    '<div class="row"><div class="col col-sm-4">' +
                        '<label>' + entity + '</label>' +
                        '<label class="mr-3">min value:</label><input type="number"><br>' +
                        '<label class="rm-3">max value:</label><input type="number"></div>' +
                    '<div class="col col-sm-2"><span class="close" aria-label="Close"> &times;</span></div></div></li>'
                );
            } else {
                var min_value = data['min'];
                var max_value = data['max'];
                var step_value = data['step'];
                $('#selected_entities').append(
                 '<li class="list-group-item" id="' + entity_id + '">' +
                    '<div class="row"><div class="col col-sm-4">' +
                        '<label>' + entity + '</label>' +
                    '</div><div class="col col-sm-6" data-toggle="tooltip" data-placement="top"' +
                        'title="' + min_value + ',' + max_value +'">' +
                        '<label class="mr-3 min">>='+min_value+'</label>' +
                        '<input type="text" class="slider" value=""'+
                         'data-slider-min="' + min_value +'" data-slider-max="' + max_value +'"' +
                        'data-slider-step="' + step_value + '" data-slider-value="['+min_value+','+max_value+']"'+
                        'name="min_max_'+ entity_id + '"/><label class="ml-3 max"><=' + max_value +'</label></div>' +
                    '<div class="col col-sm-2"><span class="close" aria-label="Close"> &times;</span></div></div>' +
                '</li>'
                ).find('input.slider').slider({});
            }
        });
    });

    // delete entity from the list, when deleted from select
    $('#numeric_entities').on('removeItem', function(event) {
        var entity_id = event.detail.value; // without dots
        $('li#'+entity_id).remove();
    });

    // delete entity from select when deleted from list
    $(document).on('click', 'span.close', function() {
        var entity_with_dots = $(this).closest('li').find('label').first().text();
        var entity_id = entity_with_dots.split('.').join('__');
        $(this).closest('li').remove();
        n_choices.removeItemsByValue(entity_id);
    });

    // slider
    $('input.slider').slider({
        tooltip: 'always',
        tooltip_split: true,
    });

    // update label when changing min max on slider
    $(document).on('slide', 'input.slider', function() {
        var min_max = $(this).val().split(',');
        $(this).parent().find('label.min').text(min_max[0]+' >=');
        $(this).parent().find('label.max').text('<= ' +min_max[1]);
    });

    if ($('#heat_map_n').length != 0) {
        var plot_data = JSON.parse($('#heat_map_n').attr('data-plot-series').replace(/'/g, '"')); //"));
        var x_categories = JSON.parse($('#heat_map_n').attr('data-categories').replace(/'/g, '"')); //"));
        var y_categories = x_categories;
        $('#heat_map_n').removeAttr('data-plot-series');
        $('#heat_map_n').removeAttr('data-categories');
        Highcharts.chart('heat_map_n', {
            chart: {
                type: 'heatmap',
                marginTop: 40,
                marginBottom: 80,
                plotBorderWidth: 1
            },
            title: {
                text: 'Correlation between numeric entities'
            },

            xAxis: {
                categories: x_categories,
            },

            yAxis: {
                categories: y_categories,
                title: null
            },

            colorAxis: {
                min: 0,
                minColor: '#FFFFFF',
                maxColor: Highcharts.getOptions().colors[0]
            },

            legend: {
                align: 'right',
                layout: 'vertical',
                margin: 0,
                verticalAlign: 'top',
                y: 25,
                symbolHeight: 280
            },

            tooltip: {
                formatter: function () {
                    return '<b>' + this.series.xAxis.categories[this.point.x] + '</b> <br><b>' +
                        this.series.yAxis.categories[this.point.y] + '</b><br>Correlation: ' + this.point.value +
                        '<br><b>p value: </b>' + this.point.pvalue;
                }
            },

            series: [{
                name: 'Correlation',
                borderWidth: 1,
                data: plot_data,
                pointStart: 0,
                pointInterval: 1,
                dataLabels: {
                    enabled: true,
                    color: '#000000'
                }
            }]

        });
    }


    // stacked  plot:

    if ($('#stacked_chart').length != 0) {
        var x_categories = JSON.parse($('#stacked_chart').attr('data-x-categories').replace(/'/g, '"')); //"));
        var plot_series = JSON.parse($('#stacked_chart').attr('data-plot-series').replace(/'/g, '"')); //"));
        Highcharts.chart('container', {
            chart: {
                type: 'bar'
            },
            title: {
                text: 'Stacked bar chart'
            },
            xAxis: {
                categories: x_categories, // ['Apples', 'Oranges', 'Pears', 'Grapes', 'Bananas']
            },
            yAxis: {
                min: 0,
                title: {
                    text: 'Number of patients per category'
                }
            },
            legend: {
                reversed: true
            },
            plotOptions: {
                series: {
                    stacking: 'normal'
                }
            },
            series: plot_series,
//            [{
//                name: 'John',
//                data: [5, 3, 4, 7, 2]
//            }, {
//                name: 'Jane',
//                data: [2, 2, 3, 2, 1]
//            }, {
//                name: 'Joe',
//                data: [3, 4, 4, 2, 5]
//            }]
        });
    }
});