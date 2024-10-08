import {test, expect} from "vitest";
import {get_label, capitalize} from "./misc";

test('get_label', () => {
    expect(get_label('default_label', 'custom_label')).toBe('custom_label');
    expect(get_label('default_label', undefined)).toBe('default_label');
    expect(get_label('default_label', 'custom %DEFAULT%')).toBe('custom default_label');
});

test('capitalize', () => {
    expect(capitalize('test')).toBe('Test');
    expect(capitalize('Test')).toBe('Test');
    expect(capitalize('TEST')).toBe('TEST');
    expect(capitalize('test test')).toBe('Test test');
});