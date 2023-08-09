import {PatientFilterComponentProps} from './common';
import {delete_all_filters} from '../../services/patient_filter';

function PatientFilterDeleteAllButton(props: PatientFilterComponentProps) {
    const action = async () => {
        await delete_all_filters();
        await props.refresh_filters();
    }

    return (
        <button type="button" className="btn btn-sm btn-outline-info patient-filter-all-delete-button"
             onClick={action}
        >
            Delete All
        </button>
    );
}

export {PatientFilterDeleteAllButton};