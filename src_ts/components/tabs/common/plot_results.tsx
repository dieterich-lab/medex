import Plot from 'react-plotly.js';
import {useEffect, useState} from "react";
import {http_fetch} from "../../../utility/http";
import {report_error} from "../../../utility/user_feedback";
import {AbstractPlot} from "../../../utility/plots/abstract_plot";
import {DownloadLink} from "./download_link";
import {ResultFrame} from "./result_frame";

interface PlotResultsProps<Parameters> {
    plot: AbstractPlot<Parameters>,
    parameters: Parameters | null,
    onError: () => void,
}

function PlotResults<Parameters>(props: PlotResultsProps<Parameters>) {
    const [data, set_data] = useState<any>(null);
    const plot = props.plot;
    const error_message = props.parameters ? plot.check_for_errors(props.parameters) : null;
    useEffect(
        () => fetch_data(props, set_data, error_message),
        [props, set_data]
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
    const download_link = plot.get_download_link(props.parameters);
    const download_file_name = plot.get_download_file_name();
    const plots = plot.get_plot_data_from_response_data(data).map(
        x => <Plot {...x} />
    )
    return (
        <ResultFrame>
            <DownloadLink url={download_link} filename={download_file_name}/>
            {plots}
        </ResultFrame>
    );
}

function fetch_data<Parameters>(
    props: PlotResultsProps<Parameters>,
    set_data: (data: any) => void,
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
