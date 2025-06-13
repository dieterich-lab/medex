import {FilterStatus} from "../../typia/patient_filter.ts";
import {M} from "../common/message_catalog.tsx";

interface Props {
    filters: FilterStatus|null
}

function PatientCount(props: Props) {
    const count = props.filters?.filtered_patient_count
    switch ( count ) {
        case 0: { return <div> (no <M id="patients" />)</div>}
        case 1: { return <div> (1 <M id="patient" /></div>}
        case null: { return <div /> }
        case undefined: { return <div /> }
        default: { return <div> ({count} <M id="patients"/>)</div> }
    }
}

export {PatientCount};