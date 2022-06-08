$(function () {


function cd(start, end) {
        $('#Date span').html(start.format('YYYY-MM-DD') + ' - ' + end.format('YYYY-MM-DD'));
    }
    $('#Date').daterangepicker({
        startDate: start,
        endDate: end,
    },cd);

    cd(start,end);

var instance,
    min = 10,
    max = 100



$('#range').ionRangeSlider({
    type: "double",
    skin: "big",
    grid: true,
    grid_num: 4,
    min: min,
    max: max,
    step: 0.001,
    onStart: updateInputs,
    onChange: updateInputs
});
instance = $('#range').data("ionRangeSlider");


function updateInputs (data) {

	from = data.from;
    to = data.to;
    min = data.min;
    max = data.max;
    $('#input1').prop("value", from);
    $('#input2').prop("value", to);

}

$('#input1').on("input", function () {
    var val = $(this).prop("value");
    // validate
    if (val < min ) {
        val = min;
    } else if (val > to) {
        val = to;
    }
    instance.update({
        from: val
    });

});

$('#input2').on("input", function () {
    var val = $(this).prop("value");
    // validate
    if (val < from) {
        val = from;
    } else if (val > max) {
        val = max;
    }
    instance.update({
        to: val
    });

});

//change subcategories if category change
$('#id_numerical_filter').change(function () {
    var entity =$(this).val(), values = df[entity] || [];
    min =values['min']
    max =values['max']

    $('#input1').prop("value", min);
    $('#input2').prop("value", max);
    instance.update({
        min: min,
        max: max,
        from: min,
        to: max
    });

});

$(".range").ionRangeSlider({
    type: "double",
    skin: "big",
    grid: true,
    grid_num: 4,
    step: 0.001,
    to_fixed:true,//block the top
    from_fixed:true//block the from
});



    $("#clean").click(function(){
        var clean = document.getElementById("categorical_filter").value;
        $.ajax({
            type: "POST",
            url: "/filtering",
            data: JSON.stringify({'clean':'clean'}),
            contentType: "application/json",
            dataType: 'json',
            success: function(response) {
                    $("#demo").empty();
                    $("#demo2").empty();
                }
            });
    });

    remove_filter = function(span) {
        var val = $(span).closest("div").find("button.btn").val();
        span.closest("div").remove();
            $.ajax({
            type: "POST",
            url: "/filtering",
            data: JSON.stringify({'clean': val}),
            contentType: "application/json",
            dataType: 'json',
            success: function(response) {
                    $("#demo").empty();
                    $("#demo2").empty();
                }
            });
    }


    $("#add_filter").click(function() {
        if (document.getElementById("categorical_filter_check").checked) {
            var filter_cat = document.getElementById("categorical_filter").value;
            var filter_sub_cat = $('#subcategory_filter').val();
            var filters = [
            {"cat": filter_cat},
            {"sub": filter_sub_cat},
            ];
            $.ajax({
              type: "POST",
              url: "/filtering",
              data: JSON.stringify(filters),
              contentType: "application/json",
              dataType: 'json',
              success: function(response) {
                var content = "<div class='categorical_filter'>"
                content += "<button type='button' style='width: 100%; word-wrap: break-word; white-space: normal;' class='btn btn-outline-primary text-left' value = '"+ response.filter +"'>"
                content += "<span class='close' onclick='remove_filter(this)' >x </span>"
                content += response.filter + ' is ' + response.subcategory
                content += "</button></div>"

                $("#demo").append(content)
                }
            });
        }
        else{
            var filter_num = document.getElementById("id_numerical_filter").value;
            var num_from_to = document.getElementById("range").value;
            var filters = [
            {"num": filter_num},
            {"from_to": num_from_to},
            ];
            $.ajax({
              type: "POST",
              url: "/filtering",
              data: JSON.stringify(filters),
              contentType: "application/json",
              dataType: 'json',
              success: function(response) {
                var content = "<div class='categorical_filter'>"
                content += "<button type='button' style='width: 100%; word-wrap: break-word; white-space: normal;' class='btn btn-outline-primary text-left' value = '"+ response.filter +"'>"
                content += "<span class='close' onclick='remove_filter(this)' >x </span>"
                content += response.filter + ' is ' + response.subcategory
                content += "</button></div>"

                $("#demo").append(content)
                }
            });
        }


    });
});