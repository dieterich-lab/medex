import {Cache} from "../utility/cache.ts";
import {AppConfig, to_app_config} from "../typia/app_config.ts";
import {http_fetch} from "../utility/http.ts";

class MyCache extends Cache<AppConfig> {
    get_raw_promise() {
        return http_fetch(
            'GET', '/app_config.json',
            'loading application config',
            false,
            false
        );
    }
    decode(raw: unknown) {
        return to_app_config(raw)
    }
}

const my_cache = new MyCache();

async function get_app_config(): Promise<AppConfig> {
    return my_cache.get_data()
}

export {get_app_config, type AppConfig};
