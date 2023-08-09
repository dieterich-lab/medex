import {JSX, useEffect, useState} from "react";
import {EntityType} from "../../services/entity";
import {SingleEntitySelect} from "../common/single_entity_select";
import {PlotTab} from "./common/plot_tab";
import {BarchartDescriptor, BarchartParameters, BarchartPlotType} from "../../utility/plots/barchart";
import {MultiMeasurementSelect} from "../common/multi_measurement_select";
import {CategorySelect} from "../common/category_select";
import {ParameterItem} from "../common/parameter_item";
import {RadioButtons} from "../common/radio_buttons";

interface MyPlotTypeProps{
    value: BarchartPlotType
    onChange: (x: BarchartPlotType) => void,
}

function Barchart() {
    const [params, set_params] = useState<BarchartParameters|null>(null);
    const plot = new BarchartDescriptor();
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
                label="Group by"
                value={params.entity}
                onChange={(x) => set_params({...params, entity: x, categories: x.categories})}
                allowedEntityTypes={[EntityType.CATEGORICAL]}
            />
            <CategorySelect
                entity={params.entity}
                values={params.categories ? params.categories : []}
                onChange={(x) => set_params({...params, categories: x})}
            />
            <MyPlotType
                value={params.plot_type}
                onChange={(x) => set_params({...params, plot_type: x})}
            />
        </PlotTab>
    );
}

const LABELS_BY_PLOT_TYPE: Map<BarchartPlotType, JSX.Element> = new Map([
    [BarchartPlotType.PERCENT, <div>Percent</div>],
    [BarchartPlotType.COUNT, <div>Count</div>],
])

function MyPlotType(props: MyPlotTypeProps) {
    return (
        <ParameterItem>
            <RadioButtons
                value={props.value}
                onChange={props.onChange}
                labels_by_value={LABELS_BY_PLOT_TYPE} />
        </ParameterItem>
    );
}

export {Barchart};
