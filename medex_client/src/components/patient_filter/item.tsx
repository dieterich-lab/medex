import {PatientFilterComponentProps} from './common';
import {CategoricalFilter, NumericalFilter} from '../../services/patient_filter';
import {PatientFilterDeleteButton} from './delete_button';

interface PatientFilterItemProps extends PatientFilterComponentProps {
    key: string,
    item: CategoricalFilter|NumericalFilter,
}

function PatientFilterItem(props: PatientFilterItemProps) {
    const measurement_text = props.item.measurement == null ? '' : ` (${props.item.measurement})`;
    const filter_text = get_filter_as_text(props.item);
    return (
        <div id={`pateint-filter-item-${props.item.entity_key}`} className="card-body patient-filter-item">
            <span>{props.item.entity_key}{measurement_text}:&nbsp;&nbsp;&nbsp;&#32;{filter_text}</span>
            <PatientFilterDeleteButton entity_key={props.item.entity_key} refresh_filters={props.refresh_filters}/>
        </div>
    );
}

function get_filter_as_text(item: CategoricalFilter|NumericalFilter) {
    if ( 'categories' in item ) {
        return item.categories.join(', ');
    }
    if ( 'from_value' in item && 'to_value' in item ) {
        return `${item.from_value} - ${item.to_value}`;
    }
    throw Error('Internal Error: patient_filter.get_filter_as_text() called with bad item!');
}

export {PatientFilterItem};
