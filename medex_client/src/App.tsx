import {useEffect, useState} from 'react';
import $ from 'jquery';
import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.css';
import './App.css'
import {NavigationBar, NavigationTab} from "./components/navigation.tsx";
import {PatientFilter} from "./components/patient_filter.tsx";
import {StatusBar} from "./components/status_bar.tsx";
import {SelectedTab} from "./components/tabs/selected_tab.tsx";
import {get_message} from "./services/message_catalog.ts";
import {HeadlineTitle} from "./components/headline_title.tsx";
import {AppConfig, get_app_config} from "./services/app_config.ts";


declare global {
    interface Window {
        jQuery: (x: unknown) => unknown;
        JQuery: (x: unknown) => unknown;
    }
}

window.JQuery = $;
window.jQuery = $;

function App() {
    const [active_tab, set_active_tab] = useState(NavigationTab.TableBrowser);
    const [nav_tabs, set_nav_tabs] = useState<NavigationTab[]>([NavigationTab.TableBrowser])
    useEffect(() => {
        async function setup() {
            set_nav_tabs(get_navigation_bars(await get_app_config()))
        }
        setup().catch(e => console.log(`Failed to setup nab bar: ${e}`))
    }, []);

    const sidebar = active_tab == NavigationTab.Tutorial ? null : <PatientFilter/>;

    useEffect(() => { get_message('window_title').then(x => document.title = x) })

    return (
        <div id="page" className="mx-4">
            <HeadlineTitle />
            <NavigationBar active_tab={active_tab} set_active_tab={set_active_tab} all_tabs={nav_tabs}/>
            <StatusBar/>
            <div className="frame-container">
                {sidebar}
                <SelectedTab tab={active_tab} />
            </div>
        </div>
    )
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
        {tab: N.TableBrowser, switch: true},
        {tab: N.BasicStats, switch: f.basic_stats},
        {tab: N.ScatterPlot, switch: f.scatter_plot},
        {tab: N.Barchart, switch: f.barchart},
        {tab: N.Histogram, switch: f.histogram},
        {tab: N.Boxplot, switch: f.boxplot},
        {tab: N.HeatMap, switch: f.heatmap}
    ]

    return map.filter(x => x.switch).map(x => x.tab)
}

export default App
