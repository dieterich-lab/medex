"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.get_measurement_display_name = exports.configure_multiple_measurement_select = exports.configure_single_measurement_select = exports.init = void 0;
var misc_js_1 = require("../utility/misc.ts");
var http_js_1 = require("../utility/http.ts");
var measurement_list_promise = null;
var measurement_list = null;
var measurement_display_name = null;
function init() {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    if (!measurement_list_promise) {
                        measurement_list_promise = (0, http_js_1.http_fetch)('GET', '/measurement/', load_data, null, false);
                    }
                    return [4 /*yield*/, measurement_list_promise];
                case 1:
                    _a.sent();
                    return [2 /*return*/];
            }
        });
    });
}
exports.init = init;
function load_data(measurement_info) {
    return __awaiter(this, void 0, void 0, function () {
        var info;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, measurement_info];
                case 1:
                    info = _a.sent();
                    measurement_display_name = info['display_name'];
                    measurement_list = info['values'];
                    return [2 /*return*/];
            }
        });
    });
}
function get_measurement_display_name_async(plural) {
    if (plural === void 0) { plural = false; }
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, init()];
                case 1:
                    _a.sent();
                    return [2 /*return*/, get_measurement_display_name(plural)];
            }
        });
    });
}
function get_measurement_display_name(plural) {
    if (plural === void 0) { plural = false; }
    var name = measurement_display_name ? measurement_display_name : 'Measurement';
    return plural ? "".concat(name, "s") : name;
}
exports.get_measurement_display_name = get_measurement_display_name;
function configure_single_measurement_select(id, parent_id, initial_value, allow_none) {
    if (initial_value === void 0) { initial_value = null; }
    if (allow_none === void 0) { allow_none = false; }
    return __awaiter(this, void 0, void 0, function () {
        var initial_values;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    initial_values = initial_value === null ? [] : [initial_value];
                    return [4 /*yield*/, render_select_html(id, parent_id, false, allow_none)];
                case 1:
                    _a.sent();
                    add_select2_component(id, initial_values, allow_none);
                    return [2 /*return*/];
            }
        });
    });
}
exports.configure_single_measurement_select = configure_single_measurement_select;
function render_select_html(id, parent_id, allow_multiple, allow_none) {
    return __awaiter(this, void 0, void 0, function () {
        var multiple, label, measurement_values, display, options;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    multiple = allow_multiple ? 'multiple' : '';
                    return [4 /*yield*/, get_measurement_display_name_async(allow_multiple)];
                case 1:
                    label = _a.sent();
                    return [4 /*yield*/, get_measurement_list()];
                case 2:
                    measurement_values = _a.sent();
                    display = measurement_values.length > 1 ? 'block' : 'none';
                    return [4 /*yield*/, get_options(allow_multiple, allow_none)];
                case 3:
                    options = _a.sent();
                    document.getElementById(parent_id).innerHTML = "\n        <div class=\"form-group\" style=\"display: ".concat(display, "\">\n            <label for=\"").concat(id, "\">").concat(label, ":</label>\n            <select ").concat(multiple, " id=\"").concat(id, "\" style=\"width: 100%\">\n                ").concat(options, "\n            </select>\n        </div>\n    ");
                    return [2 /*return*/];
            }
        });
    });
}
function get_options(allow_multiple, allow_none) {
    return __awaiter(this, void 0, void 0, function () {
        var options_as_list, measurement_values;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    options_as_list = [];
                    if (allow_multiple) {
                        options_as_list.push("\n               <option value=\"Select all\">Select all</option>");
                    }
                    else {
                        if (allow_none) {
                            options_as_list.push("\n               <option value=\"\">None</option>");
                        }
                        else {
                            options_as_list.push("\n               <option value=\"\" disabled selected>Search entity</option>");
                        }
                    }
                    return [4 /*yield*/, get_measurement_list()];
                case 1:
                    measurement_values = _a.sent();
                    options_as_list.push.apply(options_as_list, measurement_values.map(function (x) {
                        return "\n        \t    <option value=\"".concat(x, "\">").concat(x, "</option>");
                    }));
                    return [2 /*return*/, options_as_list.join('')];
            }
        });
    });
}
function add_select2_component(id, initial_values, allow_none) {
    var element = $("#".concat(id));
    var select2_properties = allow_none ? {} : { placeholder: "Search entity" };
    element.select2(select2_properties);
    element.on("select2:select", function (e) { return (0, misc_js_1.handle_select_special_choices)(e, id); });
    initial_values.forEach(function (x) { return $("#".concat(id, " > option[value=\"").concat(x, "\"]")).prop("selected", true); });
    $("#".concat(id, " > option[value=\"\"]")).prop("selected", false);
    element.trigger("change");
}
function configure_multiple_measurement_select(id, parent_id, initial_values) {
    if (initial_values === void 0) { initial_values = null; }
    return __awaiter(this, void 0, void 0, function () {
        var cooked_initial_values, _a;
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0:
                    if (!(initial_values === null)) return [3 /*break*/, 2];
                    return [4 /*yield*/, get_measurement_list()];
                case 1:
                    _a = _b.sent();
                    return [3 /*break*/, 3];
                case 2:
                    _a = initial_values;
                    _b.label = 3;
                case 3:
                    cooked_initial_values = _a;
                    return [4 /*yield*/, render_select_html(id, parent_id, true, false)];
                case 4:
                    _b.sent();
                    add_select2_component(id, cooked_initial_values, false);
                    return [2 /*return*/];
            }
        });
    });
}
exports.configure_multiple_measurement_select = configure_multiple_measurement_select;
function get_measurement_list() {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, init()];
                case 1:
                    _a.sent();
                    return [2 /*return*/, measurement_list];
            }
        });
    });
}
