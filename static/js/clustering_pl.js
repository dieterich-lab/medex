$(function() {
    $('#export_excel').click(function() {
        // find closest parent with the class .card (accordion section)
        // and within the card find a table, which will be exported
        ($(this).closest('.card').find('#table')).table2excel({
            // todo: change the filename
        });
    });
    // export table as .csv file
    $('#export_csv').click(function() {
        // the same: find closest parent with the class .card (accordion section)
        // and within the card find a table, which will be exported
        ($(this).closest('.card').find('#table')).tableToCSV();
    });


    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

    $('#Plot').click(function(){
        // disable button
        $(this).html('<span class="spinner-border spinner-border0sm" role="status" aria-hidden="true"></span> Loading ...');

        });



    // pretify the select input for numerical and categorical entities
    $("#measurement").select2();
    $("#measurement_cat").select2();
    $("#measurement_mix").select2();
    $("#numeric_entities").select2({placeholder:"Search entity"});
    $("#categorical_entities").select2({placeholder:"Search entity"});
    $("#mixed_entities").select2({placeholder:"Search entity"});


});