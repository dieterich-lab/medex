'use client';
import {NavigationButton} from './naviagtion_button';

enum NavigationTab {
    Tutorial = 'Tutorial',
    TableBrowser = 'Table Browser',
    BasicStats = ' Basic Stats',
    ScatterPlot = 'Scatter Plot',
    Barchart = 'Barchart',
    Histogram = 'Histogram',
    Boxplot = 'Boxplot',
    HeatMap = 'Heatmap',
}


// We will fix that once were is a better solution to get the keys
// of an enum ...
// See https://github.com/microsoft/TypeScript/issues/17198
const NAVIGATION_ITEMS = [
    NavigationTab.Tutorial,
    NavigationTab.TableBrowser,
    NavigationTab.BasicStats,
    NavigationTab.ScatterPlot,
    NavigationTab.Barchart,
    NavigationTab.Histogram,
    NavigationTab.Boxplot,
    NavigationTab.HeatMap,
]

interface NavigationBarProps {
    active_tab: NavigationTab,
    set_active_tab: (x: NavigationTab) => void
}

function NavigationBar(props: NavigationBarProps) {
    return (
        <nav id="nav_bar" className="navbar navbar-light bg-light">
            <ul className="nav nav-pills mx-auto">
                {
                    NAVIGATION_ITEMS.map(x =>
                        <NavigationButton
                            id={get_nav_button_id(x)}
                            key={x}
                            on_click={() => props.set_active_tab(x)}
                            is_active={props.active_tab === x}
                        >
                            {x.valueOf()}
                        </NavigationButton>
                    )
                }
            </ul>
        </nav>
    )
}

function get_nav_button_id(x: NavigationTab) {
    // NavigationTab.TableBrowser -> 'nav_button_table_browser'
    return 'nav_button_' + (x as string).toLowerCase().replace(' ', '_');
}

export {NavigationBar, NavigationTab}