$(function () {

        // export table as .xl file
    $('#export_excel').click(function() {
        // find closest parent with the class .card (accordion section)
        // and within the card find a table, which will be exported
        ($(this).closest('.card-body').find('#table')).table2excel({
            // todo: change the filename
        });
    });
    // export table as .csv file
    $('#export_csv').click(function() {
        // the same: find closest parent with the class .card (accordion section)
        // and within the card find a table, which will be exported
        ($(this).closest('.card-body').find('#table')).tableToCSV();
    });

    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });



    // use plugin select2 for selector
    $("#numeric_entities").select2({
    placeholder:"Search entity"
    });
    $('#categorical_entities').select2({
    placeholder:"Search entity"
    });
    $('#entities').select2({
    placeholder:"Search entity"
    });


    $('#example').DataTable( {
        "order": [[ 3, "desc" ], [ 0, 'asc' ]],
        "scrollX": true
    } );



});