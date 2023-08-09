import {NavigationTab} from "../navigation";
import {TabFrame} from "./common/frame";
import {TableBrowser} from "./table_browser";
import {BasicStats} from "./basic_stats";
import {ScatterPlot} from "./scatter_plot";
import {Barchart} from "./barchart";
import {Boxplot} from "./boxplot";
import {Histogram} from "./histogram";
import {Heatmap} from "./heatmap";
import {Tutorial} from "./tutorial";

interface SelectedTabProps {
    tab: NavigationTab,
}

function SelectedTab(props: SelectedTabProps) {
    switch ( props.tab ) {
        case NavigationTab.Tutorial:
            return <Tutorial/>;
        case NavigationTab.TableBrowser:
            return <TableBrowser/>;
        case NavigationTab.BasicStats:
            return <BasicStats/>;
        case NavigationTab.ScatterPlot:
            return <ScatterPlot/>;
        case NavigationTab.Barchart:
            return <Barchart/>;
        case NavigationTab.Histogram:
            return <Histogram/>;
        case NavigationTab.Boxplot:
            return <Boxplot/>;
        case NavigationTab.HeatMap:
            return <Heatmap/>;
        default:
            return (
                <TabFrame>
                    <div className="card">
                        <div className="card-body">
                            Not implemented
                        </div>
                    </div>
                </TabFrame>
            );
    }
}

export {SelectedTab};