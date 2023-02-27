import * as patient_filter from "./patient_filter.js";

async function init() {
    await patient_filter.init();
}

window.patient_filter = patient_filter;
document.addEventListener("DOMContentLoaded", init);
