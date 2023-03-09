import * as patient_filter from "./patient_filter.js";
import * as database_info from "./basic_stats/database_info.js";
import * as basic_stats from "./basic_stats/entities_info.js";
import * as plot_barchart from "./plots/barchart.js";
import * as plot_boxplot from "./plots/boxplot.js";
import * as plot_heatmap from "./plots/heatmap.js";
import * as plot_histogram from "./plots/histogram.js";
import * as plot_scatter_plot from "./plots/scatter_plot.js";

async function init() {
    await patient_filter.init();
}

window.patient_filter = patient_filter;
window.database_info = database_info;
window.basic_stats = basic_stats;
window.plot_barchart = plot_barchart;
window.plot_boxplot = plot_boxplot;
window.plot_heatmap = plot_heatmap;
window.plot_histogram = plot_histogram;
window.plot_scatter_plot = plot_scatter_plot;

document.addEventListener("DOMContentLoaded", init);
