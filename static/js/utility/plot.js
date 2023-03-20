import {create_download_link, process_fetch, show_collapsed} from "./misc.js";
import {report_error} from "./error.js";

function handle_plot(descriptor) {
    try {
        const query_parameters = descriptor.get_query_parameters();
        const url = `${descriptor.plot_url}?${query_parameters}`;
        process_fetch('GET', url, data => process_results(descriptor, data, query_parameters));
    }
    catch(error) {
        report_error(error);
    }
}

function process_results(descriptor, data, query_parameters) {
    if (data.data.length === 0) {
        throw 'No matching data found to display';
    }
    descriptor.decode_data(data);
    create_download_link(
        `${descriptor.download_url}?${query_parameters}`,
        descriptor.download_file_name
    );
    show_collapsed('results_div')
}

export {handle_plot};