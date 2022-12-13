import {handle_select_all_choices} from "./utility.js";

$(function () {
    $('.measurement').each(function() {
        $(this).on("select2:select", (e) => handle_select_all_choices(e, this.id));
    });
});