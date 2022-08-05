$(function () {

    var column = $('#tab').attr('column');
    if (column !== undefined){
    var column =  JSON.parse($('#tab').attr('column').replace(/'/g, '"')); //"));
    $('#serverside_table').DataTable({
            select: {
            style: 'multi'
        },
    sDom: 'lrtip',
    bProcessing: true,
    bServerSide: true,
    scrollX: true,
    sPaginationType: "full_numbers",
    lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
    bjQueryUI: true,
    sAjaxSource: '/data/data1',
    columns: column

  });
  }


});