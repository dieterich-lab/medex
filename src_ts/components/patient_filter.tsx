import {useEffect, useState} from 'react';
import {FilterStatus, get_filter_status} from '../services/patient_filter';
import {PatientFilterEditor} from './patient_filter/editor';
import {PatientFilterStatus} from './patient_filter/status';
import {clear_busy, report_busy} from "../utility/user_feedback";

function PatientFilter() {
    const [active_filters, set_active_filters] = useState<FilterStatus|null>(null);

    const refresh_filters = async () => {
        report_busy('Refreshing filters ...');
        set_active_filters(await get_filter_status());
        clear_busy();
    }

    useEffect(() => {
        get_filter_status()
            .then((x) => set_active_filters(x))
    },[]);

    return (
        <div className="patient-filter-frame">
            <PatientFilterEditor refresh_filters={refresh_filters}/>
            <PatientFilterStatus active_filters={active_filters} refresh_filters={refresh_filters}/>
        </div>
    );
}

export {PatientFilter};