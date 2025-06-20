import {test, expect} from "vitest";
import {capitalize} from "./misc";

test('capitalize', () => {
    expect(capitalize('test')).toBe('Test');
    expect(capitalize('Test')).toBe('Test');
    expect(capitalize('TEST')).toBe('TEST');
    expect(capitalize('test test')).toBe('Test test');
});