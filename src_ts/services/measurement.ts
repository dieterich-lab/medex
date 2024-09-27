import {http_fetch} from "../utility/http";
import {assertEquals} from "typia";

interface MeasurementInfoRaw {
    display_name?: string | null,
    values: string[],
}

let raw_measurement_info_promise = http_fetch(
    'GET', '/measurement/',
    'loading measurements',
    false,
    false
);
let measurement_info_promise = async_assert_equals(raw_measurement_info_promise);

async function async_assert_equals(raw: Promise<any>): Promise<MeasurementInfoRaw> {
    return assertEquals<MeasurementInfoRaw>(await raw);
}

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
    const info = await measurement_info_promise;
    if ( ! info ) {
        throw new Error('Failed to load database info.');
    }
    return new MeasurementInfo(info);
}

export {MeasurementInfoRaw, get_measurement_info};