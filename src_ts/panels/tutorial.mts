import {switch_nav_item} from "../utility/nav.mjs";

async function init() {
    switch_nav_item('tutorial');
}

document.addEventListener("DOMContentLoaded", init);