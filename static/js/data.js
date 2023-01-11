function display_table_with_selected_type() {
    const all_table_types = document.querySelectorAll('input[name="what_table"]');
    const measurements = get_selected_measurements();
    const entities = get_selected_entities();
    let selected_table;
    for (const table_type of all_table_types) {
        if (table_type.checked) {
            selected_table = table_type.value;
            create_datatable(selected_table, measurements, entities);
        }
    }
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

function create_datatable(selected_table, measurements, entities) {
    const url = selected_table === 'long' ? '/filtered_data/flat' : '/filtered_data/by_measurement';
    const column = define_table_columns(selected_table);
    const element = $('#serverside_table');
    if ($.fn.DataTable.isDataTable('#serverside_table')) {
        let table = element.DataTable();
        table.destroy();
        element.empty();
    }

    element.DataTable({
        destroy: true,
        processing: true,
        serverSide: true,
        ajax: {
            url: url,
            data: function (raw_data) {
                raw_data.table_data = JSON.stringify({
                    measurements: measurements,
                    entities: entities,

                });
            },
        },
        columns: column,
        sDom: 'lrtip',
        select: {style: 'multi'},
        scrollX: true,
        sPaginationType: 'full_numbers',
        lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
     });
}

function define_table_columns(selected_table) {
    let column = [
        {data: 'name_id', title: 'name_id'},
        {data: 'measurement', title: 'measurement'},
    ]
    if (selected_table === 'long') {
        column = column.concat([
            {data: 'key', title: 'key'},
            {data: 'value', title: 'value'},
        ]);
    } else if (selected_table === 'short') {
        const entities = get_selected_entities();
        const entity_columns = entities.map((x) => {
            return {data: `${x}`, title: `${x}`};
        });
        column = column.concat(entity_columns);
    }
    return column;
}
