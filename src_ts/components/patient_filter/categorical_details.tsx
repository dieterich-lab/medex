import {PatientFilterEntityDetailsProps} from './common';
import {AddOrUpdateButton} from './add_or_update_button';
import {useState} from 'react';
import {add_or_update_categorical_filter} from '../../services/patient_filter';
import {CategorySelect} from '../common/category_select';

function CategoricalDetails(props: PatientFilterEntityDetailsProps) {
    const [categories, set_categories] = useState<string[]>([]);

    const button_action = async () => {
        await add_or_update_categorical_filter(
            props.entity.key,
            categories,
            props.measurement
        );
        props.refresh_filters();
    };

    return (
        <div>
            <CategorySelect entity={props.entity} onChange={set_categories} values={categories} />
            <AddOrUpdateButton on_click={button_action}/>
        </div>
    );
}

export {CategoricalDetails};
