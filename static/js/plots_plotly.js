$(function () {

    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });


    // use plugin select2 for selector
    $("#x_axis").select2();
    $("#y_axis").select2();
    $("#x_visit").select2();
    $("#y_visit").select2();
    $("#categorical_entities").select2();


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

    // initiate value for subcategory selector
    var $cat = $('#subcategory_entities').select2({
    placeholder:"Search entity"
    });

    // handling select all choice
    $('#subcategory_entities').on("select2:select", function (e) {
           var data = e.params.data.text;
           if(data=='Select all'){
            $("#subcategory_entities> option").prop("selected","selected");
            $("#subcategory_entities").trigger("change");
           }
      });
    //change subcategories if category change
    $('#categorical_entities').change(function () {
        var entity =$(this).val(), values = cat[entity] || [];

        var html = $.map(values, function(value){
            return '<option value="' + value + '">' + value + '</option>'
        }).join('');
        $cat.html('<option value="Select all">Select all</option>'+html)
    });



});

