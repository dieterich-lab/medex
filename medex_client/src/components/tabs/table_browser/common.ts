import {Entity} from "../../../services/entity";

enum TableFormat{
    Flat = 'flat',
    ByMeasurement = 'by_measurement',
}

interface TableBrowserResultParameters {
    measurements: string[],
    entities: Entity[],
    format: TableFormat,
}

export {TableFormat, type TableBrowserResultParameters};