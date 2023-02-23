$(function () {

    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });
    // use plugin select2 for selector
    $(".numeric_entities").select2({
    placeholder:"Search entity"
    });
    $(".categorical_entities").select2({
    placeholder:"Search entity",
    });
    $("#date_entities").select2({
    placeholder:"Search entity"
    });

    // add spinner
    // $('#Result').click(function(){
    //     $(this).html('<span class="spinner-border spinner-border0sm" role="status" aria-hidden="true"></span> Loading ...');
    // });
    $('#Result_categorical').click(function(){
        $(this).html('<span class="spinner-border spinner-border0sm" role="status" aria-hidden="true"></span> Loading ...');
    });
    $('#Result_date').click(function(){
        $(this).html('<span class="spinner-border spinner-border0sm" role="status" aria-hidden="true"></span> Loading ...');
    });
});