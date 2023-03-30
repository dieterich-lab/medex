import {http_fetch} from "../utility/http.mjs";

interface DatabaseInfo {
    number_of_patients: number
    number_of_numerical_entities: number
    number_of_categorical_entities: number
    number_of_date_entities: number
    number_of_numerical_data_items: number
    number_of_categorical_data_items: number
    number_of_date_data_items: number
}

let info_promise = null;
let info: DatabaseInfo = null;

async function init() {
    if ( ! info_promise ) {
        info_promise = http_fetch(
            'GET', '/database_info/',
            async db_info => { info = await db_info },
            null, false
        );
    }
    await info_promise;
}

async function get_database_info(): Promise<DatabaseInfo> {
    await init();
    return info;
}

export {get_database_info};
