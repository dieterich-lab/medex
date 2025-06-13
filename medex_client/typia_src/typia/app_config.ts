import {assertEquals} from "typia";

interface AppConfig {
    features: {
        tutorial: boolean,
        table_browser: boolean,
        basic_stats:  boolean,
        scatter_plot:  boolean,
        barchart:  boolean,
        histogram:  boolean,
        boxplot: boolean,
        heatmap: boolean
    }
}

function to_app_config(x: unknown): AppConfig {
    return assertEquals<AppConfig>(x);
}

export {to_app_config, type AppConfig};
