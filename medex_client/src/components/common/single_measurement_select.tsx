import {useEffect, useId, useState} from "react";
import {ParameterItem} from './parameter_item';
import {SingleSelectProps} from "../../utility/selection";
import {SingleSelect} from "./single_select";
import {MeasurementSelectionState, populate_measurement_selection_state} from "../../utility/measurement_selection";
import {M} from "./message_catalog.tsx";

function SingleMeasurementSelect(props: SingleSelectProps<string>) {
    const [state, set_state] = useState<MeasurementSelectionState|null>(null);
    useEffect(() => populate_measurement_selection_state(set_state, state, false), [state, set_state]);
    const label_id = useId();
    if ( state == null ) {
        return <div>Loading ...</div>;
    }
    return (
        <ParameterItem show={state.options.length > 1}>
            <label id={label_id}><M id="Measurement" custom={props.label}/>:</label>
           <SingleSelect
                options={state.options}
                labelledBy={label_id}
                value={props.value}
                onChange={props.onChange}
                hasSelectNone={props.hasSelectNone}
            />
        </ParameterItem>
    );
}

export {SingleMeasurementSelect};
