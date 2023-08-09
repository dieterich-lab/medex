import {get_measurement_info} from "../services/measurement";
import {Option} from "react-multi-select-component";
import {get_options_from_strings} from "./selection";

interface MeasurementSelectionState {
    options: Option[],
    display_name: string,
}

function populate_measurement_selection_state(
    set_state: (x: MeasurementSelectionState|null) => void,
    old_state: MeasurementSelectionState|null,
    plural_flag: boolean,
) {
    if ( old_state ) {
        return;
    }
    get_measurement_info().then(
        (info) => set_state({
            options: get_options_from_strings(info.values),
            display_name: info.get_display_name(plural_flag),
        })
    );
}

export {MeasurementSelectionState, populate_measurement_selection_state};