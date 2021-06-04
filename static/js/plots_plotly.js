$(function () {

    // apply filters for add group by
    $(document).on('change', '#add_group_by', function() {
        if(this.checked == false) {
          $('#add_group').addClass('d-none');
        } else {
            $('#add_group').removeClass('d-none');
        }
    });

    // hide choice scale for x and y axis
    $("#log2").hide();

    // show choice for log scale for x and y axis if we choose log
    $(document).on('change', '#log', function() {
        if(this.checked == false) {
          $("#log2").hide();
        } else {
            $("#log2").show();
        }
    });

    // hide choice scale for x and y axis if we choose linear
    $(document).on('change', '#linear', function() {
        if(this.checked == false) {
          $("#log2").show();
        } else {
            $("#log2").hide();
        }
    });



});

