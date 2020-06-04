$(function () {

    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

    // apply filter
    $(document).on('change', '#add_group_by', function() {
        if(this.checked == false) {
          $('#add_group').addClass('d-none');
        } else {
            $('#add_group').removeClass('d-none');
        }
    });

    $("#x_axis").select2();
    $("#y_axis").select2();
    $("#add_group_by").select2();



    // scatter plot

    if ($('#add_group_by:checkbox:checked').length > 0) {

        var x_axis = $('#scatter_plot').attr('data-plot-x');
        var y_axis = $('#scatter_plot').attr('data-plot-y');
        var plot_data = $('#scatter_plot').attr('data-plot-series').replace(/'/g, '"'); //");
        if ($('#scatter_plot').length != 0) {
            plot_data = JSON.parse(plot_data);
            Plotly.newPlot('scatter_plot',
            plot_data,
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
     }else{
        var x_axis = $('#scatter_plot').attr('data-plot-x');
        var y_axis = $('#scatter_plot').attr('data-plot-y');
        var plot_data = $('#scatter_plot').attr('data-plot-series').replace(/'/g, '"'); //");
        if ($('#scatter_plot').length != 0) {
            plot_data = JSON.parse(plot_data);
            Plotly.newPlot('scatter_plot',
            plot_data,
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
        }



});

