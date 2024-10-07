import {assertEquals} from "typia";

interface MeasurementInfoRaw {
    display_name?: string | null,
    values: string[],
}

function to_measurement_info_raw(raw: unknown): MeasurementInfoRaw {
    return assertEquals<MeasurementInfoRaw>(raw);
}

export {type MeasurementInfoRaw, to_measurement_info_raw};
