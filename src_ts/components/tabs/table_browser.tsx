import {useEffect, useState} from "react";
import {TabFrame} from "./common/frame";
import {get_measurement_info} from "../../services/measurement";
import {ALL_ENTITY_TYPES, Entity} from "../../services/entity";
import {TableBrowserResultParameters, TableFormat} from "./table_browser/common";
import {MultiMeasurementSelect} from "../common/multi_measurement_select";
import {MultiEntitySelect} from "../common/multi_entity_select";
import {TableBrowserFormatSelection} from "./table_browser/format_selection";
import {ResultsButton} from "./common/results_button";
import {TableBrowserResults} from "./table_browser/results";

function TableBrowser() {
    const [measurements, set_measurements] = useState<string[]|null>(null);
    const [entities, set_entities] = useState<Entity[]>([]);
    const [format, set_format] = useState<TableFormat>(TableFormat.Flat);
    const [result_parameters, set_result_parameters] = useState<TableBrowserResultParameters|null>(null);

    useEffect(() => {get_measurement_info().then(x => set_measurements(x.values))}, []);

    if ( measurements == null ) {
        return <div>Loading ...</div>;
    }

    const onClick = () => {
        set_result_parameters({
            measurements: measurements,
            entities: entities,
            format: format
        });
    }

    return (
        <TabFrame>
            <div className="card">
                <div className="card-body">
                    <MultiMeasurementSelect values={measurements} onChange={set_measurements} />
                    <MultiEntitySelect values={entities} onChange={set_entities} allowedEntityTypes={ALL_ENTITY_TYPES}/>
                    <TableBrowserFormatSelection format={format} onChange={set_format}/>
                    <ResultsButton onClick={onClick} />
                </div>
            </div>
            <TableBrowserResults parameters={result_parameters} onError={() => set_result_parameters(null)} />
        </TabFrame>
    );
}

export {TableBrowser};