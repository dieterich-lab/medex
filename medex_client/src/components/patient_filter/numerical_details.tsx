import {PatientFilterEntityDetailsProps} from './common';
import {useEffect, useState} from 'react';
import {add_or_update_numerical_filter} from '../../services/patient_filter';
import {AddOrUpdateButton} from './add_or_update_button';
import {RangeSlider} from '../common/range_slider';


interface Values {
    from_value: number,
    to_value: number,
}


function NumericalDetails(props: PatientFilterEntityDetailsProps) {
    if ( props.entity?.min == null || props.entity?.max == null ) {
        throw new Error('Internal Error: NumericalDetails called for non-numerical entity!');
    }
    const [values, set_values] = useState<Values>({
        from_value: props.entity.min,
        to_value: props.entity.max
    });
    useEffect(() => {
            if ( props?.entity.min != undefined && props?.entity.max != undefined ) {
                set_values({
                    from_value: props.entity.min,
                    to_value: props.entity.max
                });
            }
        }, [props.entity]
    )
    const on_change = (from_value: number, to_value: number) => set_values({
        from_value: from_value,
        to_value: to_value}
    );

    const button_action = async () => {
        await add_or_update_numerical_filter(
            props.entity.key,
            values.from_value,
            values.to_value,
            props.measurement
        );
        props.refresh_filters();
    };

    return (
        <div>
            <RangeSlider
                from_value={values.from_value}
                to_value={values.to_value}
                min={props.entity.min}
                max={props.entity.max}
                on_change={on_change}
            />
            <AddOrUpdateButton on_click={button_action}/>
        </div>
    );
}

export {NumericalDetails};
