import {Option, SelectProps} from 'react-multi-select-component';
import {Entity, EntityType, get_entity_list} from '../services/entity';

const NO_VALUE_SELECTED_MARKER = '_%_VALUE_SELECTED_MARKER_%_';
const MAX_OPTIONS = 20;


interface CommonSelectOptions {
    hasSelectNone?: boolean,
    ItemRenderer?: SelectProps['ItemRenderer'],
    filterOptions?: SelectProps['filterOptions'],
}

interface GenericSelectProps extends CommonSelectOptions {
    options: Option[],
    labelledBy: SelectProps['labelledBy'],
}

interface SingleSelectProps<T> extends CommonSelectOptions {
    value: T|null,
    onChange: (new_value: T | null) => void,
    disabled?: SelectProps['disabled'],
    hasSelectNone?: boolean,
    label?: string,
}

interface MultiSelectProps<T> extends CommonSelectOptions {
    values: T[],
    onChange: (new_values: T[]) => void,
    hasSelectAll?: SelectProps['hasSelectAll'],
    disabled?: SelectProps['disabled'],
    label?: string,
}

interface EntityOption extends Option {
    value: Entity | null,
}

const LOADING_OPTION: EntityOption = {
    value: null,
    label: '... loading ...',
    disabled: true,
};

const ECLIPSE_OPTION: EntityOption = {
    value: null,
    label: '...',
    disabled: true,
}

class EntityOptionCache {
    private cache: Map<string, Option[]>;

    constructor() {
        this.cache = new Map();
    }

    private get_key(entity_types: EntityType[]): string {
        return entity_types.sort().map(x => x.valueOf()).join('/');
    }

    async get_truncated_options(
        entity_types: EntityType[],
        values: Entity[],
        present_options?: EntityOption[],
        predicate?: (x: EntityOption) => boolean
    ): Promise<EntityOption[]> {
        const all_options = await this.get_all_options(entity_types);
        return this.truncate(all_options, values, present_options, predicate);
    }

    private async get_all_options(entity_types: EntityType[]): Promise<EntityOption[]> {
        const key = this.get_key(entity_types);
        const cached_result = this.cache.get(key);
        if ( cached_result ) {
            return cached_result;
        }
        const all_entities = await get_entity_list();
        const result = all_entities
            .filter((x) => entity_types.includes(x.type))
            .map((x) => get_option_from_entity(x));
        this.cache.set(key, result);
        return result;
    }

    try_get_truncated_options(
        entity_types: EntityType[],
        values: Entity[],
        present_options?: EntityOption[],
        predicate?: (x: EntityOption) => boolean
    ): EntityOption[] {
        const key = this.get_key(entity_types);
        const cached_options = this.cache.get(key);
        if (!cached_options) {
            return [LOADING_OPTION]
        } else {
            return this.truncate(cached_options, values, present_options, predicate);
        }
    }

    private truncate(
        all_options: EntityOption[],
        values: Entity[],
        present_options?: EntityOption[],
        predicate?: (x: EntityOption) => boolean
    ): EntityOption[] {
        const result: EntityOption[] = [];
        let count = 0;
        for (let i = 0; i < all_options.length; i +=1 ) {
            if ( this.is_valid_option(all_options[i], predicate) ) {
                count += 1;
                if ( count > MAX_OPTIONS ) {
                    result.push(ECLIPSE_OPTION);
                    break;
                } else {
                    this.add_option(result, all_options[i], present_options);
                }
            }
        }
        this.append_selected_options(result, values, present_options);
        return result;
    }

    private is_valid_option(option: EntityOption, predicate?: (x: EntityOption) => boolean): boolean {
        if ( option.value == null) {
            return false;
        }
        return !predicate || predicate(option);
    }

    private append_selected_options(options: EntityOption[], values: Entity[], present_options?: EntityOption[]) {
        values.forEach(
            value => {
                const is_missing = options.filter(x => x.value?.key == value.key).length == 0;
                if ( is_missing ) {
                    this.add_option(options, get_option_from_entity(value), present_options);
                }
            }
        )
    }

    private add_option(result: EntityOption[], new_option: EntityOption, present_options?: EntityOption[]): void {
        if ( present_options ) {
            const candidates = present_options.filter(x => x.value?.key == new_option.value?.key);
            if ( candidates.length > 0 ) {
                result.push(candidates[0]);
                return;
            }
        }
        result.push(new_option);
    }
}

function get_option_from_string(x: string): Option {
    return {label: x, value: x};
}

function get_options_from_strings(options: string[]): Option[] {
    return options.map((x) => get_option_from_string(x));
}

const option_cache = new EntityOptionCache();

function set_entity_options(
    allowed_entity_types: EntityType[],
    values: Entity[],
    set_options: (options: Option[]|null) => void,
): void {
    option_cache.get_truncated_options(allowed_entity_types, values).then(
        x => set_options(x)
    )
}

function get_option_from_entity(entity: Entity): Option {
    return {label: entity.key, value: entity};
}

function entity_select_search(
    allowed_entity_types: EntityType[],
    present_options: EntityOption[],
    values: Entity[],
    search_sting: string,
): EntityOption[] {
	const lower_case_search_string = search_sting.toLowerCase();
    return option_cache.try_get_truncated_options(
        allowed_entity_types,
        values,
        present_options,
        (x) => matches_entity(lower_case_search_string, x)
    )
}

function matches_entity(search_string: string, option: EntityOption): boolean {
    return option.value != null && option.value.key.toLowerCase().includes(search_string)
        || ( option.value?.description != null && option.value.description.toLowerCase().includes(search_string) );
}

export {
    NO_VALUE_SELECTED_MARKER,
    type GenericSelectProps,
    type MultiSelectProps, type SingleSelectProps,
    get_option_from_string, get_options_from_strings,
    set_entity_options, entity_select_search
};
