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
    $('#export_excel1').click(function() {
        // find closest parent with the class .card (accordion section)
        // and within the card find a table, which will be exported
        ($(this).closest('.card').find('#table')).table2excel({
            // todo: change the filename
        });
    });
    // export table as .csv file
    $('#export_csv1').click(function() {
        // the same: find closest parent with the class .card (accordion section)
        // and within the card find a table, which will be exported
        ($(this).closest('.card').find('#table')).tableToCSV();
    });

    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

    $('#visit').on("select2:select", function (e) {
           var data = e.params.data.text;
           if(data=='Select all'){
            $("#visit> option").prop("selected","selected");
            $("#visit").trigger("change");
           }
      });

    $('#visit1').on("select2:select", function (e) {
           var data = e.params.data.text;
           if(data=='Select all'){
            $("#visit1> option").prop("selected","selected");
            $("#visit1").trigger("change");
           }
      });

    // use plugin select2 for selector
    $("#visit").select2({
    placeholder:"Search entity"
    });
    $("#numeric_entities").select2({
    placeholder:"Search entity"
    });
    $("#visit1").select2({
    placeholder:"Search entity"
    });
    $("#categorical_entities").select2({
    placeholder:"Search entity"
    });

});

