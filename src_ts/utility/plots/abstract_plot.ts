interface AbstractPlotParameters {
    filter_status_revision: number,
}

interface PlotData {
    data: any,
    layout: any,
}

abstract class AbstractPlot<Parameters> {
    abstract check_for_errors(params: Parameters): string | null;
    abstract get_json_link(params: Parameters): string;
    abstract get_download_link(params: Parameters): string;
    abstract get_download_file_name(): string;
    abstract initialize_parameters(params: Parameters|null, set_params: (value: Parameters) => void): void;
    abstract get_plot_data_from_response_data(data: any): PlotData[];
}

abstract class SimpleAbstractPlot<Parameters> extends AbstractPlot<Parameters> {
    get_plot_data_from_response_data(data: any) {
        return [
            {data: data.data, layout: data.layout}
        ];
    }
}

export {AbstractPlot, SimpleAbstractPlot, AbstractPlotParameters};
