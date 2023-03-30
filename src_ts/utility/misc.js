"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DOWNLOAD_DIV_ID = exports.remove_download_link = exports.create_download_link = exports.get_selected_categories = exports.get_selected_measurements = exports.get_selected_items = exports.show_collapsed = exports.handle_select_special_choices = void 0;
function handle_select_special_choices(event, element_id) {
    var selected_item = event.params.data.text;
    if (selected_item === 'Select all') {
        $("#".concat(element_id, "> option")).prop("selected", "selected");
        $("#".concat(element_id, "> option[value=\"Select all\"]")).prop("selected", false);
        $("#".concat(element_id, "> option[value=\"\"]")).prop("selected", false);
        $("#".concat(element_id)).trigger("change");
    }
    if (selected_item === 'Select none') {
        $("#".concat(element_id, "> option")).prop("selected", false);
        $("#".concat(element_id, "> option[value=\"\"]")).prop("selected", true);
        $("#".concat(element_id)).trigger("change");
    }
}
exports.handle_select_special_choices = handle_select_special_choices;
function show_collapsed(element_id) {
    var element = document.getElementById(element_id);
    if (!element.classList.contains('show')) {
        element.classList.add('show');
    }
}
exports.show_collapsed = show_collapsed;
function get_selected_items(element_id) {
    var parent = document.getElementById(element_id);
    var children = Array.from(parent.childNodes);
    return children.filter(function (x) { return x.selected; }).map(function (x) { return x.value; });
}
exports.get_selected_items = get_selected_items;
function get_selected_categories() {
    return get_selected_items('subcategory_entities');
}
exports.get_selected_categories = get_selected_categories;
function get_selected_measurements() {
    return get_selected_items('measurement');
}
exports.get_selected_measurements = get_selected_measurements;
var DOWNLOAD_DIV_ID = 'download_div';
exports.DOWNLOAD_DIV_ID = DOWNLOAD_DIV_ID;
function create_download_link(uri, file_name) {
    var div = document.getElementById(DOWNLOAD_DIV_ID);
    div.innerHTML = "\n        <div class=\"card-body\">\n            <a href=\"".concat(uri, "\" class=\"btn btn-outline-info\" download=\"").concat(file_name, "\">Download</a>\n        </div>\n    ");
}
exports.create_download_link = create_download_link;
function remove_download_link() {
    var div = document.getElementById(DOWNLOAD_DIV_ID);
    div.innerHTML = '';
}
exports.remove_download_link = remove_download_link;
