$(function () {
    // export table as .xl file
    $('#export_excel').click(function() {
        // find closest parent with the class .card (accordion section)
        // and within the card find a table, which will be exported
        ($(this).closest('.card').find('.table')).table2excel({
            // todo: change the filename
        });
    });
    // export table as .csv file
    $('#export_csv').click(function() {
        // the same: find closest parent with the class .card (accordion section)
        // and within the card find a table, which will be exported
        ($(this).closest('.card').find('.table')).tableToCSV();
    });

    // prettify the select input for numerical entities
    new Choices('#numeric_entities', {
        allowSearch: true,
        removeItemButton: true,
        //maxItemCount: 2,
    });

    // prettify the select input for categorical entities
    new Choices('#categorical_entities', {
        allowSearch: true,
        removeItemButton: true,
    });

    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

});