import {AbstractPlotParameters, SimpleAbstractPlot} from "./abstract_plot";
import {Entity} from "../../services/entity";
import {get_measurement_info} from "../../services/measurement";

enum BarchartPlotType {
    PERCENT = 'percent',
    COUNT = 'count',
}

interface BarchartParameters extends AbstractPlotParameters {
    measurements: string[],
    entity: Entity | null,
    categories: string[] | null,
    plot_type: BarchartPlotType,
}

class BarchartDescriptor extends SimpleAbstractPlot<BarchartParameters> {
    check_for_errors(params: BarchartParameters): string|null {
        if ( !params.measurements || params.measurements.length == 0 ) {
            return `Please select one or more measurements.`;
        }
        if ( !params.entity ) {
            return 'Please select the entity to group by.';
        }
        if ( !params.categories || params.categories.length == 0 ) {
            return 'Please select one or more subcategories.';
        }
        return null;
    }

    get_json_link(params: BarchartParameters): string {
        const query_parameters = this.get_parameter_string(params);
        return `/barchart/json?${query_parameters}`;
    }

    get_download_link(params: BarchartParameters): string {
        const query_parameters = this.get_parameter_string(params);
        return `/barchart/download?${query_parameters}`;
    }

    private get_parameter_string(params: BarchartParameters): URLSearchParams {
        return new URLSearchParams({
            barchart_data: JSON.stringify({
                measurements: params.measurements,
                key: params.entity?.key,
                categories: params.categories,
                plot_type: params.plot_type,
            })
        });
    }

    get_download_file_name(): string {
        return 'barchart.svg';
    }

    initialize_parameters(params: BarchartParameters|null, set_params: (value: BarchartParameters) => void) {
        if ( params != null ) {
            return;
        }
        get_measurement_info().then(info => {
            set_params({
                filter_status_revision: 0,
                measurements: info.values,
                entity: null,
                categories: null,
                plot_type: BarchartPlotType.PERCENT,
            });
        });
    }
}

export {type BarchartParameters, BarchartDescriptor, BarchartPlotType};
