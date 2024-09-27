import {JSX} from "react";
import {FilterStatus} from '../../services/patient_filter';
import {PatientFilterComponentProps} from './common';
import {PatientFilterItem} from './item'
import {PatientFilterMenu} from "./menu";

interface PatientFilterStatusProps extends PatientFilterComponentProps {
    active_filters: FilterStatus|null,
}

function PatientFilterStatus(props: PatientFilterStatusProps) {
    const count_text = get_patient_filter_count_as_text(props.active_filters);
    const active_filters = get_active_filters_dom(props);
    return (
        <div className="card patient-filter-status">
            <div className="card-body">
                Active Filters {count_text}
                <PatientFilterMenu refresh_filters={props.refresh_filters}/>
            </div>
            <div>
                {active_filters}
            </div>
        </div>
    )
}

function get_patient_filter_count_as_text(filter_status: FilterStatus|null): string {
    const count = filter_status?.filtered_patient_count;
    return  count == null ? ''                     :
            count == 0    ? ' (no patients)'       :
            count == 1    ? ' (1 patient)'         :
                            ` (${count} patients)` ;
}

function get_active_filters_dom(props: PatientFilterStatusProps): JSX.Element[] {
    let results = [];
    if ( ! props.active_filters ) {
        results.push(<div/>);
    } else {
        const active_filters = props.active_filters.filters;
        active_filters.forEach((filter, entity_key) => {
            results.push(
                <PatientFilterItem
                    key={entity_key}
                    item={filter}
                    refresh_filters={props.refresh_filters}
                />
            );
        });
    }
    return results;
}

export {PatientFilterStatus};