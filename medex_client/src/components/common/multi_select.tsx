import {MultiSelect as MultiSelectOrig, Option} from 'react-multi-select-component';
import {JSX} from 'react';
import {GenericSelectProps, MultiSelectProps, NO_VALUE_SELECTED_MARKER} from "../../utility/selection";


interface GenericMultiSelectProps<T> extends MultiSelectProps<T>, GenericSelectProps {}

function MultiSelect<T>(props: GenericMultiSelectProps<T>): JSX.Element {
    return <MultiSelectOrig
        options={props.options}
        value={get_value_options(props)}
        onChange={(options: Option[]) => multi_on_change(props.onChange, options, props?.values)}
        labelledBy={props.labelledBy}
        hasSelectAll={props?.hasSelectAll}
        ItemRenderer={props?.ItemRenderer}
        filterOptions={props?.filterOptions}
        closeOnChangedValue={true}
        ClearSelectedIcon={get_clear_selection_icon(props)}
        disabled={props.disabled}
    />;
}

function get_value_options<T>(props: GenericMultiSelectProps<T>): Option[] {
    if ( props.values == null ) {
        return [];
    }
    return props.options.filter(x => props.values.includes(x.value))
}

function multi_on_change<T>(
    orig_on_change: (x: T[]) => void,
    new_options: Option[],
    initial_values?: T[]
) {
    const new_values = new_options.map(x => x.value);
    if ( new_values.includes(NO_VALUE_SELECTED_MARKER) && initial_values != null && initial_values.length > 0  ) {
        orig_on_change([]);
    } else {
        orig_on_change(new_values.filter(x => x !== NO_VALUE_SELECTED_MARKER));
    }
}

function get_clear_selection_icon<T>(props: MultiSelectProps<T>) {
    if ( props?.hasSelectNone ) {
        return (
            <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2"
                 className="dropdown-search-clear-icon gray">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        );
    } else {
        return null;
    }
}

export {MultiSelect};
