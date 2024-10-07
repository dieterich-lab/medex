import {http_fetch} from "../utility/http";
import {to_measurement_info_raw, MeasurementInfoRaw} from "../typia/measurement_info_raw.ts";
import {Cache} from "../utility/cache.ts";


class MyCache extends Cache<MeasurementInfoRaw> {
    get_raw_promise() {
        return http_fetch(
            'GET', '/measurement/',
            'loading measurements',
            false,
            false
        );
    }

    decode(raw: unknown) {
        return to_measurement_info_raw(raw)
    }
}

const my_cache = new MyCache();

class MeasurementInfo {
    readonly values: string[];
    raw_display_name?: string | null;

    constructor(new_raw: MeasurementInfoRaw) {
        this.values = new_raw.values;
        this.raw_display_name = new_raw.display_name;
    }

    public get_display_name(plural_flag: boolean): string {
        const name = this.raw_display_name ? this.raw_display_name : 'Measurement';
        return plural_flag ? `${name}s` : name;
    }
}

async function get_measurement_info(): Promise<MeasurementInfo> {
    return new MeasurementInfo(await my_cache.get_data());
}

export {MeasurementInfo, get_measurement_info};