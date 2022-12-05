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
    let filter_measurement_select = $("#filter_measurement");
    filter_measurement_select.select2({
        placeholder:"Search entity"
    });
    filter_measurement_select.change( () => {
        set_filter_measurement(filter_measurement_select.val());
    });
    window.set_filter_measurement = function (new_measurement) {
        fetch('/filter/set_measurement', {
            method: 'POST',
            headers:{
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({'measurement': new_measurement}),
        }).then(response => {
            refresh_filter_panel();
        }).catch(error => {
            console.log(error);
            refresh_filter_panel();
        });
    }


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
        fetch('/filter/all', {
            method: 'DELETE',
        }).then(response => {
            refresh_filter_panel();
        }).catch(error => {
            console.log(error);
            refresh_filter_panel();
        });
    });

    $( document ).ready(refresh_filter_panel)

    function refresh_filter_panel() {
        fetch('/filter/all', {method: 'GET'})
        .then(response => response.json())
        .then(data => {
            clear_filter_panel();
            const filters = data['filters'];
            const filter_entities_sorted = Object.keys(filters).sort();
            filter_entities_sorted.forEach(entity => {
                const filter = filters[entity];
                if ('categories' in filter) {
                    render_categorical_filter(entity, filter);
                } else {
                    render_numerical_filter(entity, filter);
                }
            })
            update_filtered_patient_count(data['filtered_patient_count']);
        })
        .catch(error => {
            console.log(error)
        })
    }

    function clear_filter_panel() {
        let div = document.getElementById('active_filters');
        let child = div.lastElementChild;
        while (child) {
            div.removeChild(child);
            child = div.lastElementChild;
        }
    }

    function render_categorical_filter(entity, filter) {
        const categories = filter['categories'].join(', ');
        render_filter(entity, `
             <button type="button" style="width: 100%; word-wrap: break-word; white-space: normal;"
                     class="btn btn-outline-primary text-left" value="${entity}">
                  <span class="close" id="remove_filter/${entity}">x</span>
                  ${entity} is ${categories}
             </button>
        `);
    }

    function render_filter(entity, inner_html) {
        let div = document.getElementById('active_filters');
        let child = document.createElement('div');
        child.setAttribute('id', `filter/${entity}`);
        child.setAttribute('class', 'categorical_filter');
        child.innerHTML = inner_html;
        div.appendChild(child);
        let remover = document.getElementById(`remove_filter/${entity}`);
        remover.addEventListener('click', () => { remove_filter(entity) }, false);
    }

    function render_numerical_filter(entity, filter) {
        render_filter(entity, `
            <span class="close" id="remove_filter/${entity}">x</span>
            <input type="hidden" class="name" value="${entity}"/> ${entity}
            <input type="text" class="range"  name="loan_term"  data-min="${filter.min}" data-max="${filter.max}"
                   data-from="${filter.from_value}" data-to="${filter.to_value}"/>
        `);
        // ToDo: The following lines are ugly - and jquery
        $(".range").ionRangeSlider({
            type: "double",
            skin: "big",
            grid: true,
            grid_num: 4,
            step: 0.001,
            to_fixed: true,//block the top
            from_fixed: true//block the from
        });
    }

    function update_filtered_patient_count(filtered_patient_count) {
        let span = document.getElementById('filtered_patient_count');
        if (filtered_patient_count === null) {
            span.innerHTML = '';
        } else {
            span.innerHTML = ` (${filtered_patient_count} patients)`;
        }
    }

    function remove_filter(entity) {
        fetch('/filter/delete', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({'entity': entity}),
        }).then(response => {
            refresh_filter_panel();
        }).catch(error => {
            console.log(error);
            refresh_filter_panel();
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
                body: JSON.stringify({'entity': entity, 'categories': categories}),
            }).then(response => {
                refresh_filter_panel();
            }).catch(error => {
                console.log(error)
                refresh_filter_panel();
            })
        } else{
            const entity = document.getElementById("id_numerical_filter").value;
            const from_to = document.getElementById("range").value.split(';');
            const request_json = {
                'entity': entity,
                'from_value': parseFloat(from_to[0]),
                'to_value': parseFloat(from_to[1]),
                'min': min,
                'max': max,
            };
            fetch('/filter/add_numerical', {
                method: 'POST',
                headers:{
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(request_json),
            }).then(response => {
                refresh_filter_panel();
            }).catch(error => {
                console.log(error);
                refresh_filter_panel();
            })
        }
    });
});

