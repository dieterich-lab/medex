import {Option, SelectProps} from 'react-multi-select-component';
import {Entity, EntityType, get_entity_list} from '../services/entity';

const NO_VALUE_SELECTED_MARKER = '_%_VALUE_SELECTED_MARKER_%_';

interface GenericSelect {
    options: Option[],
    hasSelectNone?: boolean,
    labelledBy: SelectProps['labelledBy'],
    ItemRenderer?: SelectProps['ItemRenderer'],
    filterOptions?: SelectProps['filterOptions'],
}

interface SingleSelectProps extends GenericSelect {
    value: any,
    onChange: (new_value: any) => void,
    disabled?: SelectProps['disabled'],
}

interface MultiSelectProps extends GenericSelect {
    values: any[],
    onChange: (new_values: any[]) => void,
    hasSelectAll?: SelectProps['hasSelectAll'],
    disabled?: SelectProps['disabled'],
}

interface TypedSingleSelectProps<T> {
    value: T|null,
    onChange: (x: T) => void,
    hasSelectNone?: boolean,
    label?: string,
}

interface TypedMultiSelectProps<T> {
    values: T[],
    onChange: (x: T[]) => void,
    hasSelectNone?: boolean,
    hasSelectAll?: SelectProps['hasSelectAll'],
    label?: string,
}

function get_option_from_string(x: string): Option {
    return {label: x, value: x};
}

function get_options_from_strings(options: string[]): Option[] {
    return options.map((x) => get_option_from_string(x));
}

function set_entity_options(
    allowed_entity_types: EntityType[],
    set_options: (options: Option[]|null) => void,
    old_options: Option[]|null,
): void {
    if ( old_options ) {
        return;
    }
    get_entity_list().then(
        (all_entities) => set_options(
            all_entities
                .filter((x) => allowed_entity_types.includes(x.type))
                .map((x) => get_option_from_entity(x))
        )
    );
}

function get_option_from_entity(entity: Entity): Option {
    return {label: entity.key, value: entity};
}

interface EntityOption extends Option {
    value: Entity,
}

function entity_select_search(
    current_data: EntityOption[],
    search_sting: string,
): EntityOption[] {
	const lower_case_search_string = search_sting.toLowerCase();
	return current_data
		.filter((x) => matches_entity(lower_case_search_string, x));
}

function matches_entity(search_string: string, option: EntityOption): boolean {
    return option.value.key.toLowerCase().includes(search_string)
        || ( option.value?.description != null && option.value.description.toLowerCase().includes(search_string) );
}

export {
    NO_VALUE_SELECTED_MARKER,
    MultiSelectProps, SingleSelectProps,
    TypedSingleSelectProps, TypedMultiSelectProps,
    get_option_from_string, get_options_from_strings,
    set_entity_options, entity_select_search
};
