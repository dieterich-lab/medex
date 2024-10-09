/**
 * @vitest-environment jsdom
 */

import {test, expect, vi} from "vitest";
import {fireEvent, render} from '@testing-library/react';
import {PatientFilterStatus} from './status';
import {FilterStatus, delete_all_filters, CategoricalFilter, NumericalFilter} from "../../services/patient_filter.ts";

vi.mock('../../services/patient_filter');

test('PatientFilterStatus - null', () => {

    const {container} = render(
        <PatientFilterStatus active_filters={null} refresh_filters={() => {}}/>
    );
    const file_input = container.querySelector('#patient-filter-menu-file-to-load-input') as Element;
    const file_input_click_handler = vi.fn();
    file_input.addEventListener('click', file_input_click_handler);

    const menu_button = container.querySelector('#patient-filter-menu-button') as Element;
    fireEvent.click(menu_button);

    expect(delete_all_filters).toBeCalledTimes(0)
    const delete_all_button = container.querySelector('#patient-filter-menu-delete-all') as Element;
    fireEvent.click(delete_all_button);
    expect(delete_all_filters).toBeCalledTimes(1);

    expect(file_input_click_handler).toHaveBeenCalledTimes(0);
    const load_button = container.querySelector('#patient-filter-menu-load') as Element;
    fireEvent.click(load_button);
    expect(file_input_click_handler).toHaveBeenCalled();
});

test('PatientFilterStatus - simple filter', () => {
    const cat_filter: CategoricalFilter = {
        entity_key: 'xyz', measurement: null, categories: ['a', 'b', 'c']
    };
    const num_filter: NumericalFilter = {
        entity_key: 'one', measurement: 'base', from_value: 17, to_value: 18
    };
    const filter_status: FilterStatus = {
        filtered_patient_count: 11,
        filters: new Map<string, NumericalFilter|CategoricalFilter>([
            ['xyz', cat_filter],
            ['one', num_filter]
        ])
    };

    const {getByText} = render(
        <PatientFilterStatus active_filters={filter_status} refresh_filters={() => {}}/>
    );

    expect(getByText(/xyz/)).toBeInTheDocument()
});