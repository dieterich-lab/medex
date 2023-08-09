"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.http_send_as_json = exports.http_fetch = void 0;
var error_js_1 = require("./error.ts");
function http_fetch(method, uri, process_data, process_error, clear_error_flag) {
    if (process_data === void 0) { process_data = null; }
    if (process_error === void 0) { process_error = null; }
    if (clear_error_flag === void 0) { clear_error_flag = true; }
    return fetch(uri, { 'method': method })
        .then(function (response) { return handle_response(response); })
        .then(function (data) { return handle_data(data, process_data, clear_error_flag); })
        .catch(function (error) { return handle_error(error, process_error, method, uri); });
}
exports.http_fetch = http_fetch;
function handle_response(response) {
    if (response.ok) {
        return response.json();
    }
    else {
        return Promise.reject(response);
    }
}
function handle_data(data, process_data, clear_error_flag) {
    if (clear_error_flag) {
        (0, error_js_1.clear_error)();
    }
    if (process_data) {
        process_data(data);
    }
}
function handle_error(error, process_error, method, uri) {
    var cooked_error = get_cooked_error(method, uri, error);
    (0, error_js_1.report_error)(cooked_error);
    if (process_error) {
        process_error(error);
    }
}
function get_cooked_error(method, uri, error) {
    if (error instanceof error_js_1.UserError) {
        return error;
    }
    var annotation = "Failed on ".concat(method, " ").concat(uri, ":");
    if ('status' in error && 'statusText' in error) {
        return new error_js_1.HTTPError("".concat(annotation, " ").concat(error.status, " ").concat(error.statusText));
    }
    if (error instanceof Error) {
        error.message = "".concat(annotation, " ").concat(error.message);
        return error;
    }
    return "".concat(annotation, " ").concat(error);
}
function http_send_as_json(method, uri, data, process_data, process_error, clear_error_flag) {
    if (process_data === void 0) { process_data = null; }
    if (process_error === void 0) { process_error = null; }
    if (clear_error_flag === void 0) { clear_error_flag = true; }
    return fetch(uri, {
        'method': method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    })
        .then(function (response) { return handle_response(response); })
        .then(function (data) { return handle_data(data, process_data, clear_error_flag); })
        .catch(function (error) { return handle_error(error, process_error, method, uri); });
}
exports.http_send_as_json = http_send_as_json;
