$(function () {
function stringMatch(term, candidate) {
    return candidate && candidate.toLowerCase().indexOf(term.toLowerCase()) >= 0;
}

function matchCustom(params, data) {
    // If there are no search terms, return all of the data
    if ($.trim(params.term) === '') {
        return data;
    }
    // Do not display the item if there is no 'text' property
    if (typeof data.text === 'undefined') {
        return null;
    }
    // Match text of option
    if (stringMatch(params.term, data.text)) {
        return data;
    }
    // Match attribute "data-foo" of option
    if (stringMatch(params.term, $(data.element).attr('data-foo'))) {
        return data;
    }
    // Return `null` if the term should not be displayed
    return null;
}

function formatCustom(state) {
    return $(
        '<div><div>' + state.text + '</div><div class="foo">'
            + $(state.element).attr('data-foo')
            + '</div></div>'
    );
    }

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

    $(".measurement").select2({
    placeholder:"Search entity"
    });
    $("#measurement_categorical").select2({
    placeholder:"Search entity"
    });
    $("#measurement_numeric").select2({
    placeholder:"Search entity"
    });
    $("#x_measurement").select2({
    placeholder:"Search entity"
    });
    $("#y_measurement").select2({
    placeholder:"Search entity"
    });
    $('.Plot').click(function(){
        $(this).html('<span class="spinner-border spinner-border0sm" role="status" aria-hidden="true"></span> Loading ...');
    });

});