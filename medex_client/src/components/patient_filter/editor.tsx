import {useState} from 'react';
import {PatientFilterComponentProps} from './common';
import {ALL_ENTITY_TYPES, Entity, EntityType} from '../../services/entity';
import {SingleMeasurementSelect} from '../common/single_measurement_select';
import {SingleEntitySelect} from '../common/single_entity_select';
import {CategoricalDetails} from './categorical_details';
import {NumericalDetails} from './numerical_details';
import {ParameterItem} from '../common/parameter_item';


interface MyEntityDetailsProps extends PatientFilterComponentProps {
    measurement: string|null,
    entity: Entity|null,
}

function PatientFilterEditor(props: PatientFilterComponentProps) {
    const [selected_measurement, set_selected_measurement] = useState<string|null>(null);
    const [selected_entity, set_select_entity] = useState<Entity|null>(null);

    return (
        <div className="card">
            <div className="card-body">
                <h5 className="card-title">Filter</h5>

                <SingleMeasurementSelect
                    value={selected_measurement}
                    onChange={set_selected_measurement}
                    hasSelectNone={true}
                />

                <SingleEntitySelect
                    value={selected_entity}
                    onChange={set_select_entity}
                    allowedEntityTypes={ALL_ENTITY_TYPES}
                />

                <MyEntityDetails
                    entity={selected_entity}
                    measurement={selected_measurement}
                    refresh_filters={props.refresh_filters}
                />
            </div>
        </div>
    );
}

function MyEntityDetails(props: MyEntityDetailsProps) {
    if ( props.entity == null ) {
        return <div />;
    } else if ( props.entity.type == EntityType.CATEGORICAL ) {
        return <CategoricalDetails
            measurement={props.measurement}
            entity={props.entity}
            refresh_filters={props.refresh_filters}
        />;
    } else if ( props.entity.type == EntityType.NUMERICAL ) {
        return <NumericalDetails
            measurement={props.measurement}
            entity={props.entity}
            refresh_filters={props.refresh_filters}
        />;
    } else {
        return <ParameterItem>
            Date filters are not implemented.
        </ParameterItem>
    }
}

export {PatientFilterEditor};
