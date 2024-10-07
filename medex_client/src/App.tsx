import { useState } from 'react';
import $ from 'jquery';
import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.css';
import './App.css'
import {NavigationBar, NavigationTab} from "./components/navigation.tsx";
import {PatientFilter} from "./components/patient_filter.tsx";
import {StatusBar} from "./components/status_bar.tsx";
import {SelectedTab} from "./components/tabs/selected_tab.tsx";


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

    const sidebar = active_tab == NavigationTab.Tutorial ? null : <PatientFilter/>;

    return (
        <div id="page" className="mx-4">
            <NavigationBar active_tab={active_tab} set_active_tab={set_active_tab}/>
            <StatusBar/>
            <div className="frame-container">
                {sidebar}
                <SelectedTab tab={active_tab} />
            </div>
        </div>
    )
}

export default App
