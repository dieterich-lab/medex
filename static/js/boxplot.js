$(function () {
    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });


    $("#numeric_entities").select2();
    $("#group_by").select2();


});

// https://jsfiddle.net/2o8dgsnL/2/
//https://plot.ly/javascript/histograms/#overlaid-histgram
