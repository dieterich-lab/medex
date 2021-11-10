$(function () {

    var column = JSON.parse($('#tab').attr('column').replace(/'/g, '"')); //"));
    $('#serverside_table').DataTable({
    bProcessing: true,
    bServerSide: true,
    scrollX: true,
    sPaginationType: "full_numbers",
    lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
    bjQueryUI: true,
    sAjaxSource: '/calculator/table',
    columns: column
  });


});