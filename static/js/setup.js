import * as patient_filter from "./patient_filter.js";
import {configure_entity_selection} from "./entity_selection.js";

async function init() {
    await patient_filter.init();
}

window.patient_filter = patient_filter;
document.addEventListener("DOMContentLoaded", init);
