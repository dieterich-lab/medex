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

    $(".range").ionRangeSlider({
        type: "double",
        skin: "big",
        grid: true,
        grid_num: 4,
        step: 0.001,
        to_fixed:true,//block the top
        from_fixed:true//block the from
    });


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

   filter_check = function(input) {
    if (document.getElementById('categorical_filter_check').checked) {
        document.getElementById('categorical_filter_check_block').style.display = 'block';
        document.getElementById('numerical_filter_check_block').style.display = 'none';
    }
    else if (document.getElementById('numerical_filter_check').checked){
        document.getElementById('numerical_filter_check_block').style.display = 'block';
        document.getElementById('categorical_filter_check_block').style.display = 'none';}

    }

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

    $("#clean").click(function(){
        var clean = document.getElementById("categorical_filter").value;
        $.ajax({
            type: "POST",
            url: "/filtering",
            data: JSON.stringify([{'clean':'clean'}]),
            contentType: "application/json",
            dataType: 'json',
            success: function(response) {
                    $("#demo").empty();
                    $("#demo2").empty();
                }
            });
    });

    remove_filter = function(span) {
        var val_cat = $(span).closest("div").find("button.btn").val();
        var val_num = $(span).closest("div").find("input.name").val();
        span.closest("div").remove()
        $.ajax({
            type: "POST",
            url: "/filtering",
            data: JSON.stringify([{'clean_one_filter': [val_cat,val_num]}]),
            contentType: "application/json",
            dataType: 'json',
            success: function(response) {
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
                content += "<button type='button' style='width: 100%; word-wrap: break-word; white-space: normal;'"
                content += "class='btn btn-outline-primary text-left' value = '"+ response.filter +"'>"
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
            {"min_max": [min,max]}
            ];

            $.ajax({
              type: "POST",
              url: "/filtering",
              data: JSON.stringify(filters),
              contentType: "application/json",
              dataType: 'json',
              success: function(response) {
                var content = "<div class='numerical_filter'>"
                content += "<span onclick='remove_filter(this)'  class='close'> x </span>"
                content += "<input type='hidden' class='name' value="+ response.filter +"/>" + response.filter
                content += "<input type='text' class='range'  name='loan_term'  data-min='"+ min
                content += "' data-max='"+ max +"'data-from='"+ response.from_num +"'data-to='"+ response.to_num +"'/>"
                content += "</div>"
                $("#demo2").append(content)
                },
              complete: function(response){
                    $(".range").ionRangeSlider({
                    type: "double",
                    skin: "big",
                    grid: true,
                    grid_num: 4,
                    step: 0.001,
                    to_fixed:true,//block the top
                    from_fixed:true//block the from
                });
               }
            });

        }


    });
});