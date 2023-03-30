import '../resources/style.css';
import $ from 'jquery';

declare global {
    interface Window {
        jQuery: (any) => any;
        JQuery: (any) => any;
    }
}

window.JQuery = $;
window.jQuery = $;

function init() {
    let nav_bar = document.getElementById('page');
    nav_bar.setAttribute('style', 'display: block');
}

document.addEventListener("DOMContentLoaded", init);

import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.css';