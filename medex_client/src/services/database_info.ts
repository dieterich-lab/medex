import {http_fetch} from '../utility/http';
import {to_database_info, DatabaseInfo} from "../typia/database_info.ts";
import {Cache} from '../utility/cache.ts';


class MyCache extends Cache<DatabaseInfo> {
    get_raw_promise() {
        return http_fetch(
            'GET', '/database_info/',
            'loading database info',
            false,
            false
        );
    }

    decode(raw: unknown) {
        return to_database_info(raw)
    }
}

const my_cache = new MyCache();

async function get_database_info(): Promise<DatabaseInfo> {
    return my_cache.get_data()
}

export {get_database_info, type DatabaseInfo};
