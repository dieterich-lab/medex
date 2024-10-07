import {Entity, EntityType} from '../../services/entity';
import {ParameterItem} from './parameter_item';
import {useEffect, useId, useState} from "react";
import {SingleSelect} from "./single_select";
import {Option} from "react-multi-select-component";
import {entity_select_search, set_entity_options, SingleSelectProps} from "../../utility/selection";
import {EntityOptionItem} from "./entity_option_item";
import {get_label} from "../../utility/misc";

interface SingleEntitySelectProps extends SingleSelectProps<Entity> {
    allowedEntityTypes: EntityType[],
}

function SingleEntitySelect(props: SingleEntitySelectProps) {
    const [options, set_options] = useState<Option[]|null>(null);
    const selected_values = props.value ? [props.value] : [];
    useEffect(
        () => set_entity_options(props.allowedEntityTypes, props.value ? [props.value] : [], set_options),
        [props.value, props.allowedEntityTypes, set_options]
    );
    const label_id = useId();
    const label = get_label('Entity', props.label);
    if ( options == null ) {
        return <div>Loading ...</div>;
    }
    const filter_options = (present_options: Option[], search_string: string) => {
        return entity_select_search(props.allowedEntityTypes, present_options, selected_values, search_string)
    }

    return (
        <ParameterItem>
            <label id={label_id}>{label}:</label>
            <SingleSelect
                options={options}
                labelledBy={label_id}
                value={props.value}
                onChange={x => props.onChange(x)}
                filterOptions={filter_options}
                ItemRenderer={EntityOptionItem}
            />
        </ParameterItem>
    );
}

export {SingleEntitySelect};
