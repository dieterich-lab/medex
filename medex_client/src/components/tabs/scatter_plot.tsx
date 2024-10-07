import {useEffect, useState} from "react";
import {EntityType} from "../../services/entity";
import {ScatterBoxCategoricalEntity} from "./scatter_plot/categorical_entity";
import {SingleMeasurementSelect} from "../common/single_measurement_select";
import {SingleEntitySelect} from "../common/single_entity_select";
import {ScatterBoxScaleButtons} from "./scatter_plot/scale_buttons";
import {PlotTab} from "./common/plot_tab";
import {ScatterPlotDescriptor, ScatterPlotParameters} from "../../utility/plots/scatter_plot";

function ScatterPlot() {
    const [params, set_params] = useState<ScatterPlotParameters|null>(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
    const plot = new ScatterPlotDescriptor();
    useEffect(() => {plot.initialize_parameters(params, set_params)}, [params, set_params, plot]);

    if ( params == null ) {
        return <div>Loading ...</div>;
    }

    return (
        <PlotTab plot={plot} parameters={params} setParameters={set_params}>
            <SingleMeasurementSelect
                label="X %DEFAULT%"
                value={params?.x_measurement}
                onChange={m => set_params({...params, x_measurement: m})}
            />
            <SingleEntitySelect
                label="X %DEFAULT%"
                value={params.x_entity}
                onChange={e => set_params({...params, x_entity: e})}
                allowedEntityTypes={[EntityType.NUMERICAL]}
            />
            <SingleMeasurementSelect
                label="Y %DEFAULT%"
                value={params.y_measurement}
                onChange={m => set_params({...params, y_measurement: m})}
            />
            <SingleEntitySelect
                label="Y %DEFAULT%"
                value={params.y_entity}
                onChange={e => set_params({...params, y_entity: e})}
                allowedEntityTypes={[EntityType.NUMERICAL]}
            />
            <ScatterBoxScaleButtons
                logX={params.x_log_scale} logY={params.y_log_scale}
                onChange={(x, y) => set_params({...params, x_log_scale: x, y_log_scale: y})}
            />
            <ScatterBoxCategoricalEntity
                entity={params.categorical_entity}
                categories={params.categories}
                onChange={(e, c) => set_params({...params, categorical_entity: e, categories: c})}
                    />
        </PlotTab>
    );
}

export {ScatterPlot};
