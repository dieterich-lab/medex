import {switch_nav_item} from "../utility/nav.js";

async function init() {
    switch_nav_item('logout');
}

document.addEventListener("DOMContentLoaded", init);