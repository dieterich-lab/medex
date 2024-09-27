import {PatientFilterComponentProps} from './common';
import {Dropdown} from "react-bootstrap";
import {delete_all_filters} from '../../services/patient_filter';
import {ChangeEventHandler, useId} from "react";
import {http_send_blob} from "../../utility/http";


function PatientFilterMenu(props: PatientFilterComponentProps) {
    const file_to_load_id = useId();
    const ask_for_file_to_load = async () => {
        document.getElementById(file_to_load_id)?.click();
    }

    const load_filters: ChangeEventHandler<HTMLInputElement> = async (event) => {
        const files = event?.target?.files;
        if ( files !== null && files?.length > 0) {
            await http_send_blob('' +
                '/filter/load',
                files[0],
                'application/json',
                'loading filters'
            ).catch(() => {})
            props.refresh_filters();
        }
    }

    const delete_all = async () => {
        await delete_all_filters();
        props.refresh_filters();
    }

    return (
        <Dropdown className="btn btn-sm patient-filter-menu">
            <input
                type="file"
                id={file_to_load_id}
                className="hidden"
                onChange={load_filters}
                accept=".json"
            />
            <Dropdown.Toggle>...</Dropdown.Toggle>
            <Dropdown.Menu>
                <Dropdown.Item href="/filter/save">
                    Save
                </Dropdown.Item>
                <Dropdown.Item onClick={ask_for_file_to_load}>
                    Load
                </Dropdown.Item>
                <Dropdown.Item onClick={delete_all}>
                    Delete all
                </Dropdown.Item>
            </Dropdown.Menu>
        </Dropdown>
    );
}

export {PatientFilterMenu};