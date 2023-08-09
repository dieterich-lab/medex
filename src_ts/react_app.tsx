import {createRoot} from 'react-dom/client';
import {useEffect, useState} from 'react';
import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.css';
import './resources/style.css';
import $ from 'jquery';
import {NavigationBar, NavigationTab} from './components/navigation';
import {PatientFilter} from './components/patient_filter';
import {ErrorMessage} from "./components/error_message";
import {init_error_handling} from "./utility/error";
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
    const [active_tab, set_active_tab] = useState(NavigationTab.TableBrowser)
    const [error_message, set_error_message] = useState<string|null>(null);

    useEffect(() => {
        init_error_handling(set_error_message);
    }, [set_error_message])

    const sidebar = active_tab == NavigationTab.Tutorial ? null : <PatientFilter/>;

    return (
        <div id="page" className="mx-4">
            <NavigationBar active_tab={active_tab} set_active_tab={set_active_tab}/>
            <ErrorMessage message={error_message}/>
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
