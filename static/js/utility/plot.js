import {create_download_link, remove_download_link, show_collapsed} from "./misc.js";
import {report_error, UserError} from "./error.js";
import {http_fetch} from "./http.js";

class Plot {
    handle_plot() {
        try {
            const query_parameters = this.get_query_parameters();
            const base_url = this.get_plot_url();
            const url = `${base_url}?${query_parameters}`;
            http_fetch('GET', url, data => this.process_results(data, query_parameters));
        } catch (error) {
            this.clear_result();
            report_error(error);
        }
    }

    get_query_parameters() {
        throw TypeError('Please overwrite abstract method');
    }

    decode_data(data) {
        throw TypeError('Please overwrite abstract method');
    }

    get_name() {  // Used as default for many others
        throw TypeError('Please overwrite abstract method');
    }

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

    is_empty(data) {
            return data.data.length === 0;
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

export {Plot};
