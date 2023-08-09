import {PropsWithChildren, useEffect, useState} from "react";
import {get_filter_status_revision} from "../../../services/patient_filter";
import {AbstractPlot} from "../../../utility/plots/abstract_plot";
import {TabFrame} from "./frame";
import {ResultsButton} from "./results_button";
import {PlotResults} from "./plot_results";

interface PlotTabProps<Parameters> {
    plot: AbstractPlot<Parameters>,
    parameters: Parameters | null,
    setParameters: (params: Parameters|null) => void,
}

function PlotTab<Parameters>(props: PropsWithChildren<PlotTabProps<Parameters>>) {
    const [result_params, set_result_params] = useState<Parameters|null>(null);
    const plot = props.plot;

    return (
        <TabFrame>
            <div className="card">
                <div className="card-body">
                    {props.children}
                    <ResultsButton onClick={() => set_result_params(get_cooked_result_parameters(props.parameters))} />
                </div>
            </div>
            <PlotResults plot={plot} parameters={result_params} onError={() => set_result_params(null)} />
        </TabFrame>
    );
}

function get_cooked_result_parameters<Parameters>(params: Parameters): Parameters {
    return {
        ...params,
        filter_status_revision: get_filter_status_revision(),
    }
}

export {PlotTab};