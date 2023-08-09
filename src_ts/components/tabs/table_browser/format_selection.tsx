import {JSX} from "react";
import {TableFormat} from "./common";
import {ParameterItem} from "../../common/parameter_item";
import {RadioButtons} from "../../common/radio_buttons";

interface TableBrowserFormatRadioProps {
    format: TableFormat,
    onChange: (format: TableFormat) => void,
}


const LABELS_BY_VALUE: Map<TableFormat, JSX.Element> = new Map([
    [TableFormat.Flat, <div>long format / one row per value</div>],
    [TableFormat.ByMeasurement, <div>entities as columns</div>],
])

function TableBrowserFormatSelection(props: TableBrowserFormatRadioProps) {
    return (
        <ParameterItem>
            <RadioButtons
                value={props.format}
                onChange={props.onChange}
                labels_by_value={LABELS_BY_VALUE} />
        </ParameterItem>
    );
}

export {TableBrowserFormatSelection};
