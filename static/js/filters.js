$(function () {


    $("#clean").click(function(){
        $("#demo").empty();
    });

    $("#Add").click(function() {
        var e =document.getElementById("categorical_filter");
        var mag = e.options[e.selectedIndex].value;
        var e2 =$('#subcategory_filter').val();
        var m1 = mag
        var mm = mag + " is " +e2
        document.getElementById("demo").innerHTML = document.getElementById("demo").innerHTML +"  <button  style='display: block; width: 100%' class='btn btn-outline-primary'  ><span onclick='remove(this)'  class='close' > x </span><input type='hidden' name='filter' value='" + mm +"'><input type='hidden' name='cat' value='" + m1+"'>" + mm + "</button>";

    });

});