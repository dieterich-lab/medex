import {assertEquals} from "typia";

interface FilterStatus {
    filtered_patient_count: number | null,
    filters: Map<string, CategoricalFilter|NumericalFilter>,
}

interface RawFilterStatus {
    filtered_patient_count: string | number | null,
    filters: Map<string, object>,
}

interface GenericFilter {
    entity_key: string,
    measurement: string | null,
}

interface CategoricalFilter extends GenericFilter {
    categories: string[],
}

interface NumericalFilter extends GenericFilter {
    from_value: number,
    to_value: number,
}

async function to_filter_status(raw: unknown): Promise<FilterStatus> {
    // Seems that typia has some limitations with Maps.
    // So we have to that manually.
    const almost_raw = raw as RawFilterStatus;
    if ( almost_raw?.filters ) {
        const orig_filters = almost_raw.filters;
        almost_raw.filters = new Map<string, CategoricalFilter|NumericalFilter>();
        for ( const [entity_key, raw_filter] of Object.entries(orig_filters) ) {
            if ( raw_filter instanceof Object ) {
                const cooked_filter = {...raw_filter, entity_key: entity_key}
                almost_raw.filters.set(entity_key, assertEquals<CategoricalFilter|NumericalFilter>(cooked_filter));
            } else {
                throw new Error(`Internal Error: Bad filter: ${JSON.stringify(raw_filter)}`);
            }
        }
    }
    return assertEquals<FilterStatus>(almost_raw);
}

export {
    type FilterStatus, type CategoricalFilter, type NumericalFilter,
    to_filter_status
};
