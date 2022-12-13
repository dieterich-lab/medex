import * as patient_filter from "./patient_filter.js";
import * as basic_stats_categorical from "./basic_stats_categorical.js";
import * as scatter_plot from "./scatter_plot.js";

async function init() {
    await patient_filter.init();
    await basic_stats_categorical.init();
    await scatter_plot.init();
}

window.patient_filter = patient_filter;
document.addEventListener("DOMContentLoaded", init);
