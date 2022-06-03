$(document).ready(function () {


    $('.add_filter').on('click', function () {

        var data_id = $(this).attr('data_id');

        var invoiceNumber = $('#invoiceNumberInput' + data_id).val();
        var invoiceDate = $('#invoiceDateInput' + data_id).val();
        var weekEndDate = $('#weekEndDateInput' + data_id).val();
        var storeNumber = $('#storeNumberInput' + data_id).val();
        var description = $('#descriptionInput' + data_id).val();
        var totalExGst = $('#totalExGstInput' + data_id).val();
        var category = $('#categoryInput' + data_id).val();



        req = $.ajax({
            url: '/updatetwoInvoice',
            type: 'POST',
            data: { invoiceNumber: invoiceNumber, invoiceDate: invoiceDate, weekEndDate: weekEndDate, storeNumber: storeNumber, description: description, totalExGst: totalExGst, category: category, id: data_id }
        });

        req.done(function (data) {

            $('#dataSectiontwoInvoice' + data_id).fadeOut(1000).fadeIn(1000);

        });


    });




});