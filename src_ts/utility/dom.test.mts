import {
    get_input_value_by_id, get_radio_input_by_name, get_selected_child_values_by_id, get_input_number_by_id
} from './dom.mjs';



test('get_input_value_by_id', () => {
    document.body.innerHTML = `
        <input id="bla" value="blub"/>
    `;
    expect(get_input_value_by_id('bla')).toBe('blub');
});

test('get_radio_input_by_name', () => {
    document.body.innerHTML = `
        <input type="radio" name="other_radio" value="foo" checked="checked">
        <input type="radio" name="my_radio" value="foo">
        <input type="radio" name="my_radio" value="bar" checked="checked">
    `
    expect(get_radio_input_by_name('my_radio')).toBe('bar');
});

test('get_selected_children_values_by_id', () => {
    document.body.innerHTML = `
        <select id="my_select" multiple>
            <option value="a" selected>A</option>
            <option value="b">B</option>
            <option value="c" selected>C</option>
        </select>
    `;
    expect(get_selected_child_values_by_id('my_select')).toStrictEqual(['a', 'c']);
});

test('get_input_number_by_id', () => {
    document.body.innerHTML = `
        <input id="my_number" value="1.23" />
    `;
    expect(get_input_number_by_id('my_number')).toBe(1.23);
});
