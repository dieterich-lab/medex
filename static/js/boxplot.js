$(function () {
    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

    // use plugin select2 for selector
    $("#numeric_entities").select2();
    $('#categorical_entities').select2();
    $("#visit").select2({
    placeholder:"Search entity"
    });

    $('#Plot').click(function(){
        // disable button
        $(this).prop("disabled",true);
        $(this).html('<span class="spinner-border spinner-border0sm" role="status" aria-hidden="true"></span> Loading ...');

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

    $('#visit').on("select2:select", function (e) {
           var data = e.params.data.text;
           if(data=='Select all'){
            $("#visit> option").prop("selected","selected");
            $("#visit").trigger("change");
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

