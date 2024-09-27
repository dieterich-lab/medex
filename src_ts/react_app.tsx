import {createRoot} from 'react-dom/client';
import {useState} from 'react';
import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.css';
import './resources/style.css';
import $ from 'jquery';
import {NavigationBar, NavigationTab} from './components/navigation';
import {PatientFilter} from './components/patient_filter';
import {StatusBar} from "./components/status_bar";
import {SelectedTab} from "./components/tabs/selected_tab";

declare global {
    interface Window {
        jQuery: (x: any) => any;
        JQuery: (x: any) => any;
    }
}

window.JQuery = $;
window.jQuery = $;

function ReactApp() {
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

const root_node = document.getElementById('react_app') as Element;
const root = createRoot(root_node);
root.render(<ReactApp/>);
