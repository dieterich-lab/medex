import {JSX} from "react";
import {FilterStatus} from '../../services/patient_filter';
import {PatientFilterComponentProps} from './common';
import {PatientFilterItem} from './item'
import {PatientFilterMenu} from "./menu";
import {PatientCount} from "./patient_count.tsx";

interface PatientFilterStatusProps extends PatientFilterComponentProps {
    active_filters: FilterStatus|null,
}

function PatientFilterStatus(props: PatientFilterStatusProps) {
    const active_filters = get_active_filters_dom(props);
    return (
        <div className="card patient-filter-status">
            <div className="card-body">
                Active Filters <PatientCount filters={props.active_filters}/>
                <PatientFilterMenu refresh_filters={props.refresh_filters}/>
            </div>
            <div>
                {active_filters}
            </div>
        </div>
    )
}

function get_active_filters_dom(props: PatientFilterStatusProps): JSX.Element[] {
    const results = [];
    if ( ! props.active_filters ) {
        results.push(<div key="empty"/>);
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