import {create_download_link, remove_download_link, show_collapsed} from "./misc.mjs";
import {report_error, UserError} from "./error.mjs";
import {http_fetch} from "./http.mjs";

declare global {
    interface Window {
        display_results: () => void;
        // Plotly violently resits to be lowed via rollup ... so we load it separately
        Plotly: {
            react: (any, data, p: {}) => any,
        }
    }
}

abstract class Plot<Data> {
    handle_plot() {
        try {
            const query_parameters = this.get_query_parameters();
            const base_url = this.get_plot_url();
            const url = `${base_url}?${query_parameters}`;
            return http_fetch('GET', url, data => this.process_results(data, query_parameters));
        } catch (error) {
            this.clear_result();
            report_error(error);
            return Promise.reject()
        }
    }

    abstract get_query_parameters(): URLSearchParams;
    abstract decode_data(data: Data): void;
    abstract get_name(): string;
    abstract is_empty(data: Data): boolean;

    get_plot_url() {
        return `/${this.get_name()}/json`;
    }

    get_download_url() {
        return `/${this.get_name()}/download`;
    }

    get_download_file_name() {
        return `${this.get_name()}.svg`;
    }

    get_plot_divs() {
        return ['plot_div'];
    }

    process_results(data, query_parameters) {
        if (this.is_empty(data)) {
            this.clear_result();
            throw new UserError('No matching data found to display');
        }
        this.decode_data(data);
        const download_url = this.get_download_url();
        create_download_link(`${download_url}?${query_parameters}`, this.get_download_file_name());
        show_collapsed('results_div')
    }

    clear_result() {
        remove_download_link();
        for (const element_id of this.get_plot_divs()) {
            let div = document.getElementById(element_id);
            div.innerHTML = '';
            div.removeAttribute('class');
        }
    }
}

function setup_plot<Data>(plot: Plot<Data>, init: () => void) {
    window.display_results = () => plot.handle_plot();
    document.addEventListener("DOMContentLoaded", init);
}

const Plotly = window.Plotly;

export {Plot, Plotly, setup_plot};
