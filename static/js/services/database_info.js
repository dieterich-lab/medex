
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

export {get_database_info};
