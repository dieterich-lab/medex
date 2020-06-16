$(document).ready(function() {

    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

    // apply filters
    $(document).on('change', '#select_scale', function() {
        if(this.checked) {
          $('#scale_values').removeClass('d-none');
        } else {
            $('#scale_values').addClass('d-none');
        }
    });

    $("#log2").hide();

    $(document).on('change', '#log', function() {
        if(this.checked == false) {
          $("#log2").hide();
        } else {
            $("#log2").show();
        }
    });

    $(document).on('change', '#linear', function() {
        if(this.checked == false) {
          $("#log2").show();
        } else {
            $("#log2").hide();
        }
    });

    $("#x_axis").select2();
    $("#y_axis").select2();
    $("#category1").select2();
    $("#category2").select2();

});