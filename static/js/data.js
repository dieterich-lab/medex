$(function () {


    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });
    $('#Plot').click(function(){
        // disable button
        $(this).html('<span class="spinner-border spinner-border0sm" role="status" aria-hidden="true"></span> Loading ...');

        });


    // use plugin select2 for selector
    $("#numeric_entities").select2({
    placeholder:"Search entity"
    });
    $('#categorical_entities').select2({
    placeholder:"Search entity"
    });
    $('#entities').select2({
    placeholder:"Search entity"
    });

    $('#entities').on("select2:select", function (evt) {
      var element = evt.params.data.element;
      var $element = $(element);

      $element.detach();
      $(this).append($element);
      $(this).trigger("change");
    });

        // handling select all choice
    $('#entities').on("select2:select", function (e) {
           var data = e.params.data.text;
           if(data=='Select all'){
            $("#entities> option").prop("selected","selected");
            $("#entities ").trigger("change");
           }
      });

    var column = JSON.parse($('#tab').attr('column').replace(/'/g, '"')); //"));
    $('#serverside_table').DataTable({
    bProcessing: true,
    bServerSide: true,
    scrollX: true,
    sPaginationType: "full_numbers",
    lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
    bjQueryUI: true,
    sAjaxSource: '/data/data1',
    columns: column
  });


});