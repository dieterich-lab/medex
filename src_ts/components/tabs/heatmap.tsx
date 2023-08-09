import {useEffect, useState} from "react";
import {EntityType} from "../../services/entity";
import {PlotTab} from "./common/plot_tab";
import {HeatmapDescriptor, HeatmapParameters} from "../../utility/plots/heatmap";
import {MultiEntitySelect} from "../common/multi_entity_select";


function Heatmap() {
    const [params, set_params] = useState<HeatmapParameters|null>(null);
    const plot = new HeatmapDescriptor();
    useEffect(() => {plot.initialize_parameters(params, set_params)}, []);

    if ( params == null ) {
        return <div>Loading ...</div>;
    }

    return (
        <PlotTab plot={plot} parameters={params} setParameters={set_params}>
            <MultiEntitySelect
                label="Numerical entities"
                values={params.numerical_entities ? params.numerical_entities : []}
                onChange={(x) => set_params({...params, numerical_entities: x})}
                allowedEntityTypes={[EntityType.NUMERICAL]}
            />
        </PlotTab>
    );
}

export {Heatmap};
