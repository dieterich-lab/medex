import {http_fetch} from '../utility/http';
import {assertEquals} from "typia";

interface DatabaseInfo {
    number_of_patients: number
    number_of_numerical_entities: number
    number_of_categorical_entities: number
    number_of_date_entities: number
    number_of_numerical_data_items: number
    number_of_categorical_data_items: number
    number_of_date_data_items: number
}

let info_promise_raw = http_fetch(
    'GET', '/database_info/',
    'loading database info',
    false,
    false
);
let info_promise = async_assert_equals(info_promise_raw);

async function async_assert_equals(x: Promise<any>): Promise<DatabaseInfo> {
    return assertEquals<DatabaseInfo>(await x);
}

async function get_database_info(): Promise<DatabaseInfo> {
    const info = await info_promise;
    if ( info ) {
        return info;
    } else {
        throw new Error('Internal error - failed get database info.');
    }
}

export {get_database_info, DatabaseInfo};
