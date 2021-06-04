$(function () {
    // initiate value for subcategory selector
    var $cat = $('.subcategory_entities').select2({
    placeholder:"Search entity"
    });

    // handling select all choice
    $('.subcategory_entities').on("select2:select", function (e) {
           var data = e.params.data.text;
           if(data=='Select all'){
            $(".subcategory_entities> option").prop("selected","selected");
            $(".subcategory_entities").trigger("change");
           }
      });
    $("#categorical_filter").select2({
    placeholder:"Search entity"
    });

    //change subcategories if category change
    $('.categorical_entities').change(function () {
        var entity =$(this).val(), values = cat[entity] || [];

        var html = $.map(values, function(value){
            return '<option value="' + value + '">' + value + '</option>'
        }).join('');
        $cat.html('<option value="Select all">Select all</option>'+html)
    });

    var $filter = $('#subcategory_filter').select2({
    placeholder:"Search entity"
    });
        // handling select all choice
    $('#subcategory_filter').on("select2:select", function (e) {
           var data = e.params.data.text;
           if(data=='Select all'){
            $("#subcategory_filter> option").prop("selected","selected");
            $("#subcategory_filter").trigger("change");
           }
      });

    //change subcategories if category change
    $('#categorical_filter').change(function () {
        var entity =$(this).val(), values = filter[entity] || [];

        var html = $.map(values, function(value){
            return '<option value="' + value + '">' + value + '</option>'
        }).join('');
        $filter.html('<option value="Select all">Select all</option>'+html)
    });

    // handling select all choice
    $('.measurement').on("select2:select", function (e) {
           var data = e.params.data.text;
           if(data=='Select all'){
            $(".measurement> option").prop("selected","selected");
            $(".measurement").trigger("change");
           }
      });


});
