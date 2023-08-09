import {http_fetch, http_send_as_json} from "../utility/http";
import {assertEquals} from "typia";

interface FilterStatus {
    filtered_patient_count: number | null,
    filters: Map<string, CategoricalFilter|NumericalFilter>,
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

interface DeleteRequest {
    entity: string,
}

interface AddOrUpdateCategoricalRequest {
    entity: string,
    measurement: string | null,
    categories: string[],
}

interface AddOrUpdateNumericalRequest {
    entity: string,
    measurement: string | null,
    from_value: number,
    to_value: number,
}

let filter_status_revision: number = 0;

async function get_filter_status(): Promise<FilterStatus> {
    let work = await http_fetch(
        'GET', '/filter/all',
        false
    );
    // Seems that typia has some limitations with Maps.
    // So we have to that manually.
    if ( work?.filters instanceof Object ) {
        const orig_filters = work.filters;
        work.filters = new Map<string, CategoricalFilter|NumericalFilter>();
        for ( const [entity_key, raw_filter] of Object.entries(orig_filters) ) {
            if ( raw_filter instanceof Object ) {
                const cooked_filter = {...raw_filter, entity_key: entity_key}
                work.filters.set(entity_key, assertEquals<CategoricalFilter|NumericalFilter>(cooked_filter));
            } else {
                throw new Error(`Internal Error: Bad filter: ${JSON.stringify(raw_filter)}`);
            }
        }
    }
    return assertEquals<FilterStatus>(work);
}

async function delete_all_filters() {
    await http_fetch('DELETE', '/filter/all', false);
    filter_status_revision += 1;
}

async function delete_filter(entity_key: string) {
    await http_send_as_json<DeleteRequest>(
        'DELETE', '/filter/delete',
        {entity: entity_key},
        false
    );
    filter_status_revision += 1;
}

async function add_or_update_categorical_filter(entity_key: string, categories: string[], measurement: string|null) {
    await http_send_as_json<AddOrUpdateCategoricalRequest>(
        'POST', '/filter/add_categorical',
        {'entity': entity_key, 'measurement': measurement, 'categories': categories},
        false
    );
    filter_status_revision += 1;
}

async function add_or_update_numerical_filter(
    entity_key: string, from_value: number, to_value: number, measurement: string|null
) {
    const request_json = {
        entity: entity_key,
        measurement: measurement,
        from_value: from_value,
        to_value: to_value,
    };

    await http_send_as_json<AddOrUpdateNumericalRequest>(
        'POST','/filter/add_numerical',
        request_json,
        false
    );
    filter_status_revision += 1;
}

function get_filter_status_revision(): number {
    return filter_status_revision;
}

export {
    FilterStatus, CategoricalFilter, NumericalFilter,
    get_filter_status, delete_all_filters, delete_filter,
    add_or_update_categorical_filter, add_or_update_numerical_filter,
    get_filter_status_revision
};
