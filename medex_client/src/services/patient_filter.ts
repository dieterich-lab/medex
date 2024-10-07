import {http_fetch, http_send_as_json} from "../utility/http";
import {to_filter_status, FilterStatus, CategoricalFilter, NumericalFilter} from "../typia/patient_filter.ts";

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
    const raw = await http_fetch(
        'GET', '/filter/all',
        'refreshing filter status',
        false,
        false
    )
    return to_filter_status(raw)
}

async function delete_all_filters() {
    await http_fetch('DELETE', '/filter/all', 'deleting filters').catch(() => {});
    filter_status_revision += 1;
}

async function delete_filter(entity_key: string) {
    await http_send_as_json<DeleteRequest>(
        'DELETE', '/filter/delete',
        {entity: entity_key},
        'deleting filter'
    ).catch(() => {});
    filter_status_revision += 1;
}

async function add_or_update_categorical_filter(entity_key: string, categories: string[], measurement: string|null) {
    await http_send_as_json<AddOrUpdateCategoricalRequest>(
        'POST', '/filter/add_categorical',
        {'entity': entity_key, 'measurement': measurement, 'categories': categories},
        'adding filter'
    ).catch(() => {});
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
        'adding filter'
    ).catch(() => {});
    filter_status_revision += 1;
}

function get_filter_status_revision(): number {
    return filter_status_revision;
}

export {
    type FilterStatus, type CategoricalFilter, type NumericalFilter,
    get_filter_status, delete_all_filters, delete_filter,
    add_or_update_categorical_filter, add_or_update_numerical_filter,
    get_filter_status_revision
};
