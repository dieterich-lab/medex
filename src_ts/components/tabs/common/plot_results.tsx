import Plot from 'react-plotly.js';
import {PropsWithChildren, useEffect, useState} from "react";
import {http_fetch} from "../../../utility/http";
import {report_error} from "../../../utility/error";
import {AbstractPlot} from "../../../utility/plots/abstract_plot";
import {DownloadLink} from "./download_link";

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
        return <PlotFrame>{error_message}</PlotFrame>;
    }
    if ( data == null ) {
        return <PlotFrame>Loading ...</PlotFrame>;
    }
    const download_link = plot.get_download_link(props.parameters);
    const download_file_name = plot.get_download_file_name();
    const plots = plot.get_plot_data_from_response_data(data).map(
        x => <Plot {...x} />
    )
    return (
        <PlotFrame>
            <DownloadLink url={download_link} filename={download_file_name}/>
            {plots}
        </PlotFrame>
    );
}

interface PlotFrameProps {}

function PlotFrame(props: PropsWithChildren<PlotFrameProps>) {
    return (
        <div className="card">
            <div className="card-body">
                {props.children}
            </div>
        </div>
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
    http_fetch('GET', url)
        .then(x => set_data(x))
        .catch(
        (error) => {
            props.onError();
            report_error(error);
        }
    )
}

export {PlotResults};
