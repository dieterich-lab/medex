import {JSX} from 'react';
import {MultiSelect} from './multi_select';
import {
    GenericSelectProps,
    SingleSelectProps,
    NO_VALUE_SELECTED_MARKER
} from "../../utility/selection";

interface GenericSingleSelectProps<T> extends SingleSelectProps<T>, GenericSelectProps {}
function SingleSelect<T>(props: GenericSingleSelectProps<T>): JSX.Element {
    return <MultiSelect
        options={props.options}
        labelledBy={props.labelledBy}
        filterOptions={props?.filterOptions}
        hasSelectNone={props?.hasSelectNone}
        onChange={(values: T[]) => single_on_change<T>(values, props.onChange, props?.value)}
        values={props?.value == null ? [] : [props.value]}
        hasSelectAll={false}
        disabled={props.disabled}
    />;
}

function single_on_change<T>(
    new_values: T[],
    original_on_change?: (new_selected: T | null) => void,
    initial_value: T | null = null,
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
