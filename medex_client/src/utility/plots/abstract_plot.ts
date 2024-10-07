import {PlotParams} from "react-plotly.js";

interface AbstractPlotParameters {
    filter_status_revision: number,
}

interface PlotData {
    name: string,
    data: PlotParams['data'],
    layout: PlotParams['layout'],
}

interface SimpleRawPlotData {
    data: PlotParams['data'],
    layout: PlotParams['layout'],
}

abstract class AbstractPlot<Parameters, RawPlotData> {
    abstract check_for_errors(params: Parameters): string | null;
    abstract get_json_link(params: Parameters): string;
    abstract get_download_link(params: Parameters): string;
    abstract get_download_file_name(): string;
    abstract initialize_parameters(params: Parameters|null, set_params: (value: Parameters) => void): void;
    abstract get_plot_data_from_response_data(data: RawPlotData): PlotData[];
}

abstract class SimpleAbstractPlot<Parameters> extends AbstractPlot<Parameters, SimpleRawPlotData> {
    get_plot_data_from_response_data(data: SimpleRawPlotData) {
        return [
            {name: 'plot', data: data.data, layout: data.layout}
        ];
    }
}

export {AbstractPlot, SimpleAbstractPlot, type AbstractPlotParameters, type SimpleRawPlotData};
