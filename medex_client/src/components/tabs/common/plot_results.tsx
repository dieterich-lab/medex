import Plot from 'react-plotly.js';
import {useEffect, useState} from "react";
import {BASE_URL, http_fetch} from "../../../utility/http";
import {AbstractPlot} from "../../../utility/plots/abstract_plot";
import {DownloadLink} from "./download_link";
import {ResultFrame} from "./result_frame";

interface PlotResultsProps<Parameters, RawPlotData> {
    plot: AbstractPlot<Parameters, RawPlotData>,
    parameters: Parameters | null,
    onError: () => void,
}

function PlotResults<Parameters, RawPlotData>(props: PlotResultsProps<Parameters, RawPlotData>) {
    const [data, set_data] = useState<unknown>(null);
    const plot = props.plot;
    const error_message = props.parameters ? plot.check_for_errors(props.parameters) : null;
    useEffect(
        () => fetch_data(props, set_data, error_message),
        [props, set_data, error_message]
    )
    if ( props.parameters == null ) {
        return <div/>;
    }

    if ( error_message ) {
        return <ResultFrame>{error_message}</ResultFrame>;
    }
    if ( data == null ) {
        return <ResultFrame>Loading ...</ResultFrame>;
    }
    const download_link = BASE_URL + plot.get_download_link(props.parameters);
    const download_file_name = plot.get_download_file_name();
    const plots = plot.get_plot_data_from_response_data(data as RawPlotData).map(
        x => <Plot data={x.data} layout={x.layout} key={x.name} />
    )
    return (
        <ResultFrame>
            <DownloadLink url={download_link} filename={download_file_name}/>
            {plots}
        </ResultFrame>
    );
}

function fetch_data<Parameters, RawPlotData>(
    props: PlotResultsProps<Parameters, RawPlotData>,
    set_data: (data: unknown) => void,
    error_message: string | null
) {
    if ( props.parameters == null || error_message != null ) {
        return;
    }
    const params = props.parameters;
    const url = props.plot.get_json_link(params);
    http_fetch('GET', url, 'loading plot data')
        .then(x => set_data(x))
        .catch(
        () => {
            props.onError();
        }
    )
}

export {PlotResults};
