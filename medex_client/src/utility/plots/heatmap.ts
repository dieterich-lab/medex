import {AbstractPlotParameters, SimpleAbstractPlot} from "./abstract_plot";
import {Entity} from "../../services/entity";

interface HeatmapParameters extends AbstractPlotParameters {
    numerical_entities: Entity[] | null,
}

class HeatmapDescriptor extends SimpleAbstractPlot<HeatmapParameters> {
    check_for_errors(params: HeatmapParameters): string|null {
        if ( !params.numerical_entities || params.numerical_entities.length < 2 ) {
            return 'Please select multiple entities.';
        }
        return null;
    }

    get_json_link(params: HeatmapParameters): string {
        const query_parameters = this.get_parameter_string(params);
        return `/heatmap/json?${query_parameters}`;
    }

    get_download_link(params: HeatmapParameters): string {
        const query_parameters = this.get_parameter_string(params);
        return `/heatmap/download?${query_parameters}`;
    }

    private get_parameter_string(params: HeatmapParameters): URLSearchParams {
        return new URLSearchParams({
            heatmap_data: JSON.stringify({
                entities: params.numerical_entities?.map(x => x.key),
            })
        });
    }

    get_download_file_name(): string {
        return 'heatmap.svg';
    }

    initialize_parameters(params: HeatmapParameters|null, set_params: (value: HeatmapParameters) => void) {
        if ( params == null ) {
            set_params({
                filter_status_revision: 0,
                numerical_entities: null,
            });
        }
    }
}

export {type HeatmapParameters, HeatmapDescriptor};
