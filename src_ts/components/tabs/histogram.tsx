import {ChangeEventHandler, useEffect, useState} from "react";
import {EntityType} from "../../services/entity";
import {SingleEntitySelect} from "../common/single_entity_select";
import {PlotTab} from "./common/plot_tab";
import {MultiMeasurementSelect} from "../common/multi_measurement_select";
import {CategorySelect} from "../common/category_select";
import {ParameterItem} from "../common/parameter_item";
import {HistogramDescriptor, HistogramParameters} from "../../utility/plots/histogram";

interface NumberOfBinsProps {
    value: number,
    onChange: (x: number) => void,
}

function Histogram() {
    const [params, set_params] = useState<HistogramParameters|null>(null);
    const plot = new HistogramDescriptor();
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
                value={params.numerical_entity}
                onChange={(x) => set_params({...params, numerical_entity: x})}
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
            <NumberOfBins
                value={params.number_of_bins}
                onChange={x => set_params({...params, number_of_bins: x})}
            />
        </PlotTab>
    );
}

function NumberOfBins(props: NumberOfBinsProps) {
    const on_change: ChangeEventHandler<HTMLInputElement> = (e) => {
        const new_value_as_number = parseFloat(e.target.value);
        props.onChange(new_value_as_number);
    };

    return (
        <ParameterItem>
            <label htmlFor="histogram_number_of_bins">
                Number of bins:
            </label>
            <input type="text" value={props.value} onChange={on_change}/>
        </ParameterItem>
    );
}

export {Histogram};
