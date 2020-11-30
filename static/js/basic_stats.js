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
    $('#Plot').click(function(){
        // disable button
        $(this).html('<span class="spinner-border spinner-border0sm" role="status" aria-hidden="true"></span> Loading ...');

    });
    $('#Plot2').click(function(){
        // disable button
        $(this).html('<span class="spinner-border spinner-border0sm" role="status" aria-hidden="true"></span> Loading ...');

    });

    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

    $('#measurement').on("select2:select", function (e) {
           var data = e.params.data.text;
           if(data=='Select all'){
            $("#measurement> option").prop("selected","selected");
            $("#measurement").trigger("change");
           }
      });

    $('#measurement1').on("select2:select", function (e) {
           var data = e.params.data.text;
           if(data=='Select all'){
            $("#measurement1> option").prop("selected","selected");
            $("#measurement1").trigger("change");
           }
      });

    // use plugin select2 for selector
    $("#measurement").select2({
    placeholder:"Search entity"
    });
    $("#numeric_entities").select2({
    placeholder:"Search entity"
    });
    $("#measurement1").select2({
    placeholder:"Search entity"
    });
    $("#categorical_entities").select2({
    placeholder:"Search entity"
    });


});

