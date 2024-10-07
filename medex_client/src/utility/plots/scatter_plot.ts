import {Entity} from "../../services/entity";
import {SimpleAbstractPlot, AbstractPlotParameters} from "./abstract_plot";
import {get_measurement_info} from "../../services/measurement";

interface ScatterPlotParameters extends AbstractPlotParameters {
    x_measurement: string | null,
    x_entity: Entity | null,
    x_log_scale: boolean,
    y_measurement: string | null,
    y_entity: Entity | null,
    y_log_scale: boolean,
    categorical_entity: Entity | null,
    categories: string[] | null,
}

class ScatterPlotDescriptor extends SimpleAbstractPlot<ScatterPlotParameters> {
    check_for_errors(params: ScatterPlotParameters): string|null {
        if ( ! params.x_measurement ) {
            return 'Please select measurement for X axis.';
        }
        if ( ! params.x_entity ) {
            return 'Please select entity for X axis.';
        }
        if ( ! params.y_measurement ) {
            return 'Please select measurement for Y axis.';
        }
        if ( ! params.y_entity ) {
            return 'Please select entity for Y axis.';
        }
        if ( params.x_measurement == params.y_measurement && params.x_entity == params.y_entity ) {
            return "You can't compare same entity for the same measurement.";
        }
        if ( params.categorical_entity && ( params.categories == null || params.categories.length == 0 ) ) {
            return "Please select at least one category to group by.";
        }
        return null;
    }

    get_json_link(params: ScatterPlotParameters): string {
        const query_parameters = this.get_parameter_string(params);
        return `/scatter_plot/json?${query_parameters}`;
    }

    get_download_link(params: ScatterPlotParameters): string {
        const query_parameters = this.get_parameter_string(params);
        return `/scatter_plot/download?${query_parameters}`;
    }

    private get_parameter_string(params: ScatterPlotParameters): URLSearchParams {
        return new URLSearchParams({
            scatter_plot_data: JSON.stringify({
                measurement_x_axis: params.x_measurement,
                entity_x_axis: params.x_entity?.key,
                measurement_y_axis: params.y_measurement,
                entity_y_axis: params.y_entity?.key,
                scale: {
                    log_x: params.x_log_scale,
                    log_y: params.y_log_scale,
                },
                add_group_by: params.categorical_entity == null ? undefined : {
                    key: params.categorical_entity.key,
                    categories: params.categories,
                }
            })
        });
    }

    get_download_file_name(): string {
        return 'scatter_plot.svg';
    }

    initialize_parameters(params: ScatterPlotParameters|null, set_params: (value: ScatterPlotParameters) => void) {
        if ( params != null ) {
            return;
        }
        get_measurement_info().then(info => {
            set_params({
                filter_status_revision: 0,
                x_measurement: info.values[0],
                x_entity: null,
                x_log_scale: false,
                y_measurement: info.values[0],
                y_entity: null,
                y_log_scale: false,
                categorical_entity: null,
                categories: null,
            });
        });
    }
}

export {ScatterPlotDescriptor, type ScatterPlotParameters};
