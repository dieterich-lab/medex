"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.HTTPError = exports.UserError = exports.clear_error = exports.report_error = void 0;
var UserError = /** @class */ (function (_super) {
    __extends(UserError, _super);
    function UserError() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return UserError;
}(Error));
exports.UserError = UserError;
var HTTPError = /** @class */ (function (_super) {
    __extends(HTTPError, _super);
    function HTTPError() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return HTTPError;
}(Error));
exports.HTTPError = HTTPError;
function report_error(error) {
    var message = error instanceof Error ? error.message : error;
    if (!(error instanceof UserError) && !(error instanceof HTTPError) && error instanceof Error) {
        console.log(error.stack);
    }
    var div = document.getElementById('error_div');
    div.innerHTML = "\n        <div class=\"alert alert-danger mt-2\" role=\"alert\">\n            ".concat(message, "\n            <span id=\"error_close_button\" class=\"close\" aria-label=\"Close\"> &times;</span>\n        </div>\n    ");
    var close_button = document.getElementById('error_close_button');
    close_button.addEventListener('click', clear_error);
}
exports.report_error = report_error;
function clear_error() {
    var div = document.getElementById('error_div');
    div.innerHTML = null;
}
exports.clear_error = clear_error;
