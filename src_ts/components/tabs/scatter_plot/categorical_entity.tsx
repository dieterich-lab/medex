import {Entity, EntityType} from "../../../services/entity";
import {useState} from "react";
import {SingleEntitySelect} from "../../common/single_entity_select";
import {CategorySelect} from "../../common/category_select";

interface ScatterBoxCategoricalEntityProps {
    entity: Entity | null,
    categories: string[] | null,
    onChange: (entity: Entity|null, categories: string[]|null) => void,
}

function ScatterBoxCategoricalEntity(props: ScatterBoxCategoricalEntityProps) {
    const [collapsed, set_collapsed] = useState<boolean>(props.entity == null);
    const collapse_it = () => {
        props.onChange(null, null);
        set_collapsed(true);
    }

    if ( collapsed ) {
        return <CollapseCheckBox onClick={() => set_collapsed(false)} selected={false} />;
    } else {
       return (
            <div>
                <CollapseCheckBox onClick={collapse_it} selected={true}/>
                <SingleEntitySelect
                    label="Categorical %DEFAULT%"
                    value={props.entity}
                    onChange={e => props.onChange(e, e.categories)}
                    allowedEntityTypes={[EntityType.CATEGORICAL]}
                />
                <CategorySelect
                    entity={props.entity}
                    values={props.categories ? props.categories : []}
                    onChange={c => props.onChange(props.entity, c)}
                />
            </div>
       );
    }
}

interface CollapseCheckBoxProps {
    selected: boolean,
    onClick: () => void,
}

function CollapseCheckBox(props: CollapseCheckBoxProps) {
    return (
        <div className="sub-card">
            <div className="form-check form-check-inline">
                <input
                    type="checkbox"
                    className="form-check-input"
                    id="add_group_by"
                    onClick={props.onClick}
                    defaultChecked={props.selected}
                />
                <label htmlFor="add_group_by">Group by categorical value</label>
            </div>
        </div>
    );
}

interface SelectCategoriesProps {
    entity: Entity | null,
    categories: string[] | null,
    onChange: (c: string[]) => void,
}

export {ScatterBoxCategoricalEntity};
