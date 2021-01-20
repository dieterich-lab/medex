$(function () {

    $('#categorical_filter').select2({
    placeholder:"Search entity"
    });


    // initiate value for subcategory selector
    var $cat = $('#subcategory_filter').select2({
    placeholder:"Search entity"
    });

    // handling select all choice
    $('#subcategory_filter').on("select2:select", function (e) {
           var data = e.params.data.text;
           if(data=='Select all'){
            $("#subcategory_filter> option").prop("selected","selected");
            $('#subcategory_filter> option[value="Select all"]').prop("selected", false);
            $("#subcategory_filter").trigger("change");
           }
      });


    //change subcategories if category change
    $('#categorical_filter').change(function () {
        var entity =$(this).val(), values = cat[entity] || [];

        var html = $.map(values, function(value){
            return '<option value="' + value + '">' + value + '</option>'
        }).join('');
        $cat.html('<option value="Select all">Select all</option>'+html)
    });

});