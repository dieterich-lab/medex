import {Entity, EntityType} from "../../../services/entity";
import {MutableRefObject, useLayoutEffect, useRef} from "react";
import {DownloadLink} from "../common/download_link";
import Datatable from "datatables.net-dt";

interface EntityStatsParameters {
    entities: Entity[],
    measurements: string[],
}

interface EntityStatsResultsProps {
    entityType: EntityType,
    parameters: EntityStatsParameters | null,
}

function EntityStatsResults(props: EntityStatsResultsProps) {
    const container_ref = useRef<any>();
    const descriptor = get_descriptor(props.entityType);
    useLayoutEffect(
        () => {
            if ( props.parameters ) {
                setup_datatable(props.parameters, container_ref, descriptor);
            }
        },
        [props.parameters, container_ref, descriptor]
    );

    const params = props.parameters;
    if ( params == null ) {
        return <div/>;
    }
    if ( params.measurements.length == 0 || params.entities.length == 0 ) {
        return <div>Nothing selected</div>;
    }

    return (
        <div>
            <DownloadLink url={get_download_link(params, descriptor)}/>
            <div ref={container_ref}>
            </div>
        </div>
    );
}

function get_descriptor(entity_type: EntityType): TabDescriptor {
    const descriptor = ENTITY_TYPE_TO_DESCRIPTOR_MAP.get(entity_type);
    if ( ! descriptor ) {
        throw new Error('Not implemented!');
    }
    return descriptor;
}

interface TabDescriptor {
    name: string,
    table_columns: ColumnDescriptor[],
}

interface ColumnDescriptor {
    data: string,
    title: string,
}

const DEFAULT_TABLE_COLUMNS: ColumnDescriptor[] = [
    {data: 'key', title: 'Entity'},
    {data: 'measurement', title: 'Visit'},
    {data: 'count', title: 'Counts'},
    {data: 'count NaN', title: 'Counts NaN'},
];

const NUMERICAL_TABLE_COLUMNS:ColumnDescriptor[] = [
    {data: 'key', title: 'Entity'},
    {data: 'measurement', title: 'Visit'},
    {data: 'count', title: 'Counts'},
    {data: 'count NaN', title: 'Counts NaN'},
    {data: 'min', title: 'Min'},
    {data: 'max', title: 'Max'},
    {data: 'mean', title: 'Mean'},
    {data: 'median', title: 'Median'},
    {data: 'stddev', title: 'Std. Deviation'},
    {data: 'stderr', title: 'Std. Error'},
];

const ENTITY_TYPE_TO_DESCRIPTOR_MAP = new Map<EntityType, TabDescriptor>([
    [EntityType.NUMERICAL, {
        'name': 'numerical',
        'table_columns': NUMERICAL_TABLE_COLUMNS,
    }],
    [EntityType.CATEGORICAL, {
        'name': 'categorical',
        'table_columns': DEFAULT_TABLE_COLUMNS,
    }],
    [EntityType.DATE, {
        'name': 'date',
        'table_columns': DEFAULT_TABLE_COLUMNS,
    }]
]);

interface BasicStatsData {
    basic_stats_data: string
}

function setup_datatable(
    params: EntityStatsParameters,
    container_ref: MutableRefObject<any>,
    descriptor: TabDescriptor,
) {
    const table_id = get_table_id(descriptor.name);
    if ( container_ref.current ) {
        container_ref.current.innerHTML = `<table width="100%" id="${table_id}" class="display"></table>`;
    }
    const datatable = new Datatable(`#${table_id}`, {
        destroy: true,
        processing: true,
        info: false,
        serverSide: true,
        paging: false,
        ordering: false,
        ajax: {
            url: `/basic_stats/${descriptor.name}`,
            data: function (raw_data: BasicStatsData) {
                raw_data.basic_stats_data = get_basic_stats_data(params);
            },
        },
        columns: descriptor.table_columns,
        columnDefs: [
            {
                targets: [4, 5, 6, 7, 8, 9],
                render: format_number,
            }
        ],
        dom: 'lrtip',
    });
    return () => {
        datatable.destroy();
        if ( container_ref.current ) {
            container_ref.current.innerHTML = '';
        }
    };
}

function get_table_id(name: string): string {
    return `entity_stats_${name}_table_id`;
}

function get_basic_stats_data(params: EntityStatsParameters): string {
    return JSON.stringify({
        measurements: params.measurements,
        entities: params.entities.map(x => x.key),
    });
}

function get_download_link(params: EntityStatsParameters, descriptor: TabDescriptor): string {
    const name = descriptor.name;
    const search_params = new URLSearchParams({
        basic_stats_data: get_basic_stats_data(params),
    });
    return `/basic_stats/${ name }_csv?${ search_params }`;
}

function format_number(data: any, _type: any, _row: any) {
    if ( data === null ) {
        return 'n/a'
    } else {
        return Math.round(100 * data) / 100;
    }
}

export {EntityStatsResults, EntityStatsParameters, EntityStatsResultsProps}
