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
exports.ShowMarker = exports.EntityType = exports.try_get_entity_by_key = exports.try_get_entity_list = exports.get_entity_by_key = exports.get_entity_list = void 0;
var http_js_1 = require("../utility/http.ts");
var EntityType;
(function (EntityType) {
    EntityType["NUMERICAL"] = "Double";
    EntityType["CATEGORICAL"] = "String";
    EntityType["DATE"] = "Date";
})(EntityType || (EntityType = {}));
exports.EntityType = EntityType;
var ShowMarker;
(function (ShowMarker) {
    ShowMarker["SHOW"] = "+";
})(ShowMarker || (ShowMarker = {}));
exports.ShowMarker = ShowMarker;
var entity_list_promise = null;
var entity_list = null;
var entities_by_key = null;
function init() {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    if (!entity_list_promise) {
                        entity_list_promise = (0, http_js_1.http_fetch)('GET', '/entity/all', load_data, null, false);
                    }
                    return [4 /*yield*/, entity_list_promise];
                case 1:
                    _a.sent();
                    return [2 /*return*/];
            }
        });
    });
}
function load_data(new_entity_list) {
    return __awaiter(this, void 0, void 0, function () {
        var _i, entity_list_1, entity;
        return __generator(this, function (_a) {
            entity_list = new_entity_list;
            entities_by_key = new Map();
            for (_i = 0, entity_list_1 = entity_list; _i < entity_list_1.length; _i++) {
                entity = entity_list_1[_i];
                entities_by_key[entity.key] = entity;
            }
            return [2 /*return*/];
        });
    });
}
function get_entity_list() {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    if (!(entity_list == null)) return [3 /*break*/, 2];
                    return [4 /*yield*/, init()];
                case 1:
                    _a.sent();
                    _a.label = 2;
                case 2: return [2 /*return*/, entity_list];
            }
        });
    });
}
exports.get_entity_list = get_entity_list;
function get_entity_by_key(entity_key) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    if (!(entities_by_key == null)) return [3 /*break*/, 2];
                    return [4 /*yield*/, init()];
                case 1:
                    _a.sent();
                    _a.label = 2;
                case 2: return [2 /*return*/, entities_by_key[entity_key]];
            }
        });
    });
}
exports.get_entity_by_key = get_entity_by_key;
// The try_* functions work around limitations of the old bootstrap 4.X code,
// which can't handle async function/promises. It should be removed once we
// move to HTML5 and/or a bootstrap version based on it.
function try_get_entity_list() {
    if (entity_list == null) {
        return null;
    }
    return entity_list;
}
exports.try_get_entity_list = try_get_entity_list;
function try_get_entity_by_key(entity_key) {
    if (entities_by_key == null) {
        return null;
    }
    return entities_by_key[entity_key];
}
exports.try_get_entity_by_key = try_get_entity_by_key;
