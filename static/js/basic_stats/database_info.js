
let info_promise = null;
let info = null;

async function load_data() {
    if ( ! info_promise ) {
         info_promise = fetch('/database_info/', {method: 'GET'})
            .then(response => response.json())
            .then(async db_info => {
                info = await db_info;
            })
            .catch(error => {
                console.log(error)
        })
    }
    await info_promise;
}

async function get_database_info() {
    await load_data();
    return info;
}

async function init() {
    const info = await get_database_info();
    let element = document.getElementById('database_tab_table_id');
    element.innerHTML = `
        <tr><td>Number of patients:</td><td>${ info.number_of_patients }</td></tr>
        <tr><td>Number of numerical entities:</td><td>${ info.number_of_numerical_entities }</td></tr>
        <tr><td>Number of numerical data items:</td><td>${ info.number_of_numerical_data_items }</td></tr>
        <tr><td>Number of categorical entities:</td><td>${ info.number_of_categorical_entities }</td></tr>
        <tr><td>Number of categorical data items:</td><td>${ info.number_of_categorical_data_items }</td></tr>
        <tr><td>Number of date entities:</td><td>${ info.number_of_date_entities }</td></tr>
        <tr><td>Number of date data items:</td><td>${ info.number_of_date_data_items }</td></tr>
    `;
}

export {init};
