import {PatientFilterComponentProps} from './common';
import {delete_filter} from '../../services/patient_filter';

interface PatientFilterDeleteButtonProps extends PatientFilterComponentProps {
    entity_key: string,
}

function PatientFilterDeleteButton(props: PatientFilterDeleteButtonProps) {
    const action = async () => {
        await delete_filter(props.entity_key);
        await props.refresh_filters();
    }

    return (
        <button
            type="button" className="btn btn-outline-info btn-sm patient-filter-delete-button"
            onClick={action}
        >
            Delete
        </button>
    );

}

export {PatientFilterDeleteButton};
