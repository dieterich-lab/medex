import {Entity, EntityType} from '../../services/entity';
import {ParameterItem} from './parameter_item';
import {useEffect, useId, useState} from "react";
import {MultiSelect} from "./multi_select";
import {Option} from "react-multi-select-component";
import {entity_select_search, set_entity_options, TypedMultiSelectProps} from "../../utility/selection";
import {EntityOptionItem} from "./entity_option_item";
import {get_label} from "../../utility/misc";

interface MultiEntitySelectProps extends TypedMultiSelectProps<Entity> {
    allowedEntityTypes: EntityType[],
}

function MultiEntitySelect(props: MultiEntitySelectProps) {
    const [options, set_options] = useState<Option[]|null>(null);
    useEffect(
        () => set_entity_options(props.allowedEntityTypes, set_options, options),
        [props, set_options]
    );
    const label_id = useId();
    const label = get_label('Entities', props.label);
    if ( options == null ) {
        return <div>Loading ...</div>;
    }

    return (
        <ParameterItem>
            <label id={label_id}>{label}:</label>
            <MultiSelect
                options={options}
                labelledBy={label_id}
                values={props.values}
                onChange={x => props.onChange(x)}
                filterOptions={entity_select_search}
                ItemRenderer={EntityOptionItem}
                hasSelectNone={props.hasSelectNone}
            />
        </ParameterItem>
    );
}

export {MultiEntitySelect};
