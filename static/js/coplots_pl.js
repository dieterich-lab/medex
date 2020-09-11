$(document).ready(function() {

    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

    // use plugin select2 for selector
    $("#x_axis").select2();
    $("#y_axis").select2();
    $("#category1").select2();
    $("#category2").select2();
    $("#x_visit").select2();
    $("#y_visit").select2();


    // apply filters for Single and multiple plot
    $(document).on('change', '#select_scale', function() {
        if(this.checked) {
          $('#scale_values').removeClass('d-none');
        } else {
            $('#scale_values').addClass('d-none');
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



    // initiate value for subcategory selector
    var $cat1 = $('#category11').select2({
    placeholder:"Search entity"
    });

    // handling select all choice
    $('#category11').on("select2:select", function (e) {
           var data = e.params.data.text;
           if(data=='Select all'){
            $("#category11> option").prop("selected","selected");
            $("#category11").trigger("change");
           }
      });

    //change subcategories if category change
    $('#category1').change(function () {
        var entity =$(this).val(), values = cat[entity] || [];

        var html = $.map(values, function(value){
            return '<option value="' + value + '">' + value + '</option>'
        }).join('');
        $cat1.html('<option value="Select all">Select all</option>'+html)
    });




    // initiate value for subcategory selector
    var $cat = $('#category22').select2({
    placeholder:"Search entity"
    });

    // handling select all choice
    $('#category22').on("select2:select", function (e) {
           var data = e.params.data.text;
           if(data=='Select all'){
            $("#category22> option").prop("selected","selected");
            $("#category22").trigger("change");
           }
      });

    //change subcategories if category change
    $('#category2').change(function () {
        var entity =$(this).val(), values = cat[entity] || [];

        var html = $.map(values, function(value){
            return '<option value="' + value + '">' + value + '</option>'
        }).join('');
        $cat.html('<option value="Select all">Select all</option>'+html)
    });


});