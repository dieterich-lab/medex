$(function () {


    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });
    $('#Plot').click(function(){
        // disable button
        $(this).prop("disabled",true);
        $(this).html('<span class="spinner-border spinner-border0sm" role="status" aria-hidden="true"></span> Loading ...');

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

    var df = JSON.parse($('#tab').attr('df').replace(/'/g, '"')); //"));


    $('#example').DataTable( {
        data: df,

    } );


});