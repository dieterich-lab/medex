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
exports.is_valid_entity = exports.configure_entity_selection = void 0;
var entity_js_1 = require("../services/entity.mts");
var SEARCH_ENTITY_PLACEHOLDER = 'Search Entity';
function format_entity(state) {
    var entity = (0, entity_js_1.try_get_entity_by_key)(state.id);
    if (!entity) {
        return "<div>(not loaded yet)</div>";
    }
    if (entity.description === null) {
        return $("<div>\n\t\t\t\t <div>".concat(entity.key, "</div>\n\t\t\t </div>"));
    }
    else {
        return $("<div>\n\t\t\t\t <div>".concat(entity.key, "</div>\n\t\t\t\t <div class=\"description\">").concat(entity.description, "</div>\n\t\t\t </div>"));
    }
}
function contains(text, search_string) {
    if (!text) {
        return false;
    }
    return text.toLowerCase().includes(search_string.toLowerCase());
}
function is_matching_entity(entity, valid_entity_types, search_string) {
    if (!valid_entity_types.includes(entity['type'])) {
        return false;
    }
    if (!search_string) {
        return true;
    }
    return contains(entity['key'], search_string)
        || contains(entity['description'], search_string);
}
function configure_entity_selection(element_id, selected_entity_ids, multiple_allowed, allow_select_all) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, render_select_entity_box(element_id, selected_entity_ids, multiple_allowed)];
                case 1:
                    _a.sent();
                    $("#".concat(element_id)).select2({
                        allowClear: allow_select_all,
                        width: "100%",
                        multiple: multiple_allowed,
                        templateResult: format_entity,
                    });
                    return [2 /*return*/];
            }
        });
    });
}
exports.configure_entity_selection = configure_entity_selection;
function render_select_entity_box(element_id, selected_entities, multiple_allowed) {
    return __awaiter(this, void 0, void 0, function () {
        var select_box, all_entities, entity_types, prefix, options_html;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    select_box = document.getElementById(element_id);
                    return [4 /*yield*/, (0, entity_js_1.get_entity_list)()];
                case 1:
                    all_entities = _a.sent();
                    entity_types = select_box.getAttribute('data-entity-types').split(',');
                    prefix = multiple_allowed ? '' : "<option>".concat(SEARCH_ENTITY_PLACEHOLDER, "</option>");
                    options_html = all_entities
                        .filter(function (x) { return entity_types.includes(x.type); })
                        .map(function (x) {
                        var selected_marker = selected_entities.includes(x.key) ? ' selected' : '';
                        return "\n        \t<option value=\"".concat(x.key, "\"").concat(selected_marker, ">").concat(x.key, "</option>");
                    });
                    select_box.innerHTML = prefix + options_html.join('') + '\n';
                    return [2 /*return*/];
            }
        });
    });
}
function is_valid_entity(name) {
    return (!!name && name !== '' && name !== SEARCH_ENTITY_PLACEHOLDER);
}
exports.is_valid_entity = is_valid_entity;
