import {http_fetch} from "../utility/http.js";

let info_promise = null;
let info = null;

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

async function get_database_info() {
    await init();
    return info;
}

export {get_database_info};
