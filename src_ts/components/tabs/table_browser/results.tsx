import {JSX, MutableRefObject, useLayoutEffect, useRef} from 'react';
import {TableBrowserResultParameters, TableFormat} from './common';
import {report_error, UserError} from '../../../utility/error';
import 'datatables.net-dt';
import 'datatables.net-dt/css/jquery.dataTables.min.css';
import Datatable from "datatables.net-dt";
import {DownloadLink} from "../common/download_link";

interface TableBrowserResultsProps {
    parameters: TableBrowserResultParameters | null;
    onError?: () => void;
}

interface FilteredDataParameters {
    table_data: string
}

const TABLE_ID = 'table_browser_table_id';


function TableBrowserResults(props: TableBrowserResultsProps): JSX.Element {
    const container_ref = useRef<any>();
    useLayoutEffect(
        () => setup_datatable(props.parameters, container_ref),
        [props.parameters, container_ref]
    );

    if (props.parameters != null) {
        try {
            validate_parameters(props.parameters);
            return (
                <div className="card">
                    <div className="card-body">
                        <DownloadLink url={get_download_link(props.parameters)}/>
                        <div ref={container_ref}>
                        </div>
                    </div>
                </div>
            );
        } catch (e) {
            handle_error(e, props);
        }
    }
    return <div/>;
}

function validate_parameters(parameters: TableBrowserResultParameters) {
    if (parameters.measurements == null || parameters.measurements.length == 0) {
        throw new UserError('Please select at least one measurement.');
    }
    if (parameters.entities.length == 0) {
        throw new UserError('Please select one or more entities.');
    }
}

function handle_error(e: any, props: TableBrowserResultsProps) {
    if (e instanceof UserError) {
        report_error(e);
        if (props.onError) {
            props.onError();
        }
    } else {
        throw e;
    }
}

function setup_datatable(
    parameters: TableBrowserResultParameters | null,
    container_ref: MutableRefObject<any>
) {
    if ( !parameters ) {
        return;
    }
    container_ref.current.innerHTML = `<table width="100%" id="${TABLE_ID}" class="display"></table>`;
    const url = `/filtered_data/${parameters.format}`;
    const column = define_table_columns(parameters);
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
        container_ref.current.innerHTML = '';
    };
}

function define_table_columns(parameters: TableBrowserResultParameters) {
    let column = [
        {data: 'patient_id', title: 'patient_id'},
        {data: 'measurement', title: 'measurement'},
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
    const base_url = parameters.format == TableFormat.Flat ?
        '/filtered_data/flat_csv?' : '/filtered_data/by_measurement_csv?';
    const search_params = new URLSearchParams({
        data: JSON.stringify({
            measurements: parameters.measurements,
            entities: parameters.entities.map(x => x.key),
        })
    });
    return base_url + search_params;
}

export {TableBrowserResults};
