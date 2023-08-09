import {HTTPError, UserError, clear_error, report_error} from "./error";

type HTTP_METHOD = 'GET'|'PUT'|'POST'|'DELETE';

async function http_fetch(
    method: HTTP_METHOD,
    uri: string,
    clear_error_flag: boolean = true
): Promise<any> {
    try {
        const response = await fetch(uri, {'method': method});
        return handle_response(response, clear_error_flag);
    }
    catch (error) {
        handle_error(error, method, uri)
    }
}

async function handle_response(response: Response, clear_error_flag: boolean): Promise<any> {
    if (clear_error_flag) {
        clear_error();
    }
    if ( !response.ok ) {
        throw new HTTPError(`${response.status} ${response.statusText}`);
    }
    return await response.json();
}

function handle_error(error: any, method: HTTP_METHOD, uri: string): never {
    const cooked_error = get_cooked_error(method, uri, error);
    report_error(cooked_error);
    throw error;
}

function get_cooked_error(method: HTTP_METHOD, uri: string, error: any): Error|string {
    if (error instanceof UserError) {
        return error;
    }
    const annotation = `Failed on ${method} ${uri}:`;
    if (error instanceof Error) {
        error.message = `${annotation} ${error.message}`;
        return error;
    }
    return `${annotation} ${error}`;
}

async function http_send_as_json<T>(
    method: HTTP_METHOD,
    uri: string,
    data: T,
    clear_error_flag=true
): Promise<any> {
    try {
        const response = await fetch(uri, {
            'method': method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data),
        });
        return handle_response(response, clear_error_flag);
    }
    catch (error) {
        handle_error(error, method, uri)
    }
}

export {http_fetch, http_send_as_json};
