import {Entity} from "../../services/entity";
import {AbstractPlot, AbstractPlotParameters} from "./abstract_plot";
import {get_measurement_info} from "../../services/measurement";

interface BoxplotParameters extends AbstractPlotParameters {
    measurements: string[],
    numeric_entity: Entity | null,
    group_by_entity: Entity | null,
    categories: string[] | null,
    log_scale: boolean,
}

class BoxplotDescriptor extends AbstractPlot<BoxplotParameters> {
    check_for_errors(params: BoxplotParameters): string|null {
        if ( params.measurements == null || params.measurements.length == 0 ) {
            return 'Please select one or more measurements.';
        }
        if ( params.numeric_entity == null ) {
            return 'Please select a numerical entity';
        }
        if ( params.group_by_entity == null ) {
            return 'Please select the "Group by" entity.';
        }
        if ( params.categories == null || params.categories.length == 0 ) {
            return 'Please select one or more subcategories';
        }
        return null;
    }

    get_json_link(params: BoxplotParameters): string {
        const query_parameters = this.get_parameter_string(params);
        return `/boxplot/json?${query_parameters}`;
    }

    get_download_link(params: BoxplotParameters): string {
        const query_parameters = this.get_parameter_string(params);
        return `/boxplot/download?${query_parameters}`;
    }

    private get_parameter_string(params: BoxplotParameters): URLSearchParams {
        return new URLSearchParams({
            boxplot_data: JSON.stringify({
                measurements: params.measurements,
                numerical_entity: params.numeric_entity?.key,
                categorical_entity: params.group_by_entity?.key,
                categories: params.categories,
                plot_type: params.log_scale ? 'log' : 'linear',
            })
        });
    }

    get_download_file_name(): string {
        return 'boxplot.svg';
    }

    initialize_parameters(params: BoxplotParameters|null, set_params: (value: BoxplotParameters) => void) {
        if ( params != null ) {
            return;
        }
        get_measurement_info().then(info => {
            set_params({
                filter_status_revision: 0,
                measurements: info.values,
                numeric_entity: null,
                group_by_entity: null,
                categories: null,
                log_scale: false,
            });
        });
    }

    get_plot_data_from_response_data(data: any) {
        return [
            {data: data.table_json.data, layout: data.table_json.layout},
            {data: data.image_json.data, layout: data.image_json.layout},
        ];
    }
}

export {BoxplotDescriptor, BoxplotParameters};
