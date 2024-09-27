import {HTTPError, UserError, clear_error, report_error, report_busy, clear_busy} from "./user_feedback";
import {capitalize} from "./misc";

type HTTP_METHOD = 'GET'|'PUT'|'POST'|'DELETE';


class FetchContext {
    private readonly method: HTTP_METHOD;
    readonly uri: string;
    readonly description: string | null;
    readonly report_busy_flag: boolean;
    readonly clear_error_flag: boolean;

    constructor(
        method: HTTP_METHOD,
        uri: string,
        description: string | null = null,
        report_busy_flag: boolean = true,
        clear_error_flag: boolean = false,
    ) {
        this.method = method;
        this.uri = uri;
        this.description = description;
        this.report_busy_flag = report_busy_flag;
        this.clear_error_flag = clear_error_flag;
    }

    async fetch(body?: string | Blob, headers?: any): Promise<any> {
        if ( this.report_busy_flag ) {
            const cooked_description = this.description ? this.description : `${this.method} ${this.uri}`;
            report_busy(`${capitalize(cooked_description)} ...`);
        }
        try {
            const response = await fetch(this.uri, {
                'method': this.method,
                'body': body,
                'headers': headers,
            });
            return await this.handle_response(response);
        }
        catch (error) {
            this.handle_error(error);
        }
        finally {
            if ( this.report_busy_flag ) {
                clear_busy()
            }
        }
    }

    private async handle_response(response: Response): Promise<any> {
        if (this.clear_error_flag) {
            clear_error();
        }
        if ( !response.ok ) {
            throw new HTTPError(`${response.status} ${response.statusText}`);
        }
        return await response.json();
    }

    private handle_error(error: any): never {
        const cooked_error = this.get_cooked_error(error);
        report_error(cooked_error);
        throw error;
    }

    private get_cooked_error(error: any): Error|string {
        if (error instanceof UserError) {
            return error;
        }
        let annotation = `Failed to ${this.method} ${this.uri}:`;
        if ( this.description ) {
            annotation = `While ${this.description}: ${annotation}`;
        }
        if (error instanceof Error) {
            error.message = `${annotation} ${error.message}`;
            return error;
        }
        return `${annotation} ${error}`;
    }
}

async function http_fetch(
    method: HTTP_METHOD,
    uri: string,
    description: string | null = null,
    report_busy_flag: boolean = true,
    clear_error_flag: boolean = true
): Promise<any> {
    let ctx = new FetchContext(method, uri, description, report_busy_flag, clear_error_flag);
    return await ctx.fetch()
}

async function http_send_as_json<T>(
    method: HTTP_METHOD,
    uri: string,
    data: T,
    description: string | null = null,
    report_busy_flag: boolean = true,
    clear_error_flag: boolean = true
): Promise<any> {
    let ctx = new FetchContext(method, uri, description, report_busy_flag, clear_error_flag);
    return await ctx.fetch(JSON.stringify(data), {'Content-Type': 'application/json'});
}

async function http_send_blob(
    uri: string,
    data: Blob,
    content_type: string,
    description: string | null = null,
    report_busy_flag: boolean = true,
    clear_error_flag: boolean = true,
) {
    let ctx = new FetchContext('POST', uri, description, report_busy_flag, clear_error_flag);
    return await ctx.fetch(data, {'Content-Type': content_type});
}

export {http_fetch, http_send_as_json, http_send_blob};
