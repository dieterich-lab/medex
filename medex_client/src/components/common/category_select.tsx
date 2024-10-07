import {useId} from 'react';
import {ParameterItem} from './parameter_item';
import {MultiSelect} from './multi_select';
import {Entity} from '../../services/entity';
import {get_options_from_strings, MultiSelectProps} from '../../utility/selection';

interface CategorySelectorProps extends MultiSelectProps<string> {
    entity: Entity | null;
}

function CategorySelect(props: CategorySelectorProps) {
    const label_id = useId();
    const disabled = props.entity == null;
    const options = !props.entity?.categories || props.entity.categories.length === 0 ?
        [] : get_options_from_strings(props.entity.categories);

    return (
        <ParameterItem>
            <label id={label_id}>Categories:</label>
            <MultiSelect
                options={options}
                labelledBy={label_id}
                onChange={props.onChange}
                values={props.values}
                hasSelectAll={props?.hasSelectAll !== false}
                hasSelectNone={props?.hasSelectNone !== false}
                disabled={disabled}
            />
        </ParameterItem>
    );
}

export {CategorySelect};
