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




$('.js-range-slider').ionRangeSlider({
    type: "double",
    skin: "round",
    grid: true,
    grid_num: 4,
    min: min,
    max: max,
    step: 0.001,
    onStart: updateInputs,
    onChange: updateInputs
});
instance = $('.js-range-slider').data("ionRangeSlider");


function updateInputs (data) {
	from = data.from;
    to = data.to;

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
        var max = 'demo2';
        var e =document.getElementById("numerical_filter");
        var mag = e.options[e.selectedIndex].value;

        document.getElementById("demo2").innerHTML = document.getElementById("demo2").innerHTML + mag + "<div class='range-slider'><input  type='text' class='js-range-slider' value='' /></div>" ;

    });

});