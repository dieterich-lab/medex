$(function () {
    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

// pretify the select input for categorical entities
    $('#categorical_entities').select2({
    placeholder:"Search entity"
    });



});