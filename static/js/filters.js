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
$('#id_numerical_filter').change(function () {
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
            to_fixed:true,//block the top
            from_fixed:true//block the from
        });



    $("#clean").click(function(){
        $("#demo").empty();
        $("#demo2").empty();

        var value_categorical = '0';
        var value_numeric = '0';
        values = [value_categorical,value_numeric].join()
        document.getElementById('Add').value = values;

    });





remove_categorical = function(span) {
   var value_n_c =$("#Add").val();
   var values = value_n_c.split(",");
   var value_categorical = parseInt(values[0], 10);
   var value_numeric = parseInt(values[1], 10);
   value_categorical = isNaN(value_categorical) ? 0 : value_categorical;
   value_numeric = isNaN(value_numeric) ? 0 : value_numeric;


    var val = $(span).closest("div.categorical_filter").find("input[name='cat']").val();
    const index = categorical_filter_selected.indexOf(val);
    if (index > -1) {
      categorical_filter_selected.splice(index, 1); // 2nd parameter means remove one item only
    }
    span.closest("div.categorical_filter").remove();

    value_categorical -=1;
    values = [value_categorical,value_numeric].join()
    document.getElementById('Add').value = values;
    document.getElementById("Add").click();

}

remove_numerical = function(span) {
   var value_n_c =$("#Add").val();
   var values = value_n_c.split(",");
   var value_categorical = parseInt(values[0], 10);
   var value_numeric = parseInt(values[1], 10);
   value_categorical = isNaN(value_categorical) ? 0 : value_categorical;
   value_numeric = isNaN(value_numeric) ? 0 : value_numeric;

    var val = $(span).closest("div.fd-box2").find("input[name='name']").val();

    const index = numerical_filter_selected.indexOf(val);
    if (index > -1) {
      numerical_filter_selected.splice(index, 1); // 2nd parameter means remove one item only
    }
    span.closest("div.fd-box2").remove();

    value_numeric -=1;
    values = [value_categorical,value_numeric].join()
    document.getElementById('Add').value = values;
    document.getElementById("Add").click();



}

categorical_filter_selected  = ( typeof categorical_filter_selected  != 'undefined' && categorical_filter_selected  instanceof Array ) ? categorical_filter_selected  : []
numerical_filter_selected  = ( typeof numerical_filter_selected  != 'undefined' && numerical_filter_selected  instanceof Array ) ? numerical_filter_selected  : []



$("#Add").click(function() {
   var value_n_c =$("#Add").val();
   var values = value_n_c.split(",");
   var value_categorical = parseInt(values[0], 10);
   var value_numeric = parseInt(values[1], 10);
   value_categorical = isNaN(value_categorical) ? 0 : value_categorical;
   value_numeric = isNaN(value_numeric) ? 0 : value_numeric;


   var visit =$("#measurement_filter").val();
   document.getElementById("demo0").innerHTML = '<p>Filter by visit as on:'+ visit +'</p><input type="hidden" value='+visit+'>'
   $( "#measurement_filter").change();

   var mag =$("#categorical_filter").val();

   var e2 =$('#subcategory_filter').val();
   var mm = mag + " is: <br>" + e2
   mm = mm.replace(/,/g,"<br>")
   // if categorical filter than do nothing



   if (mag != 'Search entity' && categorical_filter_selected.includes(mag) != true ){
   value_categorical++;
   document.getElementById("demo").innerHTML = document.getElementById("demo").innerHTML  +"<div  class='categorical_filter' ><button type='button' class='btn btn-outline-primary text-left' style='display: block; width: 100%; word-wrap: break-word; white-space: normal;'  ><span onclick='remove_categorical(this)'  class='close' > x </span><input  type='hidden' name='filter' value='" + mm +"'><input type='hidden' name='cat' value='" + mag+"'>" + mm +"</button><br></div>";
   $("#categorical_filter").val('Search entity').change();
   categorical_filter_selected.push(mag);
   }




   var ed = $("#id_numerical_filter").val();
   var mag2 = $("#range").val();
   var result = mag2.split(";");
   var fieldvalue ='<div class="fd-box2" ><span onclick="remove_numerical(this)" class="close" > x </span><input type="hidden" name="name" value="'+ed+'">'+ ed +'<input type="text" class="range" name="loan_term"  data-min="' + min + '" data-max="' + max + '" data-from="'+ result[0] +'" data-to="'+result[1]+ '"/></div>'

   if (ed != 'Search entity' && numerical_filter_selected.includes(ed) != true ){
   value_numeric++;
   numerical_filter_selected.push(ed);
   $(fieldvalue).appendTo($('#demo2'));
   $("#id_numerical_filter").val('Search entity').change();
   }
   $(".range").ionRangeSlider({
        type: "double",
        skin: "big",
        grid: true,
        grid_num: 4,
        step: 0.001,
        to_fixed:true,//block the top
        from_fixed:true//block the from
   });

    values = [value_categorical,value_numeric].join()
    document.getElementById('Add').value = values;

    });


});