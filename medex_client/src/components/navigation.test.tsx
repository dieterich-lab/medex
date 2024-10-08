/**
 * @vitest-environment jsdom
 */

import {test, expect} from "vitest";
import {fireEvent, render} from '@testing-library/react';
import {NavigationBar, NavigationTab} from './navigation';


test('simple nav check', () => {
    let active_tab: NavigationTab = NavigationTab.TableBrowser;

    const {container} = render(
        <NavigationBar active_tab={active_tab} set_active_tab={(x) => active_tab = x}/>
    );
    const table_browser_button = container.querySelector('#nav_button_table_browser') as Element;
    const heatmap_button = container.querySelector('#nav_button_heatmap') as Element;

    expect(table_browser_button.classList.contains('active'));
    expect(!heatmap_button.classList.contains('active'));

    fireEvent.click(heatmap_button);

    expect(active_tab).toBe(NavigationTab.HeatMap);
    expect(!table_browser_button.classList.contains('active'));
    expect(heatmap_button.classList.contains('active'));
});