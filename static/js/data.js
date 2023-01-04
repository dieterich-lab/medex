function display_table_with_selected_type() {
    const all_table_types = document.querySelectorAll('input[name="what_table"]');
    let selected_table;
    for (const table_type of all_table_types) {
        if (table_type.checked) {
            selected_table = table_type.value;
            if (selected_table === 'long') {
                get_filtered_data_flat(selected_table);
            } else if (selected_table === 'short') {
                get_filtered_data_by_measurement(selected_table);
            }
        }
    }
}

function get_filtered_data_flat(selected_table) {
    const measurements = get_selected_measurements();
    const entities = get_selected_entities();
    fetch('/data/filtered_data_flat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({'measurements': measurements, 'entities': entities})
    })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            create_datatable(data, selected_table)
        })
        .catch(error => {
            console.log(error)
        })
}

function get_filtered_data_by_measurement(selected_table) {

}

function get_selected_measurements() {
    const parent = document.getElementById('measurement');
    const children = Array.from(parent.childNodes);
    return children.filter((x) => x.selected).map((x) => x.value);
}

function get_selected_entities() {
    const parent = document.getElementById('table_browser_entities_select');
    const children = Array.from(parent.childNodes);
    return children.filter((x) => x.selected).map((x) => x.value);
}

function create_datatable(data, selected_table) {
    let column;
    if (selected_table === 'long') {
        column = [
             {title: 'name_id'},
             {title: 'measurement'},
             {title: 'key'},
             {title: 'values'}
         ]
    } else if (selected_table === 'short') {
        // column = ?
    }
     $('#serverside_table').DataTable({
         destroy: true,
         data: data,
         Dom: 'lrtip',
         select: {style: 'multi'},
         scrollX: true,
         sPaginationType: 'full_numbers',
         lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
         columns: column,
     });
    // const column = $('#tab').attr('column');
    // if (column !== undefined){
    //     const column =  JSON.parse($('#tab').attr('column').replace(/'/g, '"'));
    //     $('#serverside_table').DataTable({
    //         data: data,
    //         select: {style: 'multi'},
    //         sDom: 'lrtip',
    //         bProcessing: true,
    //         bServerSide: true,
    //         scrollX: true,
    //         sPaginationType: "full_numbers",
    //         lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
    //         bjQueryUI: true,
    //         columns: column
    //     });
    // }
}
