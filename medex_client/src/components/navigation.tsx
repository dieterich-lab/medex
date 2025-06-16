'use client';
import {NavigationButton} from './naviagtion_button';

enum NavigationTab {
    Tutorial = 'Tutorial',
    TableBrowser = 'Table Browser',
    BasicStats = 'Basic Stats',
    ScatterPlot = 'Scatter Plot',
    Barchart = 'Barchart',
    Histogram = 'Histogram',
    Boxplot = 'Boxplot',
    HeatMap = 'Heatmap',
}

interface NavigationBarProps {
    active_tab: NavigationTab,
    set_active_tab: (x: NavigationTab) => void
    all_tabs: NavigationTab[]
}

function NavigationBar(props: NavigationBarProps) {
    return (
        <nav id="nav_bar" className="navbar navbar-light bg-light">
            <ul className="nav nav-pills mx-auto">
                {
                    props.all_tabs.map(x =>
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