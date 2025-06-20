import {Cache} from "../utility/cache.ts";
import {http_fetch} from "../utility/http.ts";

class MyCache extends Cache<Map<string, string>> {
    get_raw_promise() {
        return http_fetch(
            'GET', '/message_catalog.json',
            'loading message catalog',
            false,
            false
        );
    }
    decode(raw: unknown): Map<string, string> {
        return new Map(Object.entries(raw as object))
    }
}

const my_cache = new MyCache();

async function get_message(x: string): Promise<string> {
    const entry = (await my_cache.get_data()).get(x)
    return entry === undefined ? x : entry;
}

export {get_message};
