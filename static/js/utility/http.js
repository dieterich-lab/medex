import {report_error, clear_error, HTTPError, UserError} from "./error.js";

function http_fetch(
    method, uri,
    process_data = null,
    process_error=null,
    clear_error_flag=true
) {
    return fetch(uri, {'method': method})
    .then(response => handle_response(response))
    .then(data => handle_data(data, process_data, clear_error_flag))
    .catch(error => handle_error(error, process_error, method, uri));
}

function handle_response(response) {
    if (response.ok) {
        return response.json();
    } else {
        return Promise.reject(response);
    }
}

function handle_data(data, process_data, clear_error_flag) {
    if (clear_error_flag) {
        clear_error();
    }
    if (process_data) {
        process_data(data);
    }
}

function handle_error(error, process_error, method, uri) {
    const cooked_error = get_cooked_error(method, uri, error);
    report_error(cooked_error);
    if ( process_error ) {
        process_error(error);
    }
}

function get_cooked_error(method, uri, error) {
    if (error instanceof UserError) {
        return error;
    }
    const annotation = `Failed on ${method} ${uri}:`;
    if ('status' in error && 'statusText' in error) {
        return new HTTPError(`${annotation} ${error.status} ${error.statusText}`);
    }
    if (error instanceof Error) {
        error.message = `${annotation} ${error.message}`;
        return error;
    }
    return `${annotation} ${error}`;
}

function http_send_as_json(
    method, uri, data,
    process_data=null,
    process_error=null,
    clear_error_flag=true
) {
    return fetch(
        uri, {
            'method': method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data),
        }
    )
    .then(response => handle_response(response))
    .then(data => handle_data(data, process_data, clear_error_flag))
    .catch(error => handle_error(error, process_error, method, uri));
}

export {http_fetch, http_send_as_json};
