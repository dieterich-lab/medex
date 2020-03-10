$(function() {

    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

    // getting min_max_values and remove the attribute from ul
    var min_max_values = JSON.parse($('#selected_entities').attr('data-min-max-values').replace(/'/g, '"')); //"));
    $('#selected_entities').removeAttr('data-min-max-values');


    // prettify the select input for numerical entities
    var choices = new Choices('#numeric_entities', {
        allowSearch: true,
        removeItemButton: true,
//        maxItemCount: 1,
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

    // slider for dynamically added elements
    $(document).on('DOMNodeInserted', 'li.list-group-item', function(e) {
        var slider_input = $(e.target).find('input.slider');
        $(slider_input).slider({
            tooltip: 'always',
            tooltip_split: true,
        });
    });

    // slider for dynamically added elements
    $('input.slider').slider({
        tooltip: 'always',
        tooltip_split: true,
    });

    $(document).on('slide', 'input.slider', function() {
        var min_max = $(this).val().split(',');
        $(this).parent().find('label.min').text(min_max[0]+' >=');
        $(this).parent().find('label.max').text('<= ' +min_max[1]);
    });

    $('div[data-toggle="tooltip"]').on('show.bs.tooltip', function() {
        var min_value = $(this).find('input.slider').attr('data-slider-min');
        var max_value = $(this).find('input.slider').attr('data-slider-max');
        $(this).attr('title', min_value + ',' + max_value);
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
        choices.removeItemsByValue(entity_id);
    });
});