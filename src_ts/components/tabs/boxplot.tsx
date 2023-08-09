import {useEffect, useState} from "react";
import {EntityType} from "../../services/entity";
import {SingleEntitySelect} from "../common/single_entity_select";
import {PlotTab} from "./common/plot_tab";
import {BoxplotDescriptor, BoxplotParameters} from "../../utility/plots/boxplot";
import {MultiMeasurementSelect} from "../common/multi_measurement_select";
import {CategorySelect} from "../common/category_select";

interface MyLogScaleProps {
    value: boolean,
    onChange: (x: boolean) => void,
}

function Boxplot() {
    const [params, set_params] = useState<BoxplotParameters|null>(null);
    const plot = new BoxplotDescriptor();
    useEffect(() => {plot.initialize_parameters(params, set_params)}, []);

    if ( params == null ) {
        return <div>Loading ...</div>;
    }

    return (
        <PlotTab plot={plot} parameters={params} setParameters={set_params}>
            <MultiMeasurementSelect
                values={params.measurements}
                onChange={(x) => set_params({...params, measurements: x})}
            />
            <SingleEntitySelect
                label="Numerical entity"
                value={params.numeric_entity}
                onChange={(x) => set_params({...params, numeric_entity: x})}
                allowedEntityTypes={[EntityType.NUMERICAL]}
            />
           <SingleEntitySelect
                label="Group by"
                value={params.group_by_entity}
                onChange={(x) => set_params({...params, group_by_entity: x, categories: x.categories})}
                allowedEntityTypes={[EntityType.CATEGORICAL]}
            />
            <CategorySelect
                entity={params.group_by_entity}
                values={params.categories ? params.categories : []}
                onChange={(x) => set_params({...params, categories: x})}
            />
            <MyLogScale
                value={params.log_scale}
                onChange={(x) => set_params({...params, log_scale: x})}
            />
        </PlotTab>
    );
}

function MyLogScale(props: MyLogScaleProps) {
    return (
        <div className="sub-card">
            <label htmlFor="boxplot_scale">Scale:</label>
            <div id="boxplot_scale" className="form-check form-check-inline">
                <div className="form-check form-check-inline">
                    <input
                        id="boxplot_scale_log"
                        type="checkbox"
                        className="form-check-input"
                        checked={props.value}
                        onChange={(e) => props.onChange(e.target.checked)}
                    />
                    <label htmlFor="boxplot_scale_log">log</label>
                </div>
            </div>
        </div>
    );
}

export {Boxplot};
