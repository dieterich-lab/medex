"use client";

import {JSX, RefObject, useEffect, useLayoutEffect, useRef, useState} from 'react';
import {TableBrowserResultParameters, TableFormat} from './common';
import 'datatables.net-dt';
import 'datatables.net-dt/css/jquery.dataTables.min.css';
import Datatable from "datatables.net-dt";
import {DownloadLink} from "../common/download_link";
import {ResultFrame} from "../common/result_frame";
import {BASE_URL} from "../../../utility/http";
import {get_message} from "../../../services/message_catalog.ts";

interface TableBrowserResultsProps {
    parameters: TableBrowserResultParameters | null;
    onError?: () => void;
}

interface FilteredDataParameters {
    table_data: string
}

const TABLE_ID = 'table_browser_table_id';


function TableBrowserResults(props: TableBrowserResultsProps): JSX.Element {
    const container_ref = useRef<HTMLDivElement>(null);
    const error_message = props.parameters ? check_for_errors(props.parameters) : null;
    const [patient_id_label, set_patient_id_label] = useState<string>('patient_id')
    const [measurement_label, set_measurement_label] = useState<string>('measurement')
    useLayoutEffect(
        () => setup_datatable(props.parameters, container_ref, error_message, patient_id_label, measurement_label),
        [props.parameters, container_ref, error_message, patient_id_label, measurement_label]
    );
    useEffect(() => {
            async function setup() {
                set_patient_id_label(await get_message('patient_id'))
                set_measurement_label(await get_message('measurement'))
            }
            setup().catch(e=> console.log(`Failed to load message catalog: ${e}`))
        }, []
    )

    if ( props.parameters == null ) {
        return <div/>;
    }
    if ( error_message ) {
        return <ResultFrame>{error_message}</ResultFrame>;
    }
    return (
        <ResultFrame>
            <DownloadLink url={get_download_link(props.parameters)}/>
            <div ref={container_ref}>
            </div>
        </ResultFrame>
    );
}

function check_for_errors(parameters: TableBrowserResultParameters): string | null {
    if (parameters.measurements == null || parameters.measurements.length == 0) {
        return 'Please select at least one measurement.';
    }
    if (parameters.entities.length == 0) {
        return 'Please select one or more entities.';
    }
    return null;
}

function setup_datatable(
    parameters: TableBrowserResultParameters | null,
    container_ref: RefObject<HTMLDivElement>,
    error_message: string | null,
    patient_id_label: string,
    measurement_label: string
) {
    if ( !parameters || error_message ) {
        return;
    }
    if ( container_ref.current !== null ) {
        container_ref.current.innerHTML = `<table width="100%" id="${TABLE_ID}" class="display"></table>`;
    }
    const url = `${BASE_URL}/filtered_data/${parameters.format}`;
    const column = define_table_columns(parameters, patient_id_label, measurement_label);
    const datatable = new Datatable(`#${TABLE_ID}`, {
        destroy: true,
        processing: true,
        serverSide: true,
        ajax: {
            url: url,
            data: (raw_data: FilteredDataParameters) => {
                raw_data.table_data = JSON.stringify({
                    measurements: parameters.measurements,
                    entities: parameters.entities.map(x => x.key),
                });
            },
        },
        columns: column,
        dom: 'lrtip',
        scrollX: true,
        pagingType: 'full_numbers',
        lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
    });

    return () => {
        datatable.destroy();
        if ( container_ref.current ) {
            container_ref.current.innerHTML = '';
        }
    };
}

function define_table_columns(
    parameters: TableBrowserResultParameters,
    patient_id_label: string,
    measurement_label: string
) {
    let column = [
        {data: 'patient_id', title: patient_id_label},
        {data: 'measurement', title: measurement_label},
    ]
    if (parameters.format == TableFormat.Flat) {
        column = column.concat([
            {data: 'key', title: 'key'},
            {data: 'value', title: 'value'},
        ]);
    } else {
        const entity_columns = parameters.entities.map((x) => {
            return {data: `${x.key}`, title: `${x.key}`};
        });
        column = column.concat(entity_columns);
    }
    return column;
}

function get_download_link(parameters: TableBrowserResultParameters) {
    const path = parameters.format == TableFormat.Flat ?
        '/filtered_data/flat_csv?' : '/filtered_data/by_measurement_csv?';
    const search_params = new URLSearchParams({
        data: JSON.stringify({
            measurements: parameters.measurements,
            entities: parameters.entities.map(x => x.key),
        })
    });
    return BASE_URL + path + search_params;
}

export {TableBrowserResults};
