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
    min = df['Delta0']['min'],
    max = df['Delta0']['max']




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
    if (val < min) {
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
$('#numerical_filter').change(function () {
    var entity =$(this).val(), values = df[entity] || [];
    var min =values['min']
    var max =values['max']

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
        });



    $("#clean").click(function(){
        $("#demo").empty();
        $("#demo2").empty();
    });

    $("#Add").click(function() {
        var e =document.getElementById("categorical_filter");
        var mag = e.options[e.selectedIndex].value;
        var e2 =$('#subcategory_filter').val();
        var m1 = mag
        var mm = mag + " is " +e2
        document.getElementById("demo").innerHTML = document.getElementById("demo").innerHTML +"  <button  style='display: block; width: 100%' class='btn btn-outline-primary'  ><span onclick='remove(this)'  class='close' > x </span><input type='hidden' name='filter' value='" + mm +"'><input type='hidden' name='cat' value='" + m1+"'>" + mm + "</button>";

    });

    $("#Add2").click(function() {

        var e =document.getElementById("numerical_filter").value;
        var mag = document.getElementById("range").value;
        var result = mag.split(";");
        var fieldvalue ='<div><input type="hidden" name="name" value="'+e+'">'+ e +'<input type="text" class="range" name="loan_term"  data-min="' + min + '" data-max="' + max + '" data-from="'+ result[0] +'" data-to="'+result[1]+ '"/></div>'

        $(fieldvalue).appendTo($('#demo2'));
        $(".range").ionRangeSlider({
            type: "double",
            skin: "big",
            grid: true,
            grid_num: 4,
            step: 0.001,
        });

    });

});