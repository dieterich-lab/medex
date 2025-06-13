'use client';
import {NavigationButton} from './naviagtion_button';
import {AppConfig, get_app_config} from "../services/app_config.ts";
import {useEffect, useState} from "react";

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
}

function NavigationBar(props: NavigationBarProps) {
    const [nav_tabs, set_nav_tabs] = useState<NavigationTab[]>([NavigationTab.TableBrowser])
    useEffect(() => {
        async function setup() {
            set_nav_tabs(get_navigation_bars(await get_app_config()))
        }
        setup().catch(e => console.log(`Failed to setup nab bar: ${e}`))
    }, []);
    return (
        <nav id="nav_bar" className="navbar navbar-light bg-light">
            <ul className="nav nav-pills mx-auto">
                {
                    nav_tabs.map(x =>
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

function get_navigation_bars(app_config: AppConfig): NavigationTab[] {
    interface TabToFeatureSwitch {
        tab: NavigationTab
        switch: boolean
    }
    const f = app_config.features
    const N = NavigationTab
    const map: TabToFeatureSwitch[] = [
        {tab: N.Tutorial, switch: f.tutorial},
        {tab: N.TableBrowser, switch: f.table_browser},
        {tab: N.BasicStats, switch: f.basic_stats},
        {tab: N.ScatterPlot, switch: f.scatter_plot},
        {tab: N.Barchart, switch: f.barchart},
        {tab: N.Histogram, switch: f.histogram},
        {tab: N.Boxplot, switch: f.boxplot},
        {tab: N.HeatMap, switch: f.heatmap}
    ]
    
    return map.filter(x => x.switch).map(x => x.tab)
}

export {NavigationBar, NavigationTab}