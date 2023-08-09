import {useEffect, useId, useState} from "react";
import {ParameterItem} from './parameter_item';
import {TypedMultiSelectProps} from "../../utility/selection";
import {MultiSelect} from "./multi_select";
import {MeasurementSelectionState, populate_measurement_selection_state} from "../../utility/measurement_selection";
import {get_label} from "../../utility/misc";

function MultiMeasurementSelect(props: TypedMultiSelectProps<string>) {
    const [state, set_state] = useState<MeasurementSelectionState|null>(null);
    useEffect(() => populate_measurement_selection_state(set_state, state, true), []);
    const label_id = useId();
    if ( state == null ) {
        return <div>Loading ...</div>;
    }
    const label = get_label(state.display_name, props.label);
    return (
        <ParameterItem show={state.options.length > 1}>
            <label id={label_id}>
                {label}:
            </label>
           <MultiSelect
                options={state.options}
                labelledBy={label_id}
                values={props.values}
                onChange={props.onChange}
                hasSelectNone={props.hasSelectNone}
            />
        </ParameterItem>
    );
}

export {MultiMeasurementSelect};
