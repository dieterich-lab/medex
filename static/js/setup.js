import * as patient_filter from "./patient_filter.js";
import * as basic_stats_categorical from "./basic_stats_categorical.js";

async function init() {
    await patient_filter.init();
    await basic_stats_categorical.init();
}

window.patient_filter = patient_filter;
document.addEventListener("DOMContentLoaded", init);
