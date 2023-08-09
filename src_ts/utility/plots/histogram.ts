import {AbstractPlotParameters, SimpleAbstractPlot} from "./abstract_plot";
import {Entity} from "../../services/entity";
import {get_measurement_info} from "../../services/measurement";

interface HistogramParameters extends AbstractPlotParameters {
    measurements: string[],
    numerical_entity: Entity | null,
    group_by_entity: Entity | null,
    categories: string[] | null,
    number_of_bins: number,
}

class HistogramDescriptor extends SimpleAbstractPlot<HistogramParameters> {
    check_for_errors(params: HistogramParameters): string|null {
        if ( !params.measurements || params.measurements.length == 0 ) {
            return `Please select one or more measurements.`;
        }
        if ( !params.numerical_entity ) {
            return 'Please select the numerical entity.';
        }
        if ( !params.group_by_entity) {
            return 'Please select the "Group by" entity.';
        }
        if ( !params.categories?.length ) {
            return 'Please select one or more subcategories.';
        }
        if ( params.number_of_bins <= 0 ) {
            return 'Please select a positive number of bins.';
        }
        return null;
    }

    get_json_link(params: HistogramParameters): string {
        const query_parameters = this.get_parameter_string(params);
        return `/histogram/json?${query_parameters}`;
    }

    get_download_link(params: HistogramParameters): string {
        const query_parameters = this.get_parameter_string(params);
        return `/histogram/download?${query_parameters}`;
    }

    private get_parameter_string(params: HistogramParameters): URLSearchParams {
        return new URLSearchParams({
            histogram_data: JSON.stringify({
                measurements: params.measurements,
                numerical_entity: params.numerical_entity?.key,
                categorical_entity: params.group_by_entity?.key,
                categories: params.categories,
                bins: params.number_of_bins,
            })
        });
    }

    get_download_file_name(): string {
        return 'histogram.svg';
    }

    initialize_parameters(params: HistogramParameters|null, set_params: (value: HistogramParameters) => void) {
        if ( params != null ) {
            return;
        }
        get_measurement_info().then(info => {
            set_params({
                filter_status_revision: 0,
                measurements: info.values,
                numerical_entity: null,
                group_by_entity: null,
                categories: null,
                number_of_bins: 20,
            });
        });
    }
}

export {HistogramParameters, HistogramDescriptor};
