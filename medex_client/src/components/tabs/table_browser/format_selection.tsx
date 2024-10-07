import {TableFormat} from "./common";
import {ParameterItem} from "../../common/parameter_item";
import {RadioButtons} from "../../common/radio_buttons";
import {JSX} from "react";

interface TableBrowserFormatRadioProps {
    format: TableFormat,
    onChange: (format: TableFormat) => void,
}


const TABLE_TYPE_MAP: Map<TableFormat, JSX.Element> = new Map([
    [TableFormat.Flat, <div>long format / one row per value</div>],
    [TableFormat.ByMeasurement, <div>entities as columns</div>],
])

function TableBrowserFormatSelection(props: TableBrowserFormatRadioProps) {
    return (
        <ParameterItem>
            <RadioButtons
                value={props.format}
                onChange={props.onChange}
                label_by_value={TABLE_TYPE_MAP} />
        </ParameterItem>
    );
}

export {TableBrowserFormatSelection};
