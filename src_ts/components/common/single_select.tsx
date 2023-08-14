import {JSX} from 'react';
import {Option} from 'react-multi-select-component';
import {MultiSelect} from './multi_select';
import {NO_VALUE_SELECTED_MARKER, SingleSelectProps} from "../../utility/selection";

function SingleSelect(props: SingleSelectProps): JSX.Element {
    return <MultiSelect
        options={props.options}
        labelledBy={props.labelledBy}
        filterOptions={props?.filterOptions}
        hasSelectNone={props?.hasSelectNone}
        onChange={(values) => single_on_change(values, props.onChange, props?.value)}
        values={props?.value == null ? [] : [props.value]}
        hasSelectAll={false}
        disabled={props.disabled}
    />;
}

function single_on_change<T>(
    new_values: any[],
    original_on_change?: (new_selected: Option | null) => void,
    initial_value?: any,
) {
    for (const new_value of new_values) {
        if (new_value == initial_value) {
            continue;
        }
        if ( original_on_change ) {
            original_on_change(new_value == NO_VALUE_SELECTED_MARKER ? null : new_value);
        }
        return;
    }
    if (original_on_change != null) {
        original_on_change(null);
    }
}

export {SingleSelect};
