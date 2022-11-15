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

    $('#id_numerical_filter').change(function () {
        var entity =$(this).val(), values = df[entity] || [];
        min =values['min']
        max =values['max']


        instance.update({
            min: min,
            from: min,
            max: max,
            to: max
        });
        $('#input1').prop("value", min);
        $('#input2').prop("value", max);


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

    // use plugin select2 for selector
    $("#categorical_filter").select2({
    placeholder:"Search entity"
    });
    $("#id_numerical_filter").select2({
    placeholder:"Search entity"
    });

    var $filter = $('#subcategory_filter').select2({
    placeholder:"Search entity"
    });
    // handling select all choice
    $('#subcategory_filter').on("select2:select", function (e) {
           var data = e.params.data.text;
           if(data=='Select all'){
            $("#subcategory_filter> option").prop("selected","selected");
            $('#subcategory_filter> option[value="Select all"]').prop("selected", false);
            $("#subcategory_filter").trigger("change");
           }
      });

    //change subcategories if category change
    $('#categorical_filter').change(function () {
        var entity =$(this).val(), values = filter[entity] || [];

        var html = $.map(values, function(value){
            return '<option value="' + value + '">' + value + '</option>'
        }).join('');
        $filter.html('<option value="Select all">Select all</option>'+html)
    });



    $("#clean").click(function(){
        fetch('/filter/delete_all', {
            method: 'DELETE',
        }).then(response => {
                $("#demo").empty();
                $("#demo2").empty();
        }).catch(
            error => {
                console.log(error)
            }
        );
    });

    remove_filter = function(entity) {
        fetch('/filter/delete', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({'entity': entity}),
        }).then(response => {
            document.getElementById(`filter/${entity}`).remove();
        }).catch(error => {
            console.log(error)
        })
    }


    $("#add_filter").click(function() {
        if (document.getElementById("categorical_filter_check").checked){
            let entity = document.getElementById("categorical_filter").value;
            let categories = $('#subcategory_filter').val();
            fetch('/filter/add_categorical', {
                method: 'POST',
                headers:{
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify([{'entity': entity}, {'category': categories}]),
            }).then(response => {
                let content = `
                        <div class="categorical_filter" id="filter/${entity}">
                             <button type='button' style='width: 100%; word-wrap: break-word; white-space: normal;'
                                     class='btn btn-outline-primary text-left' value='${entity}'>
                                  <span class='close' onclick='remove_filter(${entity})'>x</span>
                                  ${entity} is ${categories}
                             </button>
                        </div>`;
                document.getElementById("add_filter").value = response.update_filter
                $("#demo").append(content)
            }).catch(error => {
                console.log(error)
            })
        }
        else{
            let entity = document.getElementById("id_numerical_filter").value;
            fetch('/filter/add_numerical', {
                method: 'POST',
                headers:{
                    'Content-Type': 'application/json',
                },
                // the parameters from_num and to_num need to be checked else need to be created
                body: JSON.stringify([{'entity': entity}, {'from_value': from_num}, {'to_value': to_num}, {'min': min}, {'max': max}]),
            }).then(response => {
                let content = `
                        <div class="numerical_filter" id="filter/${entity}">
                            <span class='close' onclick='remove_filter(${entity})'>x</span>
                            <input type='hidden' class='name' value='${entity}'/> ${entity}
                            <input type='text' class='range'  name='loan_term'  data-min='${min}' data-max='${max}' 
                                   data-from='${response.from_num}' data-to='${response.to_num}'/>
                        </div>`;
                $("#demo2").append(content)
                document.getElementById("add_filter").value = response.update_filter
            }).then(response => {
                $(".range").ionRangeSlider({
                    type: "double",
                    skin: "big",
                    grid: true,
                    grid_num: 4,
                    step: 0.001,
                    to_fixed: true,//block the top
                    from_fixed: true//block the from
                })
            }).catch(error => {
                console.log(error)
            })
        }
    });
});