import {get_label} from "./misc";

test('get_label', () => {
    expect(get_label('default_label', 'custom_label')).toBe('custom_label');
    expect(get_label('default_label', undefined)).toBe('default_label');
    expect(get_label('default_label', 'custom %DEFAULT%')).toBe('custom default_label');
});