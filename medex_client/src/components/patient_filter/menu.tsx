import {PatientFilterComponentProps} from './common';
import {Dropdown} from "react-bootstrap";
import {delete_all_filters} from '../../services/patient_filter';
import {ChangeEventHandler} from "react";
import {BASE_URL, http_send_blob} from "../../utility/http";


const FILE_TO_LOAD_ID = 'patient-filter-menu-file-to-load-input';


function PatientFilterMenu(props: PatientFilterComponentProps) {
    const ask_for_file_to_load = async () => {
        document.getElementById(FILE_TO_LOAD_ID)?.click();
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

    const save_url = `${BASE_URL}/filter/save`

    return (
        <Dropdown className="btn btn-sm patient-filter-menu">
            <input
                type="file"
                id={FILE_TO_LOAD_ID}
                className="hidden"
                onChange={load_filters}
                accept=".json"
            />
            <Dropdown.Toggle id="patient-filter-menu-button">...</Dropdown.Toggle>
            <Dropdown.Menu>
                <Dropdown.Item href={save_url} id="patient-filter-menu-save">
                    Save
                </Dropdown.Item>
                <Dropdown.Item onClick={ask_for_file_to_load} id="patient-filter-menu-load">
                    Load
                </Dropdown.Item>
                <Dropdown.Item onClick={delete_all} id="patient-filter-menu-delete-all">
                    Delete all
                </Dropdown.Item>
            </Dropdown.Menu>
        </Dropdown>
    );
}

export {PatientFilterMenu};