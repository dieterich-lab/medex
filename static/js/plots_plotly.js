$(function () {

    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

    // apply filter
    $(document).on('change', '#add_group_by', function() {
        if(this.checked == false) {
          $('#add_group').addClass('d-none');
        } else {
            $('#add_group').removeClass('d-none');
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
    $("#category").select2();

});

