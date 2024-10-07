import {Entity, EntityType} from "../../../services/entity";
import {MultiEntitySelect} from "../../common/multi_entity_select";
import {useEffect, useState} from "react";
import {MultiMeasurementSelect} from "../../common/multi_measurement_select";
import {get_measurement_info} from "../../../services/measurement";
import {EntityStatsResults, EntityStatsParameters} from "./entity_stats_results";
import {ResultsButton} from "../common/results_button";

interface EntityStatsProps {
    entityType: EntityType,
}

function EntityStats(props: EntityStatsProps) {
    const [measurements, set_measurements] = useState<string[]|null>(null);
    const [entities, set_entities] = useState<Entity[]>([]);
    const [result_params, set_result_params] = useState<EntityStatsParameters|null>(null)
    useEffect(() => {
        if ( measurements == null ) {
            get_measurement_info().then(
                x => set_measurements(x.values)
            );
        }
    });
    const onClick = () => {
        set_result_params({
            measurements: measurements || [],
            entities: entities}
        );
    };

    if ( measurements === null ) {
        return <div>Loading ...</div>
    }
    return (
        <div>
            <div className="card">
                <div className="card-body">
                    <MultiMeasurementSelect
                        values={measurements}
                        onChange={set_measurements}
                        hasSelectNone={true}
                    />
                    <MultiEntitySelect
                        values={entities}
                        onChange={set_entities}
                        allowedEntityTypes={[props.entityType]}
                        hasSelectNone={true}
                    />
                    <ResultsButton onClick={onClick} />
                </div>
            </div>
            <div className="card">
                <div className="card-body">
                    <EntityStatsResults
                        entityType={props.entityType}
                        parameters={result_params}
                    />
                </div>
            </div>
        </div>
    );
}

export {EntityStats};
