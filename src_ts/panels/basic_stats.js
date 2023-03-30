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
var $ = require("jquery");
var measurement_js_1 = require("../services/measurement.js");
var entity_selection_js_1 = require("../utility/entity_selection.js");
var database_info_js_1 = require("../services/database_info.js");
var misc_js_1 = require("../utility/misc.js");
var nav_js_1 = require("../utility/nav.js");
require("datatables.net");
var DEFAULT_TABLE_COLUMNS = [
    { data: 'key', title: 'Entity' },
    { data: 'measurement', title: 'Visit' },
    { data: 'count', title: 'Counts' },
    { data: 'count NaN', title: 'Counts NaN' },
];
var NUMERICAL_TABLE_COLUMNS = [
    { data: 'key', title: 'Entity' },
    { data: 'measurement', title: 'Visit' },
    { data: 'count', title: 'Counts' },
    { data: 'count NaN', title: 'Counts NaN' },
    { data: 'min', title: 'Min' },
    { data: 'max', title: 'Max' },
    { data: 'mean', title: 'Mean' },
    { data: 'median', title: 'Median' },
    { data: 'stddev', title: 'Std. Deviation' },
    { data: 'stderr', title: 'Std. Error' },
];
var NUMERICAL_DESCRIPTOR = {
    'name': 'numerical',
    'table_columns': NUMERICAL_TABLE_COLUMNS,
};
var CATEGORICAL_DESCRIPTOR = {
    'name': 'categorical',
    'table_columns': DEFAULT_TABLE_COLUMNS,
};
var DATE_DESCRIPTOR = {
    'name': 'date',
    'table_columns': DEFAULT_TABLE_COLUMNS,
};
var ALL_ENTITY_DESCRIPTORS = [
    NUMERICAL_DESCRIPTOR,
    CATEGORICAL_DESCRIPTOR,
    DATE_DESCRIPTOR,
];
var init_promise = null;
function do_init() {
    return __awaiter(this, void 0, void 0, function () {
        var _i, ALL_ENTITY_DESCRIPTORS_1, descriptor, name_1;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    (0, nav_js_1.switch_nav_item)('basic_stats');
                    _i = 0, ALL_ENTITY_DESCRIPTORS_1 = ALL_ENTITY_DESCRIPTORS;
                    _a.label = 1;
                case 1:
                    if (!(_i < ALL_ENTITY_DESCRIPTORS_1.length)) return [3 /*break*/, 5];
                    descriptor = ALL_ENTITY_DESCRIPTORS_1[_i];
                    name_1 = descriptor.name;
                    return [4 /*yield*/, (0, measurement_js_1.configure_multiple_measurement_select)("basic_stats_measurement_".concat(name_1), "basic_stats_measurement_".concat(name_1, "_div"))];
                case 2:
                    _a.sent();
                    return [4 /*yield*/, (0, entity_selection_js_1.configure_entity_selection)("basic_stats_".concat(name_1, "_entities_select"), [], true, false)];
                case 3:
                    _a.sent();
                    _a.label = 4;
                case 4:
                    _i++;
                    return [3 /*break*/, 1];
                case 5: return [4 /*yield*/, show_database_info()];
                case 6:
                    _a.sent();
                    return [2 /*return*/];
            }
        });
    });
}
function init() {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    if (!(init_promise === null)) return [3 /*break*/, 2];
                    return [4 /*yield*/, do_init()];
                case 1:
                    init_promise = _a.sent();
                    _a.label = 2;
                case 2: return [2 /*return*/, init_promise];
            }
        });
    });
}
function show_database_info() {
    return __awaiter(this, void 0, void 0, function () {
        var info, element;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, (0, database_info_js_1.get_database_info)()];
                case 1:
                    info = _a.sent();
                    element = document.getElementById('database_tab_table_id');
                    element.innerHTML = "\n        <tr><td>Number of patients:</td><td>".concat(info.number_of_patients, "</td></tr>\n        <tr><td>Number of numerical entities:</td><td>").concat(info.number_of_numerical_entities, "</td></tr>\n        <tr><td>Number of numerical data items:</td><td>").concat(info.number_of_numerical_data_items, "</td></tr>\n        <tr><td>Number of categorical entities:</td><td>").concat(info.number_of_categorical_entities, "</td></tr>\n        <tr><td>Number of categorical data items:</td><td>").concat(info.number_of_categorical_data_items, "</td></tr>\n        <tr><td>Number of date entities:</td><td>").concat(info.number_of_date_entities, "</td></tr>\n        <tr><td>Number of date data items:</td><td>").concat(info.number_of_date_data_items, "</td></tr>\n    ");
                    return [2 /*return*/];
            }
        });
    });
}
function display_results(descriptor) {
    var name = descriptor.name;
    var measurements = (0, misc_js_1.get_selected_items)("basic_stats_measurement_".concat(name));
    var entities = (0, misc_js_1.get_selected_items)("basic_stats_".concat(name, "_entities_select"));
    var ok = check_for_user_errors(descriptor, measurements, entities);
    if (ok) {
        create_datatable(descriptor, measurements, entities);
        set_url_for_download(descriptor, measurements, entities);
    }
}
function check_for_user_errors(descriptor, measurements, entities) {
    var error = null;
    if (!measurements.length) {
        error = "Please select one or more visits";
    }
    else if (!entities.length) {
        error = "Please select one or more entities";
    }
    handle_error(descriptor, error);
    return error === null;
}
function handle_error(descriptor, error) {
    var name = descriptor.name;
    var div = document.getElementById("basic_stats_error_".concat(name));
    if (error) {
        div.innerHTML = "\n        <div class=\"alert alert-danger mt-2\" role=\"alert\">\n            ".concat(error, "\n            <span class=\"close\" aria-label=\"Close\"> &times;</span>\n        </div>\n        ");
    }
    else {
        div.innerHTML = '';
    }
}
function create_datatable(descriptor, measurements, entities) {
    var name = descriptor.name;
    var url = "/basic_stats/".concat(name);
    var query = "#".concat(name, "_table");
    var element = $(query);
    if ($.fn.dataTable.isDataTable(query)) {
        var table = element.DataTable();
        table.destroy();
        element.empty();
    }
    element.DataTable({
        processing: true,
        serverSide: true,
        info: false,
        paging: false,
        ordering: false,
        ajax: {
            url: url,
            data: function (raw_data) {
                raw_data.basic_stats_data = JSON.stringify({
                    measurements: measurements,
                    entities: entities,
                });
            },
        },
        columns: descriptor.table_columns,
        dom: 'lrtip',
    });
}
function set_url_for_download(descriptor, measurements, entities) {
    var name = descriptor.name;
    var search_params = new URLSearchParams({
        basic_stats_data: JSON.stringify({
            measurements: measurements,
            entities: entities,
        })
    });
    var url = "/basic_stats/".concat(name, "_csv? ").concat(search_params);
    var div = document.getElementById("basic_stats_".concat(name, "_csv_download"));
    div.innerHTML = "\n        <div class=\"card-body\">\n            <a href=\"".concat(url, "\" class=\"btn btn-outline-info\">Download</a>\n        </div>\n    ");
}
function display_numerical_results() {
    display_results(NUMERICAL_DESCRIPTOR);
}
function display_categorical_results() {
    display_results(CATEGORICAL_DESCRIPTOR);
}
function display_date_results() {
    display_results(DATE_DESCRIPTOR);
}
document.addEventListener("DOMContentLoaded", init);
window.display_numerical_results = display_numerical_results;
window.display_categorical_results = display_categorical_results;
window.display_date_results = display_date_results;
